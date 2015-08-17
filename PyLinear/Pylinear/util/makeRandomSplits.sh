#!/bin/bash
#$ -cwd
#$ -V
#$ -N makeSplits
#$ -S /bin/bash
#$ -j y -o /export/a04/wpovell/logs

# Used to move data from 'annotated_data' to proper splits
# Splits are randomized (not chronological)

copyDir() {
    mkdir -p /export/a04/wpovell/splits/$1/data/
    cp -ar /export/a04/wpovell/annotated_data/$2/ /export/a04/wpovell/splits/$1/data/$2
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