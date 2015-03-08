#!/usr/bin/env python

def followers(data):
	'''Generate feature file for number of followers a question has'''
	pass

def question_length(data):
	'''Generates feature file for length of question'''
	pass

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Generate features for dataset')

	subparsers = parser.add_subparsers(help='commands')

	listParser = subparsers.add_parser("list", help="list possible features that can be generated")

	genParser = subparsers.add_parser("gen", help="generate feature")
	genParser.add_argument('-f', '--features', required=True, nargs='+', help='features to generate')
	genParser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to generate features for')
	args = parser.parse_args()

	feature_func = {
		"followers" : followers,
		"question_length" : question_length
	}

	if 'features' in args:
		f = [f for f in args.features if f not in feature_func]
		if f:
			print("ERROR: The following features could not be generated: {}".format(', '.join(f)))
			exit(1)
		for feature in args.features:
			print("GENERATING {}".format(feature))
			feature_func[feature](args.data)
	else:
		print("Feature Options:")
		for key, value in feature_func.items():
			print("\t{} : {}".format(key, value.__doc__))