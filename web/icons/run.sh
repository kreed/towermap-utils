#!/bin/sh
bands=(unknown 2 4 12 2_4 2_12 4_12 2_4_12)
colors=(bbb 00f 0a0  f00 0ff f0f fa0 fff)

mkdir sprites
for f in *.svg; do
	for i in ${!bands[@]}; do
		out=`basename $f .svg`_${bands[$i]}
		sed -e "s/#808080/#${colors[$i]}/" $f > sprites/$out
	done
done
spritezero towers sprites
rm -r sprites
