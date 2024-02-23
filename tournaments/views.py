from django.shortcuts import render
from .models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort
from django.views.generic import View
from django.http import HttpResponse
import math


# Create your views here.

class Home(View):

    """The Homepage"""

    model = Tournament
    template_name = 'tournaments/home.html'

    def get(self, request):
        tournaments = Tournament.objects.all()
        return render(request, self.template_name, {'tournaments': tournaments})


class TournamentView(View):

    """Lists all the holidays within a tournament"""

    template_name = 'tournaments/tournament.html'

    def get(self, request, tournament):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)

        return render(request, self.template_name, {'holidays': holidays, 'tournament': tournament, 'selected_tournament': selected_tournament})


class RoundsView(View):

    """Lists all the rounds from a holiday"""

    template_name = "tournaments/rounds.html"

    def get(self, request, tournament, holiday):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        selected_holiday = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament)
        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)
        rounds_id = rounds.values('id')
        resort = Resort.objects.filter(holiday=holiday_filter)
        courses = Course.objects.filter(resort=resort.get())
        print(courses)
        
        for round_id in rounds_id:
            scores = Score.objects.filter(golf_round=round_id['id'])
            # print(scores)

        
        context = {
            'holiday': holiday_filter,
            'rounds': rounds,
            'tournament': tournament,
            'courses':courses}

        return render(request, self.template_name, context)


class ScoresView(View):
    template_name = 'tournaments/scores.html'
    stableford_lookup = {
        '2': 0,
        '1': 1,
        '0': 2,
        '-1': 3,
        '-2': 4,
        '-3': 5,
        '-4': 6,
        '-5': 7,
        '-6': 8,
        '-7': 9
    }

    def get(self, request, tournament, holiday, selected_round):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament).get()
        selected_round = GolfRound.objects.filter(
            round_number=selected_round, holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=selected_round)
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()

        selected_course = Course.objects.filter(
            hole=scores.values()[0]['hole_id']).values()[0]
        slope_rating = selected_course['slope_rating']
        course_rating = selected_course['course_rating']

        handicaps = []
        for player in players:
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=scores.values()[0]['hole_id']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']
            playing_handicap = round(
                (slope_rating/113)*float(handicap_index)*0.95)
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']

            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score.strokes for score in scores.filter(player=player['player_id'])]),
                              sum([score.strokes - score.hole.par  for score in scores.filter(player=player['player_id'])]),
                              sum([score.stableford_score for score in scores.filter(player=player['player_id'])])
                ])

        hole_numbers = [x for x in range(1, 19)]
        player_scores = [scores.filter(
            player=players[x]['player_id']) for x in range(len(players))]

        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
            "players": players,
            "hole_numbers": hole_numbers,
            "player_scores": player_scores,
            "handicaps": handicaps
        }

        return render(request, self.template_name, context)

    def post(self, request, tournament, holiday, selected_round):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament).get()
        selected_round = GolfRound.objects.filter(
            round_number=selected_round, holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=selected_round)
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()
        hole_numbers = [x for x in range(1, 19)]
        player_scores = [scores.filter(
            player=players[x]['player_id']) for x in range(len(players))]
        course = Course.objects.filter(id=Hole.objects.filter(
            id=request.POST['hole']).values()[0]['course_id'])

        # Get data on the course to calculate stableford points
        slope_rating = course.values()[0]['slope_rating']
        course_rating = course.values()[0]['course_rating']
        hole_played = Hole.objects.filter(id=request.POST['hole']).values()[0]
        print(hole_played)
        handicaps = []

        for player in players:
            scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                strokes=request.POST[f"{player['player_id']}"])
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=request.POST['hole']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']

            playing_handicap = round(
                (slope_rating/113)*float(handicap_index)*0.95)

            take_off_score = math.floor(playing_handicap/18)
            si_change = playing_handicap % 18
            shots = scores.filter(player=player['player_id'], hole=request.POST['hole']).values(
                'strokes')[0]['strokes']
            stroke_index = hole_played['stroke_index']
            par = hole_played['par']

            if stroke_index <= si_change:
                si_take_off = 1
            else:
                si_take_off = 0
            final_shots = shots - take_off_score - si_take_off - par
            try:
                points = self.stableford_lookup[f'{final_shots}']
            except:
                points = 0

            scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                stableford_score=points)
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']

            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score.strokes for score in scores.filter(player=player['player_id'])]),
                              sum([score.strokes - score.hole.par  for score in scores.filter(player=player['player_id'])]),
                              sum([score.stableford_score for score in scores.filter(player=player['player_id'])])
                ])

        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
            "players": players,
            "hole_numbers": hole_numbers,
            "player_scores": player_scores,
            'handicaps': handicaps
        }
        return render(request, self.template_name, context)


class EditScoresView(View):
    template_name = 'tournaments/edit_scores.html'

    def get(self, request, tournament, holiday, selected_round, hole):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament).get()
        selected_round = GolfRound.objects.filter(
            round_number=selected_round, holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=selected_round)
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()

        hole_numbers = [x for x in range(1, 19)]
        player_scores = [scores.filter(
            player=players[x]['player_id']) for x in range(len(players))]
        selected_hole = Hole.objects.filter(id=hole)

        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
            "players": players,
            "hole_numbers": hole_numbers,
            "player_scores": player_scores,
            "hole": selected_hole,
        }

        return render(request, self.template_name, context)
