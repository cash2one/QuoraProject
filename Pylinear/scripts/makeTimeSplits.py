from __future__ import division
from Pylinear.feature import getDataFiles
import json
import tarfile
from StringIO import StringIO

def generateFileTimestamps(data):
	lastThread = ""
	time = None

	threads = []
	first = True
	for fn, f in getDataFiles(data):
		split = fn.split("/")
		thread = split[1]
		fn = split[2]

		if first:
			first = False
			lastThread = thread
		elif thread != lastThread:
			if time is None:
				print("ERROR: Thread had no time")
			else:
				threads.append((time, lastThread))
				lastThread = thread
				time = None

		if fn.endswith('metadata.json'):
			data = json.load(f)
			time = data['postTime']

	if time is None:
		print("ERROR: Thread had no time")
	else:
		threads.append((time, lastThread))
		threads.sort()
	return threads

def makeSplits(inp, out, train=70, dev=10, tune=10, test=10):
	assert train+dev+tune+test == 100
	threads = [i[1] for i in generateFileTimestamps(inp)]
	p1 = int(len(threads) * train / 100)
	trainThreads = threads[:p1]
	p2 = p1 + int(len(threads) * dev / 100)
	devThreads = threads[p1:p2]
	p3 = p2 + int(len(threads) * tune / 100)
	tuneThreads = threads[p2:p3]
	testThreads = threads[p3:]

	trainF = tarfile.open('{}/train/data.tar.gz'.format(out), 'w:gz')
	devF   = tarfile.open('{}/dev/data.tar.gz'.format(out), 'w:gz')
	tuneF  = tarfile.open('{}/tune/data.tar.gz'.format(out), 'w:gz')
	testF  = tarfile.open('{}/test/data.tar.gz'.format(out), 'w:gz')
	for n, f in getDataFiles(inp):
		split = n.split("/")
		thread = split[1]
		fn = split[2]

		outF = None
		if thread in trainThreads:
			outF = trainF
		elif thread in devThreads:
			outF = devF
		elif thread in tuneThreads:
			outF = tuneF
		elif thread in testThreads:
			outF = testF
		else:
			print("ERROR: Thread not in any split")
			continue

		stringf = StringIO(f.read())
		info = tarfile.TarInfo('{}/{}'.format(thread, fn))
		info.size = len(stringf.buf)
		outF.addfile(info, stringf)

	trainF.close()
	devF.close()
	tuneF.close()
	testF.close()



if __name__ == '__main__':
	makeSplits('splits/train/data', 'out') #'/export/a04/wpovell/annotated_data', '/export/a04/wpovell/splits')