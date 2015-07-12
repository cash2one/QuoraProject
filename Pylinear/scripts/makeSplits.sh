#!/bin/bash
copyDir() {
	cp -r "/export/a04/wpovell/annotated_data/$2" /export/a04/wpovell/splits/$1/data/
}

echo "Tune"
rm -r /export/a04/wpovell/splits/tune/data
copyDir tune 0

echo "Dev"
rm -r /export/a04/wpovell/splits/dev/data
copyDir dev 1

echo "Test"
rm -r /export/a04/wpovell/splits/test/data
copyDir test 2

echo "Train"
rm -r /export/a04/wpovell/splits/train/data
for i in {3..9}; do
	copyDir train $i
done;

for i in {a..f}; do
	copyDir train $i
done;
echo "Done"