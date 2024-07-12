import logging
from django.contrib.auth import logout
from django.shortcuts import redirect
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .utils import set_jwt_as_cookies

logger = logging.getLogger('django')


class JWTCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        public_paths = ['/', '/login', '/register']
        if request.path in public_paths:
            return self.get_response(request)
        
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        if not access_token:
            logger.info('No access token found in cookies.')
            return redirect('/login')
        
        try:
            AccessToken(access_token)
        except TokenError:
            logger.info('Invalid access token. Trying to refresh.')
            if not refresh_token:
                logger.warning('No refresh token found in cookies.')
                return self._logout_and_redirect(request)
            try:
                refresh = RefreshToken(refresh_token)
                access_token, refresh_token = str(refresh.access_token), str(refresh)
                logger.info('Successfully refreshed tokens.')
            except TokenError:
                logger.error('Invalid refresh token.')
                return self._logout_and_redirect(request)
        
        response = self.get_response(request)
        set_jwt_as_cookies(response, access_token, refresh_token)
        return response
    
    def _logout_and_redirect(self, request):
        logout(request)
        response = redirect('/login')
        response.delete_cookie(key='access_token')
        response.delete_cookie(key='refresh_token')
        return response