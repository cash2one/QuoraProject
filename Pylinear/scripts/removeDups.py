'''Removes duplicate scrapes from raw data folder.'''
import shutil
import os

def moveToTemp(file):
	shutil.move(fn, os.path.join('/export/a04/wpovell/temp', os.path.basename(file)))

if __name__ == '__main__':
	with open('/export/a04/wpovell/logs/test.o2692577') as f:
		d = f.read().split('\n')

	for a, b in [i[i.index('['):] for i in d if i.startswith('http')]:
		af = open(a)
		aData = = json.load(af)
		af.close()
		bf = open(b)
		bData = = json.load(bf)
		bf.close()

		if aData['time'] > bData['time']:
			moveToTemp(b)
		else:
			moveToTemp(a)