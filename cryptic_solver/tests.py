from cryptic_solver.helper import *
from cryptic_solver import views
from cryptic_solver import async_calls
from cryptic_solver import haskell_interface
import unittest
from mock import patch, MagicMock, Mock
from unittest import mock
from syncer import sync
import asyncio

class DictTests(unittest.TestCase):
    def test_one(self):
        pattern = "A_E_A__" #{"0": 'A', "2":'E', "4":'A'}

        self.assertEqual(get_candidates(pattern, word_length=7), ['abeyant', 'acerata', 'acerate', 'acetals', 'acetary', 'acetars', 'acetate', 'adenase', 'agelast', 'agelaus', 'alegars', 'aleyard', 'alemana', 'ameland', 'amenage', 'amesace', 'anelace', 'apetaly', 'arecain', 'arefact', 'avenage', 'avenant', 'avenary', 'average', 'aweband', 'azelaic', 'azelate'])

    def test_two(self):
        pattern = "A_E_A__" #{0: 'A', 2:'E', 4:'A'}

        self.assertEqual(get_candidates(pattern, word_length=7), ['abeyant', 'acerata', 'acerate', 'acetals', 'acetary', 'acetars', 'acetate', 'adenase', 'agelast', 'agelaus', 'alegars', 'aleyard', 'alemana', 'ameland', 'amenage', 'amesace', 'anelace', 'apetaly', 'arecain', 'arefact', 'avenage', 'avenant', 'avenary', 'average', 'aweband', 'azelaic', 'azelate'])

class MatchingTests(unittest.TestCase):
    def test_one_solution(self):
        pattern = "A_E_A__" #{0: 'A', 2:'E', 4:'A'}
        list = ['AVERAGE', 'ACADEMY', 'ADDRESS', 'ACCUSED', 'ABILITY']

        self.assertEqual(matching(pattern, list), ['AVERAGE'])


    def test_more_solutions(self):
        pattern = "B_B_E_" #{0: 'B', 2:'B', 4:'E'}
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

class ConvertFromUnicodeTests(unittest.TestCase):
    def test_with_non_ascii_characters(self):
        text = 'ihs\\257n'
        self.assertEqual(convert_from_unicode(text), 'ihsān')

    def test_without_non_ascii_characters(self):
        text = "no non-ascii characters here"
        self.assertEqual(convert_from_unicode(text), text)

