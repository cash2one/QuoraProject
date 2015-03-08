#!/usr/bin/env python

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Classification over given features')
	parser.add_argument('-f', '--features', required=True, nargs='+', help='features to use')
	parser.add_argument('-d', '--data', nargs=1, default='train', help='dataset to use')
	args = parser.parse_args()
	print(args)