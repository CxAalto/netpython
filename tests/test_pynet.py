import unittest
from operator import itemgetter
from netpython import pynet


class TestPynet(unittest.TestCase):
    
    def setUp(self):
        pass
                
    def test_basic_Net_construction(self):
        myNet=pynet.Net()
        myNet[1,2]=10.0
        self.assertEqual(myNet[1,2],10.0)
        self.assertEqual(myNet[2,1],0.0)


        

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(TestPynet("test_basic_Net_construction"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
