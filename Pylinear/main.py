from time import time
import os

from Pylinear import BASE_PATH
from Pylinear.model import buildModel, predictData, combineFeatures

import Pylinear.feature as fg

if __name__ == '__main__':
	import argparse

	import logging
	numeric_level = getattr(logging, "DEBUG", None)
	logging.basicConfig(level=numeric_level)

	parser = argparse.ArgumentParser(description='Tool for generating feature data, traning models, and prediciting values.')
	subparsers = parser.add_subparsers(dest='command')

	### FEATURE GENERATION ###

	# Main "gen" option
	about = "Generate features"
	genP = subparsers.add_parser("gen", help=about, description=about)
	genSub = genP.add_subparsers(dest="feature")

	# All of following are options on top of "gen" to generate a particular feature

	about = "Follower count"
	followersP = genSub.add_parser("followers", help=about, description=about)
	followersP.add_argument('-s', '--split', required=True, help='split to generate features for')

	about = "Upvote count"
	upvoteP = genSub.add_parser("upvotes", help=about, description=about)
	upvoteP.add_argument('-s', '--split', required=True, help='split to generate features for')

	about = "Normalized upvote count"
	normupvoteP = genSub.add_parser("normalized_upvotes", help=about, description=about)
	normupvoteP.add_argument('-s', '--split', required=True, help='split to generate features for')

	about = "Length of entry"
	lenP = genSub.add_parser("length", help=about, description=about)
	lenP.add_argument('-s', '--split', required=True, help='split to generate features for')
	lenP.add_argument('--answer', action="store_true", help="Generate features for answers rather than questions")

	about = "Tagged topics"
	topicP = genSub.add_parser("topics", help=about, description=about)
	topicP.add_argument('-s', '--split', required=True, help='split to generate features for')
	topicP.add_argument('--answer', action="store_true", help="features for answers rather than questions")

	about = "N-gram frequency"
	ngramP = genSub.add_parser("ngram", help=about, description=about)
	ngramP.add_argument('-s', '--split', required=True, help='split to generate features for')
	ngramP.add_argument('-o', '--order', default=1, type=int, help="n-gram order to generate")
	ngramP.add_argument('-c', '--cutoff', default=3,  type=int, help="number of times a token must occur to not be OOV")
	ngramP.add_argument('--binary', action="store_true", help="binary features rather than raw counts")
	ngramP.add_argument('--answer', action="store_true", help="features for answers rather than questions")
	ngramP.add_argument('--POS', action="store_true", help="use POS tags instead of n-grams")

	'''
	about = "Term frequency–Inverse document frequency"
	tfidfP = genSub.add_parser("tfidf", help=about, description=about)
	tfidfP.add_argument('-s', '--split', required=True, help='split to generate features for')
	tfidfP.add_argument('-c', '--cutoff', default=3,  type=int, help="number of times a token must occur to not be OOV")
	tfidfP.add_argument('--POS', action="store_true", help="use POS tags instead of n-grams")
	tfidfP.add_argument('--answer', action="store_true", help="features for answers rather than questions")

	about = "Has at least N answers"
	hasAnswersP = genSub.add_parser("hasAnswers", help=about, description=about)
	hasAnswersP.add_argument('-s', '--split', required=True, help='split to generate features for')
	hasAnswersP.add_argument('-n', type=int, help="sets number of answers needed to fire")

	about = "Time taken to get an answer"
	answerTimeP = genSub.add_parser("answerTime", help=about, description=about)
	answerTimeP.add_argument('-s', '--split', required=True, help='split to generate features for')

	about = "Does an answer have more than the average number of upvotes?"
	aboveMeanUpvotesP = genSub.add_parser("aboveMeanUpvotes", help=about, description=about)
	aboveMeanUpvotesP.add_argument('-s', '--split', required=True, help='split to generate features for')
	'''

	### COMBINE FEATURES INTO TEMPLATE ###

	about = "Combine feature templates"
	templateParser = subparsers.add_parser("template", help=about, description=about)
	templateParser.add_argument('-s', '--split', required=True, help="dataset to use features for")
	templateParser.add_argument('-t', '--train', required=True, help='value or class feature that is to be predicted')
	templateParser.add_argument('-f', '--features', required=True, nargs="+", help='features to be used to predict')
	templateParser.add_argument('-i', '--idFile', default=None, help="id mapping to load")

	### BUILD LIBLINEAR MODEL FROM TEMPLATE ###

	about = "Build model from data file"
	buildParser = subparsers.add_parser("build", help=about, description=about)
	buildParser.add_argument('-t', '--trainFile', required=True, help='train file to load')

	### PREDICT USING GENERATED MODEL ###

	about = "Use model to predict values for dataset"
	predictParser = subparsers.add_parser("predict", help=about, description=about)
	predictParser.add_argument('-m', '--model', required=True, help='model file to use')
	predictParser.add_argument('-t', '--testFile', required=True, help='test file to use')

	# Unknown are additional arguments that may get passed to liblinear
	args, unknown = parser.parse_known_args()

	cmd = args.command
	if cmd == "gen":
		feat = args.feature
		path = os.path.join(BASE_PATH, "splits", args.split)

		#if feat == "ngram":
		#	fg.ngram(path, args.order, args.cutoff, args.binary, args.POS, args.answer)
		if feat == "followers":
			generator = fg.FollowerGen(path)
		elif feat == "upvotes":
			generator = fg.UpvoteGen(path)
		elif feat == "normalized_upvotes":
			generator = fg.NormalizedUpvoteGen(path)
		elif feat == "length":
			generator = fg.LengthGen(path, args.answer)
		elif feat == "topics":
			generator = fg.TopicGen(path)
		elif feat == "ngram":
			generator = fg.NGramGen(path, args.order, args.cutoff, args.binary, args.POS, args.answer)
		'''
		elif feat == "hasAnswers":
			fg.hasAnswers(path, args.n)
		elif feat == "answerTime":
			fg.answerTime(path)
		elif feat == "tfidf":
			fg.tfidf(path, args.cutoff, args.POS, args.answer)
		elif feat == "aboveMeanUpvotes":
			fg.aboveMeanUpvotes(path)
		'''

		generator.generate()

	elif cmd == "template":
		path = os.path.join(BASE_PATH, "splits", args.split)
		combineFeatures(path, args.train, args.features, args.idFile)

	elif cmd == "build":
		buildModel(args.trainFile, unknown)

	elif cmd == "predict":
		predictData(args.model, args.testFile, unknown)