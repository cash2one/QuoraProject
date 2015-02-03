from __future__ import print_function
import sys
import codecs
import time
import re
import os

import concrete.util
from concrete.util import read_communication_from_file
from concrete.validate import validate_communication
import concrete
from concrete import Communication

def create_dummy_annotation():
    ann = concrete.AnnotationMetadata()
    ann.tool = 'Quora Scrape Ingest'
    ann.timestamp = int(time.time())
    return ann

def createComm(fn):
	with codecs.open(fn, 'r', 'utf-8') as f:
		txt = f.read()

	comm = Communication()
	comm.id = fn
	comm.uuid = concrete.util.generate_UUID()
	comm.type = "QUORA ANSWER" if fn.startswith("answer") else "QUORA QUESTION"
	comm.text = txt
	comm.metadata = create_dummy_annotation()


	breaks = [i for i, ch in enumerate(txt) if ch == '\n' and i > 0 and txt[i-1] != '\n']
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

def createCommsFromDir(DIR):
	for dir1 in os.listdir(DIR):
		dir1 = os.path.join(DIR, dir1)
		for dir2 in os.listdir(dir1):
			dir2 = os.path.join(dir1, dir2)
			for dir3 in os.listdir(dir2):
				dir3 = os.path.join(dir2, dir3)
				for thread in os.listdir(dir3):
					thread = os.path.join(dir3, thread)
					files = os.listdir(thread)
					r = re.compile(r'answer\d+_text\.txt|question\.txt')
					for f in filter(r.match, files):
						f_out = '.'.join(f.split('.')[:-1])
						f_out += ".comm"
						f = os.path.join(thread, f)
						c = createComm(f)
						if c is None:
							print("ERR: Bad communication")
						else:
							f_out = os.path.join(thread, f_out)
							concrete.util.write_communication_to_file(c, f_out)

if __name__ == '__main__':
	from sys import argv

	DIR = "/export/a04/wpovell/hashed_data"
	if len(argv[1]) > 1:
		DIR = argv[1]
	createCommsFromDir(DIR)