from __future__ import print_function

import os
import re
import json
from Quora.QuoraScraper import QuoraScraper
from binascii import a2b_hex
from gzip import GzipFile
from StringIO import StringIO
import tarfile
import hashlib
import time

import concrete.util
from concrete.util import read_communication_from_file
from concrete.validate import validate_communication
import concrete
from concrete import Communication

from thrift import TSerialization
from thrift.protocol import TCompactProtocol

from pprint import pprint as print

def create_dummy_annotation():
	'''Creates empty annotation to satisfy format'''
	ann = concrete.AnnotationMetadata()
	ann.tool = 'Quora Scrape Ingest'
	ann.timestamp = int(time.time())
	return ann

def createComm(cid, ctype, txt):
	'''Creates concrete communication file from text'''
	comm = Communication()
	comm.id = cid
	comm.uuid = concrete.util.generate_UUID()
	comm.type = ctype
	txt = re.sub('[\xa0\xc2]', ' ', txt)
	txt = re.sub(r'\s*\n\s*', '\n', txt)
	if not txt.strip():
		return None
	comm.text = txt
	comm.metadata = create_dummy_annotation()

	breaks = [i for i, ch in enumerate(txt) if ch == '\n' and i > 0 and txt[i-1] != '\n']
	if not breaks or breaks[-1] != len(txt) - 1:
		breaks += [len(txt)]

	sections = []
	start = 0
	for i in breaks:
		sec = concrete.Section()
		sec.uuid = concrete.util.generate_UUID()
		sec.kind = "Passage"
		sec.textSpan = concrete.TextSpan(start, i)
		sections.append(sec)
		start = i

	comm.sectionList = sections

	if not concrete.validate.validate_communication(comm):
		return None
	return comm

def getFiles(d):
	'''Recursively lists files in directory'''
	for i in os.walk(d):
		for j in i[2]:
			yield '{}/{}'.format(i[0], j)

def binFiles(files):
	'''Returns dict in form of
	{<first three letters of hash> : <list of files that start with that hash>, ...}
	'''
	ret = {}
	for f in files:
		if not f.endswith('.out'):
			continue
		fileHash = f[::-1].split('_', 1)[0][::-1].replace('.out', '') # Get first 3 letters of file hash (sorry for this montrosity)
		key = fileHash[:3]
		if not key in ret:
			ret[key] = []
		ret[key].append((f, fileHash))
	return ret

def createEntry(name, dat, tarf):
	# Question Communication
	qtext = data['data']['question'] + "\n\n" + data['data']['details']
	comm = createComm(name, "QUORA QUESTION", data['data']['question'])
	stringf = StringIO(TSerialization.serialize(comm, protocol_factory=TCompactProtocol.TCompactProtocolFactory()))
	info = tarfile.TarInfo('{}/{}/question.comm'.format(name[2], name))
	info.size = len(stringf.buf)
	tarf.addfile(info, stringf)

	# Question Metadata
	qdata = {
		"followers" : data['data']['followers'],
		"topics"    : data['data']['topics'],
		"author"    : data['log']['author'] if 'log' in data and 'author' in data['log'] else None,
		"time"      : data['log']['time'] if 'log' in data and 'time' in data['log'] else None,
		"url"       : data['url']
	}
	stringf = StringIO(json.dumps(qdata))
	info = tarfile.TarInfo('{}/{}/metadata.json'.format(name[2], name))
	info.size = len(stringf.buf)
	tarf.addfile(info, stringf)

	# Answers
	for i, answer in enumerate(data['data']['answers']):
		# Communication
		comm = createComm(name, "QUORA ANSWER", answer['text'])
		if comm is None:
			continue
		stringf = StringIO(TSerialization.serialize(comm, protocol_factory=TCompactProtocol.TCompactProtocolFactory()))
		info = tarfile.TarInfo("{}/{}/answer{}.comm".format(name[2], name, i))
		info.size = len(stringf.buf)
		tarf.addfile(info, stringf)

		# Metadata
		adata = {
			"upvotes" : answer['upvotes'],
			"author"  : answer['author']
		}
		stringf = StringIO(json.dumps(adata))
		info = tarfile.TarInfo('{}/{}/answer{}.json'.format(name[2], name, i))
		info.size = len(stringf.buf)
		tarf.addfile(info, stringf)			

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser(description='Process raw .out files into concrete communications')
	parser.add_argument('-i', type=str, nargs='?', default='data_sorted', help='input directory')
	parser.add_argument('-o', type=str, nargs='?', default='data_new', help='output directory')
	parser.add_argument('-m', type=str, nargs='?', default='', help='file to write missing times to')
	args = parser.parse_args()

	INPUT_DIR = args.i
	OUTPUT_DIR = args.o

	if not os.path.isdir(OUTPUT_DIR):
		os.makedirs(OUTPUT_DIR)

	if args.m:
		toGetTimes = open(args.m, 'w')

	files = getFiles(INPUT_DIR)
	files = binFiles(files)

	for fileHash, fileList in files.items():
		print(fileHash)
		outPath = '{}/{}/{}'.format(OUTPUT_DIR, fileHash[0], fileHash[1])
		if not os.path.isdir(outPath):
			os.makedirs(outPath)
		tarf = tarfile.open('{}/{}.tar.gz'.format(outPath, fileHash[2]), 'w:gz')
		for fn, fullHash in fileList:
			with open(fn) as f:
				data = json.load(f)
			if 'question' not in data:
				continue
			t = data['time']
			html = data['html']
			html = a2b_hex(html)
			strFile = StringIO(html)
			html = GzipFile(fileobj=strFile).read()
			info = QuoraScraper.getQuestion(html, t)
			if args.m and not "log" in data:
				toGetTimes.write(fn + '\n')
			createEntry(fullHash, data, tarf)
		tarf.close()
