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
		
	def SOMEONE_SHOULD_FIX_THIS_test_netConfiguration(self):
		def configurationTest(ii,net,newNet):
			for i in range(0,len(net)):
				if newNet[i].deg() != net[i].deg():
					print i, newNet[i].deg(), net[i].deg()
					return False
			return True

		N=100
		p=.5
		Loop=10
		for i in range(0,Loop):
			netER = models.makeER(N,p)
			netConf = transforms.netConfiguration(netER, keepsOrigNet=True)
			success = configurationTest(i,netER,netConf)
			self.assertTrue(success)

	def test_snowball_symmnet(self):
		net = pynet.SymmNet()
		net[0][1] = 1
		net[0][2] = 2
		net[1][2] = 12
		net[2][3] = 23
		net[3][4] = 34

		sball = transforms.snowball(net, 0, 1)
		self.assertTrue(len(sball) == 3)
		self.assertTrue(len(list(sball.edges)) == 2)
		self.assertTrue(isinstance(sball, type(net)))
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

		sball = transforms.snowball(net, 0, 1, True)
		self.assertTrue(len(list(sball.edges)) == 3)
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

		sball = transforms.snowball(net, 3, 2, False)
		self.assertTrue(len(sball) == 5)
		self.assertTrue(len(list(sball.edges)) == 4)
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])
		
		sball = transforms.snowball(net, 3, 2, True)
		self.assertTrue(len(sball) == 5)
		self.assertTrue(len(list(sball.edges)) == 5)
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

	def test_snowball_dirnet(self):
		net = pynet.Net()
		net[0][1] = 1
		net[0][2] = 2
		net[1][2] = 12
		net[2][1] = 21
		net[2][3] = 23
		net[4][3] = 43

		sball = transforms.snowball(net, 0, 1)
		self.assertTrue(len(sball) == 3)
		self.assertTrue(len([1 for i,j,w in sball.edges if w > 0]) == 2)
		self.assertTrue(isinstance(sball, type(net)))
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

		sball = transforms.snowball(net, 0, 1, True)
		self.assertTrue(len(sball) == 3)
		self.assertTrue(len([1 for i,j,w in sball.edges if w > 0]) == 4)
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

		sball = transforms.snowball(net, 3, 2, False)
		self.assertTrue(len(sball) == 5)
		self.assertTrue(len([1 for i,j,w in sball.edges if w > 0]) == 5)
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])
		
		sball = transforms.snowball(net, 3, 2, True)
		self.assertTrue(len(sball) == 5)
		self.assertTrue(len([1 for i,j,w in sball.edges if w > 0]) == 6)		
		for i,j,w in sball.edges:
			self.assertTrue(w == net[i][j])

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
