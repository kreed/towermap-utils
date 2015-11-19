#!/bin/sh
echo '{"type":"FeatureCollection","features":[' > minjur.geojson
minjur ~/Dropbox/osm/tmo.osm >> minjur.geojson
sed -i 's/}$/},/' minjur.geojson
echo ']}' >> minjur.geojson

fields=band,id,tac,FIXME,microwave_uls,addr,sagis:Address
rm -f tmo.csv tmo.geojson
ogr2ogr -f geojson tmo.geojson minjur.geojson -select $fields
ogr2ogr -f csv -lco GEOMETRY=AS_XY tmo.csv minjur.geojson -select $fields
rm minjur.geojson

echo -n 'var towers = ' | cat - tmo.geojson > tmo.js
