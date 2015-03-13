import os
from time import time
import subprocess
import json
import argparse

from Pylinear.feature import generateFeatures

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

### GLOBALS ###

# Path executables
trainEx = "./liblinear/train"
predictEx = "./liblinear/predict"

# Data split names
splits = ['train', 'tune', 'dev', 'test']

### MAIN ###

def combineFeatures(data, train=None, featureNames=None, idFile=None):
	'''Makes train/test file from features

	NOTE: Because this keeps file descriptors open, a maximum of 1024 feature files are allowed.
	The benefit of this, however, is that the full feature file isn't loaded into memory.
	'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(data, argparse.Namespace):
		train = data.train
		featureNames = data.features
		idFile = data.idFile
		data = data.data
	##

	# Create feature data generators (these don't load in the whole file to memory)
	trainData = getFeatureData(data, train)
	featureData = [getFeatureData(data, f) for f in featureNames]

	# Output directory
	outDir = '{}/results/{},{}'.format(data, train,','.join(featureNames))
	if not os.path.isdir(outDir):
		os.mkdir(outDir)
	outFn = outDir + '/data.txt'
	outFile = open(outFn, 'w')

	# Feature name -> ID mapping
	# If an id file is passed in, load it and don't add new feature labels
	ignoreNew = False
	if not idFile is None:
		ignoreNew = True
		with open(idFile) as f:
			featureIDS = json.load(f)
	else:
		featureIDs = {}
		featureC = 1

	# Create libsvm input file
	first = True
	for trainEntry in trainData:
		s = '{} '.format(trainEntry[0][1])
		for f in featureData:
			features = f.next()
			for feature in features:
				if not feature[0] in featureIDs:
					if ignoreNew:
						continue
					featureIDs[feature[0]] = featureC
					featureC += 1
				i = featureIDs[feature[0]]
				s += '{}:{}'.format(i, feature[1])
		# Add comment to first line describing what features were used
		if first:
			s += " # {},{}".format(train, ','.join(featureNames))
			first = False
		outFile.write(s + '\n')
	outFile.close()

	# Write out name -> ID mapping
	with open(outDir + "/map.json", 'w') as f:
		json.dump(featureIDs, f)

	return outFn

def buildModel(trainFile, options=None):
	'''Builds model trained on given features'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(trainFile, argparse.Namespace):
		trainFile = trainFile.trainFile
	##

	if options is None:
		options = []

	outFn = '.'.join(trainFile.split('.')[:-1]) + '.model'

	libArgs = [trainEx] + options + [trainFile, outFn]
	execute(libArgs)

def predictData(model, testFile=None, options=None):
	'''Makes prediction using model on given test data'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(model, argparse.Namespace):
		options = testFile
		testFile = model.testFile
		model = model.model
	##

	outFn = '/'.join(model.split('/')[:-1]) + 'predict.out'

	libArgs = [predictEx] + options + [testFile, model, outFn]
	execute(libArgs)