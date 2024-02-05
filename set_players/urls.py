from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='set_players_home'),
]