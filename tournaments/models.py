from django.db import models
from datetime import datetime

# Create your models here.

class Tournament(models.Model):
    name = models.CharField(max_length=20)
    slug = models.SlugField(default="", null=False)

    def __str__(self):
        return f'{self.name}'

class Player(models.Model):
    first_name = models.CharField(max_length=20) 
    last_name = models.CharField(max_length=20)
    handedness = models.CharField(max_length=20)
    championships = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

class Resort(models.Model):
    name = models.CharField(max_length=20)
    country = models.CharField(max_length=20)
    latitude = models.DecimalField(decimal_places=6,max_digits=9)
    longitude = models.DecimalField(decimal_places=6,max_digits=9)

    def __str__(self) -> str:
        return f"{self.name}"

class Holiday(models.Model):
    resort = models.ForeignKey(Resort,on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament,on_delete=models.CASCADE)
    holiday_number = models.IntegerField()
    slug = models.SlugField(default="", null=False)

    def __str__(self) -> str:
        return f"{self.tournament} {self.holiday_number}"
    
class GolfRound(models.Model):
    round_number = models.IntegerField()
    holiday = models.ForeignKey(Holiday,on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=datetime(2018,11,5))

    def __str__(self):
        return f"{self.holiday} {self.round_number}"
    
class Handicap(models.Model):
    handicap_index = models.DecimalField(decimal_places=1,max_digits=3)
    player = models.ForeignKey(Player,on_delete=models.CASCADE)
    holiday = models.ForeignKey(Holiday,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.player}'s Handicap Index for {self.holiday}"

class Course(models.Model):
    course_name = models.CharField(max_length=20)
    resort = models.ForeignKey(Resort,on_delete=models.CASCADE)
    tee = models.CharField(max_length=20)
    slope_rating = models.IntegerField()
    course_rating = models.DecimalField(decimal_places=1,max_digits=3)
    slug = models.SlugField(default="", null=False)

    def __str__(self) -> str:
        return f"{self.course_name} {self.tee} Tees"
    
class Hole(models.Model):

    course = models.ForeignKey(Course,on_delete=models.CASCADE)
    yards = models.IntegerField()
    par = models.IntegerField(choices=[(3,3),(4,4),(5,5)])
    stroke_index = models.IntegerField(choices=[(x+1,x+1) for x in range(18)])
    hole_number = models.IntegerField(choices=[(x+1,x+1) for x in range(18)])


    def __str__(self) -> str:
        return f"{self.course} Hole {self.hole_number}"

class ProTip(models.Model):
    hole = models.ManyToManyField(Hole,blank=True)
    pro_tip = models.TextField(default="Pro Tip")

    
    
class Video(models.Model):
    file = models.FileField(upload_to='')
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(blank=True)

    def __str__(self) -> str:
            return self.title   
     
class Score(models.Model): 
    player = models.ForeignKey(Player,on_delete=models.CASCADE)
    hole = models.ForeignKey(Hole,on_delete=models.CASCADE)
    
    golf_round = models.ForeignKey(GolfRound,on_delete=models.CASCADE)
    strokes = models.IntegerField(blank=True,null=True)
    stableford_score = models.IntegerField(blank=True,null=True)
    sandy = models.BooleanField(default=False)
    handicap = models.ForeignKey(Handicap,on_delete=models.CASCADE,blank=True,null=True)
    highlight_link = models.ManyToManyField(Video,blank=True)
    

    def __str__(self):
        return f"{self.player} {self.hole} Score {self.golf_round}"
    