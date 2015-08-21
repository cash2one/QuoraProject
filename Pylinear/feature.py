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
		featName = "answerLen"
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

def tokensFromComm(comm, POS=False):
	'''Yields tokens in the given communication file.'''
	for section in comm.sectionList:
		if not section.sentenceList is None:
			for sentence in section.sentenceList:
				if POS:
					for token in sentence.tokenization.tokenTaggingList[1].taggedTokenList:
						yield token.tag.replace(":", "-CLN-").replace("#", "-PND-").replace(' ', '-SPC-')
				else:
					for token in sentence.tokenization.tokenList.tokenList:
						token = token.text.replace(":", "-CLN-").replace("#", "-PND-").replace(' ', '-SPC-')
						yield token

def getVocab(data, cutoff, check):
	'''Generates vocab for an entire dataset, not including tokens that occur < CUTOFF.'''
	global stopWords
	if stopWords is None:
		stopWords = loadStopWords()

	tokenDict = {}
	vocab = set()

	for n, f in getDataFiles(data + "/data"):
		if not check(n):
			continue
		comm = commFromData(f.read())
		for token in tokensFromComm(comm):
			if token.lower() in stopWords:
				token = "-STOPWORD-"
			# Continue if already in all vocabs
			if token in vocab:
				continue
			if not token in tokenDict:
				tokenDict[token] = 0
			tokenDict[token] += 1
			if tokenDict[token] >= cutoff:
				vocab.add(token)
	return vocab

def getDocumentVocab(comm, vocab=None, POS=False):
	'''Gets vocab of a single comm file.'''
	global stopWords
	if stopWords is None:
		stopWords = loadStopWords()

	docVocab = set()
	for token in tokensFromComm(comm, POS):
		if not POS:
			if vocab is not None and token not in vocab:
				token = "-OOV-"
			if token.lower() in stopWords:
				token = "-STOPWORD-"

		docVocab.add(token)
	return docVocab

def tokenFeatures(comm, vocab, n, POS):
	'''Returns n-grams for a given comm object.

	Replaces tokens not in vocab with OOV and returns tuples of length n.'''

	tokens = list(tokensFromComm(comm, POS))
	if n > 1:
		tokens = ['-START-'] + tokens + ['-END-'] * (n-1)
	ret = []
	for i in range(len(tokens)):
		toAdd = tokens[i:i+n]
		for j in range(len(toAdd)):
			if not POS and not toAdd[j] in vocab:
				toAdd[j]  = '-OOV-'
		if len(toAdd) == n and not all([j == '-END-' for j in toAdd]):
			ret.append(tuple(toAdd))
	return Counter(ret)


def ngram(data, order, cutoff, binary, POS, onAnswers):
	'''Generates feature files for n-gram features.

	Cutoff controls how many times a token has to occur in the dataset (all threads) to not be marked as an OOV.'''

	docVocabs = []

	featName = '{}-gramC{}B{}P{}A{}'.format(order, cutoff, int(binary), int(POS), int(onAnswers))
	outFile = codecs.open(os.path.join(data, 'features/{}.txt'.format(featName)), 'w', 'utf-8')
	if onAnswers:
		check = lambda x: bool(re.match(r'answer\d+\.comm', x))
	else:
		check = lambda x: x.endswith("question.comm")

	print("Getting vocab")
	vocab = None
	if not POS:
		vocab = getVocab(data, cutoff, check)

	print("Getting file features")
	dirList = set()
	for name, f in getDataFiles(os.path.join(data, "data")):
		if not check(name):
			continue

		dataDir = name.split('/')[1]
		dirList.add(dataDir)

		comm = commFromData(f.read())

		feats = tokenFeatures(comm, vocab, order, POS)

		if binary:
			line = "{} ".format(dataDir) + " ".join(["{}_{}:{}".format(featName, ','.join(k), int(bool(v))) for k, v in feats.items()])
		else:
			line = "{} ".format(dataDir) + " ".join(["{}_{}:{}".format(featName, ','.join(k), v) for k, v in feats.items()])
		outFile.write(line + "\n")

	outFile.close()
	with open(os.path.join(data, "features/{}.list.txt".format(featName)), 'w') as f:
		json.dump(list(dirList), f)
	return

def tfidf(data, cutoff, POS, onAnswers):
	if onAnswers:
		check = lambda x: bool(re.match(r'answer\d+\.comm', x))
	else:
		check = lambda x: x.endswith("question.comm")

	featName = 'tfidfC{}A{}P{}'.format(cutoff, int(onAnswers), int(POS))
	tfidfOutFile = codecs.open(os.path.join(data, 'features', featName + '.txt'), 'w', 'utf-8')

	vocab = None
	if not POS:
		vocab = getVocab(data, cutoff, check)

	numDocs = 0
	docVocabs = []
	dirList = set()
	for name, f in getDataFiles(os.path.join(data, "data")):
		if not check(name):
			continue
		dataDir = name.split('/')[1]
		dirList.add(dataDir)

		comm = commFromData(f.read())
		numDocs += 1
		docVocabs.append(getDocumentVocab(comm, vocab, POS))
	print(docVocabs)
	for n, f in getDataFiles(data + "/data"):
		if not check(n):
			continue
		results = []
		comm = commFromData(f.read())
		tokens = [token if (POS or token in vocab) else "-OOV-" for token in tokensFromComm(comm, POS)]
		tokens = Counter(tokens)
		for k, v in tokens.items():
			tf = v / sum(tokens.values())
			idf = math.log(numDocs / (len([True for i in docVocabs if k in i])))
			tfidf_val = tf * idf
			results.append("{}_{}:{}".format(featName, k,tfidf_val))
		line = dataDir + " " + ' '.join(results)
		tfidfOutFile.write(line + "\n")
	tfidfOutFile.close()
	with open(os.path.join(data,'features/{}.list.txt'.format(featName)), 'w') as f:
		json.dump(list(dirList), f)

stopWords = None