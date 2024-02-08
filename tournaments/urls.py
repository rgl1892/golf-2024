from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.Home.as_view(),name='homepage' ),
    path('<slug:slug>/',views.Tournament.as_view(),name='tournament')

]