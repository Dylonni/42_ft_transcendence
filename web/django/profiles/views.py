import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Profile
from .serializers import (
    ProfileAliasSerializer,
    ProfileAvatarSerializer,
    ProfileStatusSerializer,
    ProfileSerializer,
)

logger = logging.getLogger('django')


class ProfileListView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

profile_list = ProfileListView.as_view()


class ProfileDetailView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

profile_detail = ProfileDetailView.as_view()


# TODO
class ProfileBlockView(APIView):
    permission_classes = (IsAuthenticated,)
    
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


class ProfileMeView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

profile_me = ProfileMeView.as_view()


class ProfileAliasView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileAliasSerializer(profile)
        return Response(serializer.data)
    
    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileAliasSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f'Profile {profile.id} changed their alias to {profile.alias}')
        return Response(serializer.data)

profile_alias = ProfileAliasView.as_view()


class ProfileAvatarView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileAvatarSerializer(profile)
        return Response(serializer.data)
    
    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileAvatarSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f'Profile {profile.id} changed their avatar')
        return Response(serializer.data)

profile_avatar = ProfileAvatarView.as_view()


class ProfileStatusView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileStatusSerializer(profile)
        return Response(serializer.data)
    
    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        serializer = ProfileStatusSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(f'Profile {profile.id} changed their status')
        return Response(serializer.data)

profile_status = ProfileStatusView.as_view()


class ProfileSearchView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        alias = request.query_params.get('alias', '')
        profiles = Profile.objects.search_by_alias(alias)
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

profile_search = ProfileSearchView.as_view()