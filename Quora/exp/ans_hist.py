import json
import numpy as np
import matplotlib
# Allows matplotlib to work without display (e.g. on CLSP grid)
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def graph(hist):
	'''Graphs histogram of answer counts.
	Bins are of size one, all values above MAX are put in MAX bin.
	'''

	fig, ax = plt.subplots()

	bins = list(range(0, MAX+1, LABEL_INT))
	ax.hist(hist, bins=MAX, range=(0, MAX))

	xlabels = bins[1:]
	xlabels[-1] = '{}+'.format(MAX)
	N_labels = len(xlabels)
	plt.xticks(LABEL_INT * np.arange(N_labels) + LABEL_INT)

	ax.set_xticklabels(xlabels)
	ax.set_title("Number of Answers to Questions on Quora")
	ax.set_ylabel("Count")
	ax.set_xlabel("Number of Answers")

	plt.savefig("answer_hist.pdf")

MAX = 100
LABEL_INT = 10

if __name__ == '__main__':
	from sys import argv
	DIR = 'data/directory.json'
	if len(argv) > 1:
		DIR = argv[1]

	with open(DIR) as f:
		data = f.read()

	# File names
	data = [list(json.loads(i).values())[0]['path'] for i in data.strip().split('\n')]

	hist = []
	for fn in data:
		with open(fn) as f:
			try:
				ans = len(json.load(f)['data']['answers'])
				# Cutoff higher values
				if ans > MAX:
					ans = MAX
				hist.append(ans)
			except KeyError:
				continue

	# Output data so it can be re-graphed later
	print(np.bincount(hist))

	graph(hist)