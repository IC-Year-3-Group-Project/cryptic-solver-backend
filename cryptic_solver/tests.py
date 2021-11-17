from cryptic_solver.helper import *
import unittest

class MatchingTests(unittest.TestCase):
    def test_one_solution(self):
        pattern = {0: 'A', 2:'E', 4:'A'} #A_E_A__
        list = ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']

        self.assertEqual(matching(pattern, list), ['AVERAGE'])


    def test_more_solutions(self):
        pattern = {0: 'B', 2:'B', 4:'E'} #B_B_E_
        list = ['BABBLE', 'BABIED', 'BABIES', 'BABOON']

        self.assertEqual(matching(pattern, list), ['BABIED', 'BABIES'])


class MakeListTests(unittest.TestCase):
    def test_with_one_solution(self):
        text = "[AVERAGE]"

        self.assertEqual(make_list(text), ["AVERAGE"])


    def test_with_many_solutions(self):
        text = "['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']"

        self.assertEqual(make_list(text), ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY'])

if __name__ == '__main__':
    unittest.main()

# Create your tests here.
