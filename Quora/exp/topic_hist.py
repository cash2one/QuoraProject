import numpy as np
import matplotlib
# Allows matplotlib to work without display (e.g. on CLSP grid)
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Quora.util.stats import getData

def graph(hist):
	fig, ax = plt.subplots()

	#bins = list(range(0, MAX+1, LABEL_INT))
	#ax.hist(hist, bins=MAX, range=(0, MAX))
	plt.hist(hist,
		range=(0,max(hist)),
		bins=max(hist)+1,
		normed = False)

	ax.set_title("Number of Answers to Questions on Quora")
	ax.set_ylabel("Count")
	ax.set_xlabel("Number of Answers")

	plt.savefig("topic_hist.pdf")

if __name__ == '__main__':
	from sys import argv

	hist = []
	DIR = argv[1]
	for entry in getData(DIR):
		hist.append(len(entry['data']['topics']))
	print(np.bincount(hist))
	graph(hist)