#!/usr/bin/env python3

import csv
import os
import sys
from pprint import pprint

addr = []

with open('tmo.csv') as infile:
	reader = csv.DictReader(infile)
	for row in reader:
		if row['id']:
			addr.append(',' + row['id'] + ',')

os.system('egrep -v "(' + '|'.join(addr) + ')" ' + sys.argv[1])
