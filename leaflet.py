#!/usr/bin/env python3

import geojson
from lxml import etree
from pprint import pprint

features = []

osm = etree.ElementTree(file='/home/chris/Dropbox/osm/tmo.osm')
for n in osm.iterfind('node'):
	lat = n.get('lat')
	lon = n.get('lon')

	props = {}
	for t in n.iterfind('tag'):
		props[t.get('k')] = t.get('v')

	point = geojson.Point((float(lon), float(lat)))
	f = geojson.Feature(geometry=point, properties=props)
	features.append(f)

features = geojson.FeatureCollection(features)
with open('tmo.js', 'w') as outfile:
	outfile.write('var towers = ')
	geojson.dump(features, outfile)
