import os
import subprocess
import json
import argparse
import itertools
import re
import time

from Pylinear.feature import generateFeatures
from Pylinear.scripts.scores import scores

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

	# Create set of ids present in all feature files
	idSet = makeIDSet(data, train, featureNames)

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

	outputFolder = '/'.join(trainFile.split('/')[:-4]) + '/results/{}/'.format(int(time.time()))
	os.makedirs(outputFolder)
	outFn = outputFolder + 'data.model'

	libArgs = [trainEx] + options + [trainFile, outFn]
	list(execute(libArgs))
	with open(outputFolder + 'info.txt', 'w') as f:
		f.write(trainFile.split('/')[-2] + '\n')
		f.write(' '.join(libArgs) + '\n')
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
	# Write out F score, accuracy, precision, etc
	with open(testFile) as f:
		real = [i.split(' ')[0] for i in f.read().strip().split('\n')]
	with open(outFn) as f:
		pred = f.read().strip().split('\n')
	with open('/'.join(model.split('/')[:-1]) + '/stats.txt', 'w') as f:
		json.dump(scores(real, pred), f)

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
		data = f.read()
		data = data.strip().split('\n')
		for line in data:
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