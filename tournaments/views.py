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
from django.db.models import Q

from .view_funcs import handicap_table, stats

from PIL import Image
import math
import numpy as np
import requests
import cv2
import json


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
        
        holiday = Holiday.objects.filter(slug='2-3').get()
        scores = Score.objects.filter(golf_round__holiday=holiday).values('golf_round_id','strokes','stableford_score','hole__par')
        
        try:
            holiday = Holiday.objects.filter(slug='2-3').get()
            players= Handicap.objects.filter(holiday=holiday).values('id','player__first_name')
            rounds = GolfRound.objects.filter(holiday=holiday).values()
            scores = Score.objects.filter(golf_round__holiday=holiday).values('golf_round_id','strokes','stableford_score','hole__par','handicap_id')

            
            total_set = []
            for player in players:
                birdies = 0
                eagles = 0
                strokes = 0
                to_par_total = 0
                round_set = []
                for item in rounds:
                    score_set = []
                    
                    for score in scores:
                        if score['golf_round_id'] == item['id'] and player['id'] == score['handicap_id'] and score['strokes']:
                            score_set.append(score['stableford_score'])
                            to_par = score['strokes']-score['hole__par']
                            if to_par == -2:
                                eagles += 1
                            if to_par == -1:
                                birdies += 1
                            strokes += score['strokes']
                            to_par_total += score['strokes']-score['hole__par']
                            
                    round_set.append(sum(score_set))
                test_length = len(round_set)
                if test_length <= 2:
                    total = sum(round_set)
                elif test_length == 3:
                    total = sum(sorted(round_set)[-2:])
                else:
                    last = round_set[-1]
                    first = round_set[:-1]
                    total = sum(sorted(first)[-2:]) + last
            
                total_set.append([player['player__first_name'],round_set,total,birdies,eagles,to_par_total,strokes])
            lst = sorted(total_set,key=lambda x :x[2],reverse=True)
            
        except:
            holiday = 'Not yet'
            lst = []
        # holiday = 'Not yet'
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
            'last_rounds':last_rounds,
            'holiday':holiday,
            'lst':lst
            }
        return render(request, self.template_name, context)


class TournamentView(View):

    """Lists all the holidays within a tournament"""

    template_name = 'tournaments/tournament.html'
    def catch(self,player):
            try:
                return Handicap.objects.filter(player=player).order_by('-holiday__holiday_number').values()['handicap_index']
            except:
                return ""
    
    def get_context(self, request, tournament):
        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        holidays = Holiday.objects.filter(tournament__slug=tournament).values('id','slug','resort__name','resort__country')
        scores = Score.objects.values()
        golf_rounds = GolfRound.objects.all()

        holiday_set = []
        for holiday in holidays:
            
            data = []
            for player in Handicap.objects.filter(holiday=holiday['id']).order_by('player__first_name').values('id','player__first_name','player__last_name','holiday_id','player_id','holiday__slug','holiday__resort__name','holiday__resort__country'):
                top_scores = []
                for golf_round in golf_rounds.filter(holiday=holiday['id']).values():
                    top_scores.append(stats.getPlayerScore(golf_round=golf_round,player=player['player_id'],scores=scores))
                top_3 = sorted(top_scores)
                data.append([f"{player['player__first_name']} {player['player__last_name']}",top_scores,sum(top_3[-3:])])
            data.sort(key=lambda x : x[2],reverse=True)     
            holiday_set.append([holiday['slug'],data,holiday['resort__name'],holiday['resort__country']])
        players = Player.objects.values()
        player_list = [Handicap.objects.filter(player=player['id']).values('handicap_index','player__first_name','player__last_name','player__id').last() if Handicap.objects.filter(player=player['id']).values('handicap_index','player__first_name','player__last_name').last() else player for player in players]
        resorts = Resort.objects.all()
        
        
        context = {
            'selected_tournament':selected_tournament,
            'holidays': holidays,
            'tournament': tournament,
            'players':player_list,
            'resorts':resorts,
            'holiday_set':holiday_set}
        
        return context
    def get(self, request, tournament):
        context = self.get_context(request, tournament)

        return render(request, self.template_name, context)
    
    def post(self, request, tournament):
        print(tournament)
        
        selected_tournament = Tournament.objects.filter(slug=tournament)
        selected_resort = Resort.objects.filter(id=request.POST.get('resort'))
        try:
            holiday_number = Holiday.objects.filter(tournament__slug=tournament).order_by('holiday_number').values().last()['holiday_number'] + 1
        except:
            holiday_number = 1
        try:
            Holiday.objects.create(resort=selected_resort.get(),tournament=selected_tournament.get(),holiday_number=holiday_number,slug=f"{request.POST.get('resort')}-{holiday_number}")
            
            new_holiday = Holiday.objects.last()
            
            for key in request.POST:
                
                if len(request.POST.getlist(key)) == 2:
                    
                    player = Player.objects.filter(id=request.POST.getlist(key)[0]).get()
                    Handicap.objects.create(player=player,handicap_index=request.POST.getlist(key)[1],holiday=new_holiday)
            error = ''
        except:
            error = 'Error creating player or handicaps'
            
        context = self.get_context(request, tournament)
        context['error'] = error

        

        return render(request, self.template_name, context)


