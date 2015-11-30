#!/usr/bin/env python3

import math
import sys

minx,miny,maxx,maxy = [ float(x) for x in sys.argv[1].split(',') ]

def deg2num(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = int((lon_deg + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
	return (xtile, ytile)

print(deg2num(maxy,minx,13),deg2num(miny,maxx,13),sep=', ')
