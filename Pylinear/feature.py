from __future__ import unicode_literals, division
import json
import tarfile
import os
import argparse
import codecs
import math
from collections import Counter
import re

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TCompactProtocol
import datetime

### HELPER ###

def getFiles(d):
	'''Recursively lists files in directory'''
	for i in os.walk(d):
		for j in i[2]:
			if j.endswith('.DS_Store'):
				continue
			yield '{}/{}'.format(i[0], j)

def getDataFiles(data):
	'''Open all tar.gz files and return member data'''
	for fn in getFiles(data):
		if not fn.endswith(".tar.gz"):
			continue
		f = tarfile.open(fn, "r:gz")
		files = set()
		for tarfn in f.getmembers():
			if tarfn.name in files:
				continue
			else:
				files.add(tarfn.name)
			tarf = f.extractfile(tarfn)
			yield (tarfn.name, tarf)
			tarf.close()
		f.close()

def commFromData(data):
	'''Create Communication object from byte string'''
	comm = Communication()
	TSerialization.deserialize(comm, data, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
	return comm

### FEATURE GEN ###

def followers(data):
	'''Generates feature file for number of followers a question has'''
	dirList = set()
	outFile = open(os.path.join(data, 'features/followers.txt'), 'w')
	for name, content in getDataFiles(os.path.join(data, "data")):
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		if not name.endswith("metadata.json"):
			continue
		content = content.read()
		content = json.loads(content)
		outFile.write("{} followers:{}\n".format(dataDir, content["followers"]))
	outFile.close()

	with open(os.path.join(data, 'features/followers.list.txt'), 'w') as f:
		json.dump(list(dirList), f)

def upvotes(data):
	'''Generates feature file for number of followers a question has'''
	dirList = set()
	outFile = open(os.path.join(data, 'features/upvotes.txt'), 'w')
	for name, content in getDataFiles(os.path.join(data, "data")):
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		if not re.match(r'answer\d+\.json', name):
			continue
		content = content.read()
		content = json.loads(content)
		outFile.write("{} upvotes:{}\n".format(dataDir, content["upvotes"]))
	outFile.close()

	with open(os.path.join(data, 'features/upvotes.list.txt'), 'w') as f:
		json.dump(list(dirList), f)

def length(data, onAnswers):
	'''Generates feature file for length of question'''
	if onAnswers:
		featNane = "answerLen"
		check = lambda x: bool(re.match(r"answer\d+\.comm", x))
	else:
		featName = "questionLen"
		check = lambda x: x.endswith("question.comm")

	dirList = set()
	outFile = open(os.path.join(data, "features/{}.txt".format(featName)), 'w')
	for name, content in getDataFiles(os.path.join(data, "data")):
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		if not check(name):
			continue
		content = content.read()
		comm = commFromData(content)
		outFile.write("{} {}:{}\n".format(dataDir, featName, len(comm.text)))
	outFile.close()

	with open(os.path.join(data,'features/{}.list.txt'.format(featName)), 'w') as f:
		json.dump(list(dirList), f)

def hasAnswers(data, N):
	'''Generates binary feature file for wheather or not a question has N answers'''
	lastThread = ""
	numAnswers = 0
	first = True
	dirList = set()
	outFile = open("{}/features/has{}answers.txt".format(data, N), "w")
	for n, f in getDataFiles(os.path.join(data, "data")):
		split = n.split("/")
		thread = split[1]
		fn = split[2]
		if first:
			first = False
			lastThread = thread
		elif thread != lastThread:
			dirList.add(lastThread)
			outFile.write("{} has{}answers:{}\n".format(lastThread, N, 1 if numAnswers >= N else 0))
			lastThread = thread
			numAnswers = 0
		if re.match('answer[\d]+.comm', fn):
			numAnswers += 1
	outFile.write("{} has{}answers:{}\n".format(lastThread, N, 1 if numAnswers >= N else 0))
	outFile.close()
	with open(os.path.join(data, 'features/has{}answers.list.txt'.format(N)), 'w') as f:
		json.dump(list(dirList), f)

def topics(data, onAnswers):
	'''Generates feature file with binary feature for each topic.'''

	dirList = set()
	outFile = codecs.open(os.path.join(data, "features/questionTopics.txt"), 'w', 'utf-8')
	for name, content in getDataFiles(os.path.join(data, "data")):
		if not name.endswith("metadata.json"):
			continue
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		content = content.read()
		content = json.loads(content)
		outFile.write('{} '.format(dataDir))
		for topic in content["topics"]:
			outFile.write("{}:1 ".format(topic[1:]))
		outFile.write("\n")
	outFile.close()

	with open(os.path.join(data, 'features/questionTopics.list.txt'), 'w') as f:
		json.dump(list(dirList), f)

def answerTime(data):
	'''Generates feature of the number of days it took for a question to be answered'''
	lastThread = ""
	answer_times = []
	question_time = None
	first = True
	dirList = set()
	outFile = open(os.path.join(data, 'features/answerTime.txt'), 'w')
	for n, f in getDataFiles(os.path.join(data + "data")):
		split = n.split("/")
		thread = split[1]
		fn = split[2]
		if thread != lastThread:
			if first:
				first = False
			elif len(answer_times) != 0 and not question_time is None:
					answer_time = min(answer_times)
					d = int(datetime.timedelta(seconds=(answer_time - question_time)).total_seconds() / 60 / 60)
					if d >= 0:
						dirList.add(lastThread)
						outFile.write('{} answerTime:{}\n'.format(lastThread, d))
					else:
						print("{}: Invalid answer time".format(lastThread))
			if question_time is None:
				print("{}: Invalid question time".format(lastThread))
			lastThread = thread
			question_time = None
			answer_times = []
		if re.match('answer[\d]+.json', fn):
			answerData = json.load(f)
			t = answerData['time']
			if not t is None:
				answer_times.append(answerData['time'])
		if fn.endswith('metadata.json'):
			questionData = json.load(f)
			question_time = questionData['postTime']
			url = questionData['url']

	outFile.close()
	with open(os.path.join(data,'features/answerTime.list.txt'), 'w') as f:
		json.dump(list(dirList),f)

##
## NGRAM FEATURES
##

def loadStopWords():
	'''Loads stop words from file, to be used in replacing tokens with "-STOPWORD-"'''
	path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stopwords.txt")
	with open(path) as f:
		lines = set(filter(lambda x: not x.startswith("#"), f.read().strip().split('\n')))
	return lines

def tokensFromComm(comm, POS):
	'''Yields tokens in the given communication file.'''
	for section in comm.sectionList:
		if not section.sentenceList is None:
			for sentence in section.sentenceList:
				for token in sentence.tokenization.tokenList.tokenList:
					token = token.text.replace(":", "-CLN-").replace("#", "-PND-").replace(' ', '-SPC-')
					yield token
					

def getVocab(data, cutoffs):
	'''Generates vocab for an entire dataset, not including tokens that occur < CUTOFF.'''
	global stopWords
	if stopWords is None:
		stopWords = loadStopWords()

	tokenDict = {}
	vocabs = {c:set() for c in cutoffs}

	for n, f in getDataFiles(data + "/data"):
		if not n.endswith(".comm"):
			continue
		comm = commFromData(f.read())
		for token in tokensFromComm(comm):
			if token.lower() in stopWords:
				token = "-STOPWORD-"
			# Continue if already in all vocabs
			if token in vocabs[max(cutoffs)]:
				continue
			if not token in tokenDict:
				tokenDict[token] = 0
			tokenDict[token] += 1
			if tokenDict[token] in cutoffs:
				vocabs[tokenDict[token]].add(token)
	return vocabs

def getDocumentVocab(comm, vocab=None):
	'''Gets vocab of a single comm file.'''
	global stopWords
	if stopWords is None:
		stopWords = loadStopWords()

	docVocab = set()
	for token in tokensFromComm(comm):
		if vocab is not None and token not in vocab:
			token = "-OOV-"
		if token.lower() in stopWords:
			token = "-STOPWORD-"

		docVocab.add(token)
	return docVocab

def tokenFeatures(comm, vocab, n):
	'''Returns n-grams for a given comm object.

	Replaces tokens not in vocab with OOV and returns tuples of length n.'''

	tokens = list(tokensFromComm(comm))
	if n > 1:
		tokens = ['-START-'] + tokens + ['-END-'] * (n-1)
	ret = []
	for i in range(len(tokens)):
		toAdd = tokens[i:i+n]
		for j in range(len(toAdd)):
			if not toAdd[j] in vocab:
				toAdd[j]  = '-OOV-'
		if len(toAdd) == n and not all([j == '-END-' for j in toAdd]):
			ret.append(tuple(toAdd))
	return Counter(ret)


def ngram_features(data, order, cutoff, tfidf, binary, POS):
	'''Generates feature files for n-gram and tfidf features.

	Cutoff controls how many times a token has to occur in the dataset (all threads) to not be marked as an OOV.'''

	docVocabs = []

	featName = '{}-gramC{}T{}B{}P{}'.format(order, cutoff, int(tfidf), int(binary), int(POS))

	outFile = codecs.open(os.path.join(data, 'features/{}.txt'.format(featName)))

	print("Getting vocab")
	orders, cutoffs = zip(*ngram)
	vocabs = getVocab(DIR, cutoffs)

	print("Getting file features")
	numDocs = 0
	dirList = set()
	for name, f in getDataFiles(DIR + "/data"):
		if not name.endswith("question.comm"):
			continue
		dataDir = name.split('/')[1]
		dirList.add(dataDir)

		comm = commFromData(f.read())

		numDocs += 1
		#if tfidf:
		#	docVocabs.append(getDocumentVocab(comm, vocab))

		for n, c in ngram:
			feats = tokenFeatures(comm, vocabs[c], n)
			line = "{} ".format(dataDir) + " ".join(["{}-GRAMC{}_{}:{}".format(n, c, ','.join(k),v) for k, v in feats.items()])
			ngramOutFiles[n,c].write(line + "\n")

	if ngram:
		for n, c in ngram:
			ngramOutFiles[n,c].close()
			with open("{}/features/{}-gramC{}.list.txt".format(DIR, n, c), 'w') as f:
				json.dump(list(dirList), f)

	# Currently not working, need to fix
	'''
	if not tfidf:
		return

	results = []
	for n, f in getDataFiles(DIR + "/data"):
		if not n.endswith("question.comm"):
			continue
		results = []
		comm = commFromData(f.read())
		tokens = [token if token in vocab else "-OOV-" for token in tokensFromComm(comm)]
		tokens = Counter(tokens)
		for k, v in tokens.items():
			tf = v / sum(tokens.values())
			idf = math.log(numDocs / (len([True for i in docVocabs if k in i])))
			tfidf_val = tf * idf
			results.append("TFIDF_{}:{}".format(k,tfidf_val))
		line = "{} ".format(dataDir) + ' '.join(results)
		tfidfOutFile.write(line + "\n")
	tfidfOutFile.close()
	with open('{}/features/tfidf.list.txt'.format(N), 'w') as f:
		json.dump(list(dirList), f)
	'''

stopWords = None
##
## End NGRAM features
##

def generateFeatures(features, data=None, M=None):
	'''Generates feature files.

	Presumes directory structure <data>/features/ already exists.
	'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(features, argparse.Namespace):
		data = features.data
		M = features.M
		features = features.features
	##

	print(data)

	# Remove duplicates
	features = list(set(features))

	if M:
		print("Generating file mappings")
		writeFileMapping(data)
		writeThreadMapping(data)

	# Generate features
	ngramFeatures = []
	for feature in features:
		print(feature)
		hasAnswersRe = re.findall(r'has_(\d+)_answers', feature)
		if hasAnswersRe:
			feature_func["has_N_answers"](data, int(hasAnswersRe[0]))
		elif feature == 'tfidf' or re.match(r'\d+-gram', feature):
			ngramFeatures.append(feature)
		elif feature in features:
			feature_func[feature](data)
		else:
			print('Feature "{}" could not be generated.'.format(feature))

	# All n-gram related features are run together as they share some data
	if ngramFeatures:
		args = {}
		for feature in ngramFeatures:
			if feature == 'tfidf':
				args[i] = True
			# Matches any n-gram feature
			result = re.findall(r'(\d+)-gramC?(\d*)', feature)
			if result:
				result = list(result[0])
				if not result[1]:
					result[1] = 5 # default cutoff
				result = list(map(int, result))
				if not 'ngram' in args:
					args['ngram'] = []
				args['ngram'].append(result)
		ngram_features(data, **args)