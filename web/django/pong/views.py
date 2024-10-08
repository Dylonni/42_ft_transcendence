import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from profiles.models import Profile, ProfileBlock
from friends.models import Friendship, FriendMessage, FriendRequest
from games.models import Game, GameRound, GameMessage
from notifs.models import Notification
from .mixins import JWTCookieAuthenticationMixin, LangVerificationMixin, RedirectIfAuthenticatedMixin

UserModel = get_user_model()
logger = logging.getLogger('django')

def get_profile_context(request, profile_id=None):
    context = {}
    try:
        if profile_id:
            profile = Profile.objects.filter(id=profile_id).first()
        else: 
            if request.user.id:
                profile = Profile.objects.filter(user=request.user).first()
            else:
                profile = None
        context['profile'] = profile
        return context
    except Profile.DoesNotExist:
        return context

def get_notif_context(request, context={}):
    if not request.profile:
        return context
    notifications = Notification.objects.get_notifications_for_profile(request.profile)
    context['notifs'] = notifications
    context['has_unread_notifs'] = notifications.filter(read=False).exists()
    return context


class PublicView(RedirectIfAuthenticatedMixin, LangVerificationMixin, APIView):
    permission_classes = (AllowAny,)
    throttle_classes = [AnonRateThrottle]


class PrivateView(JWTCookieAuthenticationMixin, LangVerificationMixin, APIView):
    permission_classes = (IsAuthenticated,)
    throttle_classes = [UserRateThrottle]

class HealthzView(APIView):
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)

healthz = HealthzView.as_view()


class IndexView(PublicView):
    def get(self, request):
        context = get_profile_context(request)
        return render(request, 'modeselect.html', context)

index = IndexView.as_view()


class ModeSelectView(PublicView):
    def get(self, request):
        context = get_profile_context(request)
        context = get_notif_context(request, context)
        return render(request, 'games/game_config.html', context)

mode_select = ModeSelectView.as_view()


class PlayView(LangVerificationMixin, APIView):
    def get(self, request):
        return render(request, 'games/play.html')

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


class VerifyCodeView(PublicView):
    def get(self, request):
        code_type = request.query_params.get('type', None)
        code_token = request.query_params.get('token', None)
        code_user = request.query_params.get('user', None)
        match code_type:
            case "forget":
                target = f"/api/auth/password/reset/?token={code_token}&user={code_user}"
            case "twofa":
                target = f'/api/auth/twofa/?token={code_token}&user={code_user}'
            case "activate":
                target = f'/api/auth/activate/?token={code_token}&user={code_user}'
            case _:
                target = ""
        context = {
            'type': request.query_params.get('type', None),
            'token': code_token,
            'user': code_user,
            'target': target,
        }
        return render(request, 'accounts/verify_code.html', context)

verify_code = VerifyCodeView.as_view()


class ConfirmPasswordView(PublicView):
    def get(self, request):
        code_token = request.query_params.get('token', None)
        code_user = request.query_params.get('user', None)
        context = {'target': f'/api/auth/password/confirm/?token={code_token}&user={code_user}', 'category': 'password'}
        return render(request, 'accounts/modify_credentials.html', context)

confirm_password = ConfirmPasswordView.as_view()


class CheckCodeView(PrivateView):
    def get(self, request):
        code_type = request.query_params.get('type', None)
        code_token = request.query_params.get('token', None)
        code_user = request.query_params.get('user', None)
        match code_type:
            case "twofa":
                target = f"/api/profiles/me/code/?type=twofa&token={code_token}&user={code_user}"
            case "email":
                target = f"/api/profiles/me/code/?type=email&token={code_token}&user={code_user}"
            case "password":
                target = f"/api/profiles/me/code/?type=password&token={code_token}&user={code_user}"
            case _:
                target = ""
        context = {
            'type': code_type,
            'token': code_token,
            'user': code_user,
            'target': target,
            'profile': request.profile,
        }
        return render(request, 'accounts/verify_code.html', context)

check_code = CheckCodeView.as_view()


class ChangePasswordView(PrivateView):
    def get(self, request):
        context = {
            'target': '/api/profiles/me/password/',
            'category': 'password',
            'profile': request.profile,
        }
        return render(request, 'accounts/modify_credentials.html', context)

change_password = ChangePasswordView.as_view()


class ChangeEmailView(PrivateView):
    def get(self, request):
        context = {
            'target': '/api/profiles/me/email/',
            'category': 'email',
            'profile': request.profile,
        }
        return render(request, 'accounts/modify_credentials.html', context)

change_email = ChangeEmailView.as_view()


class AboutViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
        }
        return render(request, 'about/about.html', context)

about_priv = AboutViewPriv.as_view()


class AboutView(PublicView):
    def get(self, request):
        return render(request, 'about/about.html')

about_pub = AboutView.as_view()


class DevTeamViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
        }
        return render(request, 'about/dev_team.html', context)

dev_team_priv = DevTeamViewPriv.as_view()


class DevTeamView(PublicView):
    def get(self, request):
        return render(request, 'about/dev_team.html')

dev_team_pub = DevTeamView.as_view()


class FaqViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
        }
        return render(request, 'about/faq.html', context)

faq_priv = FaqViewPriv.as_view()


class FaqView(PublicView):
    def get(self, request):
        return render(request, 'about/faq.html')

