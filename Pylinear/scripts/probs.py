'''Generate basic conditional probabilties for features.
A = question has at least one answer
D = question has details
L = question has list
'''

from __future__ import division, print_function
import json
from sys import argv
from Pylinear.feature import getDataFiles, commFromData

def printPer(n, v):
	'''Prints percent value.'''
	print('{} = {:.2f}%'.format(n, 100 * v))

if __name__ == '__main__':
	DIR = "splits/train"
	if len(argv) > 1:
		DIR = argv[1]

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
		#if name.endswith('metadata.json'):
		#	content = json.load(content)
		#	if content['hasList']:
		#		hasList = True

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
			#if hasList:
			#	question_has_list += 1
			#if hasList and ans:
			#	question_with_list_answered += 1

			ans = False
			dets = False
			hasList = False
			dirName = curDir

	print(__doc__)
	printPer('P(A)   ', answered / questions)
	printPer('P(A|D) ', answered_with_details / details)
	printPer('P(A|!D)', answered_without_details / (questions - details))
	print()
	printPer('P(D)   ', details / questions)
	printPer('P(A,D) ', answered_with_details / questions)
	print()
	#printPer('P(L)   ', question_has_list / questions)
	#printPer('P(A|L) ', question_with_list_answered / question_has_list)