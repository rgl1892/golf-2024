from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.Home.as_view(),name='homepage' ),
    path('<slug:slug>/',views.TournamentView.as_view(),name='tournament'),
    path('<slug:slug>/<slug:holiday>',views.RoundsView.as_view(),name='rounds'),

]