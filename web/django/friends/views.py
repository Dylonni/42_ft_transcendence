import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from pong.views import PrivateView
from .models import Friendship, FriendMessage
from .serializers import FriendshipSerializer, FriendMessageSerializer

logger = logging.getLogger('django')


class FriendshipListView(PrivateView):
    def get(self, request):
        friendships = Friendship.objects.all()
        response_data = {'data': FriendshipSerializer(friendships, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

friend_list = FriendshipListView.as_view()