from django.http import HttpResponse
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

def set_jwt_cookies_for_user(response, user):
    refresh = RefreshToken.for_user(user)
    set_jwt_as_cookies(response, str(refresh.access_token), str(refresh))
    return str(refresh.access_token), str(refresh)

def set_jwt_as_cookies(response: HttpResponse, access_token, refresh_token):
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='Lax',
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite='Lax',
    )

def unset_jwt_cookies(response: HttpResponse):
    response.delete_cookie(key='access_token')
    response.delete_cookie(key='refresh_token')

def is_token_valid(token):
    try:
        AccessToken(token)
        return True
    except TokenError:
        return False

def get_jwt_from_refresh(refresh_token):
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token), str(refresh)
    except TokenError:
        return None, None