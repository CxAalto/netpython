import unittest
from operator import itemgetter
from netpython import pynet
from netpython import netio
from netpython import transforms
import os

class TestTransforms(unittest.TestCase):
    
    def setUp(self):
        self.folder=os.path.dirname(transforms.__file__)+os.path.join("a","tests","")[1:]
        self.simpleWeightedNet=netio.loadNet(self.folder+"testData/simpleWeightedNet.edg")
                
    def test_mst_kruskal(self):
        sn=self.simpleWeightedNet
        sn_minST=netio.loadNet(self.folder+"testData/transforms/simpleWeightedNet_minSpanningTree.edg")
        self.assertEqual(sorted(transforms.mst_kruskal(sn)),sorted(sn_minST))


        

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(TestTransforms("test_mst_kruskal"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
