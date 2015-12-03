#!/usr/bin/env python3

import os

need_addrs = set()

with open('ausperms.txt') as f:
	for line in f:
		fields = line.split('	')
		code = fields[1]
		addr = fields[6]
		need_addrs.add(',' + addr + '$')

print('lon,lat,austin:addr', flush=True)
os.system('egrep "(' + '|'.join(need_addrs) + ')" ausaddr.csv')
