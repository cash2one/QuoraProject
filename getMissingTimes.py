from Quora.process import getFiles
import json

inFn = '/export/a04/wpovell/scrape_data_ordered'
outFn = '/export/a04/wpovell/missingTimes.txt'

files = getFiles(inFn)
out = open(outFn, 'w')
for fn in files:
	with open(fn) as f:
		if not 'log' in json.load(f):
			out.write(fn+'\n')
out.close()