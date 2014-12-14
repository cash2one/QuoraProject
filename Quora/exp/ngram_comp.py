from Quora.util.getText import getText
import TwitterKov
from TwitterKov.ds.NGram import NGram
from TwitterKov.ds.DataCount import DataCount
from TwitterKov.pm.BackOff import BackOff

N_GRAM_ORDER = 2
ORDERS = set(range(N_GRAM_ORDER + 1))
def textToGrams(text, order):
	'''Takes an array of strings and returns their N-grams'''
	text = [TwitterKov.tkn(i.decode('utf-8')) for i in text]
	text = [TwitterKov.gramitizeTokens(i, order) for i in text]
	text = [inner for outer in text for inner in outer]
	return text

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Scores Quora data against Twitter and Newswire N-gram models')

	parser.add_argument('-t', default='twitterData/dev.gz', help="Twitter data to train on")
	parser.add_argument('-q', default='data_sorted', help="Quora data to score on")
	args = parser.parse_args()

	# Twitter data
	twitterModel = NGram()
	for tweet in TwitterKov.readGZ(args.t):
		tweet = TwitterKov.tkn(tweet)
		grams = TwitterKov.gramitizeTokens(tweet, N_GRAM_ORDER)
		twitterModel.train(grams, ORDERS, 1)

	print("LOADED TWITTER DATA")

	# Quora data
	quoraQuestionModel = DataCount()
	quoraAnswerModel = DataCount()
	for q, a in getText(args.q):
		question_text = textToGrams([q], N_GRAM_ORDER)
		quoraQuestionModel.train(question_text, twitterModel, ORDERS)

		answer_text = textToGrams(a, N_GRAM_ORDER)
		quoraAnswerModel.train(answer_text, twitterModel, ORDERS)

	print("LOADED QUORA DATA")

	yq = twitterModel.score(quoraQuestionModel, BackOff(0.5), N_GRAM_ORDER)
	ya = twitterModel.score(quoraAnswerModel, BackOff(0.5), N_GRAM_ORDER)

	print("Questions --> Twitter: {:.5}".format(yq))
	print("Answers   --> Twitter: {:.5}".format(ya))