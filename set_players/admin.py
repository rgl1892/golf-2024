from django.contrib import admin
from .models import Player, Holiday, Course, Resort,Score,Hole

# Register your models here.
admin.site.register(Player)
admin.site.register(Holiday)
admin.site.register(Course)
admin.site.register(Resort)
admin.site.register(Score)
admin.site.register(Hole)