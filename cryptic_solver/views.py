import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from cryptic_solver.helper import *
from cryptic_solver.haskell_interface import *
import requests


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
        responses = hs_solve_clue(clue, word_length)

        return JsonResponse(responses, safe=False)

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

        responses = hs_solve_with_pattern(clue, word_length, pattern)


        return JsonResponse(matching(pattern, responses), safe=False)





