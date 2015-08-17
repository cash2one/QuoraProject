'''Generates a probability graph of having a certain number of answers.
Graphed for both not given and given that the question has details.'''

from __future__ import division
from Pylinear.feature import getDataFiles, commFromData
import re
from collections import Counter
from matplotlib import pyplot as plt

def graph(x1,y1,t1,x2,y2,t2):
	width = 0.35
	probs1 = list(map(lambda a: a/t1, y1))
	probs2 = list(map(lambda a: a/t2, y2))

	plt.bar(x2, probs2, width, color="y", label="P(A<X>)")
	plt.bar(list(map(lambda a: a+width, x1)),probs1, width, color="b", label="P(A<x>|D)")

	plt.legend()
	plt.ylim([0,None])
	plt.xlim([0,25])
	plt.title("Probability a Thread has <X> Answers")
	plt.xlabel("<X>")
	plt.ylabel("Probability")
	plt.show()

if __name__ == '__main__':
	from sys import argv
	DIR = "splits/train/data"
	if len(argv) > 1:
		DIR = argv[1]

	lastThread = ""
	numThreads = 0
	numDetailThreads = 0
	numAnswers = 0
	hasDetails = False
	answered = []
	answeredDetails = []
	for n, f in getDataFiles(DIR):
		thread = n.split("/")[1]
		if thread != lastThread:
			print(thread)
			lastThread = thread
			numThreads += 1
			answered.append(numAnswers)
			if hasDetails:
				numDetailThreads += 1
				answeredDetails.append(numAnswers)
			numAnswers = 0
			hasDetails = False
		if re.search(r"answer\d+\.comm", n):
			numAnswers += 1
		if n.endswith("question.comm"):
			comm = commFromData(f.read())
			if len(comm.sectionList) > 1:
				hasDetails = True

	x1 = []
	y1 = []
	t1 = numThreads
	for k, v in Counter(answered).items():
		x1.append(k)
		y1.append(v)

	x2 = []
	y2 = []
	t2 = numDetailThreads
	for k, v in Counter(answeredDetails).items():
		x2.append(k)
		y2.append(v)

	graph(x1,y1,t1,x2,y2,t2)