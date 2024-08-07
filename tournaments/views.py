from django.shortcuts import render, redirect
from .models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video,ProTip,CarouselImage
from django.views.generic import View
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import permission_required
from .forms import UploadFileForm,EditAuthForm,EditUserForm
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files import File as DjangoFile

from PIL import Image
import math
import numpy as np
import requests
import cv2


class TemplateView(View):
    template_name = 'tournaments/template.html'

    def get(self,request):

        context = {
            'test':'result'
        }
        return render(request,self.template_name,context)

# Create your views here.
def getWeather(lat,long):
    weather_codes = {'0':'Clear sky','1':'Mainly Clear ☀️','2':'Partly Cloudy','3':'Overcast','45':'Fog','48':'Depositing Rime Fog',
                     '51':'Light Drizzle','53':'Moderate Drizzle','55':'Dense Drizzle','56':'Light Freezing Dizzle','57':'Dense Freezing Drizzle',
                     '61':'Slight Rain','63':'Moderate Rain','65':'Heavy Rain','66':'Light Freezing Rain','67':'Heavy Freezing Rain',
                     '71':'Slight Snowfall','73':'Moderate Snowfall','75':'Heavy Snowfall','77':'Snow Grains','80':'Slight Rain Showers',
                     '81':'Moderate Rain Showers','82':'Violent Rain Showers','85':'Sight Snow Showers','95':'Slight Thunderstorms','96':'Moderate Thunderstorms',
                     '99':'Thunderstorms with hail'}
   
    weather = requests.request("GET",f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&current=temperature_2m,weather_code").json()
    return [weather,weather_codes[f"{weather['current']['weather_code']}"]]

def getPlayerScore(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    stableford = sum([score.stableford_score if score.stableford_score != None else 0 for score in scores])
    return stableford

def getPlayerStrokesFull(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    strokes = [score.strokes if score.strokes != None else None for score in scores]
    clean_strokes = [item for item in strokes if item != None]
    if len(clean_strokes) == 18:
        final = sum(clean_strokes)
    else:
        final = None
    return final

def getPlayerStrokes(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    strokes = sum([score.strokes if score.strokes != None else 0 for score in scores])
    return strokes

def getPlayerToPar(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    strokes = sum([score.strokes - score.hole.par if score.strokes != None else 0 for score in scores])
    return strokes

def getPlayerToParFull(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    strokes = [score.strokes - score.hole.par if score.strokes != None else None for score in scores]
    clean_strokes = [item for item in strokes if item != None]
    if len(clean_strokes) == 18:
        final = sum(clean_strokes)
    else:
        final = None
    return final

def addProTips(tips,chosen_course):
    
    courses = Course.objects.filter(course_name=chosen_course)
    for index,tip in enumerate(tips):
        ProTip.objects.create(pro_tip=tip)
        chosen = ProTip.objects.last()
        for course in courses:
            hole = Hole.objects.filter(course=course,hole_number=(index+1)).get()
            chosen.hole.add(hole)


class Home(View):

    """The Homepage"""

    model = Tournament
    template_name = 'tournaments/home.html'

    def get(self, request):
        tournaments = Tournament.objects.all().values()
        vids = Video.objects.all()
        latest_round = GolfRound.objects.last()
        latest_scores = Score.objects.filter(golf_round=latest_round).values()

        scores = [score['strokes'] for score in latest_scores]
        scores_2 = [1 if x != None else 0 for x in scores] 
        through = round(sum(scores_2)/(len(scores_2)/18))
        
        images = CarouselImage.objects.all().order_by('?')[:4]
        last_rounds = GolfRound.objects.order_by('id').reverse().select_related().values('id','score__hole__course__course_name','score__hole__course__tee','score__hole__course__slope_rating','score__hole__course__course_rating','holiday__tournament__slug','holiday__slug','round_number').distinct()[1:5]
        
        # for index,vid in enumerate(vids):
        #     vidcap = cv2.VideoCapture(fr'C:\Users\User\Documents\golf\golf-2024\{vid.file.url}')
        #     success,image = vidcap.read()
        #     cv2.imwrite(fr'{settings.MEDIA_ROOT}\{vid.file}.jpg',image)
        #     f = DjangoFile(open(fr'media\{vid.file}.jpg','rb'))
        #     Video.objects.filter(id=vid.id).update(thumbnail=f.name[6:])

        context = {
            'tournaments': tournaments,
            'latest_round':latest_round,
            'latest_scores':latest_scores,
            'through':through,
            'images':images,
            'last_rounds':last_rounds
            }
        return render(request, self.template_name, context)


class TournamentView(View):

    """Lists all the holidays within a tournament"""

    template_name = 'tournaments/tournament.html'
    def catch(self,player):
            try:
                return Handicap.objects.filter(player=player).order_by('-holiday__holiday_number')[0].handicap_index
            except:
                return ""
    

    def get(self, request, tournament):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        resorts = Resort.objects.all()
        player_by_handicap = Handicap.objects.all().order_by('-holiday__holiday_number')

        players = Player.objects.all()
        player_list = [[player, self.catch(player)] for player in players]

        scores = Score.objects.all()
        rounds = GolfRound.objects.all()

        holiday_set = []
        for holiday in holidays:
            data = []
            for player in Handicap.objects.filter(holiday=holiday).order_by('player__first_name'):
                top_scores = []
                for golf_round in rounds.filter(holiday=holiday):
                    top_scores.append(getPlayerScore(golf_round,player.player))
                top_3 = sorted(top_scores)
                data.append([player.player,top_scores,sum(top_3[-3:])])      
            holiday_set.append([player.holiday,data])
        
        context = {
            'holidays': holidays,
            'tournament': tournament,
            'selected_tournament': selected_tournament,
            'resorts':resorts,
            'players':player_list,
            'holiday_set':holiday_set}

        return render(request, self.template_name, context)
    
    def post(self, request, tournament):
        
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        try:
            holiday_number = holidays.order_by('holiday_number').values_list('holiday_number').last()[0] + 1
        except:
            holiday_number = 1
        Holiday.objects.create(resort=Resort.objects.filter(id=request.POST['resort'])[0],tournament=selected_tournament,holiday_number=holiday_number,slug=f"{request.POST['resort']}-{holiday_number}")
        new_hol = holidays.order_by('holiday_number').last()

        for element in request.POST:
            if len(request.POST.getlist(element)) == 2:
                player = Player.objects.filter(id=request.POST.getlist(element)[0]).get()
                Handicap.objects.create(player=player,handicap_index=request.POST.getlist(element)[1],holiday=new_hol)
        
        resorts = Resort.objects.all()
        players = Player.objects.all()
        player_list = [[player, self.catch(player)] for player in players]
        rounds = GolfRound.objects.all()
        holiday_set = []
        for holiday in holidays:
            data = []
            for player in Handicap.objects.filter(holiday=holiday).order_by('player__first_name'):
                top_scores = []
                for golf_round in rounds.filter(holiday=holiday):
                    top_scores.append(getPlayerScore(golf_round,player.player))
                top_3 = sorted(top_scores)
                data.append([player.player,top_scores,sum(top_3[-3:])])      
            holiday_set.append([player.holiday,data])

        context = {
            'holidays': holidays,
            'tournament': tournament,
            'selected_tournament': selected_tournament,
            'resorts':resorts,
            'players':player_list,
            'holiday_set':holiday_set}

        return render(request, self.template_name, context)


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
        players = Handicap.objects.filter(holiday=holiday_filter)

        resort = Resort.objects.filter(holiday=selected_holiday.get())
        
        data = []
        for player in Handicap.objects.filter(holiday=selected_holiday.get()).order_by('player__first_name'):
            top_scores = []
            for golf_round in rounds.filter(holiday=selected_holiday.get()):
                top_scores.append([golf_round.round_number,getPlayerScore(golf_round,player.player),getPlayerStrokes(golf_round,player.player)])
   
            data.append([player,top_scores])      
            

        
        context = {
            'holiday': holiday_filter,
            'rounds': rounds,
            'tournament': tournament,
            'courses':courses,
            'players':players,
            'lat':resort[0].latitude,
            'long':resort[0].longitude,
            'weather':getWeather(resort[0].latitude,resort[0].longitude),
            'scores':data}

        return render(request, self.template_name, context)
    
    def post(self, request, tournament, holiday):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        selected_holiday = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament)
        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)
        rounds_id = rounds.values('id')
        resort = Resort.objects.filter(holiday=holiday_filter)
        courses = Course.objects.filter(resort=resort.get())
        players = Handicap.objects.filter(holiday=holiday_filter)
        
        resort = Resort.objects.filter(holiday=selected_holiday.get())
        course = courses.filter(id=request.POST['course']).get()
        holes = Hole.objects.filter(course=course)
        GolfRound.objects.create(holiday=holiday_filter,round_number=len(rounds)+1)
        rounds = GolfRound.objects.filter(holiday=holiday_filter)

        [[Score.objects.create(player=player.player,hole=hole,handicap=player,golf_round=rounds.last()) for hole in holes] for player in players]

        context = {
            'holiday': holiday_filter,
            'rounds': rounds,
            'tournament': tournament,
            'courses':courses,
            'players':players,
            'lat':resort[0].latitude,
            'long':resort[0].longitude,
            'weather':getWeather(resort[0].latitude,resort[0].longitude)}

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
        scores = Score.objects.filter(golf_round=selected_round).select_related().values('strokes','stableford_score','player_id','player__first_name','player__slug',
                                                                                         'hole__hole_number','hole_id','hole__par','hole__stroke_index','hole__yards',
                                                                                         'hole__course__course_name','hole__course__tee',
                                                                                         'golf_round','golf_round__holiday','hole__course__slope_rating',
                                                                                         'hole__course__course_rating','sandy').order_by('player__first_name')
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()

        selected_course = Course.objects.filter(
            hole=scores.values()[0]['hole_id']).values()[0]
        slope_rating = selected_course['slope_rating']
        course_rating = selected_course['course_rating']
    
        rounds = GolfRound.objects.filter(holiday=holiday_filter)

        holes = Hole.objects.filter(course=Course.objects.filter(hole=scores.values()[0]['hole_id']).last()).values()
        total_par = sum([hole['par'] for hole in holes])

        handicaps = []
        for player in players:
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=scores.values()[0]['hole_id']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']
            playing_handicap = round(
                ((slope_rating/113)*float(handicap_index) + float(course_rating) - total_par)*0.95)
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']


            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score['strokes'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if score['stableford_score'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              float(handicap_index),
                              sum([score['strokes'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                ])

        hole_numbers = [x for x in range(1, 19)]
        player_scores = [scores[x*18:x*18 + 18] for x in range(len(players))]
            
        # player_scores = 

        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
            "players": players,
            "hole_numbers": hole_numbers,
            "player_scores": player_scores,
            "handicaps": handicaps,
            "rounds":rounds,
            "total_par":total_par,
        }

        return render(request, self.template_name, context)

    def post(self, request, tournament, holiday, selected_round):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holiday_filter = Holiday.objects.filter(
            slug=holiday, tournament=selected_tournament).get()
        selected_round = GolfRound.objects.filter(
            round_number=selected_round, holiday=holiday_filter).get()
        scores = Score.objects.filter(golf_round=selected_round).select_related().values('strokes','stableford_score','player_id','player__first_name','player__slug',
                                                                                         'hole__hole_number','hole_id','hole__par','hole__stroke_index','hole__yards',
                                                                                         'hole__course__course_name','hole__course__tee',
                                                                                         'golf_round','golf_round__holiday','hole__course__slope_rating',
                                                                                         'hole__course__course_rating','sandy').order_by('player__first_name')
        
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()
        hole_numbers = [x for x in range(1, 19)]
        player_scores = [scores[x*18:x*18 + 18] for x in range(len(players))]
        course = Course.objects.filter(id=Hole.objects.filter(
            id=request.POST['hole']).values()[0]['course_id'])

        # Get data on the course to calculate stableford points
        slope_rating = course.values()[0]['slope_rating']
        course_rating = course.values()[0]['course_rating']
        hole_played = Hole.objects.filter(id=request.POST['hole']).values()[0]
        holes = Hole.objects.filter(course=Course.objects.filter(hole=scores.values()[0]['hole_id']).last())
        total_par = sum([hole.par for hole in holes])
        handicaps = []

        for player in players:
            scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                strokes=request.POST[f"{player['player_id']}"])
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=request.POST['hole']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']

            playing_handicap = round(
                ((slope_rating/113)*float(handicap_index) + float(course_rating) - total_par)*0.95)

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

            try:
                if int(request.POST['sandy']) == int(player['player_id']):
                    scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                stableford_score=points,sandy=1)
                else:
                    scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                stableford_score=points,sandy=0)
                
            except:
                scores.filter(player=player['player_id'], hole=request.POST['hole']).update(
                stableford_score=points,sandy=0)
            
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']
        scores = Score.objects.filter(golf_round=selected_round).select_related().values('strokes','stableford_score','player_id','player__first_name','player__slug',
                                                                                         'hole__hole_number','hole_id','hole__par','hole__stroke_index','hole__yards',
                                                                                         'hole__course__course_name','hole__course__tee',
                                                                                         'golf_round','golf_round__holiday','hole__course__slope_rating',
                                                                                         'hole__course__course_rating','sandy').order_by('player__first_name')
        player_scores = [scores[x*18:x*18 + 18] for x in range(len(players))]
        for player in players:
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=request.POST['hole']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']

            playing_handicap = round(
                ((slope_rating/113)*float(handicap_index) + float(course_rating) - total_par)*0.95)
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']
            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score['strokes'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if score['stableford_score'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
                              float(handicap_index),
                              sum([score['strokes'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['strokes'] - score['hole__par'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if (score['strokes'] != None) and (score['hole__hole_number'] <= 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                              sum([score['stableford_score'] if (score['strokes'] != None) and (score['hole__hole_number'] > 9) else 0 for score in scores if score['player_id'] == player['player_id']]),
                ])
        
        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
            "players": players,
            "hole_numbers": hole_numbers,
            "player_scores": player_scores,
            'handicaps': handicaps,
            "total_par":total_par,
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

class StatsView(View):

    template_name ='tournaments/stats.html'
    def get(self,request):
        stats = [2]
        players = Player.objects.all()
        holidays = Holiday.objects.all()
        context = {
            'stats':stats,
            'players':players,
            'holidays':holidays
        }
        return render(request, self.template_name, context)

    
class HighlightsHome(View):
    template_name = 'tournaments/highlights_home.html'

    def get(self,request):

        scores = Score.objects.exclude(highlight_link__isnull=True)
        videos = Video.objects.all()
        vids =  [vid for vid in [score.highlight_link.all() for score in scores]] 
        vid_list = []
        for x in vids:
            for y in x:
                vid_list.append(y.id)
        # vid_list = [vid.get().id for vid in [score.highlight_link.all() for score in scores]]    

        
        unholed_vids = [vid for vid in videos if vid.id not in vid_list]

        context = {
            'scores':scores,
            'other_vids':unholed_vids
        }
        return render(request, self.template_name, context)
    
class HighlightView(View):
    template_name = 'tournaments/highlight.html'

    def get(self,request,highlight):
        
        selected_highlight = Score.objects.filter(highlight_link__id=highlight)
        assigned = True
        video = 0
        if len(selected_highlight) == 0:
            video = Video.objects.filter(id=highlight)
            assigned = False
        context = {
            'highlights':selected_highlight,
            'assigned':assigned,
            'video':video

            
        }
        return render(request, self.template_name, context)
    
def signUpUser(request):
    if request.method == 'GET':

        return render(request, 'tournaments/signUpUser.html', {'form': EditUserForm()})

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('homepage')
            except IntegrityError:
                return render(request, 'tournaments/signUpUser.html', {'form': EditUserForm(), 'error': 'Username Already Taken'})

        else:

            return render(request, 'tournaments/signUpUser.html', {'form': EditUserForm(), 'error': 'Passwords did not match'})


def logOutUser(request):
    logout(request)
    return redirect('homepage')


def logInUser(request):
    if request.method == 'GET':
        return render(request, 'tournaments/login.html', {'form': EditAuthForm()})

    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user == None:
            return render(request, 'tournaments/login.html', {'form': EditAuthForm(), 'error': 'Unknown User / Incorrect Password'})
        else:
            login(request, user)
            return redirect('homepage')

def handle_uploaded_file(f):
    with open(f"media/{f}", "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def uploadHighlight(request):

    if request.method == 'GET':
        return render(request,'tournaments/new_highlight.html',{'form':UploadFileForm()})
    
    elif request.method == 'POST':
        form = UploadFileForm(request.POST,request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            vidcap = cv2.VideoCapture(fr'{settings.MEDIA_ROOT}/{request.FILES["file"]}')            
            success,image = vidcap.read()
            cv2.imwrite(fr'{settings.MEDIA_ROOT}/{str(request.FILES["file"])[:-4]}.jpg',image)
            f = DjangoFile(open(fr'{settings.MEDIA_ROOT}/{str(request.FILES["file"])[:-4]}.jpg','rb'))
            Video.objects.create(title=request.POST['title'],file=request.FILES['file'],thumbnail=f'{str(request.FILES["file"])[:-4]}.jpg')
                       
            
            if request.POST['hole'] != 0:
                rounds = GolfRound.objects.filter(holiday=request.POST['holiday'])
                selected_round = rounds[int(request.POST['round_number'])-1]
                event = Score.objects.filter(player__id=request.POST['player'],golf_round=selected_round,hole__hole_number=request.POST['hole'])
                vid_event = Video.objects.last()
                event.get().highlight_link.add(vid_event)
            return redirect('highlights')
        else:
            return redirect('new_highlight')
class PlayerStats(View):
    template_name = 'tournaments/player_stats/player_stats.html'

    def get(self,request):

        players = Player.objects.all()
        player_scores=[]
        for player in players:
            rounds = GolfRound.objects.all()
            try:
                max_score = max([getPlayerScore(player=player,golf_round=golf_round) for golf_round in rounds if getPlayerScore(player=player,golf_round=golf_round) > 0])
                min_score_set_up = [getPlayerStrokesFull(player=player,golf_round=golf_round) for golf_round in rounds if getPlayerStrokes(player=player,golf_round=golf_round) >0]
                min_score = min([item for item in min_score_set_up if item != None])
                min_set_up = [getPlayerToParFull(player=player,golf_round=golf_round) for golf_round in rounds if getPlayerStrokes(player=player,golf_round=golf_round) >0]
                min_to_par = min([item for item in min_set_up if item != None])
            except:
                max_score = ''
                min_score = ''
                min_to_par = ''
            player_scores.append([player,max_score,min_score,min_to_par])
            
        context = {'players':player_scores}

        return render(request,self.template_name,context)
    
class StatsPage(View):

    template_name ='tournaments/player_stats/stats_page.html'
    def get(self,request,player):
        
        player = Player.objects.filter(slug=player).get()
        scores = Score.objects.filter(player=player)
        rounds = round(len(scores)/18)

        pars_birdies = [len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par == -2]),
                        len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par == -1]),
                        len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par == 0]),
                        len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par == 1]),
                        len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par == 2]),
                        len([score.strokes for score in scores if score.strokes != None and score.strokes - score.hole.par > 2])
                        ]
        try:
            per_round = list(map(lambda x :round(x/rounds,2),pars_birdies))
        except:
            per_round = [pars_birdies]
        stable = [0,1,2,3,4,5,6]
        stable_scores = [len([score.stableford_score for score in scores if score.stableford_score == stable_points]) for stable_points in stable]
        try:
            stable_per_round = list(map(lambda x :round(x/rounds,2),stable_scores))
        except:
            stable_per_round = stable_scores
        avg_score = [stable_per_round[x]*x for x in range(len(stable))]
        holidays = Holiday.objects.all()
        golf_rounds = scores.values_list('golf_round').distinct()
        player_rounds = [GolfRound.objects.filter(id=choice[0]).get() for choice in golf_rounds]
        player_totals = [sum([score.strokes for score in choice.score_set.filter(player=player) if score.strokes != None]) for choice in player_rounds]
        player_stab_totals = [sum([score.stableford_score for score in choice.score_set.filter(player=player) if score.strokes != None]) for choice in player_rounds]




        context = {
            'player':player,
            'holidays':holidays,
            'rounds':rounds,
            'pars_birdies':pars_birdies,
            'per_round':per_round,
            'stable_scores':stable_scores,
            'stable_per_round':stable_per_round,
            'avg_score':avg_score,
            'player_rounds':player_rounds,
            'player_totals':player_totals,
            'player_stab_totals':player_stab_totals
        }
        return render(request, self.template_name, context)
    
