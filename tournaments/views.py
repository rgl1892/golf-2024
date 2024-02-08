from django.shortcuts import render
from .models import Tournament,Holiday
from django.views.generic import View
from django.http import HttpResponse

# Create your views here.

class Home(View):
    model = Tournament
    template_name = 'tournaments/home.html'
    
    def get(self,request):
        data = self.model.objects.all()
        return render(request,self.template_name,{'data':data})
        
    
class TournamentView(View):
    

    template_name = 'tournaments/tournament.html'
    
    def get(self,request,slug):
        selected_tournament = Tournament.objects.filter(slug=slug).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        
        return render(request,self.template_name,{'data':holidays,'slug':slug})
    
class RoundsView(View):
    
    template_name = "tournaments/rounds.html"
    
    def get(self,request,slug,id):
        selected_holiday = Holiday.objects.filter(id=id)
        return render(request,self.template_name)