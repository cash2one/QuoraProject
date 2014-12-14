import os
import json

def getText(DIR):
	'''Takes directory file and returns raw question and answer text'''
	question_text = []
	answer_text = []
	for fn in os.listdir(DIR):
		try:
			with open(os.path.join(DIR, fn)) as f:
				data = json.load(f)

			text = data['data']['question'].replace(u'\u00a0', ' ').encode('utf-8').strip()
			question_text.append(text)
			for ans in data['data']['answers']:
				text = ans['text'].replace(u'\u00a0', ' ').encode('utf-8').strip()
				answer_text.append(text)
		except KeyError:
			if DEBUG: print(fn)
	return (question_text, answer_text)

DEBUG = True

if __name__ == '__main__':
	from sys import argv

	DIR = argv[1]

	question_text, answer_text = getText(DIR)

	with open(os.path.join(DIR, 'question_text.txt'), 'w') as f:
		json.dump(question_text, f)

	with open(os.path.join(DIR, 'answer_text.txt'), 'w') as f:
		json.dump(answer_text, f)
