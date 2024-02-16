from django.shortcuts import render
from .models import Tournament,Holiday,GolfRound,Score, Player
from django.views.generic import View
from django.http import HttpResponse
import pandas as pd


# Create your views here.

class Home(View):

    """The Homepage"""

    model = Tournament
    template_name = 'tournaments/home.html'
    
    def get(self,request):
        tournaments = Tournament.objects.all()
        return render(request,self.template_name,{'tournaments':tournaments})
        
    
class TournamentView(View):
    
    """Lists all the holidays within a tournament"""

    template_name = 'tournaments/tournament.html'
    
    def get(self,request,tournament):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        
        
        
        return render(request,self.template_name,{'holidays':holidays,'tournament':tournament,'nest':{'layer':8}})
    
class RoundsView(View):
    
    """Lists all the rounds from a holiday"""

    template_name = "tournaments/rounds.html"
    
    def get(self,request,tournament,holiday):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        selected_holiday = Holiday.objects.filter(slug=holiday,tournament=selected_tournament)
        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)
        
        return render(request,self.template_name,{'holiday':holiday_filter,'rounds':rounds,'tournament':tournament})
    
class ScoresView(View):
    template_name = 'tournaments/scores.html'

    def get(self,request,tournament,holiday,round):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(slug=holiday,tournament=selected_tournament).get()
        round = GolfRound.objects.filter(round_number=round,holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=round)
        players = scores.order_by('player__first_name').values('player_id').distinct()
        
        hole_numbers = [x for x in range(1,19)]
        player_scores = [scores.filter(player=players[x]['player_id']) for x in range(len(players))]
            
        context = {
            'holiday':holiday_filter,
            'round':round,
            'tournament':tournament,
            'scores':scores,
            "players":players,
            "hole_numbers": hole_numbers,
            "player_scores":player_scores
        }

        return render(request,self.template_name,context)

class EditScoresView(View):
    template_name = 'tournaments/edit_scores.html'

    def get(self,request,tournament,holiday,round,hole):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(slug=holiday,tournament=selected_tournament).get()
        round = GolfRound.objects.filter(round_number=round,holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=round)
        players = scores.order_by('player__first_name').values('player_id').distinct()
        
        hole_numbers = [x for x in range(1,19)]
        player_scores = [scores.filter(player=players[x]['player_id']) for x in range(len(players))]
            
        context = {
            'holiday':holiday_filter,
            'round':round,
            'tournament':tournament,
            'scores':scores,
            "players":players,
            "hole_numbers": hole_numbers,
            "player_scores":player_scores
        }

        return render(request,self.template_name,context)