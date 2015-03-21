from __future__ import unicode_literals
from Pylinear.feature import getFiles
import tarfile
import codecs

def getDataFiles(DIR):
	'''Open all tar.gz files and return member data'''
	for fn in getFiles(DIR):
		if not fn.endswith(".tar.gz"):
			continue
		f = tarfile.open(fn, "r:gz")
		for tarfn in f.getmembers():
			tarf = f.extractfile(tarfn)
			yield (tarfn.name, tarf.read())
			tarf.close()
		f.close()

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