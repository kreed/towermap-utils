#!/usr/bin/env python3

import csv
import os
import sqlite3
import sys
import itertools

filename = 'micro.csv'
bbox = [-101.2555,25.6811,-89.2694,31.8122]

entity = None
if len(sys.argv) > 1:
	if sys.argv[1] == 'tmo':
		entity = '%@t-mobile.com'
	elif sys.argv[1] == 'att':
		entity = '%@att.com'

con = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/l_micro.sqlite")
cur = con.cursor()

license_locs = {}

q = ("SELECT unique_system_identifier, HD.call_sign, entity_name, grant_date, cancellation_date, location_class_code, "
	"(lat_degrees+lat_minutes/60.0+lat_seconds/3600.0)*(CASE WHEN lat_direction='S' THEN -1 ELSE 1 END) AS lat, "
	"(long_degrees+long_minutes/60.0+long_seconds/3600.0)*(CASE WHEN long_direction='W' THEN -1 ELSE 1 END) AS lon "
	"FROM EN JOIN HD USING (unique_system_identifier) JOIN LO USING (unique_system_identifier) "
	+ ("WHERE email LIKE '{}' AND ".format(entity) if entity else "WHERE ") +
	"lon>? AND lat>? AND lon<? AND lat<?")
q = cur.execute(q, bbox)
for row in q.fetchall():
	uls_no, call_sign, owner, grant_date, cancel_date, class_code, lat, lon = row

	if not uls_no in license_locs:
		license_locs[uls_no] = set(),set(),call_sign,owner,grant_date,cancel_date

	if class_code == 'T':
		license_locs[uls_no][0].add((lon,lat))
	elif class_code == 'R':
		license_locs[uls_no][1].add((lon,lat))
	else:
		print('unknown class code', class_code)

with open(filename, 'w') as f:
	w = csv.writer(f)
	w.writerow(('microwave', 'call_sign','owner','website','grant_date','cancellation_date','coords'))
	for uls_no, v in license_locs.items():
		transmitters, receivers, call_sign, owner, grant_date, cancel_date = v
		if len(transmitters) != 1 or len(receivers) < 1:
			print(uls_no, len(transmitters), 'transmitters', len(receivers), 'receivers')
			continue

		coords = '|'.join('%f|%f' % (x,y) for x,y in itertools.chain(transmitters, receivers))
		url = 'http://wireless2.fcc.gov/UlsApp/UlsSearch/license.jsp?licKey=%d' % uls_no
		w.writerow(('yes', call_sign, owner, url, grant_date, cancel_date, coords))

con.commit()
con.close()
