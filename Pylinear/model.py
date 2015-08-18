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
	with open('{}/features/{}.txt'.format(data, name)) as f:
		line = f.readline()
		while line:
			entry = line.strip().split(' ')
			yield [feature.split(':') for feature in entry]
			line = f.readline()

def makeIDSet(data, train, features):
	'''Returns set of ids present in all given feature files.'''
	with open('{}/features/{}.list.txt'.format(data, train)) as f:
		d = f.read()
		ret = set(json.loads(d))

	for name in features:
		with open('{}/features/{}.list.txt'.format(data, name)) as f:
			temp = set(json.load(f))
			ret &= temp
	return ret

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

	# Create feature data generators (these don't load in the whole file to memory)
	trainData = getFeatureData(data, train)
	featureData = [getFeatureData(data, f) for f in featureNames]

	# Create set of ids present in all feature files
	idSet = makeIDSet(data, train, featureNames)

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


	# Join feature files
	s = ''
	first = True
	try:
		while True:
			# Get next valid feature line from 'to predict'
			trainLineID = ''
			while trainLineID not in idSet:
				trainEntry = trainData.next()
				trainLineID = trainEntry[0][0]
			s += '{} '.format(trainEntry[1][1])

			# Get next valid feature lines from 'predictors'
			featureTuples = []
			for f in featureData:
				featLineID = ''
				while featLineID not in idSet:
					featEntry = f.next()
					featLineID = featEntry[0][0]
				assert trainLineID == featLineID
				features = featEntry[1:]

				# Each feature on feature line
				for feature in features:
					if not feature[0] in featureIDs:
						# Skip feature if not present in train
						if ignoreNew:
							continue
						# Add feature to index
						featureIDs[feature[0]] = featureC
						featureC += 1
					i = featureIDs[feature[0]]
					if feature[0]: # I forget why this check is necessary but now I'm afraid to remove it...
						featureTuples.append((i, feature[1]))

			# Feature IDs need to be in accending order
			featureTuples.sort()
			for ID, featureVal in featureTuples:
				s += '{}:{} '.format(ID, featureVal)

			# Add comment to first line describing what features were used
			if first:
				s += " # {},{}".format(train, ','.join(featureNames))
				first = False

			s = s.strip()
			outFile.write(s + '\n')
			s = ''
	except StopIteration:
		pass

	outFile.close()

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