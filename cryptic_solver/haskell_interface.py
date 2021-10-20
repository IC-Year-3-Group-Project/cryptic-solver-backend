import requests
import urllib.parse

haskellURL = "http://84.238.224.41:5001"

"""

Arguments:

(String) clue
(int)    solutionLength

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

def hs_solve_clue(clue, solutionLength):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solve/{clue}/{solutionLength}"

    r = requests.get(url=fullURL)


    print(unlist(r.text))
    return r

def hs_solve_with_answer(clue, solutionLength, answer):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solveWithAnswer/{clue}/{solutionLength}/{answer}"

    r = requests.get(url=fullURL)

    return r

def hs_solve_with_pattern(clue, solutionLength, pattern):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solveAll/{clue}/{solutionLength}"

    r = requests.get(url=fullURL)

    return r

def hs_solve_with_cands(clue, word_length, candidates):
    clue = urllib.parse.quote(clue, safe='')

    cand_string = candidates.reduce(lambda a, b: a + "," + b)

    fullURL = f"{haskellURL}/solveWithAnswers/{clue}/{word_length}/{cand_string}"

    r = requests.get(url=fullURL)

    return r