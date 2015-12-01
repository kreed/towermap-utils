#!/usr/bin/env python3

import csv
import geojson
import sys
from pprint import pprint

filename = 'check.geojson'
cells = {}
features = []

def make_point(row, base_props):
	props = { k: v for k,v in row.items() if k not in ('lat','lon') }
	props.update(base_props)
	geom = geojson.Point((float(row['lon']), float(row['lat'])))
	f = geojson.Feature(properties=props, geometry=geom)
	features.append(f)
	return f

with open('tmo.csv') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		for enb in row['enb'].split(';'):
			if enb:
				cells[enb] = (row,[])

with open(sys.argv[1]) as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		enb = row['enb']

		if row['gci'] == '17369858' and row['pci'] == '206':
			continue
		if row['gci'] == '18267147' and row['pci'] == '273':
			continue
		if row['gci'] == '17960715' and row['pci'] == '247':
			continue

		if not enb in cells:
			cells[enb] = (None, [])
		cells[enb][1].append(row)

for enb,v in cells.items():
	mapped_cell, mls_cells = v

	base_props = { 'enb': enb }
	tac_flag = None

	if mapped_cell:
		counter = 0
		for mls_cell in mls_cells:
			if mls_cell['tac'] != mapped_cell['tac']:
				counter += 1
		if counter == len(mls_cells):
			tac_flag = 3
		elif counter > len(mls_cells)/2:
			tac_flag = 2

	if mapped_cell:
		mapped_point = make_point(mapped_cell, base_props)
		base_props['to_map'] = False
	else:
		base_props['to_map'] = True
		gen_cell = {
			'lon': sum([ float(row['lon']) for row in mls_cells ])/len(mls_cells),
			'lat': sum([ float(row['lat']) for row in mls_cells ])/len(mls_cells),
		}
		mapped_point = make_point(gen_cell, base_props)

	tacs = set()
	bands = set()

	for mls_cell in mls_cells:
		mls_point = make_point(mls_cell, base_props)

		geom = geojson.LineString((mls_point.geometry.coordinates, mapped_point.geometry.coordinates))
		props = {}
		props.update(base_props)
		f = geojson.Feature(properties=props, geometry=geom)

		if mapped_cell:
			if mls_cell['tac'] != mapped_cell['tac']:
				props['tac_flagged'] = tac_flag if tac_flag else 1
		else:
			for k in '2','4','12':
				if mls_cell['band' + k] == 'Y':
					bands.add(int(k))
			tacs.add(mls_cell['tac'])

		if not mapped_cell:
			mapped_point.properties['tac'] = ';'.join(tacs)
			mapped_point.properties['band'] = ';'.join(str(b) for b in bands)

		features.append(f)

result = geojson.FeatureCollection(features)
with open(filename, 'w') as out:
	geojson.dump(result, out)


