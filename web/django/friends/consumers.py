import json
import logging
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.template.loader import render_to_string

logger = logging.getLogger('django')


class FriendListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_name = f'friends'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        # TODO: handle friend changing status
        status = text_data_json.get('status', {})

friend_list_consumer = FriendListConsumer.as_asgi()


class FriendChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.friendship_id = self.scope['url_route']['kwargs']['friendship_id']
        self.room_name = f"friends_{self.friendship_id}"
        logger.info(f"User {self.user} connecting to room {self.room_name}")
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
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', {})
        logger.info(f'Preparing message to send: {message}')
        sender = await self.get_profile(self.user)
        friend_message = await self.send_message(sender, message)
        logger.info(f'Broadcasting message from user {sender.alias}: {message}')
    
    async def broadcast(self, event):
        message_id = event.get('message_id', '')
        profile = await self.get_profile(self.user)
        message = await self.get_message(message_id)
        context = {'message': message, 'profile': profile}
        rendered_html = await sync_to_async(render_to_string)('friends/social_message.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    @database_sync_to_async
    def get_profile(self, user):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(user=user).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_profile_from_alias(self, alias):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.get(alias=alias)
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_message(self, message_id):
        try:
            friendmessage_model = apps.get_model('friends.FriendMessage')
            return friendmessage_model.objects.get(id=message_id)
        except LookupError:
            return None
    
    @database_sync_to_async
    def send_message(self, sender, message):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.get(id=self.friendship_id)
            friendmessage_model = apps.get_model('friends.FriendMessage')
            return friendmessage_model.objects.send_message(friendship, sender, message)
        except LookupError:
            return None

friend_chat_consumer = FriendChatConsumer.as_asgi()