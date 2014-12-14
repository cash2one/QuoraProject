import os
import shutil
from datetime import datetime
from sys import argv

def moveFile(path, out):
	'''Moves file into sorted directory based on its timestamp.
	If a file does not have a timestamp, it is not moved.
	Structure:
		DATA/
			01/ # Month
				01/ # Day
					1231231231_asdfadfs3.out # Output file
					...
				...
			...
	'''

	# Only move if has '<timestamp>_*'
	fn = os.path.split(path)[-1]
	if not fn.endswith('.out'):
		return

	# Parsed timestamp
	t = datetime.fromtimestamp(int(fn.split('_')[0]))

	MONTH_DIR = os.path.join(out, str(t.month))
	DAY_DIR = os.path.join(MONTH_DIR, str(t.day))

	# Create directories if they don't exist
	if not os.path.exists(MONTH_DIR):
		os.mkdir(MONTH_DIR)
	if not os.path.exists(DAY_DIR):
		os.mkdir(DAY_DIR)

	shutil.copy(path, os.path.join(DAY_DIR, fn))


if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Sorts data into MONTH/DATE folders')
	parser.add_argument('DIR', type=str, help="directory to read data from")
	parser.add_argument('OUT', type=str, help="directory to write datat to")
	args = parser.parse_args()

	if not os.path.exists(args.OUT):
		os.mkdir(args.OUT)

	for i, fn in enumerate(os.listdir(args.DIR)):
		if i % 1000 == 0:
			print("Files copied: {}".format(i))
		moveFile(os.path.join(args.DIR, fn), args.OUT)