class CoursesOverview(View):
    template_name = 'tournaments/courses_overview.html'

    def get(self,request):
        
        courses = Course.objects.all().order_by('resort__name')
        course_names = list(dict.fromkeys([course.course_name for course in courses]))
        courses_now = [Course.objects.filter(course_name=course_name) for course_name in course_names]
        yards = [[sum([hole.yards for hole in tee_set.hole_set.all()]) for tee_set in resort] for resort in courses_now]
        par = [[sum([hole.par for hole in tee_set.hole_set.all()]) for tee_set in resort] for resort in courses_now]
        
        strokes = [[round(sum([np.average([0 if score.strokes == None else score.strokes for score in hole.score_set.all()]) for hole in tee_set.hole_set.all()]),2) for tee_set in resort] for resort in courses_now]
        strokes = [np.where(np.isnan(x),None,x) for x in strokes] 
        strokes = [np.where(x == 0,None,x) for x in strokes] 
        points = [[round(sum([ np.average([0 if score.stableford_score == None else score.stableford_score for score in hole.score_set.all()]) for hole in tee_set.hole_set.all()]),2) for tee_set in resort] for resort in courses_now]
        
        points = [np.where(np.isnan(x),None,x) for x in points] 
        points = [np.where(x == 0,None,x) for x in points] 
        
        
        context = {
            'courses':courses,
            'course_names':course_names,
            'courses_now':courses_now,
            'yards':yards,
            'par':par,
            'strokes':strokes,
            'points':points
        }

        return render(request,self.template_name,context)
    
