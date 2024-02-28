from rest_framework import serializers
from tournaments.models import *

class TournamentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ['id','name']
        
class HoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hole
        fields = '__all__'
        depth = 1

class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields =['strokes','hole','player','sandy','stableford_score','golf_round']
        depth = 1