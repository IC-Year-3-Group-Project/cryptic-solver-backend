import requests
import urllib.parse
from cryptic_solver_project import settings

unlikelyURL = settings.unlikelyURL



"""

Arguments:

(String) clue
(String) solution_pattern
(String) letter_pattern

Returns:

(HTTPResponse) r
    - the HTTP response from Unlikely AI. This contains all possible solutions
      along with explanations.

"""

def uai_solve_clue(clue, solution_pattern):
    return call_unlikely(clue, solution_pattern)


def uai_solve_with_pattern(clue, solution_pattern, letter_pattern):
    return call_unlikely(clue, solution_pattern, letter_pattern=letter_pattern)


def call_unlikely(clue, solution_pattern, letter_pattern=""):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{unlikelyURL}&clue={clue} {solution_pattern}&cluetype=1"
    if letter_pattern != "":
        fullURL += f"&letterpattern={letter_pattern}"

    r = requests.get(url=fullURL)

    return r

if __name__ == "__main__":
    clue = "Peeling paint, profit slack, upset, in a state"
    solution_pattern = "(10)"
    r = unlikely_solve_clue(clue, solution_pattern)

    print(r.text)
