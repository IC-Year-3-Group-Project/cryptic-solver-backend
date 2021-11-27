from django.urls import path
from cryptic_solver.views import *

urlpatterns = [
    path('solve-clue', solve_clue),
    path('unlikely-solve-clue', unlikely_solve_clue),
    path('solve-and-explain', solve_and_explain),
    path('solve-with-pattern', solve_with_pattern),
    path('solve-with-pattern-unlikely', solve_with_pattern_unlikely),
    path('fetch-crossword', fetch_crossword),
    path('solve-with-dict', solve_with_dict),
    path('fetch-everyman', fetch_everyman),
    path('explain_answer', explain_answer),
    path('process-puzzle', process_puzzle),
    path('get-puzzle', get_puzzle)
]
