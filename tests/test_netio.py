import unittest
from operator import itemgetter
from netpython import pynet
from netpython import netio
from netpython import transforms
import os

class TestNetio(unittest.TestCase):
    
    def setUp(self):
        self.folder=os.path.dirname(netio.__file__)+os.path.join("a","tests","")[1:]
        self.simpleWeightedNet=netio.loadNet(self.folder+"testData/simpleWeightedNet.edg")

        self.sn_properties1=self.folder+"testData/nodeProperties/simpleWeightedNet_properties1.txt"
        self.sn_properties1_nolabels=self.folder+"testData/nodeProperties/simpleWeightedNet_properties1_nolabels.txt"                
    def test_loadingNodeProperties_workingFiles_sparse1(self):
        sn=self.simpleWeightedNet
        netio.loadNodeProperties(sn,self.sn_properties1)
        self.assertEqual(map(lambda x:sn.nodeProperty["npp"][x],sorted(list(sn))),[2,3,4,5])
        self.assertEqual(map(lambda x:sn.nodeProperty["char"][x],sorted(list(sn))),["a","b","c","d"])

    def test_loadingNodeProperties_workingFiles_sparse2(self):
        sn=self.simpleWeightedNet
        netio.loadNodeProperties(sn,self.sn_properties1_nolabels,propertyNames=["node_label","npp","char"])
        self.assertEqual(map(lambda x:sn.nodeProperty["npp"][x],sorted(list(sn))),[2,3,4,5])
        self.assertEqual(map(lambda x:sn.nodeProperty["char"][x],sorted(list(sn))),["a","b","c","d"])

    def test_loadingNodeProperties_workingFiles_sparse3(self):
        sn=self.simpleWeightedNet
        netio.loadNodeProperties(sn,self.sn_properties1_nolabels,propertyNames=["npp","char"])
        self.assertEqual(map(lambda x:sn.nodeProperty["npp"][x],sorted(list(sn))),[2,3,4,5])
        self.assertEqual(map(lambda x:sn.nodeProperty["char"][x],sorted(list(sn))),["a","b","c","d"])

    def test_loadingNodeProperties_workingFiles_full1(self):
        fn=pynet.SymmFullNet(4)
        netio.loadNodeProperties(fn,self.sn_properties1)
        self.assertEqual(map(lambda x:fn.nodeProperty["node_label"][x],sorted(list(fn))),[1,2,3,4])
        self.assertEqual(map(lambda x:fn.nodeProperty["npp"][x],sorted(list(fn))),[2,3,4,5])
        self.assertEqual(map(lambda x:fn.nodeProperty["char"][x],sorted(list(fn))),["a","b","c","d"])

    def test_loadingNodeProperties_workingFiles_full2(self):
        fn=pynet.SymmFullNet(4)
        netio.loadNodeProperties(fn,self.sn_properties1_nolabels,propertyNames=["node_label","npp","char"])
        self.assertEqual(map(lambda x:fn.nodeProperty["node_label"][x],sorted(list(fn))),[1,2,3,4])
        self.assertEqual(map(lambda x:fn.nodeProperty["npp"][x],sorted(list(fn))),[2,3,4,5])
        self.assertEqual(map(lambda x:fn.nodeProperty["char"][x],sorted(list(fn))),["a","b","c","d"])

    def test_loadingNodeProperties_brokenFiles(self):
        pass

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(TestNetio("test_loadingNodeProperties_workingFiles_sparse1"))
        suite.addTest(TestNetio("test_loadingNodeProperties_workingFiles_sparse2"))
        suite.addTest(TestNetio("test_loadingNodeProperties_workingFiles_sparse3"))
        suite.addTest(TestNetio("test_loadingNodeProperties_workingFiles_full1"))
        suite.addTest(TestNetio("test_loadingNodeProperties_workingFiles_full2"))
        suite.addTest(TestNetio("test_loadingNodeProperties_brokenFiles"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
