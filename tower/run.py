#!/usr/bin/env python3

import csv
import os
import sqlite3
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from bbox import bbox

filename = 'asrtowers.csv'
bbox_arcsecs = [ 3600 * d for d in bbox ]

entity = None
if len(sys.argv) > 1:
	if sys.argv[1] == 'tmo':
		entity = "AND (entity_name LIKE 'T-Mobile%' OR entity_name LIKE 'CCTM%') "
	elif sys.argv[1] == 'att':
		entity =  "AND (entity_name LIKE 'SBC%' OR entity_name LIKE 'CCATT%' OR entity_name LIKE 'AT%') "

con = sqlite3.connect(os.path.dirname(os.path.realpath(__file__)) + "/r_tower.sqlite")
cur = con.cursor()

q = ("SELECT unique_system_identifier, EN.registration_number, entity_name, structure_type, date_constructed, date_dismantled, "
	"latitude_total_seconds*(CASE WHEN latitude_direction='S' THEN -1 ELSE 1 END) AS lat, longitude_total_seconds*(CASE WHEN longitude_direction='W' THEN -1 ELSE 1 END) AS lon "
	"FROM EN JOIN CO USING (unique_system_identifier) JOIN RA USING (unique_system_identifier) "
	"WHERE status_code!='A' AND lon>? AND lat>? AND lon<? AND lat<? "
	+ (entity if entity else "") +
	"GROUP BY unique_system_identifier")
q = cur.execute(q, bbox_arcsecs)
with open(filename, 'w') as f:
	w = csv.writer(f)
	w.writerow(('asr','_name','_website','_structure_type','_date_constructed','_date_dismantled','lat','lon'))
	for row in q.fetchall():
		uls_no, registration_number, owner, structure_type, date_constructed, date_dismantled, lat, lon = row
		lat = float(lat) / 3600
		lon = float(lon) / 3600
		website = 'http://wireless2.fcc.gov/UlsApp/AsrSearch/asrRegistration.jsp?regKey=%d' % uls_no
		w.writerow((registration_number, owner, website, structure_type, date_constructed, date_dismantled, lat, lon))

con.commit()
con.close()
