import requests
import re
import html
import asyncio
from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
from cryptic_solver.unlikely_interface import *


async def get_and_format_unlikely(clue, pattern, letter_pattern=""):

    unlikely_solutions = []

    if letter_pattern == "":
        response = await uai_solve_clue(clue, pattern)
    else:
        response = await uai_solve_with_pattern(clue, pattern, letter_pattern)

    if response.status_code == 200:
        data = json.loads(response.text)
        unlikely_solutions = parse_unlikely_with_explanations(data)
        if not (letter_pattern == ""):
            unlikely_solutions = filter_by_pattern(unlikely_solutions, letter_pattern)

    return unlikely_solutions

async def get_and_format_haskell(clue, word_length, letter_pattern="", cands=[]):

    hs_solutions = []

    if len(cands) > 0:
        response = await hs_solve_with_cands(clue, word_length, cands)
    else:
        response = await hs_solve_and_explain_clue(clue, word_length)

    if response.status_code == 200:
        hs_solutions = format_haskell_answers(response.text)
        if not (letter_pattern == ""):
            hs_solutions = filter_by_pattern(hs_solutions, letter_pattern)

    return hs_solutions
