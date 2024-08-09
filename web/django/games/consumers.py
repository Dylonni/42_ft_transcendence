import json
import logging
from django.apps import apps
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'game_{self.game_id}'
        logger.info(f'User {self.user} connecting to room {self.room_name}')
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f'User {self.user} disconnecting from room {self.room_name} with close code {code}')
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

game_consumer = GameConsumer.as_asgi()