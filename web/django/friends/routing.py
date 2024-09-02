from django.urls import path
from . import consumers

websocket_urlpatterns = [
	path('ws/friends/', consumers.friend_list_consumer),
    path('ws/friends/<uuid:friendship_id>/', consumers.friend_chat_consumer),
]