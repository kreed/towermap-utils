#!/usr/bin/env python3

import csv
import sys
from operator import itemgetter

filename = 'check.osm'

cells = {}
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

nodes = []
ways = []
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
			tac_flag = '3'
		elif counter > len(mls_cells)/2:
			tac_flag = '2'

		base_props['_to_map'] = '0'
		site_props = dict(mapped_cell, **base_props)
	else:
		base_props['_to_map'] = '1'
		site_props = {
			'lon': str(sum([ float(row['lon']) for row in mls_cells ])/len(mls_cells)),
			'lat': str(sum([ float(row['lat']) for row in mls_cells ])/len(mls_cells)),
		}
		site_props.update(base_props)

	tacs = {}
	bands = set()

	for mls_cell in mls_cells:
		sector_props = dict(mls_cell, **base_props)
		way_props = dict(base_props)

		if mapped_cell:
			if mls_cell['tac'] != mapped_cell['tac']:
				way_props['tac_flagged'] = tac_flag if tac_flag else '1'
		else:
			for k in '2','4','12':
				if mls_cell['band' + k] == 'Y':
					bands.add(int(k))

			tac = mls_cell['tac']
			if not tac in tacs:
				tacs[tac] = 0
			tacs[tac] += 1

		nodes.append(sector_props)
		ways.append((site_props, sector_props, way_props))

	if not mapped_cell:
		site_props['band'] = ';'.join(str(b) for b in bands)
		tacs = sorted(tacs.items(), key=itemgetter(1), reverse=True)
		site_props['tac'] = tacs[0][0]
		if len(tacs) > 1:
			site_props['_all_tacs'] = str(tacs)

	nodes.append(site_props)

with open(filename, 'w') as f:
	f.write('<osm generator="check.py" upload="false" version="0.6">')

	node_id = -1
	for props in nodes:
		props['_id'] = node_id
		node_id -= 1

		f.write('<node id="%d" lat="%s" lon="%s">' % (props['_id'], props['lat'], props['lon']))
		for k,v in props.items():
			if v and k != 'lat' and k != 'lon' and k != '_id':
				f.write('<tag k="%s" v="%s"/>' % (k, v))
		f.write('</node>')

	way_id = -1
	for e in ways:
		site, sector, props = e

		f.write('<way id="%d">' % way_id)
		way_id -= 1

		f.write('<nd ref="%d"/>' % site['_id'])
		f.write('<nd ref="%d"/>' % sector['_id'])

		for k,v in props.items():
			if v:
				f.write('<tag k="%s" v="%s"/>' % (k, v))

		f.write('</way>')

	f.write('</osm>')
