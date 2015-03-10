#!/usr/bin/env python

from feature import generateFeatures, listFeatures
from train import buildModel

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Tool for generating feature data, traning models, and prediciting values.')

	subparsers = parser.add_subparsers(dest='command')

	temp = 'List possible features'
	listParser = subparsers.add_parser("list", help=temp, description=temp)

	temp = "Generate features"
	genParser = subparsers.add_parser("gen", help=temp, description=temp)
	genParser.add_argument('-f', '--features', required=True, nargs='+', help='features to generate')
	genParser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to generate features for')

	temp = "Classification over given features"
	evalParser = subparsers.add_parser("build", help=temp, description=temp)
	evalParser.add_argument('-t', '--train', required=True, nargs=1, help='feature to train on')
	evalParser.add_argument('-f', '--features', required=True, nargs='+', help='features to use')
	evalParser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to use')
	evalParser.add_argument('-o', '--options', nargs=1, help="options to pass lib-linear")

	#predictParser = subparsers.add_parser("predict", descript")

	args = parser.parse_args()

	{
		"list" : listFeatures,
		"gen"  : generateFeatures,
		"build" : buildModel
	}[args.command](args)