faq_pub = FaqView.as_view()


class GameRulesViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
        }
        return render(request, 'about/game_rules.html', context)

game_rules_priv = GameRulesViewPriv.as_view()


class GameRulesView(PublicView):
    def get(self, request):
        return render(request, 'about/game_rules.html')

game_rules_pub = GameRulesView.as_view()


class PrivacyPolicyViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
            'discord_invite': settings.DISCORD_INVITE,
            'django_mail_contact': settings.DJANGO_MAIL_CONTACT,
        }
        return render(request, 'about/privacy_policy.html', context)

privacy_policy_priv = PrivacyPolicyViewPriv.as_view()


class PrivacyPolicyView(PublicView):
    def get(self, request):
        context = {
            'discord_invite': settings.DISCORD_INVITE,
            'django_mail_contact': settings.DJANGO_MAIL_CONTACT,
        }
        return render(request, 'about/privacy_policy.html', context)

privacy_policy_pub = PrivacyPolicyView.as_view()

class TosViewPriv(PrivateView):
    def get(self, request):
        context = {
            'profile': request.profile,
            'discord_invite': settings.DISCORD_INVITE,
            'django_mail_contact': settings.DJANGO_MAIL_CONTACT,
        }
        return render(request, 'about/terms_of_service.html', context)

terms_of_service_priv = TosViewPriv.as_view()

class TosView(PublicView):
    def get(self, request):
        context = {
            'discord_invite': settings.DISCORD_INVITE,
            'django_mail_contact': settings.DJANGO_MAIL_CONTACT,
        }
        return render(request, 'about/terms_of_service.html')

terms_of_service_pub = TosView.as_view()


class HomeView(PrivateView):
    def get(self, request):
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        context['games'] = Game.objects.filter(started_at__isnull=True)
        name = request.query_params.get('name', None)
        if name:
            context['games'] = context['games'].filter(name__icontains=name)
        context = get_notif_context(request, context)
        return render(request, 'home.html', context)

home = HomeView.as_view()


class SelectGameView(PrivateView):
    def get(self, request):
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        context = get_notif_context(request, context)
        return render(request, 'modeselect.html', context)

select_game = SelectGameView.as_view()


class CustomizeGameView(PrivateView):
    def get(self, request):
        if request.profile.game:
            return redirect(f'/games/{request.profile.game.id}/', True)
        context = get_profile_context(request)
        context = get_notif_context(request, context)
        if request.query_params.get('local', None):
            context['local'] = True
        return render(request, 'games/game_config.html', context)

customize_game = CustomizeGameView.as_view()


class GameRoomView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        if request.profile not in game.players.all() or game.ended_at:
            return redirect('/home/')
        context = get_profile_context(request)
        friendships_ids = Friendship.objects.get_friendships_ids(context.get('profile', None))
        context['friends'] = Profile.objects.filter(id__in=friendships_ids)
        context['game'] = game
        if context['game'].started_at:
            context['round'] = GameRound.objects.get_current_round(game)
        context['messages'] = GameMessage.objects.get_messages(game, request.profile)
        context['players'] = game.players.all()
        context['available_friends'] = Profile.objects.get_available_friends(request.profile)
        context = get_notif_context(request, context)
        return render(request, 'games/game_room.html', context)

game_room = GameRoomView.as_view()


class ProfileView(PrivateView):
    def get(self, request):
        context = get_profile_context(request)
        context['current_profile'] = context['profile']
        context['is_self'] = True
        context['rounds'] = GameRound.objects.get_last_matches(request.profile)
        context = get_notif_context(request, context)
        return render(request, 'profile.html', context)

profile = ProfileView.as_view()


class ProfileOtherView(PrivateView):
    def get(self, request, profile_id):
        profile = get_object_or_404(Profile, id=profile_id)
        context = get_profile_context(request)
        context = get_notif_context(request, context)
        context['current_profile'] = profile
        context['is_self'] = request.profile.id == profile_id
        context['is_requested'] = FriendRequest.objects.filter(sender=request.profile, receiver=profile).first()
        context['is_friend'] = request.profile.is_friend(profile)
        if context['is_friend']:
            context['friendship'] = Friendship.objects.get_friendship(request.profile, profile)
        context['profile_block'] = request.profile.get_block(profile)
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
        context = get_profile_context(request)
        context['friendships'] = Friendship.objects.get_friendships(context.get('profile', None))
        context = get_notif_context(request, context)
        return render(request, 'friends/social.html', context)

social = SocialView.as_view()


class SocialFriendView(PrivateView):
    def get(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, id=friendship_id)
        if friendship.is_outsider(request.profile):
            return redirect('/home/')
        if friendship.removed_by == request.profile:
            return redirect('/friends/')
        context = get_profile_context(request)
        context['friendships'] = Friendship.objects.get_friendships(context.get('profile', None))
        context['messages'] = FriendMessage.objects.get_messages(friendship, request.profile)
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

settings_view = SettingsView.as_view()


class LangReloadView(PublicView):
    def post(self, request, lang):
        if lang not in dict(settings.LANGUAGES):
            lang = 'en'
        path = request.data['path']
        response_data = {'message': _('Language changed.'), 'redirect': path}
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='lang',
            value=lang,
            httponly=True,
            secure=True,
            samesite='Lax',
        )
        return response

lang_reload = LangReloadView.as_view()