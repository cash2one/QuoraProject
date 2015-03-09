#!/usr/bin/env python
import json
import hashlib
import tarfile
import os

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TCompactProtocol

def getID(url):
	'''Generate url for ID'''
	return hashlib.md5(url).hexdigest()

def getFiles(d):
	'''Recursively lists files in directory'''
	for i in os.walk(d):
		for j in i[2]:
			yield '{}/{}'.format(i[0], j)

def getDataFiles(data):
	'''Open all tar.gz files and return member data'''
	for fn in getFiles("{}/data".format(data)):
		if not fn.endswith(".tar.gz"):
			continue
		f = tarfile.open(fn, "r:gz")
		for tarfn in f.getmembers():
			tarf = f.extractfile(tarfn)
			yield (tarfn.name, tarf.read())
			tarf.close()
		f.close()

def commFromData(data):
	'''Create Communication object from byte string'''
	comm = Communication()
	TSerialization.deserialize(comm, data, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
	return comm

def followers(data):
	'''Generate feature file for number of followers a question has'''
	outFile = open("{}/features/followers.txt".format(data), 'w')
	for name, content in getDataFiles(data):
		if not name.endswith("metadata.json"):
			continue
		content = json.loads(content)
		ID = getID(content['url'])
		outFile.write("{}: {}\n".format(ID, content["followers"]))
	outFile.close()

def question_length(data):
	'''Generates feature file for length of question'''
	outFile = open("{}/features/question_length.txt".format(data), 'w')
	for name, content in getDataFiles(data):
		if not name.endswith("question.comm"):
			continue
		comm = commFromData(content)
		ID = comm.id
		outFile.write("{}: {}\n".format(ID, len(comm.text)))
	outFile.close()

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