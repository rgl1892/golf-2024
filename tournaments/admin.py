from django.contrib import admin
from .models import Player, Holiday, Course, Resort,Score,Hole,Handicap,Tournament,GolfRound,Video

# Register your models here.


class TournamentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug":["name"]}

class HolidayAdmin(admin.ModelAdmin):
    list_display = ["resort","tournament","holiday_number","id"]
    prepopulated_fields = {"slug":["resort","holiday_number"]}
    
    
admin.site.register(Player)
admin.site.register(Holiday,HolidayAdmin)
admin.site.register(Course)
admin.site.register(GolfRound)
admin.site.register(Resort)
admin.site.register(Score)
admin.site.register(Hole)
admin.site.register(Handicap)
admin.site.register(Tournament,TournamentAdmin)
admin.site.register(Video)
