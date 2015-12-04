#!/usr/bin/env python3

import os
import sqlite3

filename = 'micro.csv'
bbox = [-101.3901,27.4839,-91.6095,30.6285]

con = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/l_micro.sqlite")
cur = con.cursor()

license_locs = {}

q = ("SELECT unique_system_identifier, grant_date, cancellation_date, location_class_code, "
	"(lat_degrees+lat_minutes/60.0+lat_seconds/3600.0)*(CASE WHEN lat_direction='S' THEN -1 ELSE 1 END) AS lat, "
	"(long_degrees+long_minutes/60.0+long_seconds/3600.0)*(CASE WHEN long_direction='W' THEN -1 ELSE 1 END) AS lon "
	"FROM EN JOIN HD USING (unique_system_identifier) JOIN LO USING (unique_system_identifier) WHERE licensee_id='L00127664' AND "
	"lon>? AND lat>? AND lon<? AND lat<?")
q = cur.execute(q, bbox)
for row in q.fetchall():
	uls_no, grant_date, cancel_date, class_code, lat, lon = row

	if not uls_no in license_locs:
		license_locs[uls_no] = [],[],grant_date,cancel_date

	if class_code == 'T':
		license_locs[uls_no][0].append((lon,lat))
	elif class_code == 'R':
		license_locs[uls_no][1].append((lon,lat))
	else:
		print('unknown class code', class_code)

with open(filename, 'w') as f:
	print('microwave_uls,website,grant_date,cancellation_date,coords', file=f)
	for uls_no, v in license_locs.items():
		transmitters, receivers, grant_date, cancel_date = v
		if len(transmitters) != 1 or len(receivers) < 1:
			print(uls_no, len(transmitters), 'transmitters', len(receivers), 'receivers')
			continue

		coords = '|'.join('%f|%f' % (x,y) for x,y in (transmitters + receivers))
		print(uls_no, 'http://wireless2.fcc.gov/UlsApp/UlsSearch/license.jsp?licKey=%d' % uls_no, grant_date, cancel_date, coords, sep=',', file=f)

con.commit()
con.close()
