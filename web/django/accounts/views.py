import logging
import random
import requests
import string
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
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
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        logger.info(f'User {user.username} logged in.')
        response = Response(
            {
                'status': _('User logged in!'),
                'redirect': '/home/',
            },
            status=status.HTTP_200_OK,
        )
        login(request, user)
        set_jwt_cookies_for_user(response, user)
        return response

user_login = UserLoginView.as_view()


class UserLogoutView(PrivateView):
    def post(self, request, *args, **kwargs):
        logger.info('User logged out.')
        response = Response(
            {
                'status': _('User logged out!'),
                'redirect': '/login/',
            },
            status=status.HTTP_200_OK,
        )
        logout(request)
        unset_jwt_cookies(response)
        return response

user_logout = UserLogoutView.as_view()


class UserRegisterView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        # TODO: Resend email if account not verified yet but exists
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)
        
        logger.info(f'Account registered for user {user.username}. Activation email sent to {user.email}.')
        response = Response(
            {
                'status': _('Account registered! Please check your email to activate your account.'),
            },
            status=status.HTTP_201_CREATED,
        )
        send_activation_mail(request, user)
        return response

user_register = UserRegisterView.as_view()


class UserActivateView(PublicView):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
            Profile.objects.create_from_user(user)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist) as e:
            user = None
            logger.error(f"Error activating account: {e}")
        
        token_generator = EmailTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.is_verified = True
            user.save()
            logger.info(f'Account activated for user {user.username}. User logged in.')
            response = redirect('/home/')
            login(request, user)
            set_jwt_cookies_for_user(response, user)
            return response
        
        logger.warning('Invalid activation link or token.')
        return redirect('/login/')

user_activate = UserActivateView.as_view()


class PasswordResetRequestView(PublicView):
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid()
        user = serializer.get_user()
        if user:
            send_password_reset_mail(request, user)
        response = Response(
            {
                'status': _('Please check your email to reset your password.'),
            },
            status=status.HTTP_200_OK,
        )
        return response


password_reset_request = PasswordResetRequestView.as_view()


class PasswordResetView(PublicView):
    def get(self, request, uidb64, token, *args, **kwargs):
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
    def post(self, request, *args, **kwargs):
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


class FortyTwoLoginView(PublicView):
    def get(self, request, *args, **kwargs):
        redirect_uri = quote(settings.FORTYTWO_REDIRECT_URI, safe='')
        authorization_url = f'https://api.intra.42.fr/oauth/authorize?client_id={settings.FORTYTWO_ID}&redirect_uri={redirect_uri}&response_type=code'
        return redirect(authorization_url)

fortytwo_login = FortyTwoLoginView.as_view()


class FortyTwoCallbackView(PublicView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        if not code:
            logger.error('No authorization code received.')
            return redirect('/login')
        
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
            return redirect('/login')
        
        user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {fortytwo_access_token}'
        })
        user_info = user_info_response.json()
        fortytwo_id = user_info.get('id')
        username = "42_" + user_info.get('login')
        email = user_info.get('email')
        img = user_info.get('image', {}).get('versions', {}).get('small')
        
        try:
            user = UserModel.objects.get(fortytwo_id=fortytwo_id)
            logger.info('Update account already linked to 42')
            user.fortytwo_access_token = fortytwo_access_token
            user.fortytwo_refresh_token = fortytwo_refresh_token
            user.save()
        except UserModel.DoesNotExist as e:
            try:
                user = UserModel.objects.get(email=email)
                logger.info('Link account to 42')
                user.fortytwo_id = fortytwo_id
                user.fortytwo_access_token = fortytwo_access_token
                user.fortytwo_refresh_token = fortytwo_refresh_token
                user.save()
            except UserModel.DoesNotExist as e:
                logger.info('Create an account and link it to 42')
                # password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
                password = 'qwerty'
                user = UserModel.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    fortytwo_id=fortytwo_id,
                    fortytwo_access_token=fortytwo_access_token,
                    fortytwo_refresh_token=fortytwo_refresh_token,
                    is_verified=True,
                )
                Profile.objects.create_from_user(user)
        self._save_avatar_from_url(user, img)
        
        response = redirect('/home/')
        login(request, user)
        set_jwt_cookies_for_user(response, user)
        return response
    
    def _save_avatar_from_url(self, user, url):
        response = requests.get(url)
        if response.status_code == 200:
            file_name = url.split('/')[-1]
            profile = Profile.objects.get(user=user)
            profile.avatar.save(file_name, ContentFile(response.content), save=True)
            profile.refresh_from_db()
        else:
            logger.warning('Failed to fetch avatar from URL: %s', url)

fortytwo_callback = FortyTwoCallbackView.as_view()


class TokenVerify(PublicView):
    def post(self, request, *args, **kwargs):
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
    def post(self, request, *args, **kwargs):
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