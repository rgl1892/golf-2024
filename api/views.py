from django.shortcuts import render
from rest_framework import generics,permissions
from .serializers import *
from tournaments.models import *

# Create your views here.

class Tournaments(generics.ListAPIView):
    serializer_class = TournamentSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        return Tournament.objects.all()
    

class Holes(generics.ListAPIView):
    serializer_class = HoleSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        return Hole.objects.all()
    
class Scores(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = self.request.user
        return Score.objects.all()