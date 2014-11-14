from __future__ import division

if __name__ == '__main__':
	import json
	import argparse

	parser = argparse.ArgumentParser(description='Calculate stats for data.')
	parser.add_argument('DIR', type=str, help="directory to read data from")
	args = parser.parse_args()

	with open(args.DIR + "/directory.json") as f:
		data = f.read()
	data = data.strip().split('\n')
	data = [json.loads(i) for i in data]

	# Stats
	avg_answers = 0
	avg_followers = 0
	qs_with_answers = 0
	qs_with_details = 0

	for entry in data:
		key = entry.keys()[0]
		fn = entry[key]['path']
		with open(fn) as f:
			url_data = json.load(f)

		num_answers = len(url_data['data']['answers'])
		if num_answers != 0:
			qs_with_answers += 1
			avg_answers += num_answers

		if url_data['data']['details']:
			qs_with_details += 1

		avg_followers += url_data['data']['followers']

	print("Number of Questions: {}".format(len(data)))
	print("Average Number of Answers: {:.2f}".format(avg_answers / len(data)))
	print("Average Number of Followers: {:.2f}".format(avg_followers / len(data)))
	print("Percent Questions with Answers: {:.2f}%".format(qs_with_answers / len(data) * 100))
	print("Percent Questions with Details: {:.2f}%".format(qs_with_details / len(data) * 100))