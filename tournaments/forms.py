from django import forms
from .models import Tournament, Holiday, GolfRound, Score, Player, Hole, Handicap, Course,Resort,Video


list_of_players = [(player.id,player) for player in Player.objects.all()]
holes = [(x,x) for x in range(19)]
holidays = [(holiday.id,holiday) for holiday in Holiday.objects.all()]
round_choices = [(x+1,x+1) for x in range(5)]

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50,widget=forms.TextInput(attrs={'class': 'form-control'}))
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    player = forms.ChoiceField(choices=list_of_players,required=False,widget=forms.Select(attrs={'class': 'form-select'}))
    holiday = forms.ChoiceField(choices=holidays,required=False,widget=forms.Select(attrs={'class': 'form-select'}))
    round_number = forms.ChoiceField(choices=round_choices,widget=forms.Select(attrs={'class': 'form-select'}))
    hole = forms.ChoiceField(choices=holes,required=False,widget=forms.Select(attrs={'class': 'form-select'}))