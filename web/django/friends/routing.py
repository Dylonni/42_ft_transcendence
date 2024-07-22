from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<uuid:friendship_id>/', consumers.chat_consumer),
]