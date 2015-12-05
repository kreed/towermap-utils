#!/usr/bin/env python3

from xml.sax.saxutils import escape
from geopy.distance import great_circle
from lxml import etree
from operator import itemgetter
import csv

mapped_filename = '/home/chris/Dropbox/osm/tmo.osm'
mls_filename = 'sa.csv'
filename = 'check.osm'
imports = [
	('imports/tmotowers.csv', 'tmotowers', {}),
	('imports/ausperms.csv', 'austin:addr', {}),
	('imports/asrtowers.csv', 'asr', {}),
]

sites = []
cells = {}
microwave_sites = {}

osm = etree.ElementTree(file=mapped_filename)
for n in osm.iterfind('node'):
	lat = n.get('lat')
	lon = n.get('lon')

	props = {}
	for t in n.iterfind('tag'):
		v = t.get('v')
		if v:
			props[t.get('k')] = v

	row = dict({'lat': lat, 'lon': lon}, **props)
	site = (row,[])
	sites.append(site)

	if 'enb' in row:
		for enb in row['enb'].split(';'):
			cells[enb] = site[1]

with open(mls_filename) as infile:
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
			site = (None, [])
			sites.append(site)
			cells[enb] = site[1]
		cells[enb].append(row)

nodes = []
ways = []
for mapped_cell, mls_cells in sites:
	if mapped_cell:
		site_props = dict(mapped_cell)
		site_props['_to_map'] = '0'

		if mapped_cell.get('microwave_uls', None):
			for uls in mapped_cell['microwave_uls'].split(';'):
				if not uls in microwave_sites:
					microwave_sites[uls] = []
				microwave_sites[uls].append(site_props)

		for f, key, sites in imports:
			if mapped_cell.get(key, None):
				for e in mapped_cell[key].split(';'):
					sites[e] = site_props
	else:
		site_props = {
			'enb': mls_cells[0]['enb'],
			'_to_map': '1',
			'lon': str(sum([ float(row['lon']) for row in mls_cells ])/len(mls_cells)),
			'lat': str(sum([ float(row['lat']) for row in mls_cells ])/len(mls_cells)),
		}

	if mls_cells:
		tac_flag = None
		if mapped_cell:
			counter = 0
			for mls_cell in mls_cells:
				if mls_cell['tac'] != mapped_cell['tac']:
					counter += 1
			if counter == len(mls_cells):
				tac_flag = 'all bad tac'
			elif counter > len(mls_cells)/2:
				tac_flag = '> half bad tac'

		bands = set()
		sectors = set()
		samples = 0
		tacs = {}
		first_seen = None
		last_seen = None
		band12_first_seen = None

		for mls_cell in mls_cells:
			sector_props = dict(mls_cell)
			way_props = { 'enb': site_props['enb'] }

			bands.add(int(mls_cell['band']))
			sectors.add(int(mls_cell['sector']))
			samples += int(mls_cell['samples'])

			tac = mls_cell['tac']
			if not tac in tacs:
				tacs[tac] = 0
			tacs[tac] += 1

			if first_seen == None or mls_cell['created'] < first_seen:
				first_seen = mls_cell['created']
			if mls_cell['band'] == '12' and (band12_first_seen == None or mls_cell['created'] < band12_first_seen):
				band12_first_seen = mls_cell['created']
			if last_seen == None or mls_cell['updated'] > last_seen:
				last_seen = mls_cell['updated']

			if mapped_cell:
				if mls_cell['tac'] != mapped_cell['tac']:
					flag = tac_flag if tac_flag else '< half bad tac'
					way_props['_error_tac'] = site_props['error_tac'] = flag
					site_props['_to_map'] = '2'

				if not mls_cell['band'] in mapped_cell['band'].split(';') and mls_cell['band'] != '-1':
					way_props['_error_band'] = site_props['error_band'] = 'missing band'
					site_props['_to_map'] = '2'

			nodes.append(sector_props)
			ways.append((site_props, sector_props, way_props))

		site_props['_sectors'] = ';'.join(str(b) for b in sorted(sectors))
		site_props['_samples'] = str(samples)
		site_props['_first_seen'] = first_seen
		site_props['_last_seen'] = last_seen
		if 12 in bands:
			site_props['_band12_first_seen'] = band12_first_seen

		tacs = sorted(tacs.items(), key=itemgetter(1), reverse=True)
		if len(tacs) > 1:
			site_props['_tacs_list'] = str(tacs)

		mls_bands = ';'.join(str(b) for b in sorted(bands))
		if mapped_cell:
			known_bands = ';'.join(str(b) for b in sorted(bands - {-1}))
			if known_bands != mapped_cell['band']:
				site_props['_mls_bands'] = mls_bands
				if not 'error_band' in site_props and mls_cells:
					site_props['_error_band'] = 'extraneous band'
					site_props['_to_map'] = '2'
		else:
			site_props['tac'] = tacs[0][0]
			site_props['band'] = mls_bands

	nodes.append(site_props)

for f, key, sites in imports:
	with open(f) as infile:
		reader = csv.DictReader(infile)
		for row in reader:
			id = row[key]
			if id in sites:
				a = (float(row['lat']), float(row['lon']))
				b = (float(sites[id]['lat']), float(sites[id]['lon']))
				if great_circle(a, b).meters < 1500:
					continue

			nodes.append(dict(row))

with open('micro.csv') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		uls_no = row['microwave_uls']
		it = iter(row['coords'].split('|'))
		coords = list(zip(it,it))

		if uls_no in microwave_sites:
			mw_nodes = []
			for lon, lat in coords:
				match = None
				for site in microwave_sites[uls_no]:
					a = (float(lat), float(lon))
					b = (float(site['lat']), float(site['lon']))
					if great_circle(a, b).meters < 1500:
						match = site
						break
				mw_nodes.append(match)
		else:
			mw_nodes = [None] * len(coords)

		matched = True

		for i in range(len(coords)):
			if not mw_nodes[i]:
				matched = False
				lon, lat = coords[i]
				n = { 'lat': lat, 'lon': lon }
				mw_nodes[i] = n
				nodes.append(n)

		for receiver in mw_nodes[1:]:
			props = { k: v for k, v in row.items() if k != 'coords' }
			props['_to_map'] = '0' if matched else '1'
			ways.append((mw_nodes[0], receiver, props))

with open(filename, 'w') as f:
	f.write('<osm generator="check.py" upload="false" version="0.6">')

	node_id = -1
	for props in nodes:
		props['_id'] = node_id
		node_id -= 1

		f.write('<node id="%d" lat="%s" lon="%s">' % (props['_id'], props['lat'], props['lon']))
		for k,v in props.items():
			if v and k != 'lat' and k != 'lon' and k != '_id':
				f.write('<tag k="%s" v="%s"/>' % (k, escape(v)))
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
				f.write('<tag k="%s" v="%s"/>' % (k, escape(v)))

		f.write('</way>')

	f.write('</osm>')
