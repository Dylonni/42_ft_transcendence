from django.contrib.auth import logout
from .utils import (
    is_token_valid,
    get_jwt_from_refresh,
    unset_jwt_cookies,
)

class JWTCookieMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')
        invalid_tokens = False
        if access_token:
            if is_token_valid(access_token):
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            else:
                access_token, refresh_token = get_jwt_from_refresh(refresh_token)
                if not access_token:
                    invalid_tokens = True
        
        response = self.get_response(request)
        
        if invalid_tokens:
            unset_jwt_cookies(response)
            logout(request)
        return response