from __future__ import division
from Pylinear.feature import getDataFiles, commFromData
import re
from collections import Counter
from matplotlib import pyplot as plt

def graph(x,y):
	plt.bar(x,y)
	plt.show()

if __name__ == '__main__':
	from sys import argv
	DIR = "splits/train/data"
	if len(argv) > 1:
		DIR = argv[1]

	lastThread = ""
	numThreads = 0
	numAnswers = 0
	hasDetails = False
	data = []
	for n, f in getDataFiles(DIR):
		thread = n.split("/")[1]
		if thread != lastThread:
			lastThread = thread
			if hasDetails:
				numThreads += 1
				data.append(numAnswers)
			numAnswers = 0
			hasDetails = False
		if re.search(r"answer\d+\.comm", n):
			numAnswers += 1
		if n.endswith("question.comm"):
			comm = commFromData(f.read())
			if len(comm.sectionList) > 1:
				hasDetails = True

	x = []
	y = []
	for k, v in Counter(data).items():
		x.append(k)
		y.append(v)

	print(x)
	print(y)
	print(numThreads)
	#graph(x,y)