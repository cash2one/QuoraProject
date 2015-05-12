from __future__ import division
from Pylinear.feature import getDataFiles, commFromData
import re

if __name__ == '__main__':
	from sys import argv
	DIR = "splits/train"
	if len(argv) > 1:
		DIR = argv[1]

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