from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('games/', views.game_list, name='game_list'),
    path('games/search/', views.game_search, name='game_search'),
    path('games/<uuid:game_id>/', views.game_detail, name='game_detail'),
	path('games/<uuid:game_id>/join/', views.game_join, name='game_join'),
	path('games/<uuid:game_id>/leave/', views.game_leave, name='game_leave'),
    path('games/<uuid:game_id>/start/', views.game_start, name='game_start'),
	path('games/<uuid:game_id>/ready/', views.game_ready, name='game_ready'),
]