import requests
import urllib.parse

from requests.models import Response
from cryptic_solver_project import settings
import asyncio

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

async def uai_solve_clue(clue, solution_pattern):
    return await call_unlikely(clue, solution_pattern)

def uai_solve_clue_no_async(clue, solution_pattern):
    return call_unlikely_no_async(clue, solution_pattern)


async def uai_solve_with_pattern(clue, solution_pattern, letter_pattern):
    return await call_unlikely(clue, solution_pattern, letter_pattern=letter_pattern)


async def call_unlikely(clue, solution_pattern, letter_pattern=""):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{unlikelyURL}&clue={clue} {solution_pattern}&cluetype=1"
    if letter_pattern != "":
        fullURL += f"&letterpattern={letter_pattern}"

    try:
        r = requests.get(url=fullURL, timeout=25)
        return r
    except:
        r = Response()
        r.status_code = 408 #Timeout response
        return r

def call_unlikely_no_async(clue, solution_pattern, letter_pattern=""):
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{unlikelyURL}&clue={clue} {solution_pattern}&cluetype=1"
    if letter_pattern != "":
        fullURL += f"&letterpattern={letter_pattern}"

    try:
        r = requests.get(url=fullURL, timeout=25)
        return r
    except:
        r = Response()
        r.status_code = 408 #Timeout response
        return r