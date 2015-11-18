#!/usr/bin/env python3

import csv
from pprint import pprint

with open('points.csv') as infile, open('bandcolors.csv', 'w') as outfile:
	reader = csv.DictReader(infile)
	in_fields = set(reader.fieldnames)
	out_fields = in_fields | {'marker-color'}
	writer = csv.DictWriter(outfile, out_fields)
	writer.writeheader()
	for row in reader:
		bands = row['band'].split(';')
		color = 0
		if '2' in bands:
			color = color | 0xff0000
		if '4' in bands:
			color = color | 0x0000ff
		if '12' in bands:
			color = color | 0x00ff00
		row['marker-color'] = color and '#%06x' % color or ''
		writer.writerow(row)
