#!/bin/sh
fields=FULL_STREE
ogr2ogr -f csv -t_srs epsg:4326 -lco GEOMETRY=AS_XY addr.csv Address_Points/LOCATION_address_point.shp -select $fields
