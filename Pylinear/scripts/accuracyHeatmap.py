import re
from termcolor import colored

def colorPrint(d, out=True):
	s = '  | '
	s += ' | '.join(['{}'.format(i).ljust(7) for i in sorted(d[0.0].keys())])
	s += ' |\n'
	s += '--|' + '-' * (len(s) - 5) + '|\n'
	arr = []
	for y, i in enumerate(sorted(d.keys())):
		arr.append([])
		s += '{} |'.format(int(i))
		for j in sorted(d[i].keys()):
			arr[y].append(d[i][j])
			formatted = '{:.4f}'.format(d[i][j])
			if d[i][j] == mn:
				formatted = colored(formatted, 'red')
			if d[i][j] == mx:
				formatted = colored(formatted, 'green')
			s += ' {} |'.format(formatted)
		s += '\n'
	if out:
		print(s)

	return arr

def plot(d, arr):
	import matplotlib
	import matplotlib.pyplot as plt
	import numpy as np
	import math

	correctLen = len(arr[0])
	for i in arr:
		while len(i) < correctLen:
			i.append(np.nan)
	arr = np.array(arr)

	fig, ax = plt.subplots()
	c = ax.imshow(arr, interpolation='nearest', vmin=0, vmax=100)
	fig.colorbar(c)

	ax.set_xlabel('Cost Parameter (10^x)')
	ax.set_ylabel('Classifier ID')
	plt.title('Accuracy of Predicting "has_2_answers"\nUsing Question Length, Topics, and Unigrams')
	ax.set_xticks(np.arange(arr.shape[1]), minor=False)
	ax.set_yticks(np.arange(arr.shape[0]), minor=False)
	ax.set_xticklabels([int(math.log10(i)) for i in sorted(d[0].keys())], minor=False)
	ax.set_yticklabels([int(i) for i in sorted(d.keys())], minor=False)
	plt.show()

if __name__ == '__main__':
	import sys
	inputFile = 'work.txt'
	if len(sys.argv) > 1:
		inputFile = sys.argv[1]

	with open(inputFile) as f:
		data = f.read()

	data = [list(map(float, re.findall(r'[\d.]+', i))) for i in data.split('\n')]

	acc = [i[2] for i in data]
	mx = max(acc)
	mn = min(acc)

	d = {}
	for c, s, a in data:
		if not s in d:
			d[s] = {}
		d[s][c] = a

	arr = colorPrint(d)
	plot(d, arr)