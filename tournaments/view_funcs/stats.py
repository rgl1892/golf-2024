from ..models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video,ProTip,CarouselImage

def getPlayerScore(golf_round,player,scores):
    """
    Parameters
    ----------
    golf_round : dict
                id needed in dict
    player : int
            id as int
    scores : list of dict
    """
    stableford = sum([score['stableford_score'] if score['stableford_score'] != None else 0 for score in scores if score['player_id'] == player and score['golf_round_id'] == golf_round['id']])
    return stableford

def getPlayerStrokesFull(golf_round,player,scores):
    strokes = [score['strokes'] if score['strokes'] != None else None for score in scores if score['player_id'] == player and score['golf_round_id'] == golf_round['id']]
    clean_strokes = [item for item in strokes if item != None]
    if len(clean_strokes) == 18:
        final = sum(clean_strokes)
    else:
        final = None
    return final

def getPlayerStrokes(golf_round,player,scores):
    strokes = sum([score['strokes'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player and score['golf_round_id'] == golf_round['id']])
    return strokes

def getPlayerToPar(golf_round,player,scores):
    strokes = sum([score['strokes'] - score['hole__par'] if score['strokes'] != None else 0 for score in scores if score['player_id'] == player and score['golf_round_id'] == golf_round['id']])
    return strokes

def getPlayerToParFull(golf_round,player,scores):
    strokes = [score['strokes'] - score['hole__par'] if score['strokes'] != None else None for score in scores if score['player_id'] == player and score['golf_round_id'] == golf_round['id']]
    clean_strokes = [item for item in strokes if item != None]
    if len(clean_strokes) == 18:
        final = sum(clean_strokes)
    else:
        final = None
    return final