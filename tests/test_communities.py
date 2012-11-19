import unittest
from netpython import communities
from netpython import pynet

class TestNodeCover(unittest.TestCase):
    
    def setUp(self):
        self.cmaps = []
        self.cmaps.append({0: [0,1,2,3], 1: [4,5,6,7]})
        self.cmaps.append({0: [0,1,2,3], 1: [4,5], 2:[6,7]})
        self.cmaps.append({0: [0,1,2], 1: [3,4], 2:[5,6,7]})
        self.cmaps.append({0: [0,1,2], 1: [1,3,4], 2:[0,5,6,7]})
        self.cmaps.append(dict([(i,[i]) for i in range(8)]))
        self.cmaps.append({0: range(8)})

        self.comms = [communities.NodeCover(cmap=x) for x in self.cmaps]

    def tearDown(self):
        pass

    def test_serializing(self):
        """Test that the string representation is valid and 
        internally consistent."""
        commStr=str(self.comms[0])
        self.assert_(commStr=="0 1 2 3\n4 5 6 7")
        self.assertEqual(commStr,str(communities.NodeCover(inputStr=commStr)))
        self.assertEqual(commStr,str(communities.NodeCover(inputFile=commStr.split("\n"))))

        comms2=communities.NodeCover(inputStr=commStr)
        comms2.nodeSeparator=","
        comms2.communitySeparator=" "
        commStr2=str(comms2)
        self.assertEqual(commStr2,str(communities.NodeCover(inputStr=commStr2,nodeSeparator=",",communitySeparator=" ")))
    

    def test_getMaxVariationOfInformation_selfmatch(self):
        """A community structure must always match itself."""
        for c in self.comms:
            self.assertEqual(c.getMaxVariationOfInformation(c), 1)

    def test_getMaxVariationOfInformation_symmetry(self):
        """Variation of information must be symmetric."""
        for i, ci in enumerate(self.comms):
            for j, cj in enumerate(self.comms[i+1:]):
                self.assertEqual("%.10f" % ci.getMaxVariationOfInformation(cj),
                                 "%.10f" % cj.getMaxVariationOfInformation(ci))

    def test_getMaxVariationOfInformation_compare(self):
        """Both methods of calculation should give the same results."""
        for i, ci in enumerate(self.comms):
            j = i + 1
            for cj in self.comms[i+1:]:
                self.assertEqual("%.10f" % ci.getMaxVariationOfInformation(cj),
                                 "%.10f" % ci.getMaxVariationOfInformation_slow(cj))
                # DEBUG
                #print i, self.cmaps[i]
                #print j, self.cmaps[j]
                #print ("   %.30f" % ci.getMaxVariationOfInformation(cj),
                #       "   %.30f" % ci.getMaxVariationOfInformation_slow(cj))
                j += 1

    def test_getMaxVariationOfInformation_lessThanOne(self):
        """The value must be less than 1 when communities differ."""
        for i, ci in enumerate(self.comms):
            j = i+1
            for cj in self.comms[i+1:]:
                ij_val = ci.getMaxVariationOfInformation(cj)
                self.assert_(ij_val < 1)
                # DEBUG
                #print (i, j, ij_val, ci.getMutualInformation(cj),
                #       ci.getNormalizedMutualInformation(cj))
                j += 1

class TestNodePartition(unittest.TestCase):
    
    def setUp(self):
        self.cmaps = []
        self.cmaps.append({0: [0,1,2,3], 1: [4,5,6,7]})
        self.cmaps.append({0: [0,1,2,3], 1: [4,5], 2:[6,7]})
        self.cmaps.append({0: [0,1,2], 1: [3,4], 2:[5,6,7]})
        self.cmaps.append(dict([(i,[i]) for i in range(8)]))
        self.cmaps.append({0: range(8)})

        self.comms = [communities.NodePartition(cmap=x) for x in self.cmaps]

    def tearDown(self):
        pass

    def test_getMutualInformation_selfmatch(self):
        """Mutual information with self is entropy."""
        for c in self.comms:
            self.assertEqual(c.getMutualInformation(c), c.entropy)

    def test_getMutualInformation_symmetry(self):
        """Mutual information must be symmetric."""
        for i, ci in enumerate(self.comms):
            j = i+1
            for cj in self.comms[i+1:]:
                self.assertEqual(ci.getMutualInformation(cj), 
                                 cj.getMutualInformation(ci))
                #print i, j, ci.getMutualInformation(cj) # DEBUG
                j += 1

    def test_getMutualInformation_compare(self):
        """Two different ways of calculating mutual information must match."""
        for i, ci in enumerate(self.comms):
            for cj in self.comms[i+1:]:
                self.assertEqual(ci.getMutualInformation(cj), 
                                 ci.getMutualInformation_slow(cj))

    def test_getMImetric(self):
        """Make sure the metric is really metric."""
        for i, ci in enumerate(self.comms):
            for cj in self.comms[i+1:]:
                self.assertEqual(ci.getMutualInformation(cj), 
                                 ci.getMutualInformation_slow(cj))

    def test_modularity(self):
        net = pynet.SymmNet()
        np = self.comms[0]
        for c in np.comm:
            c = list(c)
            for n_i,i in enumerate(c):
                for j in c[n_i+1:]:
                    net[i][j] = 1
        net[3][4] = 1
        m2 = 2.0*(6+6+1)
        correct_modularity = (6*(1-3*3/m2) + 6*(1-3*4/m2))/m2
        self.assertEqual(np.modularity(net), correct_modularity)
                

if __name__ == '__main__':
    if False:
        # If true, run only the tests listed below, otherwise run all
        # tests (this option is for testing the tests :-) ).
        suite = unittest.TestSuite()
        suite.addTest(TestNodePartition("test_modularity"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
