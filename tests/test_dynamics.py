import unittest
from netpython import dynamics
import os

class TestEventBetweenness_plain(unittest.TestCase):
    
    def setUp(self):
        self.events = [(1, 1, 2),
                       (2, 1, 3),
                       (3, 2, 4),
                       (4, 3, 4),
                       (5, 4, 5),
                       (6, 5, 6)]
                
    def test_eventBetweenness(self):
        corr_result = {1:8, 2:7, 3:7, 4:10, 5:11, 6:6}
        for t, b in dynamics.eventBetweenness_plain(self.events):
            self.assertEqual(b, corr_result[t])

    def test_nodeBetweenness(self):
        nb = dict()
        nb_corr = {1:4, 2:4, 3:6, 4:12, 5:6, 6:0}
        list(dynamics.eventBetweenness_plain(self.events, nodeBetweenness=nb))
        self.assertEqual(nb, nb_corr)

    def test_nodeBetweenness_withPathEnds(self):
        nb = dict()
        nb_corr = {1:11, 2:11, 3:11, 4:16, 5:11, 6:6}
        list(dynamics.eventBetweenness_plain(self.events, nodeBetweenness=nb,
                                       include_path_ends=True))
        self.assertEqual(nb, nb_corr)


class TestEventBetweenness(unittest.TestCase):
    
    def setUp(self):
        self.events = [(1, 1, 2),
                       (2, 1, 3),
                       (3, 2, 4),
                       (4, 3, 4),
                       (5, 4, 5),
                       (6, 5, 6)]
                
    def test_eventBetweenness_delta1(self):
        """Test with delta = 1 (path length has no effect)"""
        corr_result = {1:19./16, 2:37./32, 3:43./32, 4:65./32, 5:2.0, 6:1.0}
        for b,t,i,j in dynamics.eventBetweenness(self.events, 1.0, 1.0):
            self.assertEqual(b, corr_result[t])

    def test_eventBetweenness_delta0(self):
        """Test with delta = 0, half_life = inf (only incident events
        have an effect)"""
        corr_result = {1:2, 2:3, 3:5, 4:4, 5:5, 6:1}
        for b,t,i,j in dynamics.eventBetweenness(self.events, 1000000000, 0.0):
            self.assertEqual(int(round(b)), corr_result[t])

if __name__ == '__main__':
    if True:
        # If true, run only the tests listed below, otherwise run all tests
        # (this option is for testing the tests :-) )
        suite = unittest.TestSuite()
        suite.addTest(TestEventBetweenness("test_eventBetweenness_delta0"))
        unittest.TextTestRunner().run(suite)
    else:
        # Run all tests.
        unittest.main()
