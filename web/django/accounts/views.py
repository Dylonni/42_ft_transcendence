import logging
import random
import requests
import string
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from urllib.parse import quote
from pong.views import PrivateView, PublicView
from profiles.models import Profile
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserUpdateEmailSerializer,
)
from .tokens import EmailTokenGenerator
from .utils import (
    is_token_valid,
    get_jwt_from_refresh,
    send_activation_mail,
    send_password_reset_mail,
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
            Profile.objects.set_user_status(user, Profile.StatusChoices.CONNECTED)
            logger.info('User logged in.', extra={'user': user})
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
        Profile.objects.set_user_status(request.user, Profile.StatusChoices.DISCONNECTED)
        logger.info('User logged out.', extra={'user': request.user})
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
            
            logger.info('Account registered! Please check your email to activate your account.', extra={'user': user})
            response_data = {'message': _('Account registered! Please check your email to activate your account.')}
            response = Response(response_data, status=status.HTTP_201_CREATED)
            send_activation_mail(request, user)
            return response
        except ValidationError as e:
            response_data = {'message': e.detail}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

user_register = UserRegisterView.as_view()


class UserActivateView(PublicView):
    def get(self, request: HttpRequest, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
            Profile.objects.create_from_user(user)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist) as e:
            user = None
            logger.warning('Invalid activation link.')
        
        token_generator = EmailTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.set_as_verified()
            Profile.objects.set_user_status(user, Profile.StatusChoices.CONNECTED)
            logger.info('Account activated! User logged in.', extra={'user': user})
            response = redirect('/home/')
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        
        logger.warning('Invalid activation link.')
        return redirect('/login/')

user_activate = UserActivateView.as_view()


# TODO: send mail with numeric code instead of link
class PasswordResetRequestView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request: HttpRequest):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid()
        user = serializer.get_user()
        if user:
            send_password_reset_mail(request, user)
        logger.info('Password reset request sent! Please check your email to reset your password.', extra={'user': user})
        response_data = {'message': 'Password reset request sent! Please check your email to reset your password.'}
        return Response(response_data, status=status.HTTP_200_OK)


password_reset_request = PasswordResetRequestView.as_view()


class PasswordResetView(PublicView):
    def get(self, request: HttpRequest, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        
        token_generator = EmailTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            response = Response(
                {
                    'status': _('Set your new password.'),
                    'redirect': '/password-reset/',
                },
                status=status.HTTP_200_OK,
            )
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        
        response = Response(
            {
                'status': _('Password reset link is invalid!'),
                'redirect': '/login/',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        return response

password_reset = PasswordResetView.as_view()


class PasswordResetConfirmView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request: HttpRequest):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(password=serializer.validated_data['new_password'])
        response = Response(
            {
                'status': _('Password changed!'),
                'redirect': '/home/',
            },
            status=status.HTTP_200_OK,
        )
        login(request, user)
        set_jwt_cookies_for_user(response, user)
        return response

password_reset_confirm = PasswordResetConfirmView.as_view()


class FortyTwoLoginView(APIView):
    def get(self, request: HttpRequest):
        redirect_uri = quote(settings.FORTYTWO_REDIRECT_URI, safe='')
        authorization_url = f'https://api.intra.42.fr/oauth/authorize?client_id={settings.FORTYTWO_ID}&redirect_uri={redirect_uri}&response_type=code'
        return redirect(authorization_url)

fortytwo_login = FortyTwoLoginView.as_view()


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
        fortytwo_refresh_token = token_response.get('refresh_token')
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
            logger.info('User logged in with 42.', extra={'user': user})
            user.update_fortytwo_infos(
                fortytwo_id,
                fortytwo_access_token,
                fortytwo_refresh_token,
                fortytwo_avatar_url,
                fortytwo_coalition_cover_url,
                fortytwo_coalition_color,
            )
            Profile.objects.set_user_status(user, Profile.StatusChoices.CONNECTED)
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


class UserUpdateEmailView(generics.GenericAPIView):
    queryset = UserModel.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateEmailSerializer

    # @method_decorator(ensure_csrf_cookie)
    def post(self, request: HttpRequest):
        try:
            user = UserModel.objects.get(id=request.data.get('id'))
        except UserModel.DoesNotExist as e:
            return Response({
                'status': 'User not found.',
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data['email']
        return Response({
            'status': _('Email updated succesfully!'),
            'data': email,
        }, status=status.HTTP_200_OK)