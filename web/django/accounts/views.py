import logging
import random
import requests
import string
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
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
from .serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserUpdateEmailSerializer,
)
from .tokens import EmailTokenGenerator
from .utils import (
    send_activation_mail,
    send_password_reset_mail,
    set_jwt_cookies,
    unset_jwt_cookies
)

UserModel = get_user_model()
logger = logging.getLogger('django')


class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        response = Response(
            {
                'status': _('User logged in!'),
                'redirect': '/home/',
            },
            status=status.HTTP_200_OK,
        )
        login(request, user)
        set_jwt_cookies(response, user)
        return response

user_login = UserLoginView.as_view()


class UserLogoutView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
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


class UserRegisterView(APIView):
    permission_classes = (AllowAny,)
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        # Resend email if account not verified yet but exists
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)
        
        response = Response(
            {
                'status': _('Account registered! Please check your email to activate your account.'),
            },
            status=status.HTTP_201_CREATED,
        )
        send_activation_mail(request, user)
        return response

user_register = UserRegisterView.as_view()


class UserActivateView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        
        token_generator = EmailTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            
            response = Response(
                {
                    'status': _('Account activated!'),
                    'redirect': '/home/',
                },
                status=status.HTTP_200_OK,
            )
            login(request, user)
            set_jwt_cookies(response, user)
            return response
        
        response = Response(
            {
                'status': _('Activation link is invalid!'),
                'redirect': '/login/',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
        return response

user_activate = UserActivateView.as_view()


class PasswordResetRequestView(APIView):
    permission_classes = (AllowAny,)
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid()
        user = serializer.get_user()
        response = Response(
            {
                'status': _('Please check your email to reset your password.'),
            },
            status=status.HTTP_200_OK,
        )
        if user:
            send_password_reset_mail(request, user)
        return response


password_reset_request = PasswordResetRequestView.as_view()


class PasswordResetView(APIView):
    permission_classes = (AllowAny,)
    
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
            set_jwt_cookies(response, user)
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


class PasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)
    
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
        set_jwt_cookies(response, user)
        return response

password_reset_confirm = PasswordResetConfirmView.as_view()


class FortyTwoLoginView(APIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, *args, **kwargs):
        redirect_uri = quote('http://localhost:8080/api/oauth/42/callback/', safe='')
        authorization_url = f'https://api.intra.42.fr/oauth/authorize?client_id={settings.FORTYTWO_ID}&redirect_uri={redirect_uri}&response_type=code'
        return redirect(authorization_url)

fortytwo_login = FortyTwoLoginView.as_view()


class FortyTwoCallbackView(APIView):
    def get(self, request, *args, **kwargs):
        response = requests.post('https://api.intra.42.fr/oauth/token', data={
            'grant_type': 'authorization_code',
            'client_id': settings.FORTYTWO_ID,
            'client_secret': settings.FORTYTWO_SECRET,
            'code': request.GET.get('code'),
            'redirect_uri': 'http://localhost:8080/api/oauth/42/callback/',
        })
        
        token_response = response.json()
        fortytwo_access_token = token_response['access_token']
        fortytwo_refresh_token = token_response['refresh_token']
        
        user_info_response = requests.get('https://api.intra.42.fr/v2/me', headers={
            'Authorization': f'Bearer {fortytwo_access_token}'
        })
        user_info = user_info_response.json()
        fortytwo_id = user_info['id']
        username = "42_" + user_info['login']
        email = user_info['email']
        
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
                )
        
        response = Response({
            'status': _('Authentication successful!'),
        }, status=status.HTTP_200_OK)
        login(request, user)
        set_jwt_cookies(response, user)
        return response

fortytwo_callback = FortyTwoCallbackView.as_view()


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