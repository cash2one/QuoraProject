import os
import json

def getData(DIR):
	'''Takes directory and returns json data'''
	for fn in os.listdir(DIR):
		joined = os.path.join(DIR, fn)

		if os.path.isdir(joined):
			for entry in getData(joined):
				yield entry
		elif fn.endswith('.out'):
			try:
				with open(joined) as f:
					data = json.load(f)
			except ValueError:
				yield fn, {}
				continue

			yield fn, data

if __name__ == '__main__':
	from sys import argv

	DIR = '/export/a04/wpovell/scrape_data_ordered'
	OUT = '/export/a04/wpovell/logs/fileInfo.txt'
	if len(argv) > 1:
		DIR = argv[1]
	if len(argv) > 2:
		OUT = argv[2]

	with open(OUT, 'w') as f:
		for fn, data in getData(DIR):
			hasData = 'data' in data
			hasTime = 'log' in data
			url = data['url'] if 'url' in data else ''
			f.write(json.dumps((fn, url, hasData, hasTime)) + "\n")
