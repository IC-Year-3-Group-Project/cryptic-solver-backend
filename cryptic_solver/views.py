import json
from django.http import JsonResponse
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError

from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
from cryptic_solver.image_processing.image_recognition import recognize_image
from cryptic_solver.unlikely_interface import *
from cryptic_solver.async_calls import *
import requests
import re
import html
import asyncio
from bs4 import BeautifulSoup

from cryptic_solver.models import Puzzle

allowed_crossword_prefixes = [
    "https://www.theguardian.com/crosswords/everyman",
    "https://www.theguardian.com/crosswords/cryptic",
    "https://www.theguardian.com/crosswords/quiptic"]


def option_response():
    response = HttpResponse()
    response.status_code = 204
    response["Connection"] = "keep-alive"
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "OPTIONS, POST"
    response["Access-Control-Max-Age"] = 86400
    return response


"""
{
    (String) 'clue'
    (int)    'word_length'
}
"""


def solve_clue(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        response = hs_solve_clue(clue, word_length)

        solution = make_list(response.text)

        return JsonResponse(solution, safe=False)


def unlikely_solve_clue(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        # Get data from request
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        pattern = data["pattern"]
        response = uai_solve_clue_no_async(clue, pattern)

        if response.status_code == 200:
            data = json.loads(response.text)
            solutions = parse_unlikely_with_explanations(data)
            return JsonResponse(solutions, safe=False)
        else:
            response = hs_solve_clue(clue, word_length)
            solution = []
            if response.status_code == 200:
                solution = make_list(response.text)

            return JsonResponse(solution, safe=False)



async def solve_and_explain(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        # Get data from request
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        pattern = data["pattern"]
        use_hs = not ("-" in pattern or "," in pattern)

        # get the formatted responses from both solvers
        if use_hs:
            all_solutions = await gather_and_combine(get_and_format_unlikely(clue, pattern), get_and_format_haskell(clue, word_length))
        else:
            all_solutions = await get_and_format_unlikely(clue, pattern)

        return JsonResponse(all_solutions, safe=False)

"""
{
  "word_length": 8,
  "pattern": "O?LA??M?,
  "clue": " "
  "pattern": "(8)"
}
"""


async def solve_with_pattern_unlikely(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        # Get data from request
        data = json.loads(request.body)
        clue = data["clue"]
        pattern = data["pattern"]
        letter_pattern = data["letter_pattern"]

        unlikely_solutions = []
        text, status_code = await uai_solve_with_pattern(clue, pattern, letter_pattern)

        if status_code == 200:
            data = json.loads(text)
            unlikely_solutions = parse_unlikely_with_explanations(data)

        return JsonResponse(unlikely_solutions, safe=False)



"""
{
  "word_length": 8,
  "pattern": "O?LA??M?,
  "clue": " "
  "pattern": "(8)"
}
"""


async def solve_with_pattern(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        # Get data from request
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        pattern = data["pattern"]
        letter_pattern = data["letter_pattern"]
        use_hs = not ("-" in pattern or "," in pattern)

         # get the formatted responses from both solvers
        if use_hs:
            all_solutions = await gather_and_combine(get_and_format_unlikely(clue, pattern, letter_pattern=letter_pattern), get_and_format_haskell(clue, word_length, letter_pattern=letter_pattern))
        else:
            all_solutions = await get_and_format_unlikely(clue, pattern, letter_pattern=letter_pattern)

        return JsonResponse(all_solutions, safe=False)

"""
{
    (String) 'url'
}
"""


def fetch_crossword(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        data = json.loads(request.body)
        url: str = data["url"]

        if all(not url.startswith(prefix) for prefix in allowed_crossword_prefixes):
            return HttpResponseBadRequest("Invalid crossword url.")

        response = requests.get(url)
        match = re.search('data\-crossword\-data="(.*)"', response.text)
        if match:
            json_crossword = html.unescape(match.groups()[0])
            return HttpResponse(json_crossword, content_type="application/json")
        else:
            return HttpResponseServerError("Failed to fetch crossword data.")


"""
{
  "word_length": 8,
  "pattern": "O?LA??M?,
  "clue": " "
  "pattern": "(8)"
}
"""


async def solve_with_dict(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:
        # Get data from request
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        pattern = data["pattern"]
        letter_pattern = data["letter_pattern"]
        cands = get_candidates(letter_pattern, word_length)
        use_hs = len(cands) > 0 and (not ("-" in pattern or "," in pattern))

         # get the formatted responses from both solvers
        if use_hs:
            all_solutions = await gather_and_combine(get_and_format_unlikely(clue, pattern, letter_pattern=letter_pattern), get_and_format_haskell(clue, word_length, letter_pattern=letter_pattern, cands=cands))
        else:
            all_solutions = await get_and_format_unlikely(clue, pattern, letter_pattern=letter_pattern)


        return JsonResponse(all_solutions, safe=False)


def explain_answer(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:

        answer = json.loads(request.body)['answer']
        word_length = json.loads(request.body)['word_length']
        clue = json.loads(request.body)['clue']

        response = hs_solve_with_answer(
            clue, word_length, answer, explain=True)

        explanation = get_explanation(response.text)

        return JsonResponse(explanation, safe=False)


def fetch_everyman(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        url = "https://www.theguardian.com/crosswords/series/everyman"
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, "html.parser")

        # Use set to avoid returning duplicate links
        urls = set()
        #  Filter through for everyman crossword links
        for link in soup.find_all("a"):
            l = link.get("href")
            if (
                link.has_attr("href")
                and "https://www.theguardian.com/crosswords/everyman/" in l
            ):
                urls.add(l)

        return JsonResponse({"urls": list(urls)})


def process_puzzle(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        json_object = json.loads(request.body)

        # all images are sent over in base 64
        b64_grid_image = json_object['grid']
        b64_across_image = json_object['across']
        b64_down_image = json_object['down']

        # get json grid containing the structure + all clues
        grid = recognize_image(
            b64_grid_image, b64_across_image, b64_down_image, ocr="tesseract")

        # insert grid into database
        puzzle = Puzzle.objects.create(grid_json=grid)
        puzzle.save()

        return JsonResponse({"id": puzzle.id, "grid": grid})


def get_puzzle(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        json_object = json.loads(request.body)
        id = json_object['id']

        # return empty grid if we dont have the puzzle
        x = Puzzle.objects.filter(id=id)
        if (len(x) == 0):
            return JsonResponse({"grid": {}})
        return JsonResponse({"grid": x.get().grid_json})