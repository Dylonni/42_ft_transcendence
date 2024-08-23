from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/games/<uuid:game_id>/', consumers.game_chat_consumer),
	path('ws/games/<uuid:game_id>/play/', consumers.game_play_consumer),
]