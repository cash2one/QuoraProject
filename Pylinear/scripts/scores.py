from __future__ import division

def FMeasure(pres, recall, beta=1):
	(1 + beta**2) * pres * recall / (beta**2 * pres + recall)

if __name__ == '__main__':
	from sys import argv
	import os
	if len(argv) < 2:
		print("Need argument for prediction output")
	elif len(argv) == 2:
		real = open(os.path.join(argv[1], 'data.txt'))
		pred = open(os.path.join(argv[1], 'predict.out'))
	else:
		real = open(argv[1])
		pred = open(argv[2])

	realLine = real.readline().split()[0].strip()
	predLine = pred.readline().strip()
	total = 0
	tp    = 0
	tn    = 0
	fp    = 0
	fn    = 0
	while realLine:
		total += 1
		if realLine == predLine:
			if predLine == '1':
				tp += 1
			else:
				tn += 1
		else:
			if predLine == '1':
				fp += 1
			else:
				fn += 1
		realLine = real.readline().split()[0].strip()
		predLine = pred.readline().strip()

	pres   = tp / (tp + fp)
	recall = tp / (tp + fn)
	print("Accuracy   {}%".format((tp + tn)) / total)
	print("Precision  {}%".format(pres))
	print("Recall     {}%".format(recall))
	print("F1         {}%".format(FMeasure(pres, recall)))
