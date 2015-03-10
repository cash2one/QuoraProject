#!/usr/bin/env python

from feature import generateFeatures, listFeatures
from train import buildModel

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Generate features for dataset')

	subparsers = parser.add_subparsers(help='commands', dest='command')

	listParser = subparsers.add_parser("list", description="list possible features that can be generated")

	genParser = subparsers.add_parser("gen", description="generate feature")
	genParser.add_argument('-f', '--features', required=True, nargs='+', help='features to generate')
	genParser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to generate features for')

	evalParser = subparsers.add_parser("eval", description='Classification over given features')
	evalParser.add_argument('-t', '--train', required=True, nargs=1, help='feature to train on')
	evalParser.add_argument('-f', '--features', required=True, nargs='+', help='features to use')
	evalParser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to use')
	evalParser.add_argument('-o', '--options', nargs=1, help="options to pass lib-linear")

	args = parser.parse_args()

	{
		"list" : listFeatures,
		"gen"  : generateFeatures,
		"eval" : buildModel
	}[args.command](args)