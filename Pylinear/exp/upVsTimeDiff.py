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
				for ans in answer_times:
					points.append((ans[0] - question_time, ans[1]))

			lastThread = thread
			question_time = None
			answer_times = []
		if re.findall(r'answer[\d]+\.json', fn):
			answerData = json.load(f)
			t = answerData['time']
			ups = answerData['upvotes']
			if not t is None:
				answer_times.append((answerData['time'], ups))
		if fn.endswith('metadata.json'):
			questionData = json.load(f)
			question_time = questionData['postTime']
			url = questionData['url']
	return points

def plot(data):
	import matplotlib.pyplot as plt
	timeDiff, ups = zip(*data)
	plt.scatter(ups, timeDiff)
	plt.xlabel("Upvotes")
	plt.ylabel("Time")
	plt.show()

if __name__ == '__main__':
	data = getData()
	if Pylinear.ON_GRID:
		print(json.dumps(data))
	else:
		plot(data)