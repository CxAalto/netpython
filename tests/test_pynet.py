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

        #test iterators
        self.assertEqual(list(myNet[1]),[2])
        self.assertEqual(list(myNet[2]),[1])

        myNet[2,1]=1.0
        self.assertEqual(list(myNet[1]),[2])
        
        myNet[2,3]=5.0
        self.assertEqual(list(myNet[1].iterIn()),[2])

        #test degrees
        self.assertEqual(myNet[1].inDeg(),1)
        self.assertEqual(myNet[3].inDeg(),1)
        self.assertEqual(myNet[3].outDeg(),0)

        #test deleting nodes
        del myNet[1]
        self.assertEqual(myNet[1,2],0.0)
        self.assertEqual(list(myNet[2]),[3])
        myNet[1,4]=4.0
        self.assertEqual(myNet[1,4],4.0)

        #test copying
        copyNet=myNet.__copy__()        
        self.assertEqual(sorted(list(copyNet)),[1,2,3,4])
        self.assertEqual(sorted(list(myNet)),sorted(list(copyNet)))
        self.assertEqual(map(myNet.inDeg,myNet),map(copyNet.inDeg,myNet))
        self.assertEqual(map(myNet.outDeg,myNet),map(copyNet.outDeg,myNet))
        self.assertEqual(copyNet[1,4],4.0)
        self.assertEqual(copyNet[2,3],5.0)

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

        #test copying
        copyNet=myNet.__copy__()        
        self.assertEqual(sorted(list(myNet)),sorted(list(copyNet)))
        self.assertEqual(map(lambda node:sorted(myNet[node]),myNet),map(lambda node:sorted(copyNet[node]),myNet))

        #next net
        myNet2=netType(sizeLimit=10)
        myNet2.addNode(1)
        myNet2[2,3]=1
        self.assertEqual(len(myNet2),3)
        self.assertEqual(myNet2[1,2],0)
        self.assertEqual(myNet2[2,3],1)

        #test adding empty nodes
        myNet2.addNode("empty")
        self.assertEqual(myNet2["empty"].deg(),0)

        #test copying
        copyNet2=myNet2.__copy__()        
        self.assertEqual(sorted(list(myNet2)),sorted(list(copyNet2)))
        self.assertEqual(map(lambda node:sorted(myNet2[node]),myNet2),map(lambda node:sorted(copyNet2[node]),myNet2))


    def test_basic_dir_DictDirNet(self):
        self.test_basic_dir(pynet.DictDirNet)

    def test_basic_dir_ScipySparseDirNet(self):
        self.test_basic_dir(pynet.ScipySparseDirNet)

    def test_basic_dir_NumpyFullDirNet(self):
        self.test_basic_dir(pynet.NumpyFullDirNet)

    def test_basic_dir_LCELibSparseDirNet(self):
        self.test_basic_dir(pynet.LCELibSparseDirNet)

    def test_basic_symm_DictSymmNet(self):
        self.test_basic_symm(pynet.DictSymmNet)

    def test_basic_symm_ScipySparseSymmNet(self):
        self.test_basic_symm(pynet.ScipySparseSymmNet)

    def test_basic_symm_NumpyFullSymmNet(self):
        self.test_basic_symm(pynet.NumpyFullSymmNet)

    def test_basic_symm_LCELibSparseSymmNet(self):
        self.test_basic_symm(pynet.LCELibSparseSymmNet)


def test_pynet():
    suite = unittest.TestSuite()    
    #symmetric tests:
    suite.addTest(TestPynet("test_basic_symm_DictSymmNet"))
    suite.addTest(TestPynet("test_basic_symm_ScipySparseSymmNet"))
    suite.addTest(TestPynet("test_basic_symm_NumpyFullSymmNet"))
    suite.addTest(TestPynet("test_basic_symm_LCELibSparseSymmNet"))

    #dir tests:
    suite.addTest(TestPynet("test_basic_dir_DictDirNet"))
    suite.addTest(TestPynet("test_basic_dir_ScipySparseDirNet"))
    suite.addTest(TestPynet("test_basic_dir_NumpyFullDirNet"))
    suite.addTest(TestPynet("test_basic_dir_LCELibSparseDirNet"))

    unittest.TextTestRunner().run(suite)    

if __name__ == '__main__':
    test_pynet()

