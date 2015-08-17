'''Outputs data/plots for how long it takes questions from the dataset took to get an answer'''
from __future__ import division
from Pylinear.feature import getDataFiles
import datetime
import re
import json
import numpy as np

def genData():
	times = {}
	lastThread = ""
	answer_times = []
	question_time = None
	first = True
	for n, f in getDataFiles('/export/a04/wpovell/splits/train/data'):
		if not n.endswith('.json'):
			continue
		split = n.split("/")
		thread = split[1]
		fn = split[2]
		if thread != lastThread:
			if first:
				first = False
			elif len(answer_times) != 0 and not question_time is None:
					answer_time = min(answer_times)
					year = datetime.datetime.fromtimestamp(question_time).year
					d = int(datetime.timedelta(seconds=(answer_time - question_time)).total_seconds() / 60 / 60)
					if d >= 0:
						if not year in times:
							times[year] = []
						times[year].append(d)
			lastThread = thread
			question_time = None
			answer_times = []
		if re.match('answer[\d]+.json', fn):
			answerData = json.load(f)
			t = answerData['time']
			if not t is None:
				answer_times.append(answerData['time'])
		if fn.endswith('metadata.json'):
			questionData = json.load(f)
			question_time = questionData['postTime']
			url = questionData['url']
	return times
def plot():
	import matplotlib.pyplot as plt
	with open('timeData.txt') as f:
		data = json.load(f)

	labels, data = zip(*sorted([(k, sum(v)/len(v)) for k, v in data.items()]))

	N = len(labels)
	ind = np.arange(N)  # the x locations for the groups
	width = 0.35       # the width of the bars

	fig, ax = plt.subplots()
	rects1 = ax.bar(ind, data, width, align='center')

	# add some text for labels, title and axes ticks
	ax.set_ylabel('Avg. Time in Hours')
	ax.set_xlabel('Year')
	ax.set_title('Avg. Time to Get Answer')
	plt.xticks(range(N), labels)
	plt.ylim([0, max(data)*1.1])
	#ax.set_xticks(ind+width)
	#ax.set_xticklabels(labels)

	def autolabel(rects):
	    # attach some text labels
	    for rect in rects:
	        height = rect.get_height()
	        ax.text(rect.get_x()+rect.get_width()/2., height + 40, '%d'%int(height),
	                ha='center', va='bottom')

	autolabel(rects1)

	plt.show()