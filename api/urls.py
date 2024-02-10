from django.urls import path
from . import views

urlpatterns = [
    path('tournaments',views.Tournaments.as_view()),
    path('holes',views.Holes.as_view()),
    path('scores',views.Scores.as_view()),
]