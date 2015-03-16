from Quora.QuoraScraper import QuoraScraper
import argparse
import json
import traceback

parser = argparse.ArgumentParser(description='Get missing post times.')
parser.add_argument('-i', default="missingTimes.txt", nargs="?", help='file to read urls from')
parser.add_argument('-e', default="errorUrls.txt", nargs="?", help='file to write output to')
args = parser.parse_args()
inFile = args.i

qs = QuoraScraper()

with open(inFile) as f:
	files = f.read().split('\n')

for fn in files:
	if not fn.endswith('.out'):
		continue
	with open(fn) as f:
		data = json.load(f)
	if 'log' in data:
		continue
	url = data['url']
	try:
		newData = qs.processLog(url)
	except Exception:
		print("ERROR: {}".format(fn))
		continue
	data['log'] = newData
	with open(fn, 'w') as f:
		json.dump(data, f)
	print("{}".format(fn))