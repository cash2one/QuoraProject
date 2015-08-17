import unittest
import difflib

from Pylinear.model import combineFeatures
class UnitTests(unittest.TestCase):
	def test_combineFeatures(self):
		combineFeatures('Pylinear/tests/splits/train', 'featureOne', ['featureTwo', 'featureThree'])
		with open('Pylinear/tests/splits/train/results/correct.txt') as f:
			correct = f.read()
		with open('Pylinear/tests/splits/train/results/featureOne,featureTwo,featureThree/data.txt') as f:
			toTest  = f.read()

		if correct != toTest:
			message = ''.join(difflib.ndiff(correct.splitlines(True), toTest.splitlines(True)))
			self.fail("Multi-line strings are unequal:\n" + message)

if __name__ == '__main__':
	unittest.main()