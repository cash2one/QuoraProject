import json
import tarfile
import os
import argparse

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TCompactProtocol

### HELPER ###

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

### FEATURE GEN ###

def followers(data):
	'''Generate feature file for number of followers a question has'''
	outFile = open("{}/features/followers.txt".format(data), 'w')
	for name, content in getDataFiles(data):
		if not name.endswith("metadata.json"):
			continue
		content = json.loads(content)
		outFile.write("followers:{}\n".format(content["followers"]))
	outFile.close()

def question_length(data):
	'''Generates feature file for length of question'''
	outFile = open("{}/features/question_length.txt".format(data), 'w')
	for name, content in getDataFiles(data):
		if not name.endswith("question.comm"):
			continue
		comm = commFromData(content)
		outFile.write("question_length:{}\n".format(len(comm.text)))
	outFile.close()



# Dictionary of feature names and func that generate them
feature_func = {
	"followers" : followers,
	"question_length" : question_length
}

### MAIN ###

def listFeatures(*_):
	'''Lists features that can be generated.'''
	print("Feature Options:")
	for key, value in feature_func.items():
		print("\t{} : {}".format(key, value.__doc__))

def generateFeatures(features, data=None):
	'''Generates feature files.

	Presumes directory structure <data>/features/ already exists.
	'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(features, argparse.Namespace):
		data = features.data
		features = features.features
	##

	# Check if any of requested features doesn't exist
	f = [f for f in features if f not in feature_func]
	if f:
		print("ERROR: The following feature(s) could not be generated: {}".format(', '.join(f)))
		exit(1)

	# Write line -> file mapping
	with open('{}/fileMapping.txt'.format(data), 'w') as outf:
		for fn in getFiles('{}/data'.format(data)):
			if not fn.endswith(".tar.gz"):
				continue
			f = tarfile.open(fn, "r:gz")
			for tarfn in f.getmembers():
				outf.write(tarfn.name + '\n')

	# Generate features
	for feature in features:
		feature_func[feature](data)