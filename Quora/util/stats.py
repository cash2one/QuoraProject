from __future__ import division
import os
import json

def getData(DIR):
	'''Takes directory and returns json data'''
	for fn in os.listdir(DIR):
		joined = os.path.join(DIR, fn)

		if os.path.isdir(joined):
			for entry in getData(joined):
				yield entry
		elif fn.endswith('.out'):
			with open(joined) as f:
				data = json.load(f)
			if not 'data' in data:
				continue
			yield data

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Calculate stats for data.')
	parser.add_argument('DIR', type=str, help="directory file to read data from")
	parser.add_argument('-t', '--topic', type=str, nargs=1, help="only give stats for questions labled with this topic")
	args = parser.parse_args()

	# Conditioned topic
	main_topic = args.topic[0] if args.topic else None

	'''
	with open(args.DIR) as f:
		data = f.read()
	data = data.strip().split('\n')
	data = [json.loads(i) for i in data]
	'''
	data = getData(args.DIR)

	# Stats
	avg_answers = 0
	avg_followers = 0
	qs_with_answers = 0
	qs_with_details = 0
	topic_counts = {}
	main_topic_count = 0
	details_w_ans = 0
	avg_size = 0

	LEN = 0
	for url_data in data:
		LEN += 1
		# Size based on string length
		avg_size += len(json.dumps(url_data))

		url_data['data']['topics'] = [i[1:] for i in url_data['data']['topics']]
		if not main_topic or main_topic in url_data['data']['topics']:
			main_topic_count += 1

			# Answers
			num_answers = len(url_data['data']['answers'])
			if num_answers != 0:
				qs_with_answers += 1
				avg_answers += num_answers

			# Details
			if url_data['data']['details']:
				qs_with_details += 1
				if num_answers != 0:
					details_w_ans += 1

			# Followers
			avg_followers += url_data['data']['followers']

			# Topics
			for topic in url_data['data']['topics']:
				if topic not in topic_counts:
					topic_counts[topic] = 0
				topic_counts[topic] += 1

	print("Number of Questions: {}".format(LEN))
	if main_topic:
		print("Number of Questions Labled With {}: {}".format(main_topic, main_topic_count))
	print('\tAverage Size: {:.2f}kB'.format(avg_size / LEN / 1000))
	print("\tAverage Number of Answers: {:.2f}".format(avg_answers / LEN))
	print("\tAverage Number of Followers: {:.2f}".format(avg_followers / LEN))
	print("\tPercent Questions with Answers: {:.2f}%".format(qs_with_answers / LEN * 100))
	print("\tPercent Questions with Details: {:.2f}%".format(qs_with_details / LEN * 100))
	print("\tPercent of Questions with Details that have Answers: {:.2f}%".format(details_w_ans / qs_with_details * 100))
	print('')

	topic_counts = [(count, topic) for topic, count in topic_counts.items()]
	topic_counts.sort()

	# Top topics
	if main_topic:
		print("Percent of Questions with the Topic of {}: {:.2f}%".format(main_topic, main_topic_count / LEN * 100))
		print("Top 20 Topics Co-Labled With {}:".format(main_topic))
		for count, topic in topic_counts[::-1][:20]:
			if topic != main_topic:
				print("\t{}: {:.2f}%".format(topic, count / main_topic_count * 100))
	else:
		print("Top 20 Topics:")
		for count, topic in topic_counts[::-1][:20]:
			print("\t{}: {:.2f}%".format(topic, count / LEN * 100))