class CourseView(View):
    template_name = 'tournaments/course_view.html'

    def get(self,request,course_name):
        course = Course.objects.filter(slug=course_name)

        for row in course:
            try:
                minimum_shots = [min([score.strokes for score in hole.score_set.all()]) for hole in row.hole_set.all()]
                maximum_shots = [max([score.strokes for score in hole.score_set.all()]) for hole in row.hole_set.all()]
                avg_shots = [round(np.average([score.strokes - score.hole.par for score in hole.score_set.all()]),3) for hole in row.hole_set.all()]
                avg_points = [round(np.average([score.stableford_score for score in hole.score_set.all()]),3) for hole in row.hole_set.all()]
                our_index = [sorted(avg_shots,reverse=True).index(x) +1 for x in avg_shots]
                points_index = [sorted(avg_points).index(x) +1 for x in avg_points]


            except:
                minimum_shots = ['-' for x in range(17)]
                maximum_shots = ['-' for x in range(17)]
                avg_shots = ['-' for x in range(17)]
                our_index = ['-' for x in range(17)]
                points_index = ['-' for x in range(17)]
                avg_points = ['-' for x in range(17)]

        context = {
            'course':course,
            'minimum_shots':minimum_shots,
            'maximum_shots':maximum_shots,
            'avg_shots':avg_shots,
            'course_id':course.get().id,
            'our_index':our_index,
            'points_index':points_index,
            'avg_points':avg_points
        }

        return render(request,self.template_name,context)
    
class HoleView(View):
    template_name = 'tournaments/hole.html'

    def get(self,request,course_name,hole):

        course = Course.objects.filter(slug=course_name).get()
        hole = Hole.objects.filter(course=course).filter(hole_number=hole)

        context = {
            'hole':hole,
            'course':course.id
        }
        return render(request,self.template_name,context)