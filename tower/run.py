#!/usr/bin/env python3

import os
import sqlite3

filename = 'asrtowers.csv'
bbox = [-101.2555,25.6811,-89.2694,31.8122]
bbox_arcsecs = [ 3600 * d for d in bbox ]

con = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/r_tower.sqlite")
cur = con.cursor()

q = ("SELECT unique_system_identifier, EN.registration_number, structure_type, date_constructed, date_dismantled, "
	"latitude_total_seconds*(CASE WHEN latitude_direction='S' THEN -1 ELSE 1 END) AS lat, longitude_total_seconds*(CASE WHEN longitude_direction='W' THEN -1 ELSE 1 END) AS lon "
	"FROM EN JOIN CO USING (unique_system_identifier) JOIN RA USING (unique_system_identifier) "
	"WHERE entity_name LIKE 'T-Mobile%' AND lon>? AND lat>? AND lon<? AND lat<? GROUP BY unique_system_identifier")
q = cur.execute(q, bbox_arcsecs)
with open(filename, 'w') as f:
	print('asr,_website,_structure_type,_date_constructed,_date_dismantled,lat,lon', file=f)
	for row in q.fetchall():
		uls_no, registration_number, structure_type, date_constructed, date_dismantled, lat, lon = row
		lat = float(lat) / 3600
		lon = float(lon) / 3600
		website = 'http://wireless2.fcc.gov/UlsApp/AsrSearch/asrRegistration.jsp?regKey=%d' % uls_no
		print(registration_number, website, structure_type, date_constructed, date_dismantled, lat, lon, sep=',', file=f)

con.commit()
con.close()
