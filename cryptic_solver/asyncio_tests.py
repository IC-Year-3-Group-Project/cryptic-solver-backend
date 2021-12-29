import asyncio
import time
import json
from cryptic_solver.unlikely_interface import *
from cryptic_solver.haskell_interface import *
from cryptic_solver.helper import *
from cryptic_solver.async_calls import *


def no_async_test(clue, word_length, pattern):

    unlikely_solutions = []
    hs_solutions = []

    # Gather solutions from Unlikely solver
    unlikely_response = uai_solve_clue_no_async(clue, pattern)

    # Haskell solver only handles one word answers
    if not ("-" in pattern or "," in pattern):
        # Gather solutions from Haskell solver
        hs_response = hs_solve_and_explain_clue_no_async(clue, word_length)
        if hs_response.status_code == 200:
            hs_solutions = format_haskell_answers(hs_response.text)

    if unlikely_response.status_code == 200:
        data = json.loads(unlikely_response.text)
        unlikely_solutions = parse_unlikely_with_explanations(data)

    all_solutions = combine_solutions(hs_solutions, unlikely_solutions)

    return all_solutions

def async_test(clue, word_length, pattern):
    loop = asyncio.get_event_loop()

    unlikely_solutions = []
    hs_solutions = []

    # Gather solutions from Unlikely solver
    uai_call = asyncio.gather(uai_solve_clue(clue, pattern))

    calls = asyncio.gather(uai_call)

    if not ("-" in pattern or "," in pattern):
        # Gather solutions from Haskell solver
        hs_call = asyncio.gather(hs_solve_and_explain_clue(clue, word_length))
        calls = asyncio.gather(uai_call, hs_call)

    responses = loop.run_until_complete(calls)

    for i, response in enumerate(responses):
        text, status = response[0]
        if status == 200:
            data = json.loads(text)
            if "screen-list" in data:
                unlikely_solutions = parse_unlikely_with_explanations(data)
            else:
                hs_solutions = format_haskell_answers(text)

    solutions = combine_solutions(unlikely_solutions, hs_solutions)
    return solutions

def new_async_test(clue, word_length, pattern):
    loop = asyncio.get_event_loop()

    # Gather solutions from Unlikely solver
    uai_call = asyncio.gather(get_and_format_unlikely(clue, pattern))
    calls = asyncio.gather(uai_call)

    # Haskell solver only handles one word answers
    if not ("-" in pattern or "," in pattern):
        # Gather solutions from Haskell solver
        hs_call = asyncio.gather(get_and_format_haskell(clue, word_length))
        calls = asyncio.gather(uai_call, hs_call)

    # await responses from both solvers
    solutions = loop.run_until_complete(calls)

    if len(solutions) == 2:
        all_solutions = combine_solutions(solutions[0][0], solutions[1][0])
    else:
        all_solutions = solutions[0][0]

    return all_solutions



def with_async_stats(n):
    clue = "peeling paint, profit slack, upset, in a state"
    word_length = 10
    pattern = "(10)"

    max_time = -1
    min_time = 10000
    total = 0
    times = []

    for i in range(n):
        start = time.time()
        with_async = async_test(clue, word_length, pattern)
        async_time = time.time() - start
        if async_time > max_time:
            max_time = async_time
        elif async_time < min_time:
            min_time = async_time
        total += async_time
        times.append(async_time)

    print(f"old async done {n} times")
    times.sort()

    average = float(total) / float(n)
    if n % 2 == 0:
        median = (times[int(n/2) - 1] + times[int(n/2)]) / 2
    else:
        median = times[(n - 1)/2]

    print(f"minimum time for old async: {min_time}")
    print(f"maximum time for old async: {max_time}")
    print(f"mean time for old async: {average}")
    print(f"median time for old async: {median}")
    return min_time, max_time, average, median



def new_async_stats(n):
    clue = "peeling paint, profit slack, upset, in a state"
    word_length = 10
    pattern = "(10)"

    max_time = -1
    min_time = 10000
    total = 0
    times = []

    for i in range(n):
        start = time.time()
        new_async = new_async_test(clue, word_length, pattern)
        async_time = time.time() - start
        if async_time > max_time:
            max_time = async_time
        elif async_time < min_time:
            min_time = async_time
        total += async_time
        times.append(async_time)

    print(f"new async done {n} times")
    times.sort()

    average = float(total) / float(n)
    if n % 2 == 0:
        median = (times[int(n/2) - 1] + times[int(n/2)]) / 2
    else:
        median = times[(n - 1)/2]
    print(f"minimum time for new async: {min_time}")
    print(f"maximum time for new async: {max_time}")
    print(f"mean time for new async: {average}")
    print(f"median time for new async: {median}")
    return min_time, max_time, average, median


def no_async_stats(n):
    clue = "peeling paint, profit slack, upset, in a state"
    word_length = 10
    pattern = "(10)"

    max_time = -1
    min_time = 10000
    total = 0
    times = []

    for i in range(n):
        start = time.time()
        n_async = no_async_test(clue, word_length, pattern)
        async_time = time.time() - start
        if async_time > max_time:
            max_time = async_time
        elif async_time < min_time:
            min_time = async_time
        total += async_time
        times.append(async_time)

    print(f"no async done {n} times")
    times.sort()


    average = float(total) / float(n)
    if n % 2 == 0:
        n = int(n/2)
        median = (times[n - 1] + times[n]) / 2
    else:
        median = times[int((n - 1)/2)]
    print(f"minimum time for no async: {min_time}")
    print(f"maximum time for no async: {max_time}")
    print(f"mean time for no async: {average}")
    print(f"median time for no async: {median}")
    return min_time, max_time, average, median