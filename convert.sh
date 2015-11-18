#!/bin/sh
echo '{"type":"FeatureCollection","features":[' > tmo.geojson
minjur ~/Dropbox/osm/tmo.osm >> tmo.geojson
sed -i 's/}$/},/' tmo.geojson
echo ']}' >> tmo.geojson
rm -f points.csv
ogr2ogr -f csv -lco GEOMETRY=AS_XY points.csv tmo.geojson
