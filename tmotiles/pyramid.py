#!/usr/bin/env python3

import os
import os.path
import shutil
import sys
import numpy as np
from PIL import Image

base_path = sys.argv[1]
out_path = sys.argv[2]
fallback_path = sys.argv[3] if len(sys.argv) > 3 else None
tile_path = '/{zoom}/{x}/{y}.png'
tile_size = 256

def remove_roaming(x, y, zoom):
	imagefile = base_path + tile_path.format(x=x,y=y,zoom=zoom)
	if not os.path.isfile(imagefile) or os.path.getsize(imagefile) == 0:
		return None

	orig_color = (212,212,212,255)
	replacement_color = (0,0,0,0)

	im = Image.open(imagefile)
	#im = im.convert('RGBA')
	data = np.array(im)   # "data" is a height x width x 4 numpy array
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

def pyramid_tiles(top_left, bottom_right, name, max_zoom=13, min_zoom=5):
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
				if zoom == max_zoom:
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

				y = y + 1

			x = x + 1

		zoom = zoom - 1

#pyramid_tiles((1791, 3331), (2064, 3491), 'SA')
pyramid_tiles((2563, 3660), (2635, 3693), 'Puerto Rico/Virgin Islands')
pyramid_tiles((447, 3574), (575, 3658), 'Hawaii')
pyramid_tiles((1255, 2797), (2575, 3521), 'Contiguous US')
