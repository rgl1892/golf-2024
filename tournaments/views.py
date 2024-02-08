from django.shortcuts import render
from .models import Tournament
from django.views.generic import View
from django.http import HttpResponse

# Create your views here.

class Home(View):
    model = Tournament
    template_name = 'tournaments/home.html'
    
    def get(self,request):
        data = self.model.objects.all()
        return render(request,self.template_name,{'data':data})
        
    
class Tournament(View):
    
    model = Tournament
    template_name = 'tournaments/tournament.html'
    
    def get(self,request,slug):
        data = model.objects
        return render(request,self.template_name,{'data':slug})