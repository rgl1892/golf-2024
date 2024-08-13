from ..models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video,ProTip,CarouselImage

def get_scores_context(tournament,holiday,selected_round):
    selected_tournament = Tournament.objects.filter(slug=tournament).get()
    holiday_filter = Holiday.objects.filter(
        slug=holiday, tournament=selected_tournament).get()
    selected_round_send = GolfRound.objects.filter(
        round_number=selected_round, holiday=holiday_filter).get()
   
    scores = Score.objects.filter(golf_round=selected_round_send).select_related().values('strokes','stableford_score','player_id','player__first_name','player__slug',
                                                                                        'hole__hole_number','hole_id','hole__par','hole__stroke_index','hole__yards',
                                                                                        'hole__course__course_name','hole__course__tee',
                                                                                        'golf_round','golf_round__holiday','hole__course__slope_rating',
                                                                                        'hole__course__course_rating','sandy','highlight_link','highlight_link__id').order_by('player__first_name')
       
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
            ])

    hole_numbers = [x for x in range(1, 19)]
    player_scores = [scores[x*18:x*18 + 18] for x in range(len(players))]
    team_combos = [
       [ f'{names[0]} & {names[1]} vs {names[2]} & {names[3]}',[players[0]['player_id'],players[1]['player_id'],players[2]['player_id'],players[3]['player_id']]],
       [ f'{names[0]} & {names[2]} vs {names[1]} & {names[3]}',[players[0]['player_id'],players[2]['player_id'],players[1]['player_id'],players[3]['player_id']]],
       [ f'{names[0]} & {names[3]} vs {names[2]} & {names[1]}',[players[0]['player_id'],players[3]['player_id'],players[2]['player_id'],players[1]['player_id']]],
    ]
    
    

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
        "team_combos":team_combos
    }
    return context