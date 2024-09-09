import logging
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from pong.views import PrivateView
from accounts.utils import unset_jwt_cookies
from friends.models import FriendRequest, FriendMessage, Friendship
from friends.serializers import FriendRequestSerializer, FriendshipSerializer, FriendMessageSerializer
from games.models import GameInvite
from games.serializers import GameInviteSerializer
from notifs.models import Notification

from .models import Profile, ProfileBlock
from .serializers import ProfileSerializer, ProfileBlockSerializer

logger = logging.getLogger('django')


class ProfileListView(PrivateView):
    def get(self, request):
        profiles = Profile.objects.all()
        if request.query_params.get('excludeself', None):
            profiles = profiles.exclude(id=request.profile.id)
        response_data = {'data': ProfileSerializer(profiles, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

profile_list = ProfileListView.as_view()


class ProfileSearchView(PrivateView):
    def get(self, request):
        alias = request.query_params.get('alias', '')
        profiles = Profile.objects.search_by_alias(alias)
        if not profiles.exists():
            response_data = {'message': _('Profile not found.')}
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = {'data': ProfileSerializer(profiles, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

profile_search = ProfileSearchView.as_view()


class MyDetailView(PrivateView):
    def get(self, request):
        response_data = {'data': ProfileSerializer(request.profile).data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def delete(self, request):
        if not request.user.check_password(request.data['password']):
            response_data = {'error': _('Incorrect password.')}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        # TODO: delete friends, messages, replace match history with placeholder
        Notification.objects.remove_all_for_profile(request.profile)
        user = request.user
        user.is_active = False
        user.save()
        response_data = {'message': _('Account deleted.'), 'redirect': '/'}
        response = Response(response_data, status=status.HTTP_200_OK)
        unset_jwt_cookies(response)
        return response

my_detail = MyDetailView.as_view()


class MyAliasView(PrivateView):
    def post(self, request):
        serializer = ProfileSerializer(request.profile, data=request.data, partial=True)
        if not serializer.is_valid():
            response_data = {'error': _('Alias already taken.')}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        response_data = {'message': _('Alias updated.'), 'redirect': '/settings/'}
        return Response(response_data, status=status.HTTP_200_OK)

my_alias = MyAliasView.as_view()


class MyAvatarView(PrivateView):
    def post(self, request):
        img_id = request.query_params.get('id', None)
        if img_id:
            profile = request.profile
            profile.set_avatar_url(id=img_id, path=request.user.fortytwo_avatar_url)
        else:
            serializer = ProfileSerializer(request.profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
            else:
                response_data = {'error': serializer.errors}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = {'message': _('Avatar updated.'), 'redirect': '/settings/'}
        return Response(response_data, status=status.HTTP_200_OK)

my_avatar = MyAvatarView.as_view()


class MyLangView(PrivateView):
    def post(self, request, lang):
        request.profile.set_default_lang(lang)
        translation.activate(lang)
        response_data = {'message': _('Default language changed.'), 'redirect': '/settings/'}
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='lang',
            value=lang,
        )
        return response

my_lang = MyLangView.as_view()


class MyEmailView(PrivateView):
    def post(self, request):
        # TODO: logic to send email
        response_data = {'message': _('Email to change email sent.')}
        return Response(response_data, status=status.HTTP_200_OK)

my_email = MyEmailView.as_view()


class MyPasswordView(PrivateView):
    def post(self, request):
        # TODO: logic to send email
        response_data = {'message': _('Email to change password sent.')}
        return Response(response_data, status=status.HTTP_200_OK)

my_password = MyPasswordView.as_view()


class ProfileDetailView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        response_data = {'data': ProfileSerializer(profile).data}
        return Response(response_data, status=status.HTTP_200_OK)

profile_detail = ProfileDetailView.as_view()


class ProfileInviteListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        received_invites = GameInvite.objects.get_received_invites(profile)
        response_data = {'data': GameInviteSerializer(received_invites, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        try:
            sender = get_object_or_404(Profile, id=request.profile.id)
            receiver = get_object_or_404(Profile, id=profile_id)
            GameInvite.objects.create_invite(sender=sender, receiver=receiver)
            response_data = {'message': _('Game invitation sent.')}
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

profile_invite_list = ProfileInviteListView.as_view()


class ProfileBlockListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        blocked_profiles = ProfileBlock.objects.get_blocked_profiles(profile)
        response_data = {'data': ProfileBlockSerializer(blocked_profiles, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        try:
            blocker = get_object_or_404(Profile, id=request.profile.id)
            blocked = get_object_or_404(Profile, id=profile_id)
            ProfileBlock.objects.create_block(blocker=blocker, blocked=blocked)
            response_data = {'message': _('Profile blocked.')}
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

profile_block_list = ProfileBlockListView.as_view()


class ProfileRequestListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        pending_requests = FriendRequest.objects.get_pending_requests(profile)
        response_data = {'data': FriendRequestSerializer(pending_requests, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request, profile_id):
        try:
            sender = get_object_or_404(Profile, id=request.profile.id)
            receiver = get_object_or_404(Profile, id=profile_id)
            friend_request = FriendRequest.objects.filter(sender=receiver, receiver=sender).first()
            if friend_request:
                Friendship.objects.create_friendship_from_request(friend_request)
                response_data = {'message': _('Friend request accepted.')}
                return Response(response_data, status=status.HTTP_200_OK)
            FriendRequest.objects.create_request(sender=sender, receiver=receiver)
            response_data = {'message': _('Friend request sent.')}
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

profile_request_list = ProfileRequestListView.as_view()


class ProfileFriendListView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        friendships = Friendship.objects.get_friendships(profile)
        response_data = {'data': FriendshipSerializer(friendships, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

profile_friend_list = ProfileFriendListView.as_view()


class MyInviteListView(PrivateView):
    def get(self, request):
        received_invites = GameInvite.objects.get_received_invites(request.profile)
        response_data = {'data': GameInviteSerializer(received_invites, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

my_invite_list = MyInviteListView.as_view()


class MyInviteDetailView(PrivateView):
    def post(self, request, invite_id):
        try:
            invite = get_object_or_404(GameInvite, id=invite_id)
            game_id = invite.game.id
            GameInvite.objects.accept_invite(invite)
            response_data = {'message': _('Game invitation accepted.'), 'redirect': f'/games/{game_id}/'}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, invite_id):
        try:
            invite = get_object_or_404(GameInvite, id=invite_id)
            GameInvite.objects.decline_invite(invite)
            response_data = {'message': _('Game invitation declined.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

my_invite_detail = MyInviteDetailView.as_view()


class MyBlockListView(PrivateView):
    def get(self, request):
        blocked_profiles = ProfileBlock.objects.get_blocked_profiles(request.profile)
        response_data = {'data': ProfileBlockSerializer(blocked_profiles, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

my_block_list = MyBlockListView.as_view()


class MyBlockDetailView(PrivateView):
    def delete(self, request, block_id):
        block = get_object_or_404(ProfileBlock, id=block_id)
        block.delete()
        response_data = {'message': _('Profile unblocked.')}
        return Response(response_data, status=status.HTTP_200_OK)

my_block_detail = MyBlockDetailView.as_view()


class MyRequestListView(PrivateView):
    def get(self, request):
        pending_requests = FriendRequest.objects.get_pending_requests(request.profile)
        response_data = {'data': FriendRequestSerializer(pending_requests, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

my_request_list = MyRequestListView.as_view()


class MyRequestDetailView(PrivateView):
    def post(self, request, request_id):
        try:
            friend_request = get_object_or_404(FriendRequest, id=request_id)
            Friendship.objects.create_friendship_from_request(friend_request)
            response_data = {'message': _('Friend request accepted.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, request_id):
        try:
            friend_request = get_object_or_404(FriendRequest, id=request_id)
            FriendRequest.objects.decline_request(friend_request)
            response_data = {'message': _('Friend request declined.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

my_request_detail = MyRequestDetailView.as_view()


class MyFriendListView(PrivateView):
    def get(self, request):
        friendships = Friendship.objects.get_friendships(request.profile)
        response_data = {'data': FriendshipSerializer(friendships, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

my_friend_list = MyFriendListView.as_view()


class MyFriendDetailView(PrivateView):
    def delete(self, request, friendship_id):
        try:
            friendship = get_object_or_404(Friendship, id=friendship_id)
            Friendship.objects.remove_friendship(friendship, request.profile)
            response_data = {'message': _('Friend removed.'), 'redirect': '/friends/'}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

my_friend_detail = MyFriendDetailView.as_view()


class MyFriendMessageListView(PrivateView):
    def get(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, id=friendship_id)
        serializer = FriendMessageSerializer(friendship.messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, friendship_id):
        try:
            friendship = get_object_or_404(Friendship, id=friendship_id)
            FriendMessage.objects.send_message(friendship, request.profile, request.data['message'])
            response_data = {'message': _('Message sent.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

my_friend_message_list = MyFriendMessageListView.as_view()