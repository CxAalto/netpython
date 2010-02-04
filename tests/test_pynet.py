import unittest
from operator import itemgetter
from netpython import pynet




class TestPynet(unittest.TestCase):
    
    def setUp(self):
        pass
                
    def test_basic_dir(self,netType):
        myNet=netType(sizeLimit=10)

        myNet[1,2]=10.0
        self.assertEqual(myNet[1,2],10.0)
        self.assertEqual(myNet[2,1],0.0)
        
        self.assertEqual(sorted(list(myNet)),[1,2])
        self.assertEqual(list(myNet[1]),[2])
        self.assertEqual(list(myNet[2]),[1])

        myNet[2,1]=1.0
        self.assertEqual(list(myNet[1]),[2])

        myNet[2,3]=5.0
        self.assertEqual(list(myNet[1].iterIn()),[2])
        self.assertEqual(list(myNet[3].iterIn()),[2])
        self.assertEqual(list(myNet[1].iterOut()),[2])

    def test_basic_symm(self,netType):
        myNet=netType(sizeLimit=10)

        myNet[1,2]=10.0
        self.assertEqual(myNet[1,2],10.0)
        self.assertEqual(myNet[2,1],10.0)
        
        myNet[1,"foo"]=0.1
        self.assertEqual(myNet[1].deg(),2)
        self.assertEqual(myNet.deg(1),2)

        del myNet["foo"]
        self.assertEqual(myNet[1].deg(),1)
        self.assertEqual(list(myNet[1]),[2])
        
        self.assertEqual(len(myNet),2)
        myNet.addNode("bar")
        self.assertEqual(len(myNet),3)
        self.assertEqual(myNet["bar"].deg(),0)


    def test_basic_dir_ScipySparseDirNet(self):
        self.test_basic_dir(pynet.ScipySparseDirNet)

    def test_basic_dir_NumpyFullDirNet(self):
        self.test_basic_dir(pynet.NumpyFullDirNet)

    def test_basic_symm_ScipySparseSymmNet(self):
        self.test_basic_symm(pynet.ScipySparseSymmNet)

    def test_basic_symm_NumpyFullSymmNet(self):
        self.test_basic_symm(pynet.NumpyFullSymmNet)

    def test_basic_symm_LCELibSparseSymmNet(self):
        self.test_basic_symm(pynet.LCELibSparseSymmNet)


def test_pynet():
    suite = unittest.TestSuite()    
    #symmetric tests:
    suite.addTest(TestPynet("test_basic_symm_ScipySparseSymmNet"))
    suite.addTest(TestPynet("test_basic_symm_NumpyFullSymmNet"))
    suite.addTest(TestPynet("test_basic_symm_LCELibSparseSymmNet"))

    #dir tests:
    suite.addTest(TestPynet("test_basic_dir_ScipySparseDirNet"))
    suite.addTest(TestPynet("test_basic_dir_NumpyFullDirNet"))

    unittest.TextTestRunner().run(suite)    

if __name__ == '__main__':
    runTests()

