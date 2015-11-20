#!/usr/bin/env python

from __future__ import print_function

import gzip
import sys
import time

file = gzip.GzipFile(sys.argv[1], 'r')
bbox = None
band12only = False
if len(sys.argv) == 3 and 'bbox' in sys.argv[2]:
	bbox = [-101.3901,27.4839,-91.6095,30.6285]
if len(sys.argv) == 3 and 'band12' in sys.argv[2]:
	band12only = True

print('lon,lat,enb,gci,sector,range,samples,created,updated,band2,band4,band12')
for line in file:
	if line[0:12] == 'LTE,310,260,':
		radio, mcc, net, area, cell, unit, lon, lat, range, samples, changeable, created, updated, averageSignal = line.split(',')

		flat = float(lat)
		flon = float(lon)
		if bbox and (flon < bbox[0] or flon > bbox[2] or flat < bbox[1] or flat > bbox[3]):
			continue

		sector = int(cell) & 0xff
		enb = int(cell) >> 8
		if enb > 200000:
			continue

		band4 = 'Y' if (sector >= 1 and sector <= 4) or (sector >= 101 and sector <= 104) else ''
		band2 = 'Y' if sector >= 11 and sector <= 14 else ''
		band12 = 'Y' if sector >= 21 and sector <= 24 else ''

		if band12only and not band12:
			continue

		created = time.strftime('%Y-%m-%d', time.gmtime(int(created)))
		updated = time.strftime('%Y-%m-%d', time.gmtime(int(updated)))
		print(lon,lat,enb,cell,sector,range,samples,created,updated,band2,band4,band12,sep=',')
