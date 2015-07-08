for i in $(ls /export/a04/wpovell/splits/train/results); do
	echo $i
	python -m Pylinear.scripts.scores $i
done