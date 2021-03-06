import requests
import urllib.parse

from requests.models import Response
from cryptic_solver_project import settings
from functools import reduce
import unicodedata as ud
import asyncio
import aiohttp

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
    return call_haskell_no_async("", clue, word_length, explain=explain)

async def hs_solve_and_explain_clue(clue, word_length, explain=True):
    return await call_haskell("", clue, word_length, explain=explain)

def hs_solve_and_explain_clue_no_async(clue, word_length, explain=True):
    return call_haskell_no_async("", clue, word_length, explain=explain)

def hs_solve_with_answer(clue, word_length, answer, explain=True):
    # Haskell solver likes lowercase
    answer = answer.lower()
    return call_haskell_no_async("WithAnswer", clue, word_length, answers=answer, explain=explain)


def hs_solve_with_pattern(clue, word_length, pattern):
    return call_haskell("All", clue, word_length)

async def hs_solve_with_cands(clue, word_length, candidates, explain=True):
    # Candidates cannot be empty list
    cand_string = ""
    if (len(candidates) == 1):
        cand_string = candidates[0]
    else:
        cand_string = reduce(lambda a, b: a + "," + b, candidates)

    return await call_haskell("WithAnswers", clue, word_length, explain=explain, answers=cand_string)


async def call_haskell(mode, clue, word_length, explain=False, answers=""):
    extra = "AndExplain" if explain else ""
    clue = ud.normalize('NFKD', clue)
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solve{mode}{extra}/{clue}/{word_length}/{answers}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=fullURL, timeout=25) as r:
                text = await r.text()
                return text, r.status
    except:
        r = Response()
        r.status_code = 408 #Timeout response
        return "", r.status_code


def call_haskell_no_async(mode, clue, word_length, explain=False, answers=""):
    extra = "AndExplain" if explain else ""
    clue = ud.normalize('NFKD', clue)
    clue = urllib.parse.quote(clue, safe='')

    fullURL = f"{haskellURL}/solve{mode}{extra}/{clue}/{word_length}/{answers}"

    try:
        r = requests.get(url=fullURL, timeout=25)
        return r
    except:
        r = Response()
        r.status_code = 408 #Timeout response
        return r
    return r