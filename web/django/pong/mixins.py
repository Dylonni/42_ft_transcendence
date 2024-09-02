import logging
from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils import translation
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from accounts.utils import set_jwt_as_cookies
from profiles.models import Profile

UserModel = get_user_model()
logger = logging.getLogger('django')


class LangVerificationMixin:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        lang = request.COOKIES.get('lang', 'en')
        if lang not in dict(settings.LANGUAGES):
            response.set_cookie(
                key='lang',
                value='en',
            )
            translation.activate(lang)
        return response


class RedirectIfAuthenticatedMixin:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            logger.info('User is authenticated. Redirecting to /home/.')
            return redirect('/home/')
        return super().dispatch(request, *args, **kwargs)


class JWTCookieAuthenticationMixin:
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        access_token = request.COOKIES.get('access_token', None)
        refresh_token = request.COOKIES.get('refresh_token', None)
        if access_token is None:
            logger.info('No access token found in cookies.')
            return redirect('/')
        
        try:
            access_token_obj = AccessToken(access_token)
        except TokenError:
            logger.info('Invalid access token. Trying to refresh.')
            if refresh_token is None:
                logger.warning('No refresh token found in cookies.')
                return self._logout_and_redirect(request)
            try:
                refresh = RefreshToken(refresh_token)
                access_token, refresh_token = str(refresh.access_token), str(refresh)
                access_token_obj = AccessToken(access_token)
                logger.info('Successfully refreshed tokens.')
            except TokenError:
                logger.error('Invalid refresh token.')
                return self._logout_and_redirect(request)
        
        try:
            user_id = access_token_obj['user_id']
            request.user = UserModel.objects.get(id=user_id)
            request.profile = Profile.objects.get(user__id=user_id)
            lang = request.profile.default_lang
            if lang != request.COOKIES.get('lang', 'en') and lang in dict(settings.LANGUAGES):
                response.set_cookie(
                    key='lang',
                    value=lang,
                )
                translation.activate(lang)
        except UserModel.DoesNotExist:
            logger.error('User does not exist.')
            return self._logout_and_redirect(request)
        except Profile.DoesNotExist:
            logger.error('Profile does not exist.')
            return self._logout_and_redirect(request)
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
        response = super().dispatch(request, *args, **kwargs)
        set_jwt_as_cookies(response, access_token, refresh_token)
        return response
    
    def _logout_and_redirect(self, request):
        logout(request)
        response = redirect('/login/')
        response.delete_cookie(key='access_token')
        response.delete_cookie(key='refresh_token')
        return response