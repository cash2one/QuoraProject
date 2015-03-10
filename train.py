import os
from time import time
import subprocess

### HELPER ###

def execute(command):
	'''Executes a command (blocking) and prints all output'''
	popen = subprocess.Popen(command, stdout=subprocess.PIPE)
	lines_iterator = iter(popen.stdout.readline, b"")
	for line in lines_iterator:
		print(line)

def getFeatureData(data, name):
	'''Generate features for each entry in datafile'''
	with open('{}/features/{}.txt'.format(data, name)) as f:
		line = f.readline()
		while line:
			entry = line.strip().split(' ')
			yield [feature.split(':') for feature in entry]
			line = f.readline()

### PATHS ###

train = "./liblinear/train"

### MAIN ###

def buildModel(args):
	'''Builds model trained on given features'''
	args.train = args.train[0]
	t = int(time())
	os.mkdir('{}/results/{}'.format(args.data, t))

	'''NOTE: Because this keeps file descriptors open, a maximum of 1024 feature files are allowed.
	The benefit of this, however, is that the full feature file isn't loaded into memory.'''

	trainData = getFeatureData(args.data, args.train)
	featureData = [getFeatureData(args.data, f) for f in args.features]
	featureIDs = []
	outFile = open('{}/results/{}/train.dat'.format(args.data, t), 'w')
	print("Writing training data to {}/results/{}/train.dat".format(args.data, t))

	for trainEntry in trainData:
		s = '{} '.format(trainEntry[0][1])
		for f in featureData:
			features = f.next()
			for feature in features:
				try:
					i = featureIDs.index(feature[0])
				except ValueError:
					i = len(featureIDs)
					featureIDs.append(feature[0])
				s += '{}:{}'.format(i+1, feature[1])
		outFile.write(s + '\n')
	outFile.close()

	print("Building model and writing to {}/results/{}/{}.model".format(args.data, t, args.data))
	if args.options:
		opts = args.options[0].split()
	else:
		opts = []
	libArgs = [train] + opts + ["{}/results/{}/train.dat".format(args.data, t), "{}/results/{}/{}.model".format(args.data, t, args.data)]
	execute(libArgs)