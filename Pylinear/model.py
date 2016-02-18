import os
import subprocess
import json
import argparse
import itertools
import re
import time
import hashlib

from Pylinear.util.scores import scores

### HELPER ###

def printCmd(command, quiet=False):
	'''Run command and print its output'''
	for i in execute(command):
		if not quiet: print(i)

def execute(command):
	'''Executes a command (blocking) and prints all output'''
	print(" ".join(command))
	popen = subprocess.Popen(command, stdout=subprocess.PIPE)
	lines_iterator = iter(popen.stdout.readline, b"")
	for line in lines_iterator:
		yield line

def getFeatureData(data, name):
	'''Generate features for each entry in datafile'''
	with open('{}/features/{}.json'.format(data, name)) as f:
		data = json.load(f)
	return data

### GLOBALS ###

# Path executables
trainEx = "./liblinear/train"
predictEx = "./liblinear/predict"

### MAIN ###

def combineFeatures(data, train, featureNames, idFile):
	'''Makes train/test file from features

	NOTE: Because this keeps file descriptors open, a maximum of 1024 feature files are allowed.
	The benefit of this, however, is that the full feature file isn't loaded into memory.
	'''

	# Load feature data
	trainData = getFeatureData(data, train)
	featureData = [getFeatureData(data, f) for f in featureNames]

	# Filter out features not defined for all
	sharedKeys = set(trainData.keys())
	for feature in featureData:
		sharedKeys &= set(feature.keys())

	# Merge feature data into one dict
	filteredDict = {}
	for key in sharedKeys:
		filteredDict[key] = {}
		filteredDict[key].update(trainData[key])
		for feature in featureData:
			filteredDict[key].update(feature[key])

	# Output directory
	outDir = os.path.join(data, 'results', '{},{}'.format(train,','.join(featureNames)))
	if not os.path.isdir(outDir):
		os.mkdir(outDir)
	outFn = os.path.join(outDir, 'data.txt')
	outFile = open(outFn, 'w')

	# Feature name -> ID mapping
	# If an id file is passed in, load it and don't add new feature labels
	ignoreNew = False
	if not idFile is None:
		ignoreNew = True
		with open(idFile) as f:
			featureIDs = json.load(f)
	else:
		featureIDs = {}
		featureC = 1


	# Add comment to first line describing what features were used
	s = " # {},{}\n".format(train, ','.join(featureNames))

	# Join feature files
	for key in sharedKeys:
		line = ''
		for featureName, value in filteredDict[key].items():
			if featureName == train:
				line = str(value) + line
			else:
				if ignoreNew:
					if not featureName in featureIDs:
						continue
				else:
					if featureName in featureIDs:
						featureID = featureIDs[featureName]
					else:
						featureIDs[featureName] = featureC
						featureID = featureC
						featureC += 1
				line += ' {}:{}'.format(featureID, value)
		s += line + '\n'
	outFile.write(s)

	# Write out name -> ID mapping
	with open(os.path.join(outDir, "map.json"), 'w') as f:
		json.dump(featureIDs, f)

	return outFn

def buildModel(trainFile, options):
	'''Builds model trained on given features'''

	if options is None:
		options = []
	# Set output folder to <splits folder>/results/<timestamp>_<hash>
	outputFolder = '/'.join(trainFile.split('/')[:-4]) + '/results/{}_{}/'.format(int(time.time()*1000000),hashlib.md5(str(options)+trainFile).hexdigest())
	os.makedirs(outputFolder)
	outFn = outputFolder + 'data.model'

	libArgs = [trainEx] + options + [trainFile, outFn]
	list(execute(libArgs))
	with open(outputFolder + 'info.txt', 'w') as f:
		f.write(trainFile.split('/')[-2] + '\n')
		f.write(' '.join(libArgs) + '\n')
	return outFn

def predictData(model, testFile, options):
	'''Makes prediction using model on given test data'''

	outFn = '/'.join(model.split('/')[:-1]) + '/predict.out'
	libArgs = [predictEx] + options + [testFile, model, outFn]
	printCmd(libArgs)
	# Write out F score, accuracy, precision, etc
	with open(testFile) as f:
		real = [i.split(' ')[0] for i in f.read().strip().split('\n')]
	with open(outFn) as f:
		pred = f.read().strip().split('\n')
	with open('/'.join(model.split('/')[:-1]) + '/stats.txt', 'w') as f:
		json.dump(scores(real, pred), f)

	return outFn