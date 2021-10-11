from django.urls import path
from cryptic_solver.views import * 

urlpatterns = [
    path('solve-clue', solve_clue)
]   