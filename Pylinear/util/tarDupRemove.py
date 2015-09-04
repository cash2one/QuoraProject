import tarfile
import sys
from StringIO import StringIO
from time import time
import shutil

from Pylinear.feature import getFiles

def removeDups(inpFile):
	f = tarfile.open(inpFile, 'r:gz')
	outFn = '/tmp/{}_{}'.format(int(time()), inpFile.split('/')[-1])
	out = tarfile.open(outFn, 'w:gz')
	files = set()
	for member in f.getmembers():
		nm = member.name
		if not nm in files:
			files.add(nm)
			out.addfile(member, StringIO(member.tobuf()))

	f.close()
	out.close()
	shutil.move(outFn, inpFile)

if __name__ == '__main__':
	for fn in getFiles(sys.argv[1]):
		if fn.endswith('.tar.gz'):
			removeDups(fn)