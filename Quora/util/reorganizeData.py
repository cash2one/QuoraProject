from Quora.util.fileInfo import getData
import hashlib
import json

def hashDirectory(directory, depth, urlHash):
	for c in urlHash[:depth]:
		directory = os.path.join(directory, c)
		if not os.path.exists(directory):
			os.mkdir(directory)
	directory = os.path.join(directory, urlHash)
	if not os.path.exists(directory):
		os.mkdir(directory)	
	return directory

HASH_DEPTH = 3

if __name__ == '__main__':
	from sys import argv
	import os

	DIR = '/export/a04/wpovell/scrape_data_ordered'
	OUT = '/export/a04/wpovell/out'

	if len(argv) > 1:
		DIR = argv[1]
	if len(argv) > 2:
		OUT = argv[2]

	if not os.path.exists(DIR):
		os.mkdir(DIR)
	if not os.path.exists(OUT):
		os.mkdir(OUT)

	for fn, data in getData(DIR):
		url = data["url"]
		md5hash = hashlib.md5(url).hexdigest()
		directory = hashDirectory(OUT, HASH_DEPTH, md5hash)

		with open(os.path.join(directory, 'question.txt'), 'w') as f:
			f.write(data['data']['question'].encode('utf8'))
		with open(os.path.join(directory, 'details.txt'), 'w') as f:
			f.write(data['data']['details'].encode('utf8'))

		metadata = {
			"url" : data["url"],
			"followers": data['data']['followers'],
			"topics" : data['data']['topics']
		}

		with open(os.path.join(directory, 'metadata.json'), 'w') as f:
			json.dump(metadata, f)

		for i, answer in enumerate(data['data']['answers']):
			with open(os.path.join(directory, 'answer{}_text.txt'.format(i)), 'w') as f:
				f.write(answer['text'].encode('utf8'))
			answer_metadata = {
				"author" : answer['author'],
				"upvotes" : answer['upvotes']
			}
			with open(os.path.join(directory, 'answer{}_metadata.json'.format(i)), 'w') as f:
				json.dump(answer_metadata, f)