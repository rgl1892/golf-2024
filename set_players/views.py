from django.shortcuts import render
from .models import Tournament

# Create your views here.
def home(request):
    tournaments = Tournament.objects.all()

    return render(request,'set_players/home.html',{'data':tournaments})