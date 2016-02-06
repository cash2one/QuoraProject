'''This module contains classes for generating features from tar.gz'd data in splits/'''
from __future__ import unicode_literals, division
import json
import tarfile
import os
import argparse
import codecs
import math
import re
import logging
from collections import Counter

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TCompactProtocol
import datetime

class FeatureGenerator:
	'''Abstract class inherited by classes generating different features for the dataset'''
	def __init__(self, data):
		self.data = data

	@staticmethod
	def listDirectory(directory):
		'''Recursively lists files in <directory>.'''
		for i in os.walk(directory):
			for j in i[2]:
				if j.endswith('.DS_Store'):
					continue
				yield '{}/{}'.format(i[0], j)

	@staticmethod
	def threadID(fileName):
		'''Returns thread name (md5 hash of url) assosicated with file.'''
		ID = re.findall(r"[0-9a-z]{32}",fileName)
		if ID:
			return ID[0]
		else:
			return None

	@classmethod
	def featureID(cl, fileName):
		'''Generates a unique ID for a feature.
		Thread features are in the form "T<thread hash>"
		Answer features are in the form "T<thread hash>A<answer #>"
		'''
		featID = "T" + cl.threadID(fileName)

		d = cl.answerNumber(fileName)
		if d:
			featID += "A" + d

		return featID

	@staticmethod
	def answerNumber(fileName):
		'''Returns answer # of a filename (error return is None).'''
		d = re.findall(r'answer(\d+)\.', fileName)
		if d:
			return d[0]
		else:
			return None

	@staticmethod
	def commFromData(data):
		'''Returns Communication object generated from byte string'''
		comm = Communication()
		TSerialization.deserialize(comm, data, protocol_factory=TCompactProtocol.TCompactProtocolFactory())
		return comm

	def getDataFiles(self, regex=None):
		'''Open all tar.gz files in directory <data> and returns (file name, file object)'''
		for fn in self.listDirectory(self.data):
			if not fn.endswith(".tar.gz"):
				continue
			f = tarfile.open(fn, "r:gz")
			files = set()
			for tarfn in f.getmembers():
				if tarfn.name in files or (regex and not re.findall(regex, tarfn.name)):
					continue
				else:
					files.add(tarfn.name)
				tarf = f.extractfile(tarfn)
				yield (tarfn.name, tarf)
				tarf.close()
			f.close()

	def getDataFilesByThread(self, regex=None):
		'''Open all tar.gz files in directory <data> and returns (threadID, [thread files]) for each thread'''
		for fn in self.listDirectory(self.data):
			if not fn.endswith(".tar.gz"):
				continue
			f = tarfile.open(fn, "r:gz")
			files = set()

			lastThread = ""
			threadFiles = []
			for tarfn in f.getmembers():
				if tarfn.name in files or (regex and not re.findall(regex, tarfn.name)):
					continue
				else:
					files.add(tarfn.name)

				thread = self.threadID(tarfn.name)
				if lastThread and thread != lastThread:
					yield lastThread, threadFiles
					threadFiles = []
				lastThread = thread

				tarf = f.extractfile(tarfn)
				threadFiles.append((tarfn.name, tarf.read()))
				tarf.close()
			yield lastThread, threadFiles
			f.close()

	def writeFeature(self, features):
		'''Writes generated feature to a JSON file.'''
		outputFile = os.path.join(self.data, 'features/{}.json'.format(self.FEATURE_NAME))
		logging.debug("Writing to {}".format(outputFile))
		with open(outputFile, 'w') as f:
			json.dump(features, f)

	def generate(self):
		raise NotImplementedError

### FEATURE GEN ###

class FollowerGen(FeatureGenerator):
	'''Feature for follower count of threads.'''
	FEATURE_NAME = "followers"
	def generate(self):
		features = {}
		for fileName, fileObj in self.getDataFiles(regex=r'metadata\.json'):
			content = fileObj.read()
			content = json.loads(content)

			featureID = self.featureID(fileName)
			features[featureID] = {}
			features[featureID][self.FEATURE_NAME] = content["followers"]
		self.writeFeature(features)

class UpvoteGen(FeatureGenerator):
	'''Feature for upvote count of comments.'''
	FEATURE_NAME = "upvotes"
	def generate(self):
		features = {}
		for fileName, fileObj in self.getDataFiles(regex=r'answer\d+\.json'):
			content = fileObj.read()
			content = json.loads(content)

			featureID = self.featureID(fileName)
			features[featureID] = {}
			features[featureID][self.FEATURE_NAME] = content['upvotes']

		self.writeFeature(features)

class NormalizedUpvoteGen(FeatureGenerator):
	'''Feature for normalized upvote count of comments.
	Upvotes are normalized by comment with highest upvote count in thread.'''
	FEATURE_NAME = "normalized_upvotes"
	MIN_ANSWERS = 4
	def generate(self):
		features = {}
		for threadID, threadFiles in self.getDataFilesByThread(regex=r'answer\d+\.json'):
			# [(filename, upvotes), ...]
			answerUpvotes = [(fileName, json.loads(i)['upvotes']) for fileName, i in threadFiles]
			if len(answerUpvotes) < self.MIN_ANSWERS:
				continue
			# Max is bumped up to 1 to prevent div by 0
			maxUpvotes = max(1,max(zip(*answerUpvotes)[1]))
			for fileName, upvotes in answerUpvotes:
				featureID = self.featureID(fileName)
				features[featureID] = {}
				features[featureID][self.FEATURE_NAME] = upvotes / maxUpvotes

		self.writeFeature(features)

