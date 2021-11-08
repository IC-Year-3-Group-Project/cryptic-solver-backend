import json
from django.http import JsonResponse
from django.http import response
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError


from django.views.decorators.csrf import csrf_exempt
from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
from cryptic_solver.unlikely_interface import *
import requests
import re
import html

from bs4 import BeautifulSoup

allowed_crossword_prefixes = ["https://www.theguardian.com/crosswords/everyman"]


def option_response():
    response = JsonResponse({})
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


@csrf_exempt
def solve_clue(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        response = hs_solve_clue(clue, word_length)

        solution = makeList(response.text)

        return JsonResponse(solution, safe=False)


@csrf_exempt
def unlikely_solve_clue(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        solution_pattern = format_word_length(word_length)
        response = unlikely_solve_clue(clue, solution_pattern)

        if response.status_code == 200:
            solutions = response["candidate-list"]
            solution = get_most_confident(solutions)
            return JsonResponse(makeList(solution), safe=False)
        else:
            response = hs_solve_clue(clue, word_length)

            solution = makeList(response.text)

            return JsonResponse(solution, safe=False)






"""
{
    (String) 'clue'
    (int)    'word_length'
    (dict)   'pattern' e.g (index 3 -> 'e', index 5 -> 'a')  == ___E_A
}
"""


@csrf_exempt
def solve_with_pattern(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data["clue"]
        word_length = data["word_length"]
        pattern = data["pattern"]

        response = hs_solve_with_pattern(clue, word_length, pattern)

        solutions = makeList(response.text)

        return JsonResponse(matching(pattern, solutions), safe=False)


"""
{
    (String) 'url'
}
"""


@csrf_exempt
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
  "word_length": 7,
  "pattern": {"0": "a", "1": "v"},
  "clue": " "
}
"""

@csrf_exempt
def solve_with_dict(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:

        pattern = json.loads(request.body)['pattern']
        word_length = json.loads(request.body)['word_length']
        clue = json.loads(request.body)['clue']

        cands = getCandidates(pattern, word_length)

        response = hs_solve_with_cands(clue, cands)

        solutions = makeList(response.text)

        return JsonResponse(solutions, safe=False)

@csrf_exempt
def explain_answer(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:

        answer = json.loads(request.body)['answer']
        word_length = json.loads(request.body)['word_length']
        clue = json.loads(request.body)['clue']

        response = hs_solve_with_answer(clue, word_length, answer, explain=True)

        explanation = getExplanation(response.text)

        return JsonResponse(explanation, safe=False)

@csrf_exempt
def fetch_everyman(request):
    if request.method == "OPTIONS":
        return option_response()
    else:
        url = "https://www.theguardian.com/crosswords/series/everyman"
        reqs = requests.get(url)
        soup = BeautifulSoup(reqs.text, "html.parser")

        # Use set to avoid returning duplicate links
        urls = set()
        #  Filter throuhg for everyman crossword links
        for link in soup.find_all("a"):
            l = link.get("href")
            if (
                link.has_attr("href")
                and "https://www.theguardian.com/crosswords/everyman/" in l
            ):
                urls.add(l)

        print(urls)
        return JsonResponse({"urls": list(urls)})

