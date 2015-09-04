from __future__ import division
import os
import re
import json
import Pylinear
from Pylinear.feature import getDataFiles

def getData():
	points = []
	lastThread = ""
	thread     = ""
	first = True
	for fn, f in getDataFiles(os.path.join(Pylinear.BASE_PATH,'splits/train/data')):
		split = fn.split("/")
		thread = split[0]
		fn = split[1]
		if thread != lastThread:
			if first:
				first = False
			elif not question_time is None:
				for upvotes, timeDiff in answer_times:
					points.append((timeDiff - question_time, upvotes))
			lastThread = thread
			question_time = None
			answer_times = []
		if re.findall(r'answer[\d]+\.json', fn):
			answerData = json.load(f)
			t = answerData['time']
			ups = answerData['upvotes']
			if not t is None:
				answer_times.append((ups, answerData['time']))
		if fn.endswith('metadata.json'):
			questionData = json.load(f)
			question_time = questionData['postTime']
			url = questionData['url']
	return points

def plot(data):
	import matplotlib.pyplot as plt
	oldData = data
	data = [(t,u) for t,u in data if u != 0]
	print(len(oldData) - len(data))
	timeDiff, ups = zip(*data)
	timeDiff = list(map(lambda x: x / 60 / 60 / 24 , timeDiff))
	plt.scatter(ups, timeDiff)
	plt.title("Answer Upvotes vs Time Since Question Post ")
	plt.xlabel("Upvotes")
	plt.xscale('log')
	plt.ylabel("Time (Days)")
	plt.show()

if __name__ == '__main__':
	if Pylinear.ON_GRID:
		data = getData()
		print(json.dumps(data))
	else:
		with open('uVt.dat') as f:
			data = json.load(f)
		plot(data)