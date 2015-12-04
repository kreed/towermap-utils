#!/usr/bin/env python3

import os
import sqlite3

filename = 'asrtowers.csv'
bbox = [-101.3901,27.4839,91.6095,30.6285]
bbox_arcsecs = [ 3600 * d for d in bbox ]

con = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/r_tower.sqlite")
cur = con.cursor()

q = ("SELECT unique_system_identifier, EN.registration_number, structure_type, date_constructed, date_dismantled, "
	"latitude_total_seconds*(CASE WHEN latitude_direction='S' THEN -1 ELSE 1 END) AS lat, longitude_total_seconds*(CASE WHEN longitude_direction='W' THEN -1 ELSE 1 END) AS lon "
	"FROM EN JOIN CO USING (unique_system_identifier) JOIN RA USING (unique_system_identifier) WHERE licensee_id='L01748971' AND "
	"lon>? AND lat>? AND lon<? AND lat<?")
q = cur.execute(q, bbox_arcsecs)
with open(filename, 'w') as f:
	print('asr,website,structure_type,date_constructed,date_dismantled,lat,lon', file=f)
	for row in q.fetchall():
		uls_no, registration_number, structure_type, date_constructed, date_dismantled, lat, lon = row
		lat = float(lat) / 3600
		lon = float(lon) / 3600
		website = 'http://wireless2.fcc.gov/UlsApp/AsrSearch/asrRegistration.jsp?regKey=' + registration_number
		print(uls_no, website, structure_type, date_constructed, date_dismantled, lat, lon, sep=',', file=f)

con.commit()
con.close()
