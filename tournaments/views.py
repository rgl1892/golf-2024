from django.shortcuts import render
from .models import Tournament,Holiday,GolfRound,Score
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
    
    def get(self,request,tournament):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        
        return render(request,self.template_name,{'data':holidays,'tournament':tournament,'nest':{'layer':8}})
    
class RoundsView(View):
    
    template_name = "tournaments/rounds.html"
    
    def get(self,request,tournament,holiday):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        selected_holiday = Holiday.objects.filter(slug=holiday,tournament=selected_tournament)
        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)
        for row in rounds.values():
            score = Score.objects.filter(golf_round_id=row['round_number'])
            print(score)
        return render(request,self.template_name,{'holidays':selected_holiday,'rounds':rounds,'tournament':tournament})
    
class ScoresView(View):
    template_name = 'tournaments/scores.html'

    def get(self,request,slug,holiday,round):
        selected_tournament = Tournament.objects.filter(slug=slug).get()
        selected_holiday = Holiday.objects.filter(slug=holiday,tournament=selected_tournament)
        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)