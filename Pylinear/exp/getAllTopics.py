'''Generate list of all topic tags found in dataset.'''
from __future__ import unicode_literals
from Pylinear.feature import getDataFiles
import codecs

if __name__ == '__main__':
	from sys import argv
	import json

	inp = argv[1] if len(argv) > 1 else 'train/data'
	out = argv[2] if len(argv) > 2 else 'topics.txt'

	topics = set()
	for name, content in getDataFiles(inp):
		if name.endswith('metadata.json'):
			data = json.loads(content)
			try:
				for topic in data['topics']:
					topics.add(topic)
			except KeyError:
				print("BAD DATA")
				continue
	with codecs.open(out, 'w', 'utf-8') as f:
		for i in topics:
			f.write(i + '\n')