class LengthGen(FeatureGenerator, object):
	'''Feature for length of question or answer text.'''
	def __init__(self, data, onAnswers):
		if onAnswers:
			self.regex = r"answer\d\.comm"
			self.FEATURE_NAME = "answer_length"
		else:
			self.regex = r"question\.comm"
			self.FEATURE_NAME = "question_length"
		super(LengthGen, self).__init__(data)

	def generate(self):
		features = {}
		for fileName, fileObj in self.getDataFiles(regex=self.regex):
			featureID = self.featureID(fileName)
			if self.FEATURE_NAME == "answer_length":
				featureID += "A" + self.answerNumber(fileName)
			content = fileObj.read()
			comm = self.commFromData(content)
			features[featureID] = {}
			features[featureID][self.FEATURE_NAME] = len(comm.text)

		self.writeFeature(features)

# Only generates for questions, could be modified to generate for answers as well
class TopicGen(FeatureGenerator):
	'''Feature for topics a thread is tagged with.'''
	FEATURE_NAME = "topic"
	def generate(self):
		features = {}
		for fileName, fileObj in self.getDataFiles(regex=r'metadata\.json'):
			featureID = self.featureID(fileName)
			content = fileObj.read()
			content = json.loads(content)
			features[featureID] = {}
			for topic in content["topics"]:
				features[featureID]["TOPIC_"+topic[1:]] = 1

		self.writeFeature(features)			

##
## NGRAM FEATURES
##

class NGramGen(FeatureGenerator, object):
	'''Feature for N-grams in question or answers.'''
	def __init__(self, data, order, cutoff, binary, POS, onAnswers):
		'''
		Args:
			data      (str): Dataset to generate for.
			order     (int): N-gram order to generate (e.g. unigram, bigram, etc.).
			cutoff    (int): Minimum times a token must appear to not be replaced with "-OOV-".
			binary    (bool): If True, feature values will be binary (1/0) rather than frequencies.
			POS       (bool): If True, N-grams will be from part-of-speech tags rather than text tokens.
			onAnswers (bool): If True, features will be generated for answer text, rather than question text.
		'''
		self.order = order
		self.cutoff = cutoff
		self.binary = binary
		self.POS = POS

		if onAnswers:
			self.regex = r"answer\d\.comm"
		else:
			self.regex = r"question\.comm"


		self.FEATURE_NAME = '{}-gram_cut{}'.format(order, cutoff)
		if binary:
			self.FEATURE_NAME += "_bin"
		if POS:
			self.FEATURE_NAME += "_pos"

		if onAnswers:
			self.FEATURE_NAME = "answer_" + self.FEATURE_NAME
		else:
			self.FEATURE_NAME = "question_" + self.FEATURE_NAME

		self.stopWords = self.readStopWords()
		super(NGramGen, self).__init__(data)

	@staticmethod
	def readStopWords():
		'''Loads stop words from file, to be used in replacing tokens with "-STOPWORD-"'''
		path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stopwords.txt")
		with open(path) as f:
			# Remove commented out lines
			lines = set(filter(lambda x: not x.startswith("#"), f.read().strip().split('\n')))
		return lines

	def tokensFromComm(self, comm):
		'''Yields tokens in the given communication file.'''
		for section in comm.sectionList:
			if not section.sentenceList is None:
				for sentence in section.sentenceList:
					# Part of speech tagged tokens
					if self.POS:
						tokens = [i.tag for i in sentence.tokenization.tokenTaggingList[1].taggedTokenList]
					# Normal text tokens
					else:
						tokens = [i.text for i in sentence.tokenization.tokenList.tokenList]

					for token in tokens:
						yield token.replace(":", "-CLN-").replace("#", "-PND-").replace(' ', '-SPC-')

	def getVocab(self):
		'''Generates vocab for an entire dataset, not including tokens that occur < CUTOFF.'''
		tokenDict = {}
		vocab = set()

		for fileName, fileObj in self.getDataFiles(regex=self.regex):
			comm = self.commFromData(fileObj.read())
			for token in self.tokensFromComm(comm):
				# Replace stopwords with special token
				if not self.POS and token.lower() in self.stopWords:
					token = "-STOPWORD-"

				# Continue if already in vocab
				if token in vocab:
					continue
				if not token in tokenDict:
					tokenDict[token] = 0
				tokenDict[token] += 1
				if tokenDict[token] >= self.cutoff:
					vocab.add(token)
					del tokenDict[token]
		return vocab

	def tokenFeatures(self, comm, vocab):
		'''Returns n-grams for a given comm object.
		Replaces tokens not in vocab with OOV and returns tuples of length n.
		'''

		tokens = list(self.tokensFromComm(comm))
		if self.order > 1:
			tokens = ['-START-'] + tokens + ['-END-'] * (self.order-1)
		ret = []
		for i in range(len(tokens)):
			toAdd = tokens[i:i+self.order]
			for j in range(len(toAdd)):
				if not self.POS and not toAdd[j] in vocab:
					toAdd[j]  = '-OOV-'
			if len(toAdd) == self.order and not all([j == '-END-' for j in toAdd]):
				ret.append(tuple(toAdd))
		return Counter(ret)

	def generate(self):
		docVocabs = []
		vocab = None
		if not self.POS:
			logging.debug("Generating vocab.")
			vocab = self.getVocab()

		features = {}
		for fileName, fileObj in self.getDataFiles(regex=self.regex):
			featureID = self.featureID(fileName)
			comm = self.commFromData(fileObj.read())
			feats = self.tokenFeatures(comm, vocab)

			if self.binary:
				features[featureID] = [(self.FEATURE_NAME + '_' + ','.join(k), int(bool(v))) for k, v in feats.items()]
			else:
				features[featureID] = {self.FEATURE_NAME + '_' + ','.join(k) : v for k, v in feats.items()}

		self.writeFeature(features)

