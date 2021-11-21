from cryptic_solver.helper import *
import unittest

class DictTests(unittest.TestCase):
    def test_one(self):
        pattern = {"0": 'A', "2":'E', "4":'A'} #A_E_A__

        self.assertEqual(get_candidates(pattern, word_length=7), ['abeyant', 'acerata', 'acerate', 'acetals', 'acetary', 'acetars', 'acetate', 'adenase', 'agelast', 'agelaus', 'alegars', 'aleyard', 'alemana', 'ameland', 'amenage', 'amesace', 'anelace', 'apetaly', 'arecain', 'arefact', 'avenage', 'avenant', 'avenary', 'average', 'aweband', 'azelaic', 'azelate'])

    def test_two(self):
        pattern = {0: 'A', 2:'E', 4:'A'} #A_E_A__

        self.assertEqual(get_candidates(pattern, word_length=7), ['abeyant', 'acerata', 'acerate', 'acetals', 'acetary', 'acetars', 'acetate', 'adenase', 'agelast', 'agelaus', 'alegars', 'aleyard', 'alemana', 'ameland', 'amenage', 'amesace', 'anelace', 'apetaly', 'arecain', 'arefact', 'avenage', 'avenant', 'avenary', 'average', 'aweband', 'azelaic', 'azelate'])

class MatchingTests(unittest.TestCase):
    def test_one_solution(self):
        pattern = {0: 'A', 2:'E', 4:'A'} #A_E_A__
        list = ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']

        self.assertEqual(matching(pattern, list), ['AVERAGE'])


    def test_more_solutions(self):
        pattern = {0: 'B', 2:'B', 4:'E'} #B_B_E_
        list = ['BABBLE', 'BABIED', 'BABIES', 'BABOON']

        self.assertEqual(matching(pattern, list), ['BABIED', 'BABIES'])

class LoadWordsTests(unittest.TestCase):
    def test(self):
        dict = load_words()
        self.assertEqual(len(dict.search("___")), 2130)
        self.assertEqual(len(dict.search("____")), 7186)
        self.assertEqual(len(dict.search("_____")), 15918)

class TrieTests(unittest.TestCase):
    def test_one(self):
        trie = Trie()
        trie.add("average")
        self.assertEqual(trie.search("a______"), ["average"])

    def test_two(self):
        trie = Trie()
        trie.add("average")
        trie.add("averian")
        self.assertEqual(trie.search("a_____e"), ["average"])
        self.assertEqual(trie.search("aver___"), ["average", "averian"])


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
