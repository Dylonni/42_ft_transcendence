from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from jwt import decode as jwt_decode, exceptions as jwt_exceptions
from django.conf import settings

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        from django.contrib.auth.models import AnonymousUser  # Moved here
        from django.contrib.auth import get_user_model

        User = get_user_model()
        headers = dict(scope['headers'])
        cookies = self.get_cookies_from_headers(headers)
        access_token = cookies.get('access_token', None)
        if access_token:
            try:
                payload = jwt_decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
                user = await self.get_user(payload['user_id'])
                scope['user'] = user
            except (jwt_exceptions.ExpiredSignatureError, jwt_exceptions.InvalidTokenError):
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)

    @staticmethod
    def get_cookies_from_headers(headers):
        cookies = {}
        if b'cookie' in headers:
            cookie_header = headers[b'cookie'].decode('utf-8')
            cookies = {key: value for key, value in (pair.split('=') for pair in cookie_header.split('; '))}
        return cookies

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            from django.contrib.auth.models import AnonymousUser
            return AnonymousUser()


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))