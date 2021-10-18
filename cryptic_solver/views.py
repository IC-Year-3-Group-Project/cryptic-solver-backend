import json
from django.http import JsonResponse
from django.http import response
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
import requests
import re
import html

allowed_crossword_prefixes = ["https://www.theguardian.com/crosswords/everyman"]

def option_response():
    response = JsonResponse({})
    response.status_code = 204
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS, POST'
    response['Access-Control-Max-Age'] = 86400
    return response

"""
{
    (String) 'clue'
    (int)    'word_length'
}
"""

@csrf_exempt
def solve_clue(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data['clue']
        word_length = data['word_length']
        response = hs_solve_clue(clue, word_length)

        solution = makeList(response.text)

        #TODO: need to check what sort of data is actually required in the response
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
    if request.method == 'OPTIONS':
        return option_response()
    else:
        data = json.loads(request.body)
        clue = data['clue']
        word_length = data['word_length']
        pattern = data['pattern']

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
    if request.method == 'OPTIONS':
        return option_response()
    else:
        data = json.loads(request.body)
        url: str = data["url"]

        if all(not url.startswith(prefix) for prefix in allowed_crossword_prefixes):
            return HttpResponseBadRequest("Invalid crossword url.")

        response = requests.get(url)
        match = re.search("data\-crossword\-data=\"(.*)\"", response.text)
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



