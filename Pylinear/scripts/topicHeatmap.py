from __future__ import division

import json
import pickle
import itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Pylinear.feature import getDataFiles

def plot(sortedTopics, topicPairs, total, n=None):
	makeLabels=False
	if not n is None:
		sortedTopics = sortedTopics[:n]
		makeLabels = True

	heatmap = []
	for y, (_, i) in enumerate(sortedTopics):
		heatmap.append([])
		for x, (_, j) in enumerate(sortedTopics):
			if i == j:
				heatmap[y].append(np.nan)
				continue

			key = tuple(sorted([i, j]))
			if key in topicPairs:
				v = 100 * topicPairs[key] / total
			else:
				v = 0
			heatmap[y].append(v)

	heatmap = np.array(heatmap)

	fig, ax = plt.subplots()
	c = ax.imshow(heatmap, interpolation='nearest', vmin=0, vmax=100)
	fig.colorbar(c)

	ax.xaxis.tick_top()
	if makeLabels:
		ax.set_xticks(np.arange(heatmap.shape[0]), minor=False)
		ax.set_yticks(np.arange(heatmap.shape[1]), minor=False)
		labels = [i[1:] for _, i in sortedTopics]
		ax.set_xticklabels(labels, minor=False)
		ax.set_yticklabels(labels, minor=False)
		plt.xticks(rotation=90)
		plt.tight_layout()
		plt.savefig('topicHeatmapTop.png')
	else:
		fig.patch.set_visible(False)
		plt.axis('off')
		plt.savefig('topicHeatmap.png')

if __name__ == '__main__':

	topicPairs = {}
	topicCounts = {}

	total = 0
	for n, f in getDataFiles('/export/a04/wpovell/splits/train'):
		if not n.endswith('metadata.json'):
			continue
		total += 1
		topics = json.load(f)['topics']
		for i in topics:
			if not i in topicCounts:
				topicCounts[i] = 0
			topicCounts[i] += 1

		for i in itertools.combinations(topics, 2):
			key = tuple(sorted(i))
			if not key in topicPairs:
				topicPairs[key] = 0
			topicPairs[key] += 1

	sortedTopics = [(v, k) for k, v in topicCounts.items()]
	sortedTopics.sort(reverse=True)

	with open('topicHeatmapData.pckl', 'wb') as f:
		pickle.dump([sortedTopics,topicPairs,total], f)

	plot(sortedTopics, topicPairs, total)
	plot(sortedTopics, topicPairs, total, n=10)