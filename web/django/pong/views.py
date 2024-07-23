import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.auth.models import AnonymousUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from profiles.models import Profile
from friends.models import Friendship, FriendMessage
from .mixins import JWTCookieAuthenticationMixin, LangVerificationMixin, RedirectIfAuthenticatedMixin

UserModel = get_user_model()
logger = logging.getLogger('django')

def get_profile_context(request, profile_id=None):
    context = {}
    try:
        if profile_id:
            profile = Profile.objects.get(id=profile_id)
        else: 
            if request.user.id:
                profile = Profile.objects.get(user=request.user)
            else:
                profile = None
        context['profile'] = profile
        return context
    except Profile.DoesNotExist:
        return context

def get_friend_context(request, profile_id=None):
    context = get_profile_context(request)
    try:
        profile = context.get('profile', None)
        if profile is None:
            return context
        friends_ids = Friendship.objects.get_friend_ids(profile)
        context['friends'] = Profile.objects.filter(id__in=friends_ids)
        return context
    except Profile.DoesNotExist:
        return context

def render_with_sub_template(request, path, title, context={}):
    sub_template = render_to_string(path, context, request)
    context = {
        'sub_template': sub_template,
        'title': title,
    }
    return render(request, 'index.html', context)

def render_response(request, path, title, context={}):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context['title'] = title
        html = render_to_string(path, context, request)
        return HttpResponse(html)
    return render_with_sub_template(request, path, title, context)


class PublicView(RedirectIfAuthenticatedMixin, LangVerificationMixin, APIView):
    permission_classes = (AllowAny,)


class PrivateView(JWTCookieAuthenticationMixin, LangVerificationMixin, APIView):
    permission_classes = (IsAuthenticated,)


class IndexView(PublicView):
    def get(self, request):
        context = get_profile_context(request)
        return render_with_sub_template(request, 'modeselect.html', _('Transcendence'), context)

index = IndexView.as_view()


class LoginView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/login.html', _('Login'))

login = LoginView.as_view()


class RegisterView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/register.html', _('Register'))

register = RegisterView.as_view()


class ForgotPasswordView(PublicView):
    def get(self, request):
        return render_response(request, 'accounts/forgot_password.html', _('Forgot Password'))

forgot_password = ForgotPasswordView.as_view()


class HomeView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'home.html', _('Home'), context)

home = HomeView.as_view()

class SelectGameView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'modeselect.html', _('Choose Mode'), context)

select_game = SelectGameView.as_view()

class CustomizeGameView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'customize_game.html', _('Customize Game'), context)

customize_game = CustomizeGameView.as_view()

class ProfileView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'profile.html', _('Profile'), context)

profile = ProfileView.as_view()


class ProfileOtherView(PrivateView):
    def get(self, request, profile_id):
        context = get_profile_context(request, profile_id)
        return render_response(request, 'profile.html', _('Profile'), context)

profile_other = ProfileOtherView.as_view()


class LeaderboardView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'leaderboard.html', _('Leaderboard'), context)

leaderboard = LeaderboardView.as_view()


class SocialView(PrivateView):
    def get(self, request):
        friends_ids = Friendship.objects.get_friend_ids(request.profile)
        if friends_ids:
            first_friend_id = next(iter(friends_ids))
            first_friend = Profile.objects.get(id=first_friend_id)
            friendship_id = Friendship.objects.get_friendship_id(request.profile, first_friend)
            if friendship_id:
                return redirect(f'/friends/{friendship_id}/')
        return render_response(request, 'social.html', _('Social'))

social = SocialView.as_view()


class SocialFriendView(PrivateView):
    def get(self, request, friend_id):
        context = get_friend_context(request)
        context['messages'] = FriendMessage.objects.get_messages(friend_id)
        return render_response(request, 'social.html', _('Social'), context)

social_friend = SocialFriendView.as_view()


class SettingsView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render_response(request, 'settings.html', _('Settings'), context)

settings = SettingsView.as_view()


class LangReloadView(PublicView):
    def post(self, request, lang):
        logger.info(f'Changing language to: "{lang}".')
        path = request.data.get('path')
        translation.activate(lang)
        response = redirect(path)
        response.set_cookie(
            key='lang',
            value=lang,
        )
        return response

lang_reload = LangReloadView.as_view()