class RoundsView(View):

    """Lists all the rounds from a holiday"""

    template_name = "tournaments/rounds.html"

    def get(self, request, tournament, holiday):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()
        selected_holiday = Holiday.objects.filter(slug=holiday, tournament__slug=tournament)


        holiday_filter = selected_holiday.get()
        rounds = GolfRound.objects.filter(holiday=holiday_filter)
        resort = Resort.objects.filter(holiday=holiday_filter)
        courses = Course.objects.filter(resort=resort.get())
        players = Handicap.objects.filter(holiday=holiday_filter)

        resort = Resort.objects.filter(holiday=selected_holiday.get())
        
        data = []
        scores = Score.objects.values()
        for player in Handicap.objects.filter(holiday=selected_holiday.get()).order_by('player__first_name').values('player_id','player__first_name','player__handedness','handicap_index','player__championships'):
            top_scores = []
            for golf_round in rounds.filter(holiday=selected_holiday.get()).values():
                top_scores.append([golf_round['round_number'],stats.getPlayerScore(golf_round,player['player_id'],scores=scores),stats.getPlayerStrokes(golf_round,player['player_id'],scores=scores)])
   
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
        
        context = handicap_table.get_scores_context(tournament,holiday,selected_round)

        
        return render(request, self.template_name, context)

    def post(self, request, tournament, holiday, selected_round):
        
        # set up post details
        request_items = request.POST.copy()
        hole = request_items['hole']
        try:
            sandy = request_items['sandy']
            del request_items['sandy'] 
        except:
            sandy = ''
        del request_items['csrfmiddlewaretoken'] 
        del request_items['hole'] 
        
        # set up course details for stableford calc

        course = Course.objects.filter(hole__id=hole).values().get()
        holiday_item = Holiday.objects.filter(slug=holiday).values().get()['id']
        holes = Hole.objects.filter(course=course['id']).values()
        hole_details = Hole.objects.filter(id=hole).values().get()
        total_par = sum([hole['par'] for hole in holes])
        
        for player_id, strokes in request_items.items():
            if strokes:
                handicap_index = Handicap.objects.filter(player=player_id,holiday_id=holiday_item).values().get()['handicap_index']

                # calculate stableford score
                
                playing_handicap = round(float(handicap_index) * (course['slope_rating']/113) + float(course['course_rating'] - total_par))
                
                
                extra_shots = math.floor(playing_handicap/18)
                if hole_details['stroke_index'] <= playing_handicap % 18:
                    si_change = 1
                else:
                    si_change = 0

                final_shots = int(strokes) - extra_shots - si_change - hole_details['par']
                try:
                    points = int(self.stableford_lookup[f"{final_shots}"])
                except:
                    points = 0
                if player_id == sandy:
                    Score.objects.filter(player=player_id,hole=hole,golf_round__round_number=selected_round,golf_round__holiday__slug=holiday).update(stableford_score=points,strokes=strokes,sandy=True)
                else:
                    Score.objects.filter(player=player_id,hole=hole,golf_round__round_number=selected_round,golf_round__holiday__slug=holiday).update(stableford_score=points,strokes=strokes,sandy=False)

                # print(f'Strokes: {strokes}\t si_change: {si_change}\t Player: {player_id} \t Handi: {playing_handicap} \t Mod 18: {playing_handicap % 18}')

            else:
                Score.objects.filter(player=player_id,hole=hole,golf_round__round_number=selected_round,golf_round__holiday__slug=holiday).update(stableford_score=None,strokes=None)
        try:
            scores_to_compare = Score.objects.filter(hole=hole,golf_round__round_number=selected_round,golf_round__holiday__slug=holiday).values()
            high_1 = []
            high_2 = []
            compare_test = 0
            for score in scores_to_compare:
                if score['strokes']:
                    compare_test += 1
            if compare_test == 4:
                for row in scores_to_compare: 
                    if row['team'] == '1':
                        high_1.append(row['stableford_score'])
                    else:
                        high_2.append(row['stableford_score'])
                if max(high_1) > max(high_2):
                    scores_to_compare.update(match_play_result=1)
                elif max(high_1) < max(high_2):
                    scores_to_compare.update(match_play_result=-1)
                else:
                    scores_to_compare.update(match_play_result=0)
            else:
                scores_to_compare.update(match_play_result=None)
        except:
            scores_to_compare = 0 
        context = handicap_table.get_scores_context(tournament,holiday,selected_round)
        return render(request, self.template_name, context)

