import unittest
from operator import itemgetter
from netpython import visuals_R as visuals
from netpython import pynet
# import visuals_R
import Image
import pylab
from pylab import *

# This file contains tests for the visualization code.  Some very
# simple tests are created for starters, more to be added later.
#
# Visualizations are tricky to test automatically. The solution was to
# print out some .eps files that can be compared with earlier
# versions. If the new .eps files don't come out neat, something is
# broken in the code.
#
# The automatic tests should however notice if the code stumbles
# altogether and is unable to produce output.
# 
#   - Jun 23 2009  Riitta 



class TestVisuals(unittest.TestCase):
    
    def setUp(self):
        # Construct acceptable data
        # A triangle network:
        self.m=pynet.SymmNet()
        self.m[0][1]=1.0
        self.m[1][2]=3.5
        self.m[0][2]=5.0
        # Coordinates (a dictionary that contains 2-tuples) 
        self.xy={}
        self.xy[0]=(0,0)
        self.xy[1]=(4,0)
        self.xy[2]=(2,3)

        self.goodEdgeColorMapName='winter'
        self.wrongEdgeColorMapName='wint'
        
        

    def test_missing_input(self):
        # TypeErrors should be raised if less than two input values
        self.assertRaises(TypeError, visuals.VisualizeNet, self.m)
        self.assertRaises(TypeError, visuals.VisualizeNet, self.xy)
        
        
    def test_unacceptable_input(self):
        # if input in wrong order: 
        # self.assertRaises(AttributeError, visuals.VisualizeNet, self.xy, self.m)
        self.assertRaises(AssertionError, visuals.VisualizeNet, self.m, self.xy, edgeColorMap=self.wrongEdgeColorMapName) 
               
    def test_simplePlot1(self):
        """ Test that a very simple plot without any parameters can be created """
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy))
        #f.print_eps("figures/current/test_simplePlot1.eps",dpi=80.0)

    def test_input_combinations(self):
        # Note: this test detects a known bug, Jari plans to fix the bug - June 23 2009
        """ Testing different combinations of inputs """
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy,equalsize=True))
        f.print_eps("figures/current/test_simplePlot1.eps",dpi=80.0)

        

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(TestVisuals("test_simplePlot1"))
        suite.addTest(TestVisuals("test_missing_input"))
        suite.addTest(TestVisuals("test_unacceptable_input"))
        # suite.addTest(TestVisuals("test_input_combinations"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
