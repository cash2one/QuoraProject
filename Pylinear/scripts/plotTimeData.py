from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import json

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