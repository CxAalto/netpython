import unittest
from operator import itemgetter
#from netpython import pynet
from netpython import percolator

import os

class TestPercolator(unittest.TestCase):
    
	def setUp(self):
		pass

	def test_KtreeInteger(self):
		ktree=percolator.KtreeInteger(size=0) #For dynamic size
		self.assertEqual(ktree.giantSize,0)
		ktree.setSize(4)
		self.assertEqual(ktree.giantSize,1)
		ktree.mergeSets(0,1)
		self.assertEqual(ktree.giantSize,2)
		self.assertEqual(ktree.getSetIndex(0),ktree.getSetIndex(1))
		ktree.mergeSets(2,3)
		self.assertEqual(ktree.getSusceptibility(),2)

		ktree=percolator.KtreeInteger(size=4) #For static size
		self.assertEqual(ktree.giantSize,1)
		ktree.mergeSets(0,1)
		self.assertEqual(ktree.giantSize,2)
		self.assertEqual(ktree.getSetIndex(0),ktree.getSetIndex(1))
		ktree.mergeSets(2,3)
		self.assertEqual(ktree.getSusceptibility(),2)


def test_percolator():
	suite = unittest.TestSuite()
	suite.addTest(TestPercolator("test_KtreeInteger"))
	unittest.TextTestRunner().run(suite)

if __name__ == '__main__':
	test_percolator()
