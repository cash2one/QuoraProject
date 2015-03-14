import os
import subprocess
import json
import argparse
import itertools
import re

from Pylinear.feature import generateFeatures

### HELPER ###

def printCmd(command, quiet=False):
	for i in execute(command):
		if not quiet: print(i)

def execute(command):
	'''Executes a command (blocking) and prints all output'''
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

### GLOBALS ###

# Path executables
trainEx = "./liblinear/train"
predictEx = "./liblinear/predict"

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
			featureIDs = json.load(f)
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
	list(execute(libArgs))
	return outFn

def predictData(model, testFile=None, options=None):
	'''Makes prediction using model on given test data'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(model, argparse.Namespace):
		options = testFile
		testFile = model.testFile
		model = model.model
	##

	outFn = '/'.join(model.split('/')[:-1]) + '/predict.out'
	libArgs = [predictEx] + options + [testFile, model, outFn]
	printCmd(libArgs)
	return outFn

def getVal(trainFile, devFile, options):
	modelFn = '/'.join(trainFile.split('/')[:-1]) + '/grid.model'
	buildArgs = [trainEx] + options + [trainFile, modelFn]
	predictArgs = [predictEx, trainFile, modelFn, '/dev/null']
 	list(execute(buildArgs))
	line = list(execute(predictArgs))[0]
	return re.findall(r'([.\d]+)', line)[0], "%" if line.startswith("Accuracy") else " (Mean squared error)"

def gridSearch(args, _):
	flags = {}
	with open(args.options) as f:
		for line in f.read().split('\n'):
			line = line.split()
			flags[line[0]] = line[1:]
	# Get every combination of options
	opts = []
	for combo in itertools.product(*[[(item[0], val) for val in item[1]] for item in flags.items()]):
		# Combine options into a single list
		opts.append(list(itertools.chain(*combo)))

	# Get necessary padding
	pad = len(max([' '.join(i) for i in opts], key=len))

	clss = []
	reg  = []

	# Try each combo
	for opt in opts:
		val, ending = getVal(args.trainFile, args.devFile, opt)
		if ending == '%':
			clss.append((float(val), opt))
		else:
			reg.append((float(val), opt))

		print('{1: <{0}} : {2: <{0}}'.format(pad, ' '.join(opt), val + ending))
	if clss:
		best = max(clss)
	if reg:
		best = min(reg)
	print('Best output with flags "{}" = {}'.format(' '.join(best[1]), best[0]))