import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from profiles.models import Profile
from friends.models import Friendship
from .mixins import JWTCookieAuthenticationMixin, RedirectIfAuthenticatedMixin

UserModel = get_user_model()
logger = logging.getLogger('django')

def get_profile_context(request, profile_id=None):
    context = {}
    if profile_id:
        try:
            profile = Profile.objects.get(id=profile_id)
            context['profile'] = profile
            friends_ids = Friendship.objects.friends_ids_of_profile(profile)
            context['friends'] = Profile.objects.filter(id__in=friends_ids)
            return context
        except Profile.DoesNotExist:
            return context
    try:
        profile = Profile.objects.get(user=request.user)
        context['profile'] = profile
        friends_ids = Friendship.objects.friends_ids_of_profile(profile)
        context['friends'] = Profile.objects.filter(id__in=friends_ids)
    except Profile.DoesNotExist:
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


class PublicView(RedirectIfAuthenticatedMixin, APIView):
    permission_classes = (AllowAny,)


class PrivateView(JWTCookieAuthenticationMixin, APIView):
    permission_classes = (IsAuthenticated,)


class IndexView(PublicView):
    def get(self, request):
        return render_with_sub_template(request, 'accounts/login.html', _('Login'))

index = IndexView.as_view()


class LoginView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/login.html', _('Login'), False)

login = LoginView.as_view()


class RegisterView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/register.html', _('Register'), False)

register = RegisterView.as_view()

class ForgotPasswordView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/forgot_password.html', _('Forgot Password'), False)

forgot_password = ForgotPasswordView.as_view()


class HomeView(PrivateView):
    def get(self, request):
        return render_response(request, 'home.html', _('Home'), True)

home = HomeView.as_view()


class ProfileView(PrivateView):
    def get(self, request):
        return render_response(request, 'profile.html', _('Profile'), True)

profile = ProfileView.as_view()


class ProfileOtherView(PrivateView):
    def get(self, request, profile_id):
        context = {}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            context = get_profile_context(request, profile_id)
            context['title'] = _('Profile')
            html = render_to_string('profile.html', context, request)
            return HttpResponse(html)
        context = get_profile_context(request, profile_id)
        return render_with_sub_template(request, 'profile.html', _('Profile'), context)

profile_other = ProfileOtherView.as_view()


class LeaderboardView(PrivateView):
    def get(self, request):
        return render_response(request, 'leaderboard.html', _('Leaderboard'), False)

leaderboard = LeaderboardView.as_view()


class SocialView(PrivateView):
    def get(self, request):
        return render_response(request, 'social.html', _('Social'), True)

social = SocialView.as_view()


class SettingsView(PrivateView):
    def get(self, request):
        return render_response(request, 'settings.html', _('Settings'), True)

settings = SettingsView.as_view()