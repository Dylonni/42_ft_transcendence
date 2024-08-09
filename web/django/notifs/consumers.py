import json
import logging
from django.apps import apps
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')


class NotifConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("NOTIF CONNECT")
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.group_name = f'user_{self.user.id}_notifications'
        logger.info(f'User {self.user} connecting to notifications.')
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f'User {self.user} disconnecting from notifications with close code {code}.')
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data = None):
        text_data_json = json.loads(text_data)
        notification = text_data_json['notification']
        logger.info(f'Preparing notification to send: {notification}')
        command = notification.get('command', None)
        if command == 'read_notification':
            notification_id = notification.get('id', None)
            await self.mark_notification_as_read(notification_id)
    
    async def send_notification(self, event):
        notification = event['notification']
        logger.info(f'Sending notification to user {self.user}: {notification}')
        await self.send(text_data=json.dumps({'notification': notification}))
    
    @database_sync_to_async
    def notify_profile(self, sender, receiver, category, content):
        try:
            notification_model = apps.get_model('notifs.Notification')
            notification = notification_model.objects.filter(sender=sender, receiver=receiver, category=category, content=content)
            if notification.exists():
                return None
            return notification_model.objects.send_notification(sender, receiver, category, content)
        except LookupError:
            logger.info('Error sending notification.')
            return None

notif_consumer = NotifConsumer.as_asgi()