import requests
import urllib.parse

haskellURL = "http://84.238.224.41:5001"

# calls out to the Haskell server and returns
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

    print(unlist(r.text))
    return r

def hs_solve_with_pattern(clue, solutionLength, pattern):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solveAll/{clue}/{solutionLength}"

    r = requests.get(url=fullURL)

    print(unlist(r.text))
    return r


def unlist(response):
    return response[2:-2]

if __name__ == "__main__":
    hs_solve_clue("Peeling paint, profit slack, upset, in a state", 10)
    hs_solve_clue("Following kick-off, running back for corner", 4)
    hs_solve_with_answer("Peeling paint, profit slack, upset, in a state", 10, "california")
