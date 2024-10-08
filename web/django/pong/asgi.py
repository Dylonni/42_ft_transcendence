"""
ASGI config for pong project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import friends.routing
import games.routing
import notifs.routing
from .middlewares import JWTAuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JWTAuthMiddlewareStack(URLRouter(
            friends.routing.websocket_urlpatterns
			+ games.routing.websocket_urlpatterns
			+ notifs.routing.websocket_urlpatterns
    )),
})