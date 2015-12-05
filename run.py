#!/usr/bin/env python

from __future__ import print_function

import gzip
import sys
import time

file = gzip.GzipFile(sys.argv[1], 'r')
bbox = None
if len(sys.argv) == 3 and 'bbox' in sys.argv[2]:
	bbox = [-101.2555,25.6811,-89.2694,31.8122]

print('lon,lat,enb,gci,sector,range,tac,pci,samples,created,updated,band')
for line in file:
	if line[0:12] == 'LTE,310,260,':
		radio, mcc, net, tac, cell, pci, lon, lat, range, samples, changeable, created, updated, averageSignal = line.split(',')

		flat = float(lat)
		flon = float(lon)
		if bbox and (flon < bbox[0] or flon > bbox[2] or flat < bbox[1] or flat > bbox[3]):
			continue

		sector = int(cell) & 0xff
		enb = int(cell) >> 8
		if enb > 150000:
			continue

		band = '-1'
		if (sector >= 1 and sector <= 4) or (sector >= 101 and sector <= 104):
			band = '4'
		elif sector >= 11 and sector <= 14:
			band = '2'
		elif sector >= 21 and sector <= 24:
			band = '12'

		created = time.strftime('%Y-%m-%d', time.gmtime(int(created)))
		updated = time.strftime('%Y-%m-%d', time.gmtime(int(updated)))

		if band == '-1' and updated == created:
			continue

		print(lon,lat,enb,cell,sector,range,tac,pci,samples,created,updated,band,sep=',')
