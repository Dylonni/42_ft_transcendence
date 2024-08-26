import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from profiles.models import Profile, ProfileBlock
from friends.models import Friendship, FriendMessage
from games.models import Game, GameRound
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

def get_friend_context(request):
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

def get_friendship_context(request):
    context = get_profile_context(request)
    try:
        profile = context.get('profile', None)
        if profile is None:
            return context
        friendships = Friendship.objects.get_friendships(profile)
        context['friendships'] = friendships
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

def get_notif_context(request, context={}):
    if request.profile:
        return context
    notifications = Notification.objects.get_notifications_for_profile(request.profile)
    context['notifs'] = notifications
    context['has_unread_notifs'] = notifications.filter(read=False).exists()
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
        context = get_notif_context(request, context)
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
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        context = get_game_context(context)
        context = get_notif_context(request, context)
        return render(request, 'home.html', context)

home = HomeView.as_view()


class SelectGameView(PrivateView):
    def get(self, request):
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        return render(request, 'modeselect.html', context)

select_game = SelectGameView.as_view()


class CustomizeGameView(PrivateView):
    def get(self, request):
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        return render(request, 'customize_game.html', context)

customize_game = CustomizeGameView.as_view()


class GameRoomView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        if request.profile not in game.players.all():
            return redirect('/home/')
        context = get_friend_context(request)
        context['game'] = game
        context['players'] = game.players.all()
        return render(request, 'game_room.html', context)

game_room = GameRoomView.as_view()


class ProfileView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context['is_self'] = True
        context['rounds'] = GameRound.objects.get_last_matches(request.profile)
        context = get_notif_context(request, context)
        return render(request, 'profile.html', context)

profile = ProfileView.as_view()


class ProfileOtherView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        context = get_profile_context(request, profile_id)
        context = get_notif_context(request, context)
        context['is_self'] = request.profile.id == profile_id
        context['is_friend'] = request.profile.is_friend(context['profile'])
        if context['is_friend']:
            context['friendship'] = Friendship.objects.get_friendship(request.profile, profile)
        context['profile_block'] = request.profile.get_block(context['profile'])
        context['rounds'] = GameRound.objects.get_last_matches(profile)
        return render(request, 'profile.html', context)

profile_other = ProfileOtherView.as_view()


class LeaderboardView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context['players'] = Profile.objects.get_ranked_profiles()
        context = get_notif_context(request, context)
        return render(request, 'leaderboard.html', context)

leaderboard = LeaderboardView.as_view()


class SocialView(PrivateView):
    def get(self, request):
        context = get_friendship_context(request)
        context = get_notif_context(request, context)
        return render(request, 'friends/social.html', context)

social = SocialView.as_view()


class SocialFriendView(PrivateView):
    def get(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, id=friendship_id)
        if friendship.is_outsider(request.profile):
            return redirect('/home/')
        context = get_friendship_context(request)
        context['messages'] = FriendMessage.objects.get_messages(friendship_id)
        context['current_friend'] = Friendship.objects.get_other(friendship_id, request.profile)
        context['friendship'] = friendship
        context['profile_block'] = request.profile.get_block(context['current_friend'])
        context = get_notif_context(request, context)
        return render(request, 'friends/social.html', context)

social_friend = SocialFriendView.as_view()


class SettingsView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context = get_notif_context(request, context)
        return render(request, 'settings.html', context)

settings = SettingsView.as_view()


class LangReloadView(PublicView):
    def post(self, request, lang):
        path = request.data['path']
        translation.activate(lang)
        response_data = {'message': _('Language changed.'), 'redirect': path}
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='lang',
            value=lang,
        )
        return response

lang_reload = LangReloadView.as_view()