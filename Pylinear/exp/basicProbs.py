'''Various functions I\'ve written to generate stats, conditional probabilities, etc.'''

from __future__ import division, print_function
import json
import re
from sys import argv
from Pylinear.feature import commFromData, getDataFiles


def printPer(n, v):
	'''Prints percent value.'''
	print('{} = {:.2f}%'.format(n, 100 * v))

def p1(DIR):
	'''Generate basic conditional probabilties for features.
A = question has at least one answer
D = question has details
L = question has list
'''
	questions = 0
	answered = 0
	details = 0
	question_has_list = 0
	question_with_list_answered = 0
	answered_with_details = 0
	answered_without_details = 0

	dirName = ''
	ans = False
	dets = False
	hasList = True
	for name, content in getDataFiles(DIR):
		if 'answer' in name:
			ans = True
		if name.endswith('question.comm'):
			comm = commFromData(content.read())
			if len(comm.sectionList) > 1:
				dets = True
		if name.endswith('metadata.json'):
			content = json.load(content)
			if hasList in content and content['hasList']:
				hasList = True

		curDir = name.split('/')[1]
		if dirName != curDir:
			questions += 1
			if ans:
				answered += 1
			if dets:
				details += 1
			if ans and dets:
				answered_with_details += 1
			if ans and not dets:
				answered_without_details += 1
			if hasList:
				question_has_list += 1
			if hasList and ans:
				question_with_list_answered += 1

			ans = False
			dets = False
			hasList = False
			dirName = curDir

	print(__doc__)
	print("DEBUG\n========")
	print('Threads:{}\nA:{}\nD:{}\nAWD:{}\nAWOD:{}'.format(questions, answered, details, answered_with_details, answered_without_details))
	printPer('P(A)   ', answered / questions)
	printPer('P(A|D) ', answered_with_details / details)
	printPer('P(A|!D)', answered_without_details / (questions - details))
	print()
	printPer('P(D)   ', details / questions)
	printPer('P(A,D) ', answered_with_details / questions)
	print()
	printPer('P(L)   ', question_has_list / questions)
	printPer('P(A|L) ', question_with_list_answered / question_has_list)

def p2(DIR):
	'''Generate counts for having various number of answers with and without details.'''
	C_nD      = 0
	C_D       = 0
	C_Agt1_D  = 0
	C_Agt1_nD = 0

	C_A0_D    = 0
	C_A1_D    = 0
	C_Agt1_D  = 0

	C_A0_nD   = 0
	C_A1_nD   = 0
	C_Agt1_nD = 0

	lastThread = ""
	numAnswers = 0
	first = True
	hasDetails = False
	for n, f in getDataFiles(DIR):
		thread = n.split("/")[1]
		if first:
			lastThread = thread
			first = False
		if thread != lastThread:
			if hasDetails:
				C_D += 1
			else:
				C_nD += 1

			if numAnswers == 0:
				if hasDetails:
					C_A0_D += 1
				else:
					C_A0_nD += 1
			elif numAnswers == 1:
				if hasDetails:
					C_A1_D += 1
				else:
					C_A1_nD += 1
			else:
				if hasDetails:
					C_Agt1_D += 1
				else:
					C_Agt1_nD += 1

			numAnswers = 0
			hasDetails = False
		if re.search(r"answer\d+\.comm", n):
			numAnswers += 1
		if n.endswith("question.comm"):
			comm = commFromData(f.read())
			if len(comm.sectionList) > 1:
				hasDetails = True

	print("C(      D) = {}".format(C_D))
	print("C(     !D) = {}".format(C_nD))
	print("C(A>1,  D) = {}".format(C_Agt1_D))
	print("C(A>1, !D) = {}".format(C_Agt1_nD))
	print()
	print("C(A=0,  D) = {}".format(C_A0_D))
	print("C(A=1,  D) = {}".format(C_A1_D))
	print("C(A>1,  D) = {}".format(C_Agt1_D))
	print()
	print("C(A=0, !D) = {}".format(C_A0_nD))
	print("C(A=1, !D) = {}".format(C_A1_nD))
	print("C(A>1, !D) = {}".format(C_Agt1_nD))

if __name__ == '__main__':
	DIR = "splits/train"
	if len(argv) > 1:
		DIR = argv[1]
	p1(DIR)
	p2(DIR)