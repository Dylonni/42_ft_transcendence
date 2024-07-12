import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from profiles.models import Profile
from profiles.views import profile_detail
from .models import FriendRequest, Friendship, FriendMessage
from .serializers import FriendMessageSerializer, FriendRequestSerializer, FriendshipSerializer

logger = logging.getLogger('django')


class FriendshipListView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        profile = Profile.objects.get(id=profile_id)
        friendships = Friendship.objects.friendships(profile)
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data)

friend_list = FriendshipListView.as_view()


class FriendshipDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        return profile_detail(request, profile_id=profile_id)
    
    def delete(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        removed_by = Profile.objects.get_by_user(request.user)
        Friendship.objects.remove_friendship(removed_by, profile)
        logger.info(f'Friend {profile.alias} removed by {removed_by.alias}')
        return Response(status=status.HTTP_204_NO_CONTENT)

friend_detail = FriendshipDetailView.as_view()


class FriendSearchView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        alias = request.query_params.get('alias', '')
        friends = Friendship.objects.search_by_alias(alias)
        serializer = FriendshipSerializer(friends, many=True)
        return Response(serializer.data)

friend_search = FriendSearchView.as_view()


class FriendRequestListCreateView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        profile = Profile.objects.get(id=profile_id)
        requests = FriendRequest.objects.pending_requests(profile)
        serializer = FriendRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FriendRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        friend_request = FriendRequest.objects.create_request(
            sender=serializer.validated_data['sender'],
            receiver=serializer.validated_data['receiver'],
        )
        logger.info(f'Friend request {friend_request.id} sent by {friend_request.sender} to {friend_request.receiver}')
        return Response(status=status.HTTP_201_CREATED)

friend_request_list_create = FriendRequestListCreateView.as_view()


class FriendRequestDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def delete(self, request, request_id):
        try:
            FriendRequest.objects.remove_request_by_id(request_id)
            logger.info(f'Friend request {request_id} declined by {request.user}')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except FriendRequest.DoesNotExist:
            logger.error(f'Friend request {request_id} does not exist')
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request, request_id):
        try:
            friend_request = FriendRequest.objects.get(id=request_id)
            Friendship.objects.create_friendship_from_request(friend_request)
            FriendRequest.objects.remove_request(friend_request)
            logger.info(f'Friend request {request_id} accepted by {request.user}')
            return Response(status=status.HTTP_201_CREATED)
        except FriendRequest.DoesNotExist:
            logger.error(f'Friend request {request_id} does not exist')
            return Response(status=status.HTTP_404_NOT_FOUND)

friend_request_detail = FriendRequestDetailView.as_view()


class FriendMessageView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, receiver_id):
        sender = get_object_or_404(Profile, user=request.user)
        receiver = get_object_or_404(Profile, id=receiver_id)
        message = request.data.get('message')
        if not message:
            return Response({'error': 'Message content cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)
        friendship_id = Friendship.objects.get_id(sender, receiver)
        if not friendship_id:
            return Response({'error': 'You can only send messages to friends.'}, status=status.HTTP_400_BAD_REQUEST)
        friend_message = FriendMessage.objects.send_message(sender, receiver, message, friendship_id)
        serializer = FriendMessageSerializer(friend_message)
        logger.error(f'Friend message from {sender.alias} to {receiver.alias}: {message}')
        return Response(serializer.data, status=status.HTTP_201_CREATED)

friend_message = FriendMessageView.as_view()


class FriendConversationView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        user_profile = get_object_or_404(Profile, user=request.user)
        other_profile = get_object_or_404(Profile, id=profile_id)
        conversation = FriendMessage.objects.get_conversation(user_profile, other_profile)
        serializer = FriendMessageSerializer(conversation, many=True)
        return Response(serializer.data)

friend_conversation = FriendConversationView.as_view()