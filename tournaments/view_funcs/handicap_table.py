from ..models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video,ProTip,CarouselImage
import random

def get_scores_context(tournament,holiday,selected_round):
    selected_tournament = Tournament.objects.filter(slug=tournament).get()
    holiday_filter = Holiday.objects.filter(
        slug=holiday, tournament=selected_tournament).get()
    selected_round_send = GolfRound.objects.filter(
        round_number=selected_round, holiday=holiday_filter).get()
   
    scores = Score.objects.filter(golf_round=selected_round_send).select_related().values('strokes','stableford_score','player_id','player__first_name','player__slug','team',
                                                                                        'hole__hole_number','hole_id','hole__par','hole__stroke_index','hole__yards',
                                                                                        'hole__course__course_name','hole__course__tee','golf_round__round_number',
                                                                                        'golf_round','golf_round__holiday','hole__course__slope_rating','match_play_result',
                                                                                        'hole__course__course_rating','sandy').order_by('player__first_name').distinct()
       
    players = scores.order_by('player__first_name').values(
        'player_id').distinct()

    selected_course = Course.objects.filter(
        hole=scores.values()[0]['hole_id']).values()[0]
    slope_rating = selected_course['slope_rating']
    course_rating = selected_course['course_rating']

    rounds = GolfRound.objects.filter(holiday=holiday_filter)

    holes = Hole.objects.filter(course=Course.objects.filter(hole=scores.values()[0]['hole_id']).last()).values()
    total_par = sum([hole['par'] for hole in holes])
    
    
    # calculate total shots etc  for each player
    
    handicaps = []
    names = []
    for player in players:
        handicap_index = Handicap.objects.filter(id=scores.filter(player=player['player_id'],
                                                                    hole=scores.values()[0]['hole_id']).values('handicap_id')[0]['handicap_id']).values()[0]['handicap_index']
        playing_handicap = round(
            ((slope_rating/113)*float(handicap_index) + float(course_rating) - total_par))
        player_name = Player.objects.filter(
            id=player['player_id']).values('first_name')[0]['first_name']
        names.append(player_name)

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
                            sum([score['match_play_result'] if score['match_play_result'] != None else 0 for score in scores if score['player_id'] == player['player_id']]),
            ])

    hole_numbers = [x for x in range(1, 19)]
    player_scores = [scores[x*18:x*18 + 18] for x in range(len(players))]
    if len(players) == 4:
        team_combos = [
                [ f'{names[0]} & {names[1]} vs {names[2]} & {names[3]}',[players[0]['player_id'],players[1]['player_id'],players[2]['player_id'],players[3]['player_id']]],
                [ f'{names[0]} & {names[2]} vs {names[1]} & {names[3]}',[players[0]['player_id'],players[2]['player_id'],players[1]['player_id'],players[3]['player_id']]],
                [ f'{names[0]} & {names[3]} vs {names[2]} & {names[1]}',[players[0]['player_id'],players[3]['player_id'],players[2]['player_id'],players[1]['player_id']]],
            ]
        check_current_teams = Score.objects.filter(golf_round=selected_round_send,hole__hole_number=1).values('team','player__first_name').order_by('team','player__first_name')
        
        if check_current_teams[0]['team']:
            current_teams = [f"{check_current_teams[0]['player__first_name']} & {check_current_teams[1]['player__first_name']}", f"{check_current_teams[2]['player__first_name']} & {check_current_teams[3]['player__first_name']}"]
        else:
            current_teams = None
    else:
        team_combos = None
        current_teams = None
        
    if current_teams:
        
        team1 = Score.objects.filter(golf_round=selected_round_send,team=1).select_related().values('strokes','stableford_score','player_id','team','hole__hole_number')
        team2 = Score.objects.filter(golf_round=selected_round_send,team=2).select_related().values('strokes','stableford_score','player_id','team','hole__hole_number')
        team1_points = [{'hole':hole,'points_1':max([score['stableford_score'] if (score['hole__hole_number'] == hole and score['strokes'] != None) else 0 for score in team1 ])} for hole in hole_numbers]
        team2_points = [{'hole':hole,'points_2':max([score['stableford_score'] if (score['hole__hole_number'] == hole and score['strokes'] != None) else 0 for score in team2 ])} for hole in hole_numbers]
        team1_total = sum(item['points_1'] for item in team1_points)
        team2_total = sum(item['points_2'] for item in team2_points)
        match_play = [[{**u, **v} for u, v in zip(team1_points,team2_points)],team1_total,team2_total]
    else:
        match_play = None
    circle = ''
    for x in range(50):
        circle += f'<circle cx="{random.randint(2,28)}" cy="{random.randint(2,28)}" r="1" fill="rgb(194, 178, 128)"></circle>'

    context = {
        'holiday': holiday_filter,
        'selected_round': selected_round_send,
        'tournament': tournament,
        'scores': scores,
        "players": players,
        "hole_numbers": hole_numbers,
        "player_scores": player_scores,
        "handicaps": handicaps,
        "rounds":rounds,
        "total_par":total_par,
        "team_combos":team_combos,
        "current_teams":current_teams,
        'match_play':match_play,
        'circle':circle,
    }

    return context