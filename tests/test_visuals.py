import unittest
from operator import itemgetter
from netpython import visuals
from netpython import pynet
import Image
import pylab
from pylab import *
import sys,os

# This file contains tests for the visualization code.  Some very
# simple tests are created for starters, more to be added later.
#
# Visualizations are tricky to test automatically. The solution is to
# print out some .eps files that can be compared with earlier
# versions. If the new .eps files don't come out neat, something is
# broken in the code.
#
# The automatized tests can be used to make sure that the code can
# handle various input combinations, and that the correct exceptions
# are raised when input is erroneous.
# 
#   - June 23 2009  Riitta 
#
# Changes: 
# 

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
        
        self.labels={0: 'FirstNode', 1: 'SecondNode', 2: 'ThirdNode'}        
        self.folder=os.path.dirname(visuals.__file__)+'/tests/test_visuals_figures/current/'

    def test_missing_input(self):
        # TypeErrors should be raised if less than two input values
        self.assertRaises(TypeError, visuals.VisualizeNet, self.m)
        self.assertRaises(TypeError, visuals.VisualizeNet, self.xy)
        
        
    def test_unacceptable_input(self):
        # if input in wrong order: 
        # self.assertRaises(AttributeError, visuals.VisualizeNet, self.xy, self.m)
        self.assertRaises(TypeError, visuals.VisualizeNet, self.m, self.xy, edgeColorMap=self.wrongEdgeColorMapName) 
               
    def test_simplePlot1(self):
        """ Test that a very simple plot without any parameters can be created """
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy))
        f.print_eps(self.folder+'test_simplePlot1.eps',dpi=80.0)

    def test_input_combinations(self):
        """ Testing different combinations of inputs """
        
        # Equally sized nodes. Note: this test detects a bug that was fixed in version 1.4 
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy,equalsize=True,nodeSize=12))
        f.print_eps(self.folder+'test_equalsize.eps',dpi=80.0)
        # Labeling nodes by their indices. 
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy,uselabels='all'))
        f.print_eps(self.folder+'test_nodelabels1.eps',dpi=80.0)
        # Labeling nodes with given labels 
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy,labels=self.labels))
        f.print_eps(self.folder+'test_nodelabels2.eps',dpi=80.0)
        # Coloring selected nodes (node 1 should be green, node 2 dark red, node 3 white (default)) 
        f=FigureCanvasBase(visuals.VisualizeNet(self.m,self.xy,equalsize=True,nodeSize=12,nodeColors={0:(.6,.9,0),1:(.6,0,.5)}))
        f.print_eps(self.folder+'test_nodecolors1.eps',dpi=80.0)

        
class Test_visualizeNet(unittest.TestCase):
    
    def setUp(self):
        self.dirnet = pynet.Net()
        self.dirnet[0][1] = 1
        self.dirnet[0][2] = 1
        self.dirnet[0][3] = 1

        self.symmnet = pynet.SymmNet()
        self.symmnet[0][1] = 1
        self.symmnet[0][2] = 1
        self.symmnet[1][2] = 1

        self.folder = ("%s/tests/test_visuals_figures/current/" 
                       % (os.path.dirname(visuals.__file__),))

    def test_dirnet(self):
        fig = pylab.figure(figsize=(6,6/np.sqrt(2)))
        ax = fig.add_axes([0.2,0.2,0.2,0.2])
        coords = {0:(0,0),1:(2,0),2:(-2/np.sqrt(2),2/np.sqrt(2)),
                  3:(-2/np.sqrt(2),-2/np.sqrt(2))}
        visuals.visualizeNet(self.dirnet, axes=ax, frame=True,
                             coords=coords, margin=0.05,
                             defaultNodeColor='white',
                             defaultNodeEdgeColor='blue',
                             defaultEdgeColor='red',
                             defaultNodeSize=6,
                             defaultEdgeWidth=0.1,
                             defaultNodeEdgeWidth=0.4,
                             labelAllNodes=True,
                             defaultLabelPosition='in',
                             labelAllEdges=True)
        fig.savefig(self.folder + "test_dirnet.eps")

    def test_symmnet(self):
        fig = pylab.figure()
        ax = fig.add_subplot(111)
        visuals.visualizeNet(self.symmnet, axes=ax, frame=True,
                             defaultNodeColor='white',
                             defaultNodeEdgeColor='blue',
                             defaultEdgeColor='red',
                             defaultNodeSize=20,
                             defaultEdgeWidth=2,
                             defaultNodeEdgeWidth=2.0,
                             labelAllNodes=True,
                             defaultLabelPosition='in')
        fig.savefig(self.folder + "test_symmnet.eps")

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(Test_visualizeNet("test_dirnet"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
