import json
from gzip import GzipFile
from binascii import a2b_hex
from StringIO import StringIO
from sys import argv
from QuoraScraper import QuoraScraper

if __name__ == '__main__':
	fn = "data/directory.json"
	if len(argv) > 1:
		fn = argv[1]

	with open(fn) as f:
		data = f.read()
	data = [json.loads(i) for i in data.strip().split('\n')]
	for i in data:
		fn = list(i.values())[0]['path']
		print(fn)
		with open(fn) as f:
			entry = json.load(f)
		html_data = GzipFile(fileobj=StringIO(a2b_hex(entry['html']))).read()
		reparsed = QuoraScraper.getQuestion(html_data)
		entry['data'] = reparsed
		with open(fn, 'w') as f:
			json.dump(entry, f)