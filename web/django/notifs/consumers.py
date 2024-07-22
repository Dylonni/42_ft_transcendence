import json
import logging
from django.apps import apps
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')


class NotifConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.notif_id = self.scope['url_route']['kwargs']['notif_id']
        self.room_name = f'notif_{self.notif_id}'
        logger.info(f'User {self.user} connecting to notifications')
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f'User {self.user} disconnecting from notifications with close code {code}')
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data = None):
        text_data_json = json.loads(text_data)
        notification = text_data_json['notification']
        logger.info(f'Preparing notification to send: {notification}')
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'notification',
                'notification': notification
            }
        )
    
    async def notif_message(self, event):
        notification = event['notification']
        logger.info(f'Sending notification to user {self.user}: {notification}')
        await self.send(text_data=json.dumps({'notification': notification}))

notif_consumer = NotifConsumer.as_asgi()