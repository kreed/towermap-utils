#!/usr/bin/env python3

import json
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from bbox import bbox

print('lat,lon,tmotowers,_name')
with open('tmotowers.json') as infile:
	for t in json.load(infile):
		flat = float(t['latitude'])
		flon = float(t['longitude'])
		if flon < bbox[0] or flon > bbox[2] or flat < bbox[1] or flat > bbox[3]:
			continue

		print(t['latitude'], t['longitude'], t['photo_id'], t['photo_name'], sep=',')
