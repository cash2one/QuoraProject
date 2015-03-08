from Quora.QuoraScraper import QuoraScraper
import argparse
import json

parser = argparse.ArgumentParser(description='Get missing post times.')
parser.add_argument('-i', type=str, default="missingTimes.txt", nargs="?", help='file to read urls from')
parser.add_argument('-o', type=str, default="newTimes.txt", nargs="?", help='file to output new data to')
args = parser.parse_args()
inFile = args.i
outFile = args.o

qs = QuoraScraper()

with open(inFile) as f:
	files = f.read().split('\n')

outF = open(outFile, 'w')
for file in files:
	with open(file) as f:
		data = json.load(f)
	url = data['url']
	newData = qs.processLog(url)
	outF.write(json.dumps({url:newData}) +"\n")
outF.close()