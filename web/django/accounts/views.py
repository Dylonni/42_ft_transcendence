from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserUpdateEmailSerializer,
)
from .tokens import AccountActivationTokenGenerator
import logging

CustomUser = get_user_model()
logger = logging.getLogger('django')


class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        logger.info('User attempt registration')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(is_active=False)  # Deactivate account till it is confirmed
        
        current_site = get_current_site(request)
        mail_subject = 'Activate your account'
        token_generator = AccountActivationTokenGenerator()
        message = render_to_string('accounts/activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        })
        to_email = serializer.validated_data.get('email')
        send_mail(
            subject=mail_subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            html_message=message,
        )
        
        return Response({
            'status': 'Registration successful! Please check your email to activate your account.',
            'redirect': '/login',
        }, status=status.HTTP_201_CREATED)


class UserActivateView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None
        
        token_generator = AccountActivationTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            
            refresh = RefreshToken.for_user(user)
            request.session['access_type'] = 'username-password'
            request.session['access_token'] = str(refresh.access_token)
            request.session['refresh_token'] = str(refresh)
            
            return Response({
                'status': 'Account activated successfully!',
                'redirect': '/settings',
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Activation link is invalid!',
                'redirect': '/login',
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    
    @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        logger.info('User attempt login')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        request.session['access_type'] = 'username-password'
        request.session['access_token'] = str(refresh.access_token)
        request.session['refresh_token'] = str(refresh)
        
        return Response({
            'status': 'Authentication successful!',
            'redirect': '/settings',
        }, status=status.HTTP_200_OK)


class UserUpdateEmailView(generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    # permission_classes = (IsAuthenticated,)
    serializer_class = UserUpdateEmailSerializer

    # @method_decorator(ensure_csrf_cookie)
    def post(self, request, *args, **kwargs):
        try:
            user = CustomUser.objects.get(id=request.data.get('id'))
        except CustomUser.DoesNotExist as e:
            return Response({
                'status': 'User not found.',
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data['email']
        return Response({
            'status': 'Email updated succesfully!',
            'data': email,
        }, status=status.HTTP_200_OK)

