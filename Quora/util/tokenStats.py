from __future__ import division
from Quora.util.fileInfo import getData
import re
import math

def mean(l):
	return sum(l) / len(l)

def varaince(l, mean):
	var = 0
	c = 0
	for i in l:
		var += (mean - i) ** 2
		c += 1
	return var / c

if __name__ == '__main__':
	from sys import argv
	DIR = '/export/a04/wpovell/scrape_data_ordered'
	if len(argv) > 1:
		DIR = argv[1]

	TOKENIZE = re.compile(r'\s+')

	answer_token = []
	question_token = []
	details_token = []

	data_gen = getData(DIR)
	for fn, data in data_gen:
		if not 'data' in data:
			continue
		question_token.append(len(re.split(TOKENIZE, data['data']['question'])))
		details_token.append(len(re.split(TOKENIZE, data['data']['details'])))

		for answer in data['data']['answers']:
			answer_token.append(len(re.split(TOKENIZE, answer['text'])))

	q_mean = mean(question_token)
	q_var  = varaince(question_token, q_mean)

	d_mean = mean(details_token)
	d_var  = varaince(details_token, d_mean)

	a_mean = mean(answer_token)
	a_var  = varaince(answer_token, a_mean)

	print("Question:")
	print("\tMean: {}".format(q_mean))
	print("\tVariance: {}".format(q_var))
	print("\tStd. Deviation: {}".format(q_var ** 0.5))

	print("Details:")
	print("\tMean: {}".format(d_mean))
	print("\tVariance: {}".format(d_var))
	print("\tStd. Deviation: {}".format(d_var ** 0.5))

	print("Answer:")
	print("\tMean: {}".format(a_mean))
	print("\tVariance: {}".format(a_var))
	print("\tStd. Deviation: {}".format(a_var ** 0.5))