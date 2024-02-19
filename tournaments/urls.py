from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.Home.as_view(),name='homepage' ),
    path('<slug:tournament>/',views.TournamentView.as_view(),name='tournament'),
    path('<slug:tournament>/<slug:holiday>',views.RoundsView.as_view(),name='rounds'),
    path('<slug:tournament>/<slug:holiday>/<int:selected_round>',views.ScoresView.as_view(),name='scores'),
    path('<slug:tournament>/<slug:holiday>/<int:selected_round>/<int:hole>',views.EditScoresView.as_view(),name='edit_scores'),


]