# Not currently being used, may be update if need be
'''
def hasAnswers(data, N):
	#Generates binary feature file for wheather or not a question has N answers
	numAnswers = 0
	first = True
	features = {}
	featName = "has{}answers".format(N)
	entryName = None
	for n, f in getDataFiles(os.path.join(data, "data")):
		if n.endswith('question.comm'):
			entryName = getDataDir(name)
			if first:
				first = False
				lastEntry = entryName

		if not first and entryName != lastEntry:
			if entryName in features:
				continue
			features[entryName] = {}
			features[entryName][featName] = 1 if numAnswers >= N else 0
			lastEntry = entryName
			numAnswers = 0

		if re.findall(r'answer[\d]+\.comm', n):
			numAnswers += 1

	writeFeature(features, featName, data)

# WORK HERE
def aboveMeanUpvotes(data):
	#Generates feature of the number of days it took for a question to be answered
	lastThread = ""
	answerVals = []
	first = True
	features = {}
	featName = "aboveMeanUpvotes"

	for n, f in getDataFiles(os.path.join(data, "data")):
		dataDir = getDataDir(name)
		if thread != lastThread:
			if first:
				first = False
			elif answerVals:
				mean = sum(answerVals)/len(answerVals)
				for i in answerVals:
					features[lastThread] = 1 if i > mean else 0
			lastThread = thread
			answerVals = []
		if re.findall(r'answer[\d]+\.json', fn):
			answerData = json.load(f)
			answerVals.append(answerData['upvotes'])

	writeFeature(features, featName, data)

def answerTime(data):
	#Generates feature of the number of days it took for a question to be answered
	lastThread = ""
	answer_times = []
	question_time = None
	first = True
	featName = "answerTime"
	features = {}
	for n, f in getDataFiles(os.path.join(data + "data")):
		split = n.split("/")
		thread = split[0]
		fn = split[1]
		if thread != lastThread:
			if first:
				first = False
			elif len(answer_times) != 0 and not question_time is None:
					answer_time = min(answer_times)
					d = int(datetime.timedelta(seconds=(answer_time - question_time)).total_seconds() / 60 / 60)
					if d >= 0:
						features[lastThread] = d
					else:
						print("{}: Invalid answer time".format(lastThread))
			if question_time is None:
				print("{}: Invalid question time".format(lastThread))
			lastThread = thread
			question_time = None
			answer_times = []
		if re.findall(r'answer[\d]+\.json', fn):
			answerData = json.load(f)
			t = answerData['time']
			if not t is None:
				answer_times.append(answerData['time'])
		if fn.endswith('metadata.json'):
			questionData = json.load(f)
			question_time = questionData['postTime']
			url = questionData['url']

	writeFeature(features, featName, data)

#TFIDF
def getDocumentVocab(comm, vocab=None, POS=False):
	#Gets vocab of a single comm file.
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

def tfidf(data, cutoff, POS, onAnswers):
	if onAnswers:
		check = lambda x: bool(re.findall(r'answer\d+\.comm', x))
	else:
		check = lambda x: x.endswith("question.comm")

	featName = 'tfidfC{}A{}P{}'.format(cutoff, int(onAnswers), int(POS))

	vocab = None
	if not POS:
		vocab = getVocab(data, cutoff, check)

	numDocs = 0
	docVocabs = []
	features = {}
	for name, f in getDataFiles(os.path.join(data, "data")):
		if not check(name):
			continue
		dataDir = name.split('/')[0]

		comm = commFromData(f.read())
		numDocs += 1
		docVocabs.append(getDocumentVocab(comm, vocab, POS))

	for n, f in getDataFiles(data + "/data"):
		dataDir = n.split('/')[0]
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
			results.append((featName + '_' + k, tfidf_val))
		features[dataDir] = results

	writeFeature(features, featName, data)

stopWords = None
'''