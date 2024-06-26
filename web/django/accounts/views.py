from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from django.utils.decorators import method_decorator
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
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'status': 'Authentication successful!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'redirect': '/settings',
        }, status=status.HTTP_201_CREATED)


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
        return Response({
            'status': 'Authentication successful!',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
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

