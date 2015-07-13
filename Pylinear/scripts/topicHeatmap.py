import json
import itertools
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use('Agg')

from Pylinear.feature import getDataFiles

def plot(heatmap, sortedTopics, n=None):
	labels=False
	if not n is None:
		sortedTopics = sortedTopics[:n]
		labels = True

	heatmap = []
	for y, (_, i) in enumerate(sortedTopics):
		heatmap.append([])
		for x, (_, j) in enumerate(sortedTopics):
			key = tuple(sorted([i, j]))
			if key in topicPairs:
				v = topicPairs[key]
			else:
				v = 0
			heatmap[y].append(v)

	heatmap = np.array(heatmap)
	fig, ax = plt.subplots()

	ax.pcolor(heatmap)

	# For top 10 #
	labels = [i for _, i in sortedTopics]
	ax.set_xticks(np.arange(heatmap.shape[0])+0.5, minor=False)
	ax.set_yticks(np.arange(heatmap.shape[1])+0.5, minor=False)
	ax.invert_yaxis()
	ax.xaxis.tick_top()
	if labels:
		ax.set_xticklabels(labels, minor=False)
		ax.set_yticklabels(labels, minor=False)
		plt.xticks(rotation=90)
	plt.savefig('topicHeatmap.png')

if __name__ == '__main__':

	topicPairs = {}
	topicCounts = {}

	for n, f in getDataFiles('/export/a04/wpovell/splits/train'):
		if not n.endswith('metadata.json'):
			continue
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

	print(json.dumps(sortedTopics))
	print(json.dumps(topicPairs))

	#plot(sortedTopics, topicPairs)