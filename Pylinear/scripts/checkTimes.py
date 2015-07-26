from Pylinear.feature import getDataFiles
import datetime
import re
import json

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
print(json.dumps(times))