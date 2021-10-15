from cryptic_solver.helper import *
import unittest

class MatchingTests(unittest.TestCase):
    def testOneSolution(self):
        pattern = {0: 'A', 2:'E', 4:'A'} #A_E_A__
        list = ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']

        self.assertEqual(matching(pattern, list), ['AVERAGE'])


    def testMoreSolutions(self):
        pattern = {0: 'B', 2:'B', 4:'E'} #B_B_E_
        list = ['BABBLE', 'BABIED', 'BABIES', 'BABOON']

        self.assertEqual(matching(pattern, list), ['BABIED', 'BABIES'])


class MakeListTests(unittest.TestCase):
    def testWithOneSolution(self):
        text = "[AVERAGE]"

        self.assertEqual(makeList(text), ["AVERAGE"])


    def testWithManySolutions(self):
        text = "['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']"

        self.assertEqual(makeList(text), ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY'])

if __name__ == '__main__':
    unittest.main()

# Create your tests here.
