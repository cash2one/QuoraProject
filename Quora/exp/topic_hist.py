import numpy as np
import matplotlib
# Allows matplotlib to work without display (e.g. on CLSP grid)
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Quora.util.stats import getData

def graph(hist):
	fig, ax = plt.subplots()

	plt.hist(hist, range=(-1,6), bins=[i + 0.5 for i in range(-1, 6)])
	xlabels = [''] + list(range(0,6))
	ax.set_xticklabels(xlabels)
	ax.set_title("Number of Topics Tagged in Quora Questions")
	ax.set_ylabel("Count")
	ax.set_xlabel("Number of Topics Tagged")

	plt.savefig("topic_hist.pdf")

if __name__ == '__main__':
	from sys import argv

	hist = []
	DIR = argv[1]
	for entry in getData(DIR):
		hist.append(len(entry['data']['topics']))
	print(np.bincount(hist))
	graph(hist)