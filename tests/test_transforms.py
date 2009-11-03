import unittest
from operator import itemgetter
from netpython import pynet
from netpython import netio
from netpython import transforms
from netpython import models
import os

class TestTransforms(unittest.TestCase):
    
	def setUp(self):
		self.folder=os.path.dirname(transforms.__file__)+os.path.join("a","tests","")[1:]
		self.simpleWeightedNet=netio.loadNet(self.folder+"testData/simpleWeightedNet.edg")
			
	def test_mst_kruskal(self):
		sn=self.simpleWeightedNet
		sn_minST=netio.loadNet(self.folder+"testData/transforms/simpleWeightedNet_minSpanningTree.edg")
		self.assertEqual(sorted(transforms.mst_kruskal(sn)),sorted(sn_minST))
		
	def test_netConfiguration(self):
		def configurationTest(ii,net,newNet):
			for i in range(0,len(net)):
				if newNet[i].deg()!=net[i].deg():
					return 0
			return 1

		N=100
		p=.5
		Loop=10
		for i in range(0,Loop):
			netER=models.makeER(N,p)
			netConf=transforms.netConfiguration(netER,keepsOrigNet=True)
			success=configurationTest(i,netER,netConf)
			self.assertEqual(success,1)
		
        



if __name__ == '__main__':
	if True:
		# If true, run only the tests listed below, otherwise run all tests
		# (this option is for testing the tests :-) )
		suite = unittest.TestSuite()
		suite.addTest(TestTransforms("test_mst_kruskal"))
		suite.addTest(TestTransforms("test_netConfiguration"))
		unittest.TextTestRunner().run(suite)
	else:
		# Run all tests.
		unittest.main()
