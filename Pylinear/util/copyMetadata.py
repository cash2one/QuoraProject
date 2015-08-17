'''Copies metadata from compressed to annotated files so reannotation isn't needed to update.'''
from Pylinear.feature import getFiles
import tarfile
import itertools
import shutil

def copyMetadata(frm, to):
		fromF = tarfile.open(frm, 'r:gz')
		toF = tarfile.open(to, 'r:gz')
		outFn = '/'.join(to.split('/')[:-1]) + '/out.tar.gz'
		outF = tarfile.open(outFn, 'w:gz')
		for fromMem, toMem in zip(fromF.getmembers(), toF.getmembers()):
			assert fromMem.name == toMem.name
			if fromMem.name.endswith('.json'):
				outF.addfile(fromMem, fromF.extractfile(fromMem))
			else:
				outF.addfile(toMem, toF.extractfile(toMem))
		fromF.close()
		toF.close()
		outF.close()
		shutil.move(outFn, to)

if __name__ == '__main__':
	import sys
	if len(sys.argv) < 3:
		print("ERROR: Input and output directories required as arguments.")
		exit(1)

	compressed = getFiles(sys.argv[1])
	annotated  = getFiles(sys.argv[2])
	for c_fn, a_fn in itertools.izip(compressed, annotated):
		assert '/'.join(c_fn.split('/')[-3:]) == '/'.join(a_fn.split('/')[-3:])
		copyMetadata(c_fn, a_fn)