class EndpointTests(unittest.TestCase):

    def set_up(self):
        self.one_word_request = Mock()
        self.one_word_request.method = "TEST"
        self.one_word_request.body = '{"clue" : "test clue", "word_length" : 10, "pattern" : "(10)", "letter_pattern" : "A_B_C_D_E_", "answer" : "banananana"}'

        self.multi_word_request = Mock()
        self.multi_word_request.method = "TEST"
        self.multi_word_request.body = '{"clue" : "test clue", "word_length" : 10, "pattern" : "(4,6)", "letter_pattern" : "A_B_C_D_E_", "answer" : "bana nanana"}'

        self.hs_response = Mock()
        self.hs_response.text = "['banananana']"

        self.hs_response_explain = Mock(name="hs_response_explain")
        self.hs_response_explain.text = "['banananana: nanana -> BATMAN!']"

        self.hs_solutions = [{"answer" : "banananana", "confidence" : 1.0, "explanation" : "nanana -> BATMAN!"}]


        self.uai_response = Mock()
        self.uai_response.text = '{"screen-list" : [{"candidate-list" : [{"candidate" : "banananana", "confidence" : 1.0, "explanation" : "nanana BATMAN!"}]}]}'



        views.hs_solve_and_explain_clue = mock.AsyncMock(return_value=[self.hs_response_explain.text, 200], name="views")
        views.hs_solve_with_answer = MagicMock(return_value=self.hs_response_explain)
        views.hs_solve_clue = MagicMock(return_value=self.hs_response)

        async_calls.hs_solve_and_explain_clue = mock.AsyncMock(return_value=[self.hs_response_explain.text, 200], name="async_calls_hs")
        async_calls.hs_solve_with_cands = mock.AsyncMock(return_value=[self.hs_response_explain.text, 200], name="async_calls_hs_cands")

        async_calls.uai_solve_clue = mock.AsyncMock(return_value=[self.uai_response.text, 200], name="async_calls_uai")
        async_calls.uai_solve_with_pattern = mock.AsyncMock(return_value=[self.uai_response.text, 200], name="async_calls_uai_pattern")

        views.uai_solve_clue_no_async = MagicMock(return_value=self.uai_response)

        haskell_interface.hs_solve_and_explain_clue = mock.AsyncMock(return_value=[self.hs_response_explain.text, 200], name="hs_interface")

    def test_solve_clue(self):
        self.set_up()
        solution = views.solve_clue(self.one_word_request)
        views.hs_solve_clue.assert_called_once_with('test clue', 10)

    def test_unlikely_solve_clue(self):
        self.set_up()
        views.unlikely_solve_clue(self.one_word_request)
        views.uai_solve_clue_no_async.assert_called_with('test clue', "(10)")
        views.unlikely_solve_clue(self.multi_word_request)
        views.uai_solve_clue_no_async.assert_called_with('test clue', "(4,6)")


    @sync
    async def test_get_and_format_haskell(self):
        self.set_up()
        await async_calls.get_and_format_haskell('test clue', 10)
        async_calls.hs_solve_and_explain_clue.assert_called_with('test clue', 10)

    @sync
    async def test_get_and_format_unlikely(self):
        self.set_up()
        await async_calls.get_and_format_unlikely('test clue', '(10)')
        async_calls.uai_solve_clue.assert_called_with('test clue', '(10)')

    @sync
    async def test_no_get_and_format(self):
        self.set_up()
        await haskell_interface.hs_solve_and_explain_clue('test clue', 10)
        haskell_interface.hs_solve_and_explain_clue.assert_called_with('test clue', 10)


    def test_solve_and_explain_one_word(self):
        self.set_up()
        views.solve_and_explain(self.one_word_request)
        async_calls.hs_solve_and_explain_clue.assert_called_with('test clue', 10)
        async_calls.uai_solve_clue.assert_called_with('test clue', '(10)')


    def test_solve_and_explain_multi_word(self):
        self.set_up()
        views.solve_and_explain(self.multi_word_request)
        async_calls.uai_solve_clue.assert_called_with('test clue', "(4,6)")
        async_calls.hs_solve_and_explain_clue.assert_not_called()


    def test_solve_with_pattern_one_word(self):
        self.set_up()
        views.solve_with_pattern(self.one_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(10)", "A_B_C_D_E_")
        async_calls.hs_solve_and_explain_clue.assert_called_with('test clue', 10)

    def test_solve_with_pattern_multi_word(self):
        self.set_up()
        views.solve_with_pattern(self.multi_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(4,6)", "A_B_C_D_E_")
        async_calls.hs_solve_and_explain_clue.assert_not_called()


    def test_solve_with_pattern_unlikely(self):
        self.set_up()
        views.solve_with_pattern(self.one_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(10)", "A_B_C_D_E_")
        views.solve_with_pattern(self.multi_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(4,6)", "A_B_C_D_E_")


    def test_solve_with_dict_one_word(self):
        self.set_up()
        views.get_candidates = MagicMock(return_value=["banananana"])
        views.solve_with_dict(self.one_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(10)", "A_B_C_D_E_")
        async_calls.hs_solve_with_cands.assert_called_with('test clue', 10, ["banananana"])

    def test_solve_with_dict_one_word_no_cands(self):
        self.set_up()
        views.get_candidates = MagicMock(return_value=[])
        views.solve_with_dict(self.one_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(10)", "A_B_C_D_E_")
        async_calls.hs_solve_with_cands.assert_not_called()

    def test_solve_with_dict_multi_word(self):
        self.set_up()
        views.get_candidates = MagicMock(return_value=["banananana"])
        views.solve_with_dict(self.multi_word_request)
        async_calls.uai_solve_with_pattern.assert_called_with('test clue', "(4,6)", "A_B_C_D_E_")
        async_calls.hs_solve_with_cands.assert_not_called()

    def test_explain_answer(self):
        self.set_up()
        views.explain_answer(self.one_word_request)
        views.hs_solve_with_answer.assert_called_with('test clue', 10, "banananana", explain=True)


    def test_what_is_happening(self):
        self.one_word_request = Mock()
        self.one_word_request.method = "TEST"
        self.one_word_request.body = '{"clue" : "Peeling paint, profit slack, upset, in a state", "word_length" : 10, "pattern" : "(10)", "letter_pattern" : "C_L_F_R_I_", "answer" : "california"}'

        r = views.solve_and_explain(self.one_word_request)





if __name__ == '__main__':
    unittest.main()

# Create your tests here.
