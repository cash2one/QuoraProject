import os
import shutil
from datetime import datetime
from sys import argv

def moveFile(path, dir):
	fn = os.path.split(path)[-1]
	if len(fn.split('_')) < 2:
		return
	t = datetime.fromtimestamp(int(fn.split('_')[0]))
	MONTH_DIR = os.path.join(out, str(t.month))
	DAY_DIR = os.path.join(MONTH_DIR, str(t.day))
	if not os.path.exists(MONTH_DIR):
		os.mkdir(MONTH_DIR)
	if not os.path.exists(DAY_DIR):
		os.mkdir(DAY_DIR)
	shutil.copy(path, os.path.join(DAY_DIR, fn))


if __name__ == '__main__':
	dir = argv[1]
	out = argv[2]

	if not os.path.exists(out):
		os.mkdir(out)

	for i, fn in enumerate(os.listdir(dir)):
		if i % 1000 == 0:
			print("Files copied: {}".format(i))
		moveFile(os.path.join(dir, fn), out)
