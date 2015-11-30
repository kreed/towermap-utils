#!/usr/bin/env python

from __future__ import print_function

import gzip
import sys
import time

file = gzip.GzipFile(sys.argv[1], 'r')
bbox = None
if len(sys.argv) == 3 and 'bbox' in sys.argv[2]:
	bbox = [-101.2555,25.6811,-89.2694,31.8122]

print('lon,lat,enb,gci,sector,range,tac,pci,samples,created,updated,band2,band4,band12')
for line in file:
	if line[0:12] == 'LTE,310,260,':
		radio, mcc, net, tac, cell, pci, lon, lat, range, samples, changeable, created, updated, averageSignal = line.split(',')

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

		if not band4 and not band2 and not band12 and samples == '1':
			continue

		created = time.strftime('%Y-%m-%d', time.gmtime(int(created)))
		updated = time.strftime('%Y-%m-%d', time.gmtime(int(updated)))
		print(lon,lat,enb,cell,sector,range,tac,pci,samples,created,updated,band2,band4,band12,sep=',')