class ScoresMatchPlayView(ScoresView):
         
    
    def post(self, request, tournament, holiday, selected_round):
        players = json.loads(request.POST['team_choice'])
        if request.POST['team_choice'] != 'Select':
            query = Q(player=players[0])
            query.add(Q(player=players[1]),Q.OR)
            query.add(Q(golf_round__holiday__slug=holiday),Q.AND)
            query.add(Q(golf_round__round_number=selected_round),Q.AND)
            Score.objects.filter(query).update(team='1')
            query_2 = Q(player=players[2])
            query_2.add(Q(player=players[3]),Q.OR)
            query_2.add(Q(golf_round__holiday__slug=holiday),Q.AND)
            query_2.add(Q(golf_round__round_number=selected_round),Q.AND)
            Score.objects.filter(query_2).update(team='2')

        context = handicap_table.get_scores_context(tournament,holiday,selected_round)
        

        return render(request, self.template_name, context)


class EditScoresView(View):
    template_name = 'tournaments/edit_scores.html'

    def get(self, request, tournament, holiday, selected_round, hole):

        selected_tournament = Tournament.objects.filter(slug=tournament).get()

        holiday_filter = Holiday.objects.filter(slug=holiday, tournament=selected_tournament).get()

        selected_round = GolfRound.objects.filter(round_number=selected_round, holiday=holiday_filter).get()

        scores = Score.objects.filter(golf_round=selected_round,hole=hole).order_by('player__first_name').select_related().values(
            'id', 'player_id', 'hole_id', 'golf_round_id', 'strokes', 'stableford_score', 'sandy','player_id',
            'handicap_id', 'match_play_result', 'team','player__first_name','hole__yards','hole__par','hole__stroke_index',
            'hole__hole_number'
              )
        
        context = {
            'holiday': holiday_filter,
            'selected_round': selected_round,
            'tournament': tournament,
            'scores': scores,
        }

        return render(request, self.template_name, context)

