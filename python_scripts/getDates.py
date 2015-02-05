import json
import os

def getFiles(DIR):
	for f in os.listdir(DIR):
		full_f = os.path.join(DIR, f)
		if(os.path.isdir(full_f)):
			for i in getFiles(full_f):
				yield i
		elif f.endswith('.out'):
			with open(os.path.join(DIR, f)) as fo:
				data = json.load(fo)
				if "log" in data:
					yield data["log"]["date"]



if __name__ == '__main__':
	import sys
	DIR = '/export/a04/wpovell/scrape_data_ordered'
	if len(sys.argv) > 1:
		DIR = sys.argv[1]
	for i in getFiles(DIR):
		print(i)