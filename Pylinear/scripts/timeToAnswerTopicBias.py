#!/usr/bin/env python3
from __future__ import division
import json

with open('map.json') as f:
	topicMap = json.load(f)
with open('data.txt') as f:
	data = f.read()

topicMap = {v:k for k, v in topicMap.items()}
times = {i:[] for i in topicMap.values()}

first = True
for line in data.split('\n'):
	if first:
		line = line[:line.find('#')].strip()
		first = False
	time, *topics = line.split(' ')

	for i in topics:
		times[topicMap[int(i.split(':')[0])]].append(int(time))

l = sorted([(sum(v)/len(v), k) for k, v in times.items()], reverse=True)
print("Quickest")
print('\n'.join(['{}: {:.1f}'.format(i[1], i[0]) for i in l[:15]]))
l = sorted([(sum(v)/len(v), k) for k, v in times.items()], reverse=False)
print("\nSlowest")
print('\n'.join(['{}: {:.1f}'.format(i[1], i[0]) for i in l[:15]]))

top = sorted([(len(v), k) for k, v in times.items()], reverse=True)
print("\nTop")
for i in top[:10]:
	t = times[i[1]]
	print('{}: {:.1f}'.format(i[1], sum(t)/len(t)))