class StatsView(View):

    template_name ='tournaments/stats.html'
    def get(self,request):
        stats = [2]
        players = Player.objects.values('id','first_name','last_name')
        holidays = Holiday.objects.values('id','resort__name','tournament__name','holiday_number')
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

        # Separate the videos by attached to hole or not.

        vid_list = []
        for x in vids:
            for y in x:
                vid_list.append(y.id)
        # vid_list = [vid.get().id for vid in [score.highlight_link.all() for score in scores]]    

        
        unholed_vids = [vid for vid in videos if vid.id not in vid_list]

        highlights = Score.objects.exclude(highlight_link__isnull=True).order_by('player__first_name').values(
            'player__first_name','highlight_link','highlight_link__thumbnail','highlight_link__title')
        players = []

        [players.append(cell['player__first_name']) for cell in highlights if cell['player__first_name'] not in players]

        highlight_reel = [{
            'player':player,
            'clips':[
                {'file':row['highlight_link__thumbnail'],
                 'id':row['highlight_link'],
                 'title':row['highlight_link__title']
                 } for row in highlights if row['player__first_name'] == player]} for player in players]
        context = {
            'scores':scores,
            'other_vids':unholed_vids,
            'highlights':highlight_reel
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
            # f = DjangoFile(open(fr'{settings.MEDIA_ROOT}/{str(request.FILES["file"])[:-4]}.jpg','rb'))
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

        players = Player.objects.select_related().values('id', 'first_name', 'last_name', 'handedness', 'championships', 'picture', 'info', 'slug','picture')
        scores = Score.objects.values('strokes','stableford_score','hole__par','golf_round_id','player_id')
        player_scores=[]
        for player in players:
            rounds = GolfRound.objects.values()
            # try:
            max_score = max([stats.getPlayerScore(player=player['id'],golf_round=golf_round,scores=scores) for golf_round in rounds if stats.getPlayerScore(player=player['id'],golf_round=golf_round,scores=scores) > 0])
            min_score_set_up = [stats.getPlayerStrokesFull(player=player['id'],golf_round=golf_round,scores=scores) for golf_round in rounds if stats.getPlayerStrokes(player=player['id'],golf_round=golf_round,scores=scores) >0]
            min_score = min([item for item in min_score_set_up if item != None])
            min_set_up = [stats.getPlayerToParFull(player=player['id'],golf_round=golf_round,scores=scores) for golf_round in rounds if stats.getPlayerStrokes(player=player['id'],golf_round=golf_round,scores=scores) >0]
            min_to_par = min([item for item in min_set_up if item != None])
            # except:
            #     max_score = ''
            #     min_score = ''
            #     min_to_par = ''
            player_scores.append([player,max_score,min_score,min_to_par])
            
        context = {'players':player_scores}

        return render(request,self.template_name,context)
    
class StatsPage(View):

    template_name ='tournaments/player_stats/stats_page.html'
    def get(self,request,player):
        
        player = Player.objects.filter(slug=player).values()[0]
        scores = Score.objects.filter(player=player['id']).values('strokes','hole__par','stableford_score',
                                                                  'golf_round_id','player_id','hole__par',
                                                                  'hole__hole_number','golf_round__holiday__tournament__name',
                                                                  'hole__course__course_name')
        rounds = round(len(scores)/18)



        pars_birdies = [len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] == -2]),
                        len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] == -1]),
                        len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] == 0]),
                        len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] == 1]),
                        len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] == 2]),
                        len([score['strokes'] for score in scores if score['strokes'] != None and score['strokes'] - score['hole__par'] > 2])
                        ]
        try:
            per_round = list(map(lambda x :round(x/rounds,2),pars_birdies))
        except:
            per_round = [pars_birdies]
        stable = [0,1,2,3,4,5,6]
        stable_scores = [len([score['stableford_score'] for score in scores if score['stableford_score'] == stable_points]) for stable_points in stable]
        try:
            stable_per_round = list(map(lambda x :round(x/rounds,2),stable_scores))
        except:
            stable_per_round = stable_scores
        avg_score = [stable_per_round[x]*x for x in range(len(stable))]
        holidays = Holiday.objects.all()
        golf_rounds = Score.objects.filter(player=player['id']).values('golf_round_id').distinct()
        player_rounds = [[[score['strokes'],score['stableford_score'], score['hole__par'],score['hole__hole_number'],score['golf_round__holiday__tournament__name'],score['hole__course__course_name']] for score in scores if score['strokes'] != None and score['golf_round_id'] == choice['golf_round_id']] for choice in golf_rounds]

        
        player_totals = [sum([score['strokes'] for score in scores if score['strokes'] != None and score['golf_round_id'] == choice['golf_round_id']]) for choice in golf_rounds]
        player_stab_totals = [sum([score['stableford_score'] for score in scores if score['strokes'] != None and score['golf_round_id'] == choice['golf_round_id']]) for choice in golf_rounds]
        



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
        
        courses = Course.objects.order_by('resort__name').values()
        course_names = list(dict.fromkeys([course['course_name'] for course in courses]))
        courses_now = [Course.objects.filter(course_name=course_name).values() for course_name in course_names]
        holes = Hole.objects.values()
        scores = Score.objects.values('id','strokes','stableford_score','hole__course_id')
        
        
        yards = [[sum([hole['yards'] for hole in holes if hole['course_id'] == tees['id']]) for tees in indidual_course] for indidual_course in courses_now]    
        par = [[sum([hole['par'] for hole in holes if hole['course_id'] == tees['id']]) for tees in indidual_course] for indidual_course in courses_now]
        # print([[[hole['strokes'] for hole in scores if hole['hole__course_id'] == tees['id']]for tees in indidual_course] for indidual_course in courses_now])

        # strokes = [[round(sum([np.average([0 if score.strokes == None else score.strokes for score in hole.score_set.all()]) for hole in tee_set.hole_set.all()]),2) for tee_set in resort] for resort in courses_now]
        # strokes = [np.where(np.isnan(x),None,x) for x in strokes] 
        # strokes = [np.where(x == 0,None,x) for x in strokes] 
        # points = [[round(sum([ np.average([0 if score.stableford_score == None else score.stableford_score for score in hole.score_set.all()]) for hole in tee_set.hole_set.all()]),2) for tee_set in resort] for resort in courses_now]
        
        # points = [np.where(np.isnan(x),None,x) for x in points] 
        # points = [np.where(x == 0,None,x) for x in points] 
        
        
        context = {
            'courses':courses,
            'course_names':course_names,
            'courses_now':courses_now,
            'yards':yards,
            'par':par,
        #     'strokes':strokes,
        #     'points':points
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
    
class CourseStats(View):

    template_name = 'tournaments/course_stats/course_stats.html'

    def get(self,request):
        courses = Score.objects.values('hole__course__id','hole__course__course_name','hole__course__tee').distinct()
        players = Player.objects.values()
        holidays = Holiday.objects.values('id','resort__name','holiday_number')
        all_courses = Course.objects.values('id','course_name','tee')
        context = {
            'courses':courses,
            'rounds':[1,2,3,4,5],
            'players':players,
            'holidays':holidays,
            'other_courses':all_courses
            }
        return render(request,self.template_name,context)

class SillyStats(View):

    template_name = 'tournaments/course_stats/silly_stats.html'
    
    def get(self,request):
        context = {}
        return render(request,self.template_name,context)
    
class ScoresTestView(View):
    template_name = 'tournaments/scores_test.html'
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
        
        context = handicap_table.get_scores_context(tournament,holiday,selected_round)
        

        return render(request, self.template_name, context)