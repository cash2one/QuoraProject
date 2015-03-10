from Quora.QuoraScraper import QuoraScraper
import argparse
import json

parser = argparse.ArgumentParser(description='Get missing post times.')
parser.add_argument('-i', type=str, default="missingTimes.txt", nargs="?", help='file to read urls from')
args = parser.parse_args()
inFile = args.i

qs = QuoraScraper()

with open(inFile) as f:
	files = f.read().split('\n')

for fn in files:
	with open(fn) as f:
		data = json.load(f)
	if 'log' in data:
		continue
	url = data['url']
	newData = qs.processLog(url)
	data['log'] = newData
	with open(fn, 'w') as f:
		json.dump(data, f)
	print("{}".format(fn))