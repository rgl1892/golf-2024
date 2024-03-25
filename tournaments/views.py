from django.shortcuts import render, redirect
from .models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video
from django.views.generic import View
from django.http import HttpResponse
from django.db import IntegrityError
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import permission_required
from .forms import UploadFileForm
from django.conf import settings
import math
import requests
import cv2

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

test_player = Player.objects.filter(id=1).get()
test_golf_round = GolfRound.objects.filter(id=1).get()
def getPlayerScore(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    stableford = sum([score.stableford_score if score.stableford_score != None else 0 for score in scores])
    return stableford

def getPlayerStrokes(golf_round,player):
    scores = Score.objects.filter(player=player,golf_round=golf_round)
    strokes = sum([score.strokes if score.strokes != None else 0 for score in scores])
    return strokes


class Home(View):

    """The Homepage"""

    model = Tournament
    template_name = 'tournaments/home.html'

    def get(self, request):
        tournaments = Tournament.objects.all()
        vids = Video.objects.all()

        # for index,vid in enumerate(vids):
        #     vidcap = cv2.VideoCapture(fr'C:\Users\User\Documents\golf\golf-2024\{vid.file.url}')
        #     success,image = vidcap.read()
        #     cv2.imwrite(fr'C:\Users\User\Documents\golf\golf-2024\media\{index}.jpg',image)
        #     Video.objects.filter(id=vid.id).update(thumbnail=fr'C:\Users\User\Documents\golf\golf-2024\media\{index}.jpg')
        # vids = Video.objects.filter(id=1).get()
        # vidcap = cv2.VideoCapture(fr'C:\Users\User\Documents\golf\golf-2024\{vids.file.url}')
        # success,image = vidcap.read()
        # cv2.imwrite(fr'C:\Users\User\Documents\golf\golf-2024\1.jpg',image)
        # Video.objects.filter(id=1).update(thumbnail=fr'C:\Users\User\Documents\golf\golf-2024\1.jpg')

        context = {
            'tournaments': tournaments,
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
        holiday_number = holidays.order_by('holiday_number').values_list('holiday_number').last()[0] + 1
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
        scores = [[player,Score.objects.filter(handicap=player)] for player in players]
        
        resort = Resort.objects.filter(holiday=selected_holiday.get())
        holidays = Holiday.objects.filter(tournament=selected_tournament)
        holiday_set = []
        
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
        scores = Score.objects.filter(golf_round=selected_round)
        players = scores.order_by('player__first_name').values(
            'player_id').distinct()

        selected_course = Course.objects.filter(
            hole=scores.values()[0]['hole_id']).values()[0]
        slope_rating = selected_course['slope_rating']
        course_rating = selected_course['course_rating']
        rounds = GolfRound.objects.filter(holiday=holiday_filter)

        handicaps = []
        for player in players:
            handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                      hole=scores.values()[0]['hole_id']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']
            playing_handicap = round(
                (slope_rating/113)*float(handicap_index)*0.95)
            player_name = Player.objects.filter(
                id=player['player_id']).values('first_name')[0]['first_name']

            test = [score.strokes if score.strokes != None else 0 for score in scores.filter(player=player['player_id'])]

            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score.strokes if score.strokes != None else 0 for score in scores.filter(player=player['player_id'])]),
                              sum([score.strokes - score.hole.par if score.strokes != None else 0 for score in scores.filter(player=player['player_id'])]),
                              sum([score.stableford_score if score.stableford_score != None else 0 for score in scores.filter(player=player['player_id'])])
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
            "handicaps": handicaps,
            "rounds":rounds
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

            print(request.POST)
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

            handicaps.append([playing_handicap, 
                              player_name, 
                              sum([score.strokes if score.strokes != None else 0 for score in scores.filter(player=player['player_id'])]),
                              sum([score.strokes - score.hole.par if score.strokes != None else 0 for score in scores.filter(player=player['player_id'])]),
                              sum([score.stableford_score if score.stableford_score != None else 0 for score in scores.filter(player=player['player_id'])])
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

        return render(request, 'tournaments/signUpUser.html', {'form': UserCreationForm()})

    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(
                    request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('homepage')
            except IntegrityError:
                return render(request, 'tournaments/signUpUser.html', {'form': UserCreationForm(), 'error': 'Username Already Taken'})

        else:

            return render(request, 'tournaments/signUpUser.html', {'form': UserCreationForm(), 'error': 'Passwords did not match'})


def logOutUser(request):
    logout(request)
    return redirect('homepage')


def logInUser(request):
    if request.method == 'GET':
        return render(request, 'tournaments/login.html', {'form': AuthenticationForm()})

    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user == None:
            return render(request, 'tournaments/login.html', {'form': AuthenticationForm(), 'error': 'Unknown User / Incorrect Password'})
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
            vidcap = cv2.VideoCapture(fr'{settings.MEDIA_ROOT}\{request.FILES['file']}')
            success,image = vidcap.read()
            cv2.imwrite(fr'{settings.MEDIA_ROOT}\{str(request.FILES['file'])[:-4]}.jpg',image)
            Video.objects.create(title=request.POST['title'],file=request.FILES['file'],thumbnail=fr'{settings.MEDIA_ROOT}\{str(request.FILES['file'])[:-4]}.jpg')
            if request.POST['hole'] != 0:
                rounds = GolfRound.objects.filter(holiday=request.POST['holiday'])
                selected_round = rounds[int(request.POST['round_number'])-1]
                event = Score.objects.filter(player__id=request.POST['player'],golf_round=selected_round,hole__hole_number=request.POST['hole'])
                vid_event = Video.objects.last()
                # print(vid_event)
                event.get().highlight_link.add(vid_event)
            return redirect('highlights')
        else:
            return redirect('new_highlight')
