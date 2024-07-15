import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from pong.views import PrivateView
from friends.models import FriendRequest, Friendship
from .models import Profile
from .serializers import (
    ProfileAliasSerializer,
    ProfileAvatarSerializer,
    ProfileStatusSerializer,
    ProfileSerializer,
)

logger = logging.getLogger('django')


class ProfileListView(PrivateView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

profile_list = ProfileListView.as_view()


class ProfileDetailView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

profile_detail = ProfileDetailView.as_view()


class ProfileRequestView(PrivateView):
    def post(self, request, profile_id):
        try:
            sender = Profile.objects.get(user=request.user)
            receiver = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            logger.error('Profile not found')
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        friend_request = FriendRequest.objects.create_request(sender=sender, receiver=receiver)
        logger.info(f'Friend request {friend_request.id} sent by {friend_request.sender.alias} to {friend_request.receiver.alias}')
        
        # TODO: remove later, only for testing purposes
        Friendship.objects.create_friendship_from_request(friend_request)
        logger.info(f'Friend request {friend_request.id} accepted by {friend_request.receiver.alias}')
        FriendRequest.objects.remove_request(friend_request)
        return Response({}, status=status.HTTP_201_CREATED)

profile_request = ProfileRequestView.as_view()


class ProfileRemoveView(PrivateView):
    def post(self, request, profile_id):
        try:
            removed_by = Profile.objects.get(user=request.user)
            to_remove = Profile.objects.get(id=profile_id)
        except Profile.DoesNotExist:
            logger.error('Profile not found')
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        friend_request = FriendRequest.objects.create_request(sender=sender, receiver=receiver)
        logger.info(f'Friend request {friend_request.id} sent by {friend_request.sender.alias} to {friend_request.receiver.alias}')
        
        # TODO: remove later, only for testing purposes
        Friendship.objects.create_friendship_from_request(friend_request)
        logger.info(f'Friend request {friend_request.id} accepted by {friend_request.receiver.alias}')
        FriendRequest.objects.remove_request(friend_request)
        return Response({}, status=status.HTTP_201_CREATED)

profile_remove = ProfileRemoveView.as_view()


# TODO
class ProfileBlockView(PrivateView):
    def post(self, request, profile_id):
        profile = get_object_or_404(Profile, user=request.user)
        profile_to_block = get_object_or_404(Profile, id=profile_id)
        Profile.objects.block_profile(profile, profile_to_block)
        return Response()
    
    def delete(self, request, profile_id):
        profile = get_object_or_404(Profile, user=request.user)
        profile_to_unblock = get_object_or_404(Profile, id=profile_id)
        Profile.objects.unblock_profile(profile, profile_to_unblock)
        return Response()

profile_block = ProfileBlockView.as_view()


# class ProfileMeView(PrivateView):
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data)

# profile_me = ProfileMeView.as_view()


# class ProfileAliasView(PrivateView):
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileAliasSerializer(profile)
#         return Response(serializer.data)
    
#     def patch(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileAliasSerializer(profile, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         logger.info(f'Profile {profile.id} changed their alias to {profile.alias}')
#         return Response(serializer.data)

# profile_alias = ProfileAliasView.as_view()


# class ProfileAvatarView(PrivateView):
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileAvatarSerializer(profile)
#         return Response(serializer.data)
    
#     def patch(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileAvatarSerializer(profile, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         logger.info(f'Profile {profile.id} changed their avatar')
#         return Response(serializer.data)

# profile_avatar = ProfileAvatarView.as_view()


# class ProfileStatusView(PrivateView):
#     def get(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileStatusSerializer(profile)
#         return Response(serializer.data)
    
#     def patch(self, request):
#         profile = get_object_or_404(Profile, user=request.user)
#         serializer = ProfileStatusSerializer(profile, data=request.data, partial=True)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         logger.info(f'Profile {profile.id} changed their status')
#         return Response(serializer.data)

# profile_status = ProfileStatusView.as_view()


class ProfileSearchView(PrivateView):
    def get(self, request):
        alias = request.query_params.get('alias', '')
        profiles = Profile.objects.search_by_alias(alias)
        if profiles.exists():
            profile_data = ProfileSerializer(profiles, many=True).data
            logger.info(f'Profiles found for alias "{alias}". First profile ID: {profiles[0].id}')
            response = Response(
                {
                    'status': _('Profiles found.'),
                    'profiles': profile_data,
                    'redirect': f'/profile/{profiles[0].id}/',
                },
                status=status.HTTP_200_OK,
            )
        else:
            logger.info(f'No profiles found for alias "{alias}".')
            response = Response(
                {
                    'status': _('No profiles found.'),
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        return response

profile_search = ProfileSearchView.as_view()