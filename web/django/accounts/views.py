import logging
import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import quote
from pong.views import PrivateView, PublicView
from profiles.models import Profile
from games.models import Game
from .serializers import (
    UserLoginSerializer,
    UserRegisterSerializer,
    CustomUserCodeSerializer,
)
from .tokens import EmailTokenGenerator
from .utils import (
    is_token_valid,
    get_jwt_from_refresh,
    set_jwt_as_cookies,
    set_jwt_cookies_for_user,
    unset_jwt_cookies,
)

UserModel = get_user_model()
logger = logging.getLogger('django')


class UserLoginView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request: HttpRequest):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            Profile.objects.set_user_status(user, Profile.StatusChoices.ONLINE)
            response_data = {'message': _('User logged in.'), 'redirect': '/home/'}
            response = Response(response_data, status=status.HTTP_200_OK)
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        except ValidationError as e:
            response_data = {'message': e.detail}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

user_login = UserLoginView.as_view()


class UserLogoutView(PrivateView):
    def post(self, request: HttpRequest):
        player = request.profile
        game = player.game
        if game:
            Game.objects.remove_player(game, player)
        Profile.objects.set_user_status(request.user, Profile.StatusChoices.OFFLINE)
        response_data = {'message': _('User logged out.'), 'redirect': '/'}
        response = Response(response_data, status=status.HTTP_200_OK)
        logout(request)
        unset_jwt_cookies(response)
        return response

user_logout = UserLogoutView.as_view()


