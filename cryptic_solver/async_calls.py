import requests
import re
import html
import asyncio
from typing import Any, Awaitable, List, TypeVar
from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
from cryptic_solver.unlikely_interface import *


async def get_and_format_unlikely(clue, pattern, letter_pattern=""):

    unlikely_solutions = []

    if letter_pattern == "":
        text, status = await uai_solve_clue(clue, pattern)
    else:
        text, status = await uai_solve_with_pattern(clue, pattern, letter_pattern)

    if status == 200:
        data = json.loads(text)
        unlikely_solutions = parse_unlikely_with_explanations(data)
        if not (letter_pattern == ""):
            unlikely_solutions = filter_by_pattern(unlikely_solutions, letter_pattern)

    return unlikely_solutions

async def get_and_format_haskell(clue, word_length, letter_pattern="", cands=[]):

    hs_solutions = []

    if len(cands) > 0:
        text, status = await hs_solve_with_cands(clue, word_length, cands)
    else:
        text, status = await hs_solve_and_explain_clue(clue, word_length)

    if status == 200:
        hs_solutions = format_haskell_answers(text)
        if not (letter_pattern == ""):
            hs_solutions = filter_by_pattern(hs_solutions, letter_pattern)

    return hs_solutions

# Sequentially awaits multiple started tasks.
def gather_tasks(*tasks: Awaitable) -> List:
    return asyncio.gather(*tasks)

# Combines solver solutions as a list of lists of solutions.
def combine_solver_solutions(solutions: List[List]) -> List:
    return combine_solutions(solutions[0], solutions[1]) if len(solutions) == 2 else solutions[0] if len(solutions) == 1 else []

# Calls combine_solver_solutions and gather_tasks on solver calls.
async def gather_and_combine(*args: Awaitable[List]) -> List:
    return combine_solver_solutions(await gather_tasks(*args))