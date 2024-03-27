from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('',views.Home.as_view(),name='homepage' ),
    path('stats',views.StatsView.as_view(),name='stats'),
    path('player_stats',views.PlayerStats.as_view(),name='player_stats'),
    path('login',views.logInUser,name='login'),
    path('logout',views.logOutUser,name='logout'),
    path('sign_up_user', views.signUpUser,name='sign_up_user'),
    path('courses', views.CoursesOverview.as_view(),name='courses'),
    path('highlights',views.HighlightsHome.as_view(),name='highlights'),
    path('highlights/new',views.uploadHighlight,name='new_highlight'),
    path('highlights/<int:highlight>',views.HighlightView.as_view(),name='highlight_view'),
    path('<slug:tournament>/',views.TournamentView.as_view(),name='tournament'),
    path('<slug:tournament>/<slug:holiday>',views.RoundsView.as_view(),name='rounds'),
    path('<slug:tournament>/<slug:holiday>/<int:selected_round>',views.ScoresView.as_view(),name='scores'),
    path('<slug:tournament>/<slug:holiday>/<int:selected_round>/<int:hole>',views.EditScoresView.as_view(),name='edit_scores'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)