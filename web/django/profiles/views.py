import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from pong.views import PrivateView
from friends.models import FriendRequest, FriendMessage, Friendship
from friends.serializers import FriendRequestSerializer, FriendshipSerializer, FriendMessageSerializer
from games.models import GameInvite
from games.serializers import GameInviteSerializer

from .models import Profile, ProfileBlock
from .serializers import ProfileSerializer, ProfileBlockSerializer

logger = logging.getLogger('django')


class ProfileListView(PrivateView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

profile_list = ProfileListView.as_view()


class ProfileSearchView(PrivateView):
    def get(self, request):
        alias = request.query_params.get('alias', '')
        profiles = Profile.objects.search_by_alias(alias)
        if profiles.exists():
            logger.info(f'Profiles found for alias "{alias}".')
            profiles_data = ProfileSerializer(profiles, many=True).data
            return Response(profiles_data, status=status.HTTP_200_OK)
        else:
            logger.info(f'No profiles found for alias "{alias}".')
            return Response(status=status.HTTP_204_NO_CONTENT)

profile_search = ProfileSearchView.as_view()


# TODO: add methods to patch alias, avatar and status
class MyDetailView(PrivateView):
    def get(self, request):
        serializer = ProfileSerializer(request.profile)
        return Response(serializer.data)

my_detail = MyDetailView.as_view()


class ProfileDetailView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

profile_detail = ProfileDetailView.as_view()


class ProfileInviteListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        received_invites = GameInvite.objects.get_received_invites(profile)
        serializer = GameInviteSerializer(received_invites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        sender = get_object_or_404(Profile, id=request.profile.id)
        receiver = get_object_or_404(Profile, id=profile_id)
        try:
            game_invite = GameInvite.objects.create_invite(sender=sender, receiver=receiver)
            logger.info(f'Game invite {game_invite.id} sent by {sender.alias} to {receiver.alias}.')
            serializer = GameInviteSerializer(game_invite)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

profile_invite_list = ProfileInviteListView.as_view()


class ProfileBlockListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        blocked_profiles = ProfileBlock.objects.get_blocked_profiles(profile)
        serializer = ProfileBlockSerializer(blocked_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        blocker = get_object_or_404(Profile, id=request.profile.id)
        blocked = get_object_or_404(Profile, id=profile_id)
        try:
            profile_block = ProfileBlock.objects.create_block(blocker=blocker, blocked=blocked)
            logger.info(f'Profile block {profile_block.id} executed by {blocker.alias} against {blocked.alias}.')
            serializer = ProfileBlockSerializer(profile_block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

profile_block_list = ProfileBlockListView.as_view()


class ProfileRequestListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        pending_requests = FriendRequest.objects.get_pending_requests(profile)
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        sender = get_object_or_404(Profile, id=request.profile.id)
        receiver = get_object_or_404(Profile, id=profile_id)
        try:
            friend_request = FriendRequest.objects.create_request(sender=sender, receiver=receiver)
            logger.info(f'Friend request {friend_request.id} sent by {sender.alias} to {receiver.alias}.')
            serializer = FriendRequestSerializer(friend_request)
            
            # TODO: remove later, only for testing purposes
            Friendship.objects.create_friendship_from_request(friend_request)
            logger.info(f'Friend request {friend_request.id} accepted by {receiver.alias}.')
            FriendRequest.objects.remove_request(friend_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

profile_request_list = ProfileRequestListView.as_view()


class ProfileFriendListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        friendships = Friendship.objects.get_friendships(profile)
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

profile_friend_list = ProfileFriendListView.as_view()


class MyInviteListView(PrivateView):
    def get(self, request):
        received_invites = GameInvite.objects.get_received_invites(request.profile)
        serializer = GameInviteSerializer(received_invites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

my_invite_list = MyInviteListView.as_view()


class MyInviteDetailView(PrivateView):
    def post(self, request, invite_id):
        try:
            GameInvite.objects.accept_invite(invite_id)
            logger.info(f'Game invite {invite_id} accepted by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, invite_id):
        try:
            GameInvite.objects.decline_invite(invite_id)
            logger.info(f'Game invite {invite_id} declined by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_invite_detail = MyInviteDetailView.as_view()


class MyBlockListView(PrivateView):
    def get(self, request):
        blocked_profiles = ProfileBlock.objects.get_blocked_profiles(request.profile)
        serializer = ProfileBlockSerializer(blocked_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

my_block_list = MyBlockListView.as_view()


class MyBlockDetailView(PrivateView):
    def delete(self, request, block_id):
        try:
            ProfileBlock.objects.remove_block(block_id)
            logger.info(f'Profile block {block_id} removed by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_block_detail = MyBlockDetailView.as_view()


class MyRequestListView(PrivateView):
    def get(self, request):
        pending_requests = FriendRequest.objects.get_pending_requests(request.profile)
        serializer = FriendRequestSerializer(pending_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

my_request_list = MyRequestListView.as_view()


class MyRequestDetailView(PrivateView):
    def post(self, request, request_id):
        try:
            FriendRequest.objects.accept_request(request_id)
            logger.info(f'Friend request {request_id} accepted by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, request_id):
        try:
            FriendRequest.objects.decline_request(request_id)
            logger.info(f'Friend request {request_id} declined by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_request_detail = MyRequestDetailView.as_view()


class MyFriendListView(PrivateView):
    def get(self, request):
        friendships = Friendship.objects.get_friendships(request.profile)
        serializer = FriendshipSerializer(friendships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

my_friend_list = MyFriendListView.as_view()


class MyFriendDetailView(PrivateView):
    def delete(self, request, friendship_id):
        try:
            Friendship.objects.remove_friendship(friendship_id)
            logger.info(f'Friendship {friendship_id} removed by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_friend_detail = MyFriendDetailView.as_view()


class MyFriendMessageListView(PrivateView):
    def get(self, request, friendship_id):
        messages = FriendMessage.objects.get_messages(friendship_id)
        serializer = FriendMessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, friendship_id):
        try:
            sender = request.profile
            receiver = Friendship.objects.get_other(friendship_id, sender)
            friendship = Friendship.objects.get(id=friendship_id)
            message = request.data['message']
            friend_message = FriendMessage.objects.send_message(sender, receiver, message, friendship)
            logger.info(f'Friend message {friend_message.id} sent by {sender.alias} to {friend_message.receiver.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_friend_message_list = MyFriendMessageListView.as_view()


class MyFriendMessageDetailView(PrivateView):
    # TODO: add method to edit message
    def delete(self, request, friendship_id, message_id):
        try:
            FriendMessage.objects.remove_message(message_id)
            logger.info(f'Friend message {message_id} removed by {request.profile.alias}.')
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

my_friend_message_detail = MyFriendMessageDetailView.as_view()