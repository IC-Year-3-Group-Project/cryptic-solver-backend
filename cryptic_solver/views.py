import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from helper import *
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
        responses = requests.post("endpoint", data = request)

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
        responses = requests.post("endpoint", data = request)
        pattern = json.loads(request.body)['pattern']

        return JsonResponse(matching(pattern, responses), safe=False)



            

