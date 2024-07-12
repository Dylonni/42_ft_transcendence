import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from profiles.models import Profile

UserModel = get_user_model()
logger = logging.getLogger('django')

def get_profile_context(request):
    context = {}
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer '):
        access_token = auth_header.split(' ')[1]
        try:
            access_token_obj = AccessToken(access_token)
            user_id = access_token_obj['user_id']
            user = UserModel.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)
            context['profile'] = profile
            return context
        except Exception as e:
            return context
    return context

def render_with_sub_template(request, path, title, context={}):
    sub_template = render_to_string(path, context, request)
    context = {
        'sub_template': sub_template,
        'title': title,
    }
    return render(request, 'index.html', context)

def render_response(request, path, title, need_auth):
    context = {}
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if need_auth:
            context = get_profile_context(request)
        context['title'] = title
        html = render_to_string(path, context, request)
        return HttpResponse(html)
    if need_auth:
        context = get_profile_context(request)
    return render_with_sub_template(request, path, title, context)


class IndexView(APIView):
    def get(self, request):
        return render_with_sub_template(request, 'accounts/login.html', _('Login'))

index = IndexView.as_view()


class LoginView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/home/')
        return render_response(request, 'accounts/login.html', _('Login'), False)

login = LoginView.as_view()


class RegisterView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/home/')
        return render_response(request, 'accounts/register.html', _('Register'), False)

register = RegisterView.as_view()


class HomeView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        return render_response(request, 'home.html', _('Home'), True)

home = HomeView.as_view()


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        return render_response(request, 'profile.html', _('Profile'), True)

profile = ProfileView.as_view()


class LeaderboardView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        return render_response(request, 'leaderboard.html', _('Leaderboard'), True)

leaderboard = LeaderboardView.as_view()


class SocialView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        return render_response(request, 'social.html', _('Social'), True)

social = SocialView.as_view()


class SettingsView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        return render_response(request, 'settings.html', _('Settings'), True)

settings = SettingsView.as_view()

# def verify_jwt_cookies(request):
#     access_token = request.COOKIES.get('access_token')
#     refresh_token = request.COOKIES.get('refresh_token')
    
#     if not access_token:
#         logger.info('No access token found in cookies.')
#         return False
    
#     try:
#         AccessToken(access_token)
#     except TokenError:
#         logger.info('Invalid access token. Trying to refresh.')
#         if not refresh_token:
#             logger.warning('No refresh token found in cookies.')
#             return False
#         try:
#             refresh = RefreshToken(refresh_token)
#             access_token, refresh_token = str(refresh.access_token), str(refresh)
#         except TokenError:
#             logger.error('Invalid refresh token.')
#             return False
    
#     request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
#     return True