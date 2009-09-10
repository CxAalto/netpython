import unittest
from netpython import communities

class TestCommunities(unittest.TestCase):
    
    def setUp(self):
        self.cmaps = []
        self.cmaps.append({0: [0,1,2,3], 1: [4,5,6,7]})
        #self.cmaps.append({0: [0,1,2,3], 1: [4,5], 2:[6,7]})
        #self.cmaps.append({0: [0,1,2], 1: [3,4], 2:[5,6,7]})
        self.cmaps.append({0: [0,1,2], 1: [1,3,4], 2:[0,5,6,7]})
        #self.cmaps.append(dict([(i,[i]) for i in range(8)]))
        #self.cmaps.append({0: range(8)})

        self.comms = [communities.NodeFamily(cmap=x) for x in self.cmaps]

    def tearDown(self):
        pass

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

if __name__ == '__main__':
    if False:
        # If true, run only the tests listed below, otherwise run all
        # tests (this option is for testing the tests :-) ).
        suite = unittest.TestSuite()
        suite.addTest(TestCommunities("test_getMaxVariationOfInformation_lessThanOne"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
