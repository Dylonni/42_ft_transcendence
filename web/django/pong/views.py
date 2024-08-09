import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from profiles.models import Profile
from friends.models import Friendship, FriendMessage
from games.models import Game
from notifs.models import Notification
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
        friendships_ids = Friendship.objects.get_friendships_ids(profile)
        context['friends'] = Profile.objects.filter(id__in=friendships_ids)
        return context
    except Profile.DoesNotExist:
        return context

def get_game_context(context={}):
    try:
        games = Game.objects.all()
        context['games'] = games
        # TODO: refactor model to retrieve game host and player count
        # for i, game in enumerate(games):
        #     context['games'][i]['host'] = Player.objects.get(game=game, is_host=True).profile.alias
        #     context['games'][i]['count'] = Player.objects.get(game=game).count()
        return context
    except Game.DoesNotExist:
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
        return render(request, 'modeselect.html', context)

index = IndexView.as_view()


class ModeSelectView(PublicView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'customize_game.html', context)

mode_select = ModeSelectView.as_view()


class PlayView(PublicView):
    def get(self, request):
        return render(request, 'play.html')

play = PlayView.as_view()


class LoginView(PublicView):
    def get(self, request):
        context = {}
        fortytwo = request.query_params.get('fortytwo', None)
        if fortytwo:
            context['fortytwo'] = fortytwo
        return render(request, 'accounts/login.html', context)

login = LoginView.as_view()


class RegisterView(PublicView):
    def get(self, request):
        return render(request, 'accounts/register.html')

register = RegisterView.as_view()


class ForgotPasswordView(PublicView):
    def get(self, request):
        return render(request, 'accounts/forgot_password.html')

forgot_password = ForgotPasswordView.as_view()


class HomeView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context = get_game_context(context)
        context['notifs'] = Notification.objects.get_notifications_for_profile(request.profile.id)
        return render(request, 'home.html', context)

home = HomeView.as_view()


class SelectGameView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'modeselect.html', context)

select_game = SelectGameView.as_view()


class CustomizeGameView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'customize_game.html', context)

customize_game = CustomizeGameView.as_view()


class GameRoomView(PrivateView):
    def get(self, request, game_id):
        context = get_profile_context(request)
        context['game'] = Game.objects.get(id=game_id)
        return render(request, 'game_room.html', context)

game_room = GameRoomView.as_view()


class ProfileView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'profile.html', context)

profile = ProfileView.as_view()


class ProfileOtherView(PrivateView):
    def get(self, request, profile_id):
        context = get_profile_context(request, profile_id)
        return render(request, 'profile.html', context)

profile_other = ProfileOtherView.as_view()


class LeaderboardView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context['players'] = Profile.objects.get_ranked_profiles()
        return render(request, 'leaderboard.html', context)

leaderboard = LeaderboardView.as_view()


class SocialView(PrivateView):
    def get(self, request):
        friendships_ids = Friendship.objects.get_friendships_ids(request.profile)
        if friendships_ids:
            first_friend_id = next(iter(friendships_ids))
            first_friend = Profile.objects.get(id=first_friend_id)
            friendship_id = Friendship.objects.get_friendship_id(request.profile, first_friend)
            if friendship_id:
                return redirect(f'/friends/{friendship_id}/')
        # context = {'profile': request.profile}
        # friendship_id = request.query_params.get('id', '')
        # context['messages'] = FriendMessage.objects.get_messages(friendship_id)
        return render(request, 'social.html')

social = SocialView.as_view()


class SocialFriendView(PrivateView):
    def get(self, request, friend_id):
        context = get_friend_context(request)
        friendship_id = request.query_params.get('id', '')
        context['messages'] = FriendMessage.objects.get_messages(friendship_id)
        return render(request, 'social.html', context)

social_friend = SocialFriendView.as_view()


class SettingsView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'settings.html', context)

settings = SettingsView.as_view()


class LangReloadView(PublicView):
    def post(self, request, lang):
        path = request.data.get('path')
        translation.activate(lang)
        logger.info('Language changed.', extra={'lang': lang})
        response_data = {'message': _('Language changed.'), 'redirect': path}
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='lang',
            value=lang,
        )
        return response

lang_reload = LangReloadView.as_view()