from __future__ import division

if __name__ == '__main__':
	import json
	import argparse

	parser = argparse.ArgumentParser(description='Calculate stats for data.')
	parser.add_argument('DIR', type=str, help="directory file to read data from")
	parser.add_argument('-t', '--topic', type=str, nargs=1, help="only give stats for questions labled with this topic")
	args = parser.parse_args()

	main_topic = args.topic[0] if args.topic else None
	with open(args.DIR) as f:
		data = f.read()
	data = data.strip().split('\n')
	data = [json.loads(i) for i in data]

	# Stats
	avg_answers = 0
	avg_followers = 0
	qs_with_answers = 0
	qs_with_details = 0
	topic_counts = {}
	main_topic_count = 0

	for entry in data:
		key = entry.keys()[0]
		fn = entry[key]['path']
		with open(fn) as f:
			url_data = json.load(f)
		url_data['data']['topics'] = [i[1:] for i in url_data['data']['topics']]
		if not main_topic or main_topic in url_data['data']['topics']:
			main_topic_count += 1
			num_answers = len(url_data['data']['answers'])
			if num_answers != 0:
				qs_with_answers += 1
				avg_answers += num_answers

			if url_data['data']['details']:
				qs_with_details += 1

			avg_followers += url_data['data']['followers']

			for topic in url_data['data']['topics']:
				if topic not in topic_counts:
					topic_counts[topic] = 0
				topic_counts[topic] += 1

	print("Number of Questions: {}".format(len(data)))
	if main_topic:
		print("Number of Questions Labled With {}: {}".format(main_topic, main_topic_count))
	print("\tAverage Number of Answers: {:.2f}".format(avg_answers / len(data)))
	print("\tAverage Number of Followers: {:.2f}".format(avg_followers / len(data)))
	print("\tPercent Questions with Answers: {:.2f}%".format(qs_with_answers / len(data) * 100))
	print("\tPercent Questions with Details: {:.2f}%".format(qs_with_details / len(data) * 100))
	print('')

	topic_counts = [(count, topic) for topic, count in topic_counts.items()]
	topic_counts.sort()

	if main_topic:
		print("Percent of Questions with the Topic of {}: {:.2f}%".format(main_topic, main_topic_count / len(data) * 100))
		print("Top 20 Topics Co-Labled With {}:".format(main_topic))
		for count, topic in topic_counts[::-1][:20]:
			if topic != main_topic:
				print("\t{}: {:.2f}%".format(topic, count / main_topic_count * 100))
	else:
		print("Top 20 Topics:")
		for count, topic in topic_counts[::-1][:20]:
			print("\t{}: {:.2f}%".format(topic, count / len(data) * 100))