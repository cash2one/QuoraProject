import json
from sys import argv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

MAX = 100
LABEL_INT = 10
DIR = 'data/directory.json'

if len(argv) > 1:
	DIR = argv[1]

with open(DIR) as f:
	data = f.read()

data = [list(json.loads(i).values())[0]['path'] for i in data.strip().split('\n')]
hist = []
for fn in data:
	with open(fn) as f:
		ans = len(json.load(f)['data']['answers'])
		if ans > MAX:
			ans = MAX
		hist.append(ans)


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