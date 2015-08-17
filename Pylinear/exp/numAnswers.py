'''Generates histogram of the number of Quora answers threads get'''
from matplotlib import pyplot as plt
import math
from collections import Counter

def graph(answerCounts):
	# BIN_COUNT bins of size 1
	plt.hist(answerCounts, bins=BIN_COUNT, range=(0,BIN_COUNT))

	# Labels
	plt.title("Number of Answers Quora Posts Get")
	plt.xlabel("Number of Answers")
	plt.ylabel("Frequency")
	plt.legend()
	plt.show()

	plt.boxplot(answerCounts)
	plt.title("Number of Answers Quora Posts Get")
	plt.ylabel("Number of Answers")
	plt.yscale("log")
	plt.show()

BIN_COUNT = 100

def mean(l):
	return sum(l)/len(l)

def median(l):
	l.sort()
	LEN = len(l)
	if LEN % 2 == 0:
		return (l[LEN/2] + l[LEN/2-1])/2
	else:
		return l[LEN/2]

def stdDev(l, meanVal):
	return math.sqrt(sum([(i - meanVal) ** 2 for i in l]) / (len(l) - 1))

if __name__ == "__main__":
	from sys import argv
	DIR = "splits/train/data"
	if len(argv) > 1:
		DIR = argv[1]
	thread = ""
	answerCounts = []
	numAnswers = 0
	for n in getDataFiles(DIR):
		_, newThread, fn = n.split('/')

		if newThread != thread:
			thread = newThread
			answerCounts.append(numAnswers)
			numAnswers = 0

		if fn.endswith(".comm") and fn.startswith("answer"):
			numAnswers += 1

	# Print for reprocessing on local machine
	print(Counter(answerCounts))