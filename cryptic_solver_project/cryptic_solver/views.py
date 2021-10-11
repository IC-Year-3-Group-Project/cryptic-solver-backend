import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

def option_response():
    response = JsonResponse({})
    response.status_code = 204
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'OPTIONS, POST'
    response['Access-Control-Max-Age'] = 86400
    return response

@csrf_exempt
def solve_clue(request):
    if request.method == 'OPTIONS':
        return option_response()
    else:
        responses = requests.post("endpoint", data = request)

        return JsonResponse(responses, safe=False)
