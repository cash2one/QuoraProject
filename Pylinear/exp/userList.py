'''Generates data about number of followers question authors get.'''
import json
from Pylinear.feature import getDataFiles

if __name__ == '__main__':
	from sys import argv
	dataDir = 'splits/train'
	if len(argv) > 1:
		dataDir = argv[1]

	authors = {}
	c = 0
	for i, f in getDataFiles(dataDir):
		if i.endswith('metadata.json'):
			c += 1
			data = json.load(f)
			author = data['author']
			if not author in authors:
				authors[author] = []
			authors[author].append(data['followers'])

	with open('userOut.json', 'w') as f:
		json.dump(authors, f)