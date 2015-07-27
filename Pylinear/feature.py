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

### FILE MAPPING ###

def writeFileMapping(DIR):
	'''Write line -> file mapping'''
	with open('{}/fileMapping.txt'.format(DIR), 'w') as outf:
		for fn in getFiles('{}/data'.format(DIR)):
			if not fn.endswith(".tar.gz"):
				continue
			f = tarfile.open(fn, "r:gz")
			for tarfn in f.getmembers():
				outf.write(tarfn.name + '\n')

def writeThreadMapping(DIR):
	'''Write line -> question thread mapping'''
	with open('{}/threadMapping.txt'.format(DIR), 'w') as outf:
		lastFn = ''
		for fn, _ in getDataFiles(DIR):
			fn = fn.split('/')[1]
			if lastFn != fn:
				lastFn = fn
				outf.write(fn + "\n")

### FEATURE GEN ###

def followers(data):
	'''Generates feature file for number of followers a question has'''
	dirList = set()
	outFile = open("{}/features/followers.txt".format(data), 'w')
	for name, content in getDataFiles(data + "/data"):
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		if not name.endswith("metadata.json"):
			continue
		content = content.read()
		content = json.loads(content)
		outFile.write("{} followers:{}\n".format(dataDir, content["followers"]))
	outFile.close()
	with open('{}/features/followers.list.txt'.format(data), 'w') as f:
		json.dump(list(dirList), f)

def question_length(data):
	'''Generates feature file for length of question'''
	dirList = set()
	outFile = open("{}/features/question_length.txt".format(data), 'w')
	for name, content in getDataFiles(data + "/data"):
		dataDir = name.split('/')[1]
		dirList.add(dataDir)
		if not name.endswith("question.comm"):
			continue
		content = content.read()
		comm = commFromData(content)

		outFile.write("{} question_length:{}\n".format(dataDir, len(comm.text)))
	outFile.close()
	with open('{}/features/question_length.list.txt'.format(data), 'w') as f:
		json.dump(list(dirList), f)

def has_N_answers(data, N):
	'''Generates binary feature file for wheather or not a question has N answers'''
	lastThread = ""
	numAnswers = 0
	first = True
	dirList = set()
	outFile = open("{}/features/has_{}_answers.txt".format(data, N), "w")
	for n, f in getDataFiles(data + "/data"):
		split = n.split("/")
		thread = split[1]
		fn = split[2]
		if first:
			first = False
			lastThread = thread
		elif thread != lastThread:
			dirList.add(lastThread)
			outFile.write("{} has_{}_answers:{}\n".format(lastThread, N, 1 if numAnswers >= N else 0))
			lastThread = thread
			numAnswers = 0
		if re.match('answer[\d]+.comm', fn):
			numAnswers += 1
	outFile.write("{} has_{}_answers:{}\n".format(lastThread, N, 1 if numAnswers >= N else 0))
	outFile.close()
	with open('{}/features/has_{}_answers.list.txt'.format(data, N), 'w') as f:
		json.dump(list(dirList), f)

def topics(data):
	'''Generates feature file with binary feature for each topic.'''
	dirList = set()
	outFile = codecs.open("{}/features/topics.txt".format(data), 'w', 'utf-8')
	for name, content in getDataFiles(data + "/data"):
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
	with open('{}/features/topics.list.txt'.format(data), 'w') as f:
		json.dump(list(dirList), f)

def time_to_answer(data):
	'''Generates feature of the number of days it took for a question to be answered'''
	lastThread = ""
	answer_times = []
	question_time = None
	first = True
	dirList = set()
	outFile = open('{}/features/time_to_answer.txt'.format(data), 'w')
	for n, f in getDataFiles(data + "/data"):
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
						outFile.write('{} time_to_answer:{}\n'.format(lastThread, d))
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
	with open('{}/features/time_to_answer.list.txt'.format(data), 'w') as f:
		json.dump(list(dirList),f)

##
## NGRAM FEATURES
##

def loadStopWords():
	path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stopwords.txt")
	with open(path) as f:
		lines = set(filter(lambda x: not x.startswith("#"), f.read().strip().split('\n')))
	return lines

def tokensFromComm(comm):
	for section in comm.sectionList:
		if not section.sentenceList is None:
			for sentence in section.sentenceList:
				for token in sentence.tokenization.tokenList.tokenList:
					token = token.text.replace(":", "-CLN-").replace("#", "-PND-").replace(' ', '-SPC-')
					yield token
					

def getVocab(data, CUTOFF=5):
	global stopWords
	if stopWords is None:
		stopWords = loadStopWords()

	tokenDict = {}
	vocab = set()

	for n, f in getDataFiles(data + "/data"):
		if not n.endswith(".comm"):
			continue
		comm = commFromData(f.read())
		for token in tokensFromComm(comm):
			if token in vocab:
				continue
			if token.lower() in stopWords:
				token = "-STOPWORD-"
			if not token in tokenDict:
				tokenDict[token] = 0
			tokenDict[token] += 1
			if tokenDict[token] > CUTOFF:
				tokenDict.pop(token)
				vocab.add(token)
	return vocab

def getDocumentVocab(comm, vocab=None):
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


def ngram_features(DIR, ngram=False, tfidf=False, cutofff=5):
	'''Generates feature files for n-gram and tfidf features.

	Cutoff controls how many times a token has to occur in the dataset (all threads) to not be marked as an OOV.'''

	docVocabs = []

	# Output files
	if ngram:
		ngramOutFiles = {}
		for n in ngram:
			ngramOutFiles[n] = codecs.open("{}/features/{}-gram.txt".format(DIR, n), 'w', 'utf-8')
	if tfidf:
		tfidfOutFile = codecs.open("{}/features/tfidf.txt".format(DIR), 'w', 'utf-8')

	print("Getting vocab")
	vocab = getVocab(DIR, cutofff)

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

		for n in ngram:
			feats = tokenFeatures(comm, vocab, n)
			line = "{} ".format(dataDir) + " ".join(["NGRAM_{}:{}".format(','.join(k),v) for k, v in feats.items()])
			ngramOutFiles[n].write(line + "\n")

	if ngram:
		for n in ngram:
			ngramOutFiles[n].close()
			with open('{}/features/{}-gram.list.txt'.format(DIR, n), 'w') as f:
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

# Dictionary of feature names and func that generate them
feature_func = {
	"followers"       : followers,
	"question_length" : question_length,
	"has_N_answers"   : has_N_answers,
	"time_to_answer"  : time_to_answer,
	"topics"          : topics,
	"n-gram"          : "Generates feature file of n-gram frequencies. Cutoff defaulting to 5 used.",
	"tfidf"           : "Generates feature file of tf-idf scores."
}

### MAIN ###

def listFeatures(*_):
	'''Lists features that can be generated.'''
	print("Feature Options:")
	for key, value in feature_func.items():
		value = value if type(value) == unicode else value.__doc__
		print("\t{: <16} : {}".format(key, value))

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
		hasAnswersRe = re.findall(r'has_\d+_answers', feature)
		if hasAnswersRe:
			feature_func[feature](data, int(hasAnswersRe[0]))
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
			result = re.findall(r'(\d+)-gram', feature)
			if result:
				if not 'ngram' in args:
					args['ngram'] = []
				args['ngram'].append(int(result[0]))

		ngram_features(data, **args)