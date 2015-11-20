#!/usr/bin/env python3

import csv
import sys
from pprint import pprint

cell_bands = {}

with open('tmo.csv') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		if row['id']:
			cell_bands[row['id']] = row['band'].split(';')

with open(sys.argv[1]) as infile:
	reader = csv.DictReader(infile)
	writer = csv.DictWriter(sys.stdout, reader.fieldnames)
	writer.writeheader()
	for row in reader:
		pci = row['pci']
		if pci in cell_bands:
			if row['band2'] == 'Y' and '2' in cell_bands[pci]:
				continue
			if row['band4'] == 'Y' and '4' in cell_bands[pci]:
				continue
			if row['band12'] == 'Y' and '12' in cell_bands[pci]:
				continue
		writer.writerow(row)
