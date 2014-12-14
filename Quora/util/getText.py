import os
import json

def getText(DIR):
	'''Takes directory and returns raw question and answer text'''
	for fn in os.listdir(DIR):
		joined = os.path.join(DIR, fn)

		if os.path.isdir(joined):
			for entry in getText(joined):
				yield entry
		elif fn.endswith('.out'):
			with open(joined) as f:
				data = json.load(f)
			if not 'data' in data:
				continue

			text = data['data']['question'].replace(u'\u00a0', ' ').encode('utf-8').strip()
			question_text = text
			answers = []
			for ans in data['data']['answers']:
				text = ans['text'].replace(u'\u00a0', ' ').encode('utf-8').strip()
				answers.append(text)
			yield (question_text, answers)

DEBUG = True

if __name__ == '__main__':
	from sys import argv

	DIR = argv[1]

	text = getText(DIR)
	question_text = []
	answer_text = []
	for entry in text:
		question_text.append(entry[0])
		for answer in entry[1]:
			answer_text.append(answer)

	with open('question_text.txt', 'w') as f:
		json.dump(question_text, f)

	with open('answer_text.txt', 'w') as f:
		json.dump(answer_text, f)
