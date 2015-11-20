#!/usr/bin/env python3

import csv
import geojson
from lxml import etree
from pprint import pprint

fields = set()
rows = []
features = []

osm = etree.ElementTree(file='/home/chris/Dropbox/osm/tmo.osm')
for n in osm.iterfind('node'):
	lat = n.get('lat')
	lon = n.get('lon')

	props = {}
	for t in n.iterfind('tag'):
		props[t.get('k')] = t.get('v')

	color = 0
	if 'band' in props:
		bands = props['band'].split(';')
		if '2' in bands:
			color = color | 0x0000ff
		if '4' in bands:
			color = color | 0x00ff00
		if '12' in bands:
			color = color | 0xff0000
	props['marker-color'] = color and '#%06x' % color or ''

	point = geojson.Point((float(lon), float(lat)))
	f = geojson.Feature(geometry=point, properties=props)
	features.append(f)

	row = dict({'lat': lat, 'lon': lon}, **props)
	fields |= row.keys()
	rows.append(row)

features = geojson.FeatureCollection(features)

with open('tmo.csv', 'w') as outfile:
	writer = csv.DictWriter(outfile, fields)
	writer.writeheader()
	for row in rows:
		writer.writerow(row)

with open('tmo.geojson', 'w') as outfile:
	geojson.dump(features, outfile)
with open('tmo.js', 'w') as outfile:
	outfile.write('var towers = ')
	geojson.dump(features, outfile)
