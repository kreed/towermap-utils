#!/usr/bin/env python3

import csv
import sys
from pprint import pprint

cell_bands = {}

with open('tmo.csv') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		for enb in row['enb'].split(';'):
			if enb:
				cell_bands[enb] = row['band'].split(';')

with open(sys.argv[1]) as infile:
	reader = csv.DictReader(infile)
	writer = csv.DictWriter(sys.stdout, reader.fieldnames)
	writer.writeheader()
	for row in reader:
		enb = row['enb']
		if enb in cell_bands:
			if row['band2'] == 'Y' and '2' in cell_bands[enb]:
				continue
			if row['band4'] == 'Y' and '4' in cell_bands[enb]:
				continue
			if row['band12'] == 'Y' and '12' in cell_bands[enb]:
				continue
		writer.writerow(row)
