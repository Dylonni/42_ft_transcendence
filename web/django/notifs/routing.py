from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notif/<uuid:notif_id>/', consumers.notif_consumer),
]