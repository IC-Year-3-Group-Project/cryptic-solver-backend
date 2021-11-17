import requests
import urllib.parse
from cryptic_solver_project import settings

haskellURL = settings.haskellURL


"""

Arguments:

(String) clue
(int)    word_length

(solve_with_answer)

(String) answer

(solve_with_pattern)

(dict)   pattern

(solve_with_cands)

(String) candidates - comma-separated candidate solutions based on known letters


Returns:

(HTTPResponse) r
    - the HTTP response from the Haskell server. This contains (as text)
      all the solutions returned by the Haskell solver.

"""

def hs_solve_clue(clue, word_length, explain=False):
    return call_haskell("", clue, word_length, explain=explain)

def hs_solve_and_explain_clue(clue, word_length, explain=True):
    return call_haskell("", clue, word_length, explain=explain)

def hs_solve_with_answer(clue, word_length, answer, explain=True):
    return call_haskell("WithAnswer", clue, word_length, answer=answer, explain=explain)


def hs_solve_with_pattern(clue, word_length, pattern):
    return call_haskell("All", clue, word_length)


def hs_solve_with_cands(clue, word_length, candidates):
    cand_string = candidates.reduce(lambda a, b: a + "," + b)

    return call_haskell("WithAnswers", clue, word_length, cand_string=cand_string)


def call_haskell(mode, clue, word_length, explain=False, answer="", cand_string=""):
    extra = "AndExplain" if explain else ""
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solve{mode}{extra}/{clue}/{word_length}/{answer}/{cand_string}"

    r = requests.get(url=fullURL)

    return r
