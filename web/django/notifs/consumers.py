import json
import logging
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.template.loader import render_to_string

logger = logging.getLogger('django')


class NotifConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_name = f'notifs_{self.user.id}'
        logger.info(f'User {self.user} connecting to notifications.')
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        logger.info(f'User {self.user} disconnecting from notifications with close code {code}.')
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        notification = text_data_json.get('notification', {})
        command = notification.get('command', None)
        logger.info(f'Notification received with command: {command}')
        if (command == 'notifs_read'):
            await self.mark_all_notifications_as_read()
    
    async def send_notification(self, event):
        notif = event['notification']
        logger.info(f'Sending notification to user {self.user}: {notif}')
        category = notif['category']
        notif = await self.get_notification(notif['id'])
        context = {'notif': notif}
        match category:
            case 'Game Invitation':
                rendered_html = await sync_to_async(render_to_string)('notifs/notif_game_invite.html', context)
            case 'Friend Request':
                rendered_html = await sync_to_async(render_to_string)('notifs/notif_friend_request.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    @database_sync_to_async
    def notify_profile(self, sender, receiver, category, object_id):
        try:
            notification_model = apps.get_model('notifs.Notification')
            notification = notification_model.objects.filter(sender=sender, receiver=receiver, category=category, object_id=object_id).first()
            if not notification.exists():
                notification_model.objects.send_notification(sender, receiver, category, object_id)
        except LookupError:
            logger.info('Error sending notification.')
    
    @database_sync_to_async
    def get_notification(self, notif_id):
        try:
            notification_model = apps.get_model('notifs.Notification')
            return notification_model.objects.filter(id=notif_id).first()
        except LookupError:
            logger.info('Error getting notification.')
    
    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        try:
            notification_model = apps.get_model('notifs.Notification')
            notification_model.objects.mark_all_read_for_profile(self.user.profile)
        except LookupError:
            logger.info('Error marking notifications as read.')
    
    @database_sync_to_async
    def remove_notification(self, category, object_id):
        try:
            notification_model = apps.get_model('notifs.Notification')
            notif = notification_model.objects.filter(category=category, object_id=object_id).first()
            if notif:
                notif.delete()
        except LookupError:
            logger.info('Error removing notification.')

notif_consumer = NotifConsumer.as_asgi()