class UserRegisterView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request: HttpRequest):
        try:
            serializer = UserRegisterSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            
            user = UserModel.objects.send_mail(request.data['email'], 'accounts/email_activate.html', 'Activate your Account')
            token_generator = EmailTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            response_data = {
                'message': _('Account registered! Please check your email to activate your account.'),
                'redirect': f'/verify-code/?type=activate&token={token}&user={uid}',
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

user_register = UserRegisterView.as_view()


class UserActivateView(PublicView):
    def post(self, request: HttpRequest):
        try:
            token = request.query_params.get('token', None)
            to_decode = request.query_params.get('user', None)
            uid = force_str(urlsafe_base64_decode(to_decode))
            user = UserModel.objects.filter(id=uid).first()
            if not user:
                response_data = {'error': _('Invalid url.')}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            token_generator = EmailTokenGenerator()
            if not token_generator.check_token(user, token):
                response_data = {'error': _('Invalid url.')}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            serializer = CustomUserCodeSerializer(data=request.data)
            if not serializer.is_valid():
                response_data = {'error': _('Invalid code.')}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_code(serializer.validated_data['code']):
                response_data = {'error': _('Invalid code.')}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            Profile.objects.create_from_user(user)
            user.set_as_verified()
            user.code = None
            user.code_updated_at = None
            user.save()
            Profile.objects.set_user_status(user, Profile.StatusChoices.ONLINE)
            response_data = {'message': _('Account verified.'), 'redirect': '/home/'}
            response = Response(response_data, status=status.HTTP_200_OK)
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

user_activate = UserActivateView.as_view()


class PasswordRequestView(PublicView):
    def post(self, request: HttpRequest):
        try:
            user = UserModel.objects.send_mail(request.data['email'], 'accounts/email_reset_password.html', 'Reset your Password')
            token_generator = EmailTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            response_data = {
                'message': _('Password reset request sent! Please check your email.'),
                'redirect': f'/verify-code/?type=forget&token={token}&user={uid}',
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


password_request = PasswordRequestView.as_view()


class PasswordResetView(PublicView):
    def post(self, request: HttpRequest):
        try:
            token = request.query_params.get('token', None)
            uid = request.query_params.get('user', None)
            user = UserModel.objects.filter(id=uid).first()
            if not user:
                response_data = {'message': _('Invalid url.'), 'redirect': '/'}
                return Response(response_data, status=status.HTTP_200_OK)
            token_generator = EmailTokenGenerator()
            if not token_generator.check_token(user, token):
                response_data = {'message': _('Invalid url.'), 'redirect': '/'}
                return Response(response_data, status=status.HTTP_200_OK)
            response_data = {
                'message': _('Set your new password.'),
                'redirect': f'/change-password/?token={token}&user={uid}',
            }
            response_data = {'message': _('Set your new password.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


password_reset = PasswordResetView.as_view()


class PasswordConfirmView(PublicView):
    def post(self, request: HttpRequest):
        try:
            token = request.query_params.get('token', None)
            uid = request.query_params.get('user', None)
            user = UserModel.objects.filter(id=uid).first()
            if not user:
                response_data = {'message': _('Invalid url.'), 'redirect': '/'}
                return Response(response_data, status=status.HTTP_200_OK)
            token_generator = EmailTokenGenerator()
            if not token_generator.check_token(user, token):
                response_data = {'message': _('Invalid url.'), 'redirect': '/'}
                return Response(response_data, status=status.HTTP_200_OK)
            user.set_password(request.data['new_password'])
            Profile.objects.set_user_status(user, Profile.StatusChoices.ONLINE)
            response_data = {'message': _('Password changed.'), 'redirect': '/home/'}
            response = Response(response_data, status=status.HTTP_200_OK)
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

password_confirm = PasswordConfirmView.as_view()


class FortyTwoLoginView(APIView):
    def get(self, request: HttpRequest):
        redirect_uri = quote(settings.FORTYTWO_REDIRECT_URI, safe='')
        authorization_url = f'https://api.intra.42.fr/oauth/authorize?client_id={settings.FORTYTWO_ID}&redirect_uri={redirect_uri}&response_type=code'
        return redirect(authorization_url)

fortytwo_login = FortyTwoLoginView.as_view()


class FortyTwoUnlinkView(PrivateView):
    def post(self, request: HttpRequest):
        request.profile.set_avatar_url()
        request.user.update_fortytwo_infos()
        response_data = {'message': _('42 account unlinked.'), 'redirect': '/settings/'}
        return Response(response_data, status=status.HTTP_200_OK)

fortytwo_unlink = FortyTwoUnlinkView.as_view()


class FortyTwoCallbackView(APIView):
    def get(self, request: HttpRequest):
        code = request.GET.get('code')
        if not code:
            logger.error('No authorization code received.')
            return redirect('/login/?fortytwo=nocode')
        
        response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': settings.FORTYTWO_ID,
            'client_secret': settings.FORTYTWO_SECRET,
            'code': code,
            'redirect_uri': settings.FORTYTWO_REDIRECT_URI,
        })
        token_response = response.json()
        fortytwo_access_token = token_response.get('access_token')
        if not fortytwo_access_token:
            logger.error('No access token received from 42 API.')
            return redirect('/login/?fortytwo=notoken')
        
        user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {fortytwo_access_token}'
        })
        user_info = user_info_response.json()
        fortytwo_id = user_info.get('id', '')
        fortytwo_avatar_url = user_info.get('image', {}).get('versions', {}).get('small', '')
        user_coalition_response = requests.get(f'https://api.intra.42.fr/v2/users/{fortytwo_id}/coalitions', headers={
            'Authorization': f'Bearer {fortytwo_access_token}'
        })
        last_user_coalition = user_coalition_response.json()[-1]
        fortytwo_coalition_cover_url = last_user_coalition.get('cover_url', '')
        fortytwo_coalition_color = last_user_coalition.get('color', '')
        
        try:
            access_token = request.COOKIES.get('access_token', None)
            if access_token:
                access_token_obj = AccessToken(access_token)
                user_id = access_token_obj['user_id']
                user = UserModel.objects.get(id=user_id)
            else:
                user = UserModel.objects.get(fortytwo_id=fortytwo_id)
            user.update_fortytwo_infos(
                fortytwo_avatar_url,
                fortytwo_coalition_cover_url,
                fortytwo_coalition_color,
            )
            Profile.objects.set_user_status(user, Profile.StatusChoices.ONLINE)
            response = redirect('/home/')
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        except Exception as e:
            response = redirect('/login/?fortytwo=nolink')
            logout(request)
            unset_jwt_cookies(response)
            return response

fortytwo_callback = FortyTwoCallbackView.as_view()


class TokenVerify(PublicView):
    def post(self, request: HttpRequest):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        if access_token:
            if is_token_valid(access_token):
                response = Response(
                    {
                        'status': _('Already authenticated!'),
                        'redirect': '/home/',
                    },
                    status=status.HTTP_200_OK,
                )
                return response
            else:
                access_token, refresh_token = get_jwt_from_refresh(refresh_token)
                if access_token is None:
                    response = Response(
                        {
                            'status': _('Invalid tokens!'),
                            'redirect': '/login/',
                        },
                        status=status.HTTP_200_OK,
                    )
                    unset_jwt_cookies(response)
                    return response
                else:
                    response = Response(
                        {
                            'status': _('Already authenticated!'),
                            'redirect': '/home/',
                        },
                        status=status.HTTP_200_OK,
                    )
                    set_jwt_as_cookies(response, access_token, refresh_token)
                    return response
        response = Response(
            {
                'status': _('Welcome!'),
                'redirect': '/login/',
            },
            status=status.HTTP_200_OK,
        )
        return response

token_verify = TokenVerify.as_view()