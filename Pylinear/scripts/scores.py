from __future__ import division

def FMeasure(pres, recall, beta=1):
	return (1 + beta**2) * pres * recall / (beta**2 * pres + recall)

if __name__ == '__main__':
	from sys import argv
	import os
	if len(argv) < 2:
		print("Need argument for prediction output")
	elif len(argv) == 2:
		realNm = os.path.join(argv[1], 'data.txt')
		predNm = os.path.join(argv[1], 'predict.out')
	else:
		realNm = argv[1]
		predNm = argv[2]

	with open(realNm) as f:
		real = [i.split(' ')[0] for i in f.read().strip().split('\n')]
	with open(predNm) as f:
		pred = f.read().strip().split('\n')

	total = 0
	tp    = 0
	tn    = 0
	fp    = 0
	fn    = 0
	for realLn, predLn in zip(real,pred):
		total += 1
		if realLn == predLn:
			if predLn == '1':
				tp += 1
			else:
				tn += 1
		else:
			if predLn == '1':
				fp += 1
			else:
				fn += 1

	try:
		pres = 100 * tp / (tp + fp)
	except ZeroDivisionError:
		pres = float('inf')
	try:
		recall = 100 * tp / (tp + fn)
	except ZeroDivisionError:
		recall = float('inf')
	if pres and recall:
		F = FMeasure(pres, recall)
	else:
		F = float('inf')

	print("Accuracy   {:.2f}%".format(100 * (tp + tn) / total))
	print("Precision  {:.2f}%".format(pres))
	print("Recall     {:.2f}%".format(recall))
	print("F1         {:.2f}%".format(F))