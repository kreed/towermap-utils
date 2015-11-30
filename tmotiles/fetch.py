#!/usr/bin/env python3

import geojson
import io
import math
import os
import os.path
import sys
import time
from shapely.geometry import shape, mapping, Polygon
from urllib.request import urlopen
from urllib.error import HTTPError

mp = 'Extra2_Map' if sys.argv[1] == 'nob12' else 'TMo_TechLTE_Map'
tile_url = 'http://maps.t-mobile.com/%s/{zoom}/{x}:{y}/tile.png' % mp
out_dir = sys.argv[2]

script_dir = os.path.dirname(os.path.realpath(__file__))
with open(script_dir + '/empty.png', 'rb') as f:
	empty = f.read()
with open(script_dir + '/us.geojson') as f:
	us = shape(geojson.load(f).features[0].geometry)

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

def fetch_tiles(top_left, bottom_right, name, max_zoom=13, min_zoom=13):
	zoom = max_zoom

	while zoom >= min_zoom:
		print(mp, name, zoom)

		factor = 2 ** (max_zoom - zoom)
		x = top_left[0] // factor
		max_x = bottom_right[0] // factor

		while x <= max_x:
			y = top_left[1] // factor
			max_y = bottom_right[1] // factor

			while y <= max_y:
				if tile_in_us(x, y, zoom):
					try:
						download_tile(x, y, zoom)
					except HTTPError as e:
						print('Failed downloading tile {}/{}/{}. Retrying in 60 seconds...'.format(zoom, x, y))
						time.sleep(60)
						download_tile(x, y, zoom)

				y = y + 1

			x = x + 1

		zoom = zoom - 1

#fetch_tiles((1791, 3331), (2064, 3491), 'SA')
fetch_tiles((2563, 3660), (2635, 3693), 'Puerto Rico/Virgin Islands')
fetch_tiles((447, 3574), (575, 3658), 'Hawaii')
fetch_tiles((1255, 2797), (2575, 3521), 'Contiguous US')
