#!/usr/bin/env python3

import filecmp
import os
import os.path
import shutil
import sys

a_path = sys.argv[1]
b_path = sys.argv[2]
out_path = sys.argv[3]
tile_path = '/{zoom}/{x}/{y}.png'
tile_size = 256

def pyramid_tiles(top_left, bottom_right, name, max_zoom=13, min_zoom=13):
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

				y = y + 1

			x = x + 1

		zoom = zoom - 1

pyramid_tiles((2563, 3660), (2635, 3693), 'Puerto Rico/Virgin Islands')
pyramid_tiles((447, 3574), (575, 3658), 'Hawaii')
pyramid_tiles((1255, 2797), (2575, 3521), 'Contiguous US')
