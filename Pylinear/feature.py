from __future__ import unicode_literals, division
import json
import tarfile
import os
import argparse
import codecs
import math
from collections import Counter

from concrete import Communication
from thrift import TSerialization
from thrift.protocol import TCompactProtocol

### HELPER ###

def getFiles(d):
	'''Recursively lists files in directory'''
	for i in os.walk(d):
		for j in i[2]:
			yield '{}/{}'.format(i[0], j)

def getDataFiles(data):
	'''Open all tar.gz files and return member data'''
	for fn in getFiles(data):
		if not fn.endswith(".tar.gz"):
			continue
		f = tarfile.open(fn, "r:gz")
		for tarfn in f.getmembers():
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
	outFile = open("{}/features/followers.txt".format(data), 'w')
	for name, content in getDataFiles(data + "/data"):
		if not name.endswith("metadata.json"):
			continue
		content = content.read()
		content = json.loads(content)
		outFile.write("followers:{}\n".format(content["followers"]))
	outFile.close()

def question_length(data):
	'''Generates feature file for length of question'''
	outFile = open("{}/features/question_length.txt".format(data), 'w')
	for name, content in getDataFiles(data + "/data"):
		if not name.endswith("question.comm"):
			continue
		content = content.read()
		comm = commFromData(content)

		outFile.write("question_length:{}\n".format(len(comm.text)))
	outFile.close()

def has_answers(data):
	'''Generates binary feature file for wheather or not a question has answers'''
	outFile = open("{}/features/has_answers.txt".format(data), 'w')
	lastThread = ""
	found = False
	for name, _ in getDataFiles(data + "/data"):
		split = name.split('/')
		thread = split[1]
		fn = split[2]
		if thread != lastThread:
			lastThread = thread
			outFile.write("has_answers:{}\n".format(1 if found else 0))
			found = False
		if not found:
			if fn.startswith('answer'):
				found = True
	outFile.close()

def has_list(data):
	outFile = open("{}/features/has_list.txt".format(data), 'w')
	for name, data in getDataFiles(data + "/data"):
		if name.endswith("metadata.json"):
			data = json.load(data)
			if data['hasList']:
				outFile.write('has_list:1\n')
			else:
				outFile.write('has_list:0\n')
	outFile.close()

def topics(data):
	'''Generates feature file with binary feature for each topic.'''
	outFile = codecs.open("{}/features/topics.txt".format(data), 'w', 'utf-8')
	for name, content in getDataFiles(data + "/data"):
		if not name.endswith("metadata.json"):
			continue
		content = content.read()
		content = json.loads(content)
		for topic in content["topics"]:
			outFile.write("{}:1 ".format(topic[1:]))
		outFile.write("\n")
	outFile.close()

##
## NGRAM FEATURES
##

def loadStopWords():
	path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "stopwords.txt")
	with open(path) as f:
		lines = set(filter(lambda x: not x.startswith("#"), f.read().strip().split('\n')))
	return lines

def tokensFromComm(comm):
	global stopWords
	for section in comm.sectionList:
		if not section.sentenceList is None:
			for sentence in section.sentenceList:
				for token in sentence.tokenization.tokenList.tokenList:
					token = token.text.replace(":", "-CLN-").replace("#", "-PND-")
					yield token
					

def getVocab(data, CUTOFF=5):
	global stopWords

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
	docVocab = set()
	for token in tokensFromComm(comm):
		if vocab is not None and token not in vocab:
			token = "-OOV-"
		if token.lower() in stopWords:
			token = "-STOPWORD-"

		docVocab.add(token)
	return docVocab

def tokenFeatures(comm, vocab, normalized=False):
	tokens = tokensFromComm(comm)
	tokens = Counter([i if i in vocab else "-OOV-" for i in tokens])
	if normalized:
		numTokens = sum(tokens.values())
		tokens = {k:v/numTokens for k, v in tokens.items()}
	return tokens


def ngram_features(DIR, ngram, noramlized_ngram, tfidf, cutofff=5):
	docVocabs = []

	# Output files
	if ngram:
		ngramOutFile = codecs.open("{}/features/ngram.txt".format(DIR), 'w', 'utf-8')
	if noramlized_ngram:
		normalizedOutFile = codecs.open("{}/features/normalizedNgram.txt".format(DIR), 'w', 'utf-8')
	if tfidf:
		tfidfOutFile = codecs.open("{}/features/tfidf.txt".format(DIR), 'w', 'utf-8')

	print("Getting vocab")
	vocab = getVocab(DIR)

	print("Getting file features")
	numDocs = 0
	for n, f in getDataFiles(DIR + "/data"):
		if not n.endswith("question.comm"):
			continue
		comm = commFromData(f.read())

		numDocs += 1
		if tfidf:
			docVocabs.append(getDocumentVocab(comm, vocab))

		if ngram:
			feats = tokenFeatures(comm, vocab)
			line = " ".join(["NGRAM_{}:{}".format(k,v) for k, v in feats.items()])
			ngramOutFile.write(line + "\n")
			
		if noramlized_ngram:
			feats = tokenFeatures(comm, vocab, True)
			line = " ".join(["NNGRAM_{}:{}".format(k,v) for k, v in feats.items()])
			normalizedNgram.write(line + "\n")

	if ngram:
		ngramOutFile.close()
	if noramlized_ngram:
		normalizedOutFile.close()

	if not tfidf:
		return

	tfidfOutFile = codecs.open("{}/features/tfidf.txt".format(DIR), 'w', 'utf-8')
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
			# 1 + shouldn't be necessary, but you get div by 0 otherwise
			idf = math.log(numDocs / (len([True for i in docVocabs if k in i])))
			tfidf_val = tf * idf
			results.append("TFIDF_{}:{}".format(k,tfidf_val))
		line = ' '.join(results)
		tfidfOutFile.write(line + "\n")
	tfidfOutFile.close()

stopWords = loadStopWords()

##
## End NGRAM features
##

# Dictionary of feature names and func that generate them
feature_func = {
	"followers"       : followers,
	"question_length" : question_length,
	"has_answers"     : has_answers,
	"topics"          : topics,
	"has_list"        : has_list,
	"ngram"           : None,
	"norm_ngram"      : None,
	"tfidf"           : None
}

### MAIN ###

def listFeatures(*_):
	'''Lists features that can be generated.'''
	print("Feature Options:")
	for key, value in feature_func.items():
		print("\t{} : {}".format(key, value.__doc__))

def generateFeatures(features, data=None):
	'''Generates feature files.

	Presumes directory structure <data>/features/ already exists.
	'''

	## Args can be passed in as argparse instance or as individual params
	if isinstance(features, argparse.Namespace):
		data = features.data
		features = features.features
	##

	print(data)

	# Remove duplicates
	features = list(set(features))

	ngramNames = {"ngram", "noramlized_ngram", "tfidf"}
	ngramFeatures = set(features) & set(["ngram", "norm_ngram", "tfidf"]) 
	for feat in ngramFeatures: features.pop(features.index(feat))

	# Check if any of requested features doesn't exist
	f = [f for f in features if f not in feature_func]
	if f:
		print("ERROR: The following feature(s) could not be generated: {}".format(', '.join(f)))
		exit(1)

	writeFileMapping(data)
	writeThreadMapping(data)

	if ngramFeatures:
		ngramOpts = {i:i in ngramFeatures for i in ngramNames}
		ngram_features(data, **ngramOpts)

	# Generate features
	for feature in features:
		feature_func[feature](data)