#!/usr/bin/env python3

from multiprocessing import Process, Queue
from PIL import Image
from shapely.geometry import shape, mapping, Polygon
from urllib.error import URLError
from urllib.request import urlopen
import filecmp
import geojson
import io
import math
import numpy as np
import os
import os.path
import shutil
import sys

cmd = sys.argv[1]
tile_path = '/{zoom}/{x}/{y}.png'
tile_size = 256
max_zoom = 13
min_zoom = 5
worker_count = 4

if cmd == 'fetch':
	min_zoom = max_zoom
	mp = 'Extra2_Map' if sys.argv[2] == 'nob12' else 'TMo_TechLTE_Map'
	tile_url = 'http://maps.t-mobile.com/%s/{zoom}/{x}:{y}/tile.png' % mp
	out_dir = sys.argv[3]

	script_dir = os.path.dirname(os.path.realpath(__file__))
	with open(script_dir + '/empty.png', 'rb') as f:
		empty = f.read()
	with open(script_dir + '/us.geojson') as f:
		us = shape(geojson.load(f).features[0].geometry)
elif cmd == 'pyramid':
	base_path = sys.argv[2]
	out_path = sys.argv[3]
	fallback_path = sys.argv[4] if len(sys.argv) > 4 else None
elif cmd == 'delta':
	a_path = sys.argv[2]
	b_path = sys.argv[3]
	out_path = sys.argv[4]
else:
	print('unknown cmd', cmd)
	sys.exit(-1)

def delta_copy(x, y, zoom):
	a = a_path + tile_path.format(x=x,y=y,zoom=zoom)
	b = b_path + tile_path.format(x=x,y=y,zoom=zoom)
	out = out_path + tile_path.format(x=x,y=y,zoom=zoom)
	a_exists = os.path.isfile(a)
	b_exists = os.path.isfile(b)

	if (a_exists and b_exists and not filecmp.cmp(a, b)) or (not a_exists and b_exists):
		try:
			os.makedirs(os.path.dirname(out))
		except OSError:
			pass # probably the directory already exists

		shutil.copyfile(b, out)
	elif a_exists and not b_exists:
		print('a but not b', (zoom, x, y))

def remove_roaming(x, y, zoom):
	imagefile = base_path + tile_path.format(x=x,y=y,zoom=zoom)
	if not os.path.isfile(imagefile) or os.path.getsize(imagefile) == 0:
		return None

	orig_color = (212,212,212,255)
	replacement_color = (0,0,0,0)

	im = Image.open(imagefile)
	data = np.array(im)
	data[(data == orig_color).all(axis = -1)] = replacement_color

	if not data.T[3].any():
		# all transparent
		return None

	return Image.fromarray(data)

def stitch_image(x, y, zoom):
	new_im = Image.new('RGBA', (tile_size,tile_size), (255,255,255,0))

	images = 4
	for dx in range(2):
		for dy in range(2):
			try:
				im = Image.open(out_path + tile_path.format(x=x*2+dx,y=y*2+dy,zoom=zoom+1))
			except IOError:
				images -= 1
				if not fallback_path:
					continue
				try:
					im = Image.open(fallback_path + tile_path.format(x=x*2+dx,y=y*2+dy,zoom=zoom+1))
				except IOError:
					continue

			im.thumbnail((tile_size//2,tile_size//2))
			new_im.paste(im,(dx*tile_size//2,dy*tile_size//2))

	if images:
		return new_im

def pyramid_tile(x, y, zoom, base_zoom):
	if base_zoom:
		im = remove_roaming(x, y, zoom)
	else:
		im = stitch_image(x, y, zoom)

	if im:
		out_file = out_path + tile_path.format(x=x,y=y,zoom=zoom)
		try:
			os.makedirs(os.path.dirname(out_file))
		except OSError:
			pass # probably the directory already exists
		im.save(out_file)

def download_tile(x, y, zoom):
	url = tile_url.format(x=(x + 1), y=(y + 1), zoom=(zoom + 1))
	directory = '{}/{}/{}'.format(out_dir, zoom, x)
	path = '{}/{}.png'.format(directory, y)

	if os.path.isfile(path):
		return

	data = urlopen(url).read()

	try:
		os.makedirs(directory)
	except OSError:
		pass # probably the directory already exists

	if data == empty:
		os.mknod(path)
	else:
		out = io.open(path, 'wb')
		out.write(data)
		out.close()

def worker_loop(queue):
	while True:
		msg = queue.get()
		if (msg == 'DONE'):
			break
		else:
			if cmd == 'fetch':
				# FIXME: handle HTTP errors
				try:
					download_tile(*msg)
				except URLError as e:
					print(msg, e)
			elif cmd == 'pyramid':
				x, y, zoom = msg
				pyramid_tile(x, y, zoom, zoom == max_zoom)
			elif cmd == 'delta':
				delta_copy(*msg)

def num2deg(xtile, ytile, zoom):
	n = 2.0 ** zoom
	lon_deg = xtile / n * 360.0 - 180.0
	lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
	lat_deg = math.degrees(lat_rad)
	return lon_deg, lat_deg

def tile_in_us(x, y, zoom):
	l,t = num2deg(x, y, zoom)
	r,b = num2deg(x + 1, y + 1, zoom)
	bbox = Polygon([(l,t),(r,t),(r,b),(l,b),(l,t)])
	return us.intersects(bbox)

def fetch_tiles(queue, top_left, bottom_right, name, max_zoom, min_zoom):
	zoom = max_zoom

	while zoom >= min_zoom:
		print(name, zoom)

		factor = 2 ** (max_zoom - zoom)
		x = top_left[0] // factor
		max_x = bottom_right[0] // factor

		while x <= max_x:
			y = top_left[1] // factor
			max_y = bottom_right[1] // factor

			while y <= max_y:
				if cmd != 'fetch' or tile_in_us(x, y, zoom):
					queue.put((x, y, zoom))

				y = y + 1

			x = x + 1

		zoom = zoom - 1

if __name__=='__main__':
	queue = Queue()

	workers = []
	for i in range(worker_count):
		p = Process(target=worker_loop, args=((queue),))
		p.daemon = True
		p.start()
		workers.append(p)

	fetch_tiles(queue, (2563, 3660), (2635, 3693), 'Puerto Rico/Virgin Islands', max_zoom, min_zoom)
	fetch_tiles(queue, (447, 3574), (575, 3658), 'Hawaii', max_zoom, min_zoom)
	fetch_tiles(queue, (1255, 2797), (2575, 3521), 'Contiguous US', max_zoom, min_zoom)

	for i in range(worker_count):
		queue.put('DONE')

	for p in workers:
		p.join()
