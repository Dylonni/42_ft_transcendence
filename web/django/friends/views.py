import logging
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from pong.views import PrivateView
from .models import Friendship, FriendMessage
from .serializers import FriendshipSerializer, FriendMessageSerializer

logger = logging.getLogger('django')


class FriendshipListView(PrivateView):
    def get(self, request):
        friendships = Friendship.objects.all()
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data)

friend_list = FriendshipListView.as_view()