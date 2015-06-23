#!/usr/bin/bash
copyDir() {
	cp -r "/export/a04/wpovell/annotated_data/$2" /export/a04/wpovell/splits/$1/data/
}

rm -r /export/a04/wpovell/tune/data
copyDir tune 0

rm -r /export/a04/wpovell/dev/data
copyDir dev 1

rm -r /export/a04/wpovell/test/data
copyDir test 2

rm -r /export/a04/wpovell/train/data
for i in {3..9}; do
	copyDir train $i
done;

for i in {a..f} do
	copyDir train $i
done;