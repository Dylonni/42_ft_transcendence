import json
import logging
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.db.models import OuterRef, Q, Subquery
from django.template.loader import render_to_string

logger = logging.getLogger('django')


class FriendListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.profile = await self.get_profile()
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
        status = text_data_json.get('status', {})
    
    async def update_friend_list(self, event):
        friendships = await self.get_friendships()
        context = {'friendships': friendships, 'profile': self.profile}
        friend_list = await sync_to_async(render_to_string)('friends/social_list.html', context)
        await self.send(text_data=json.dumps({'friend_list': friend_list}))
    
    @database_sync_to_async
    def get_profile(self):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(user=self.user).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_friendships(self):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            return friendship_model.objects.get_friendships(self.profile)
        except LookupError:
            return None

friend_list_consumer = FriendListConsumer.as_asgi()


class FriendChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.friendship_id = self.scope['url_route']['kwargs']['friendship_id']
        self.profile = await self.get_profile()
        self.room_name = f'friends_{self.friendship_id}'
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
        await self.mark_messages_as_read()
        await self.channel_layer.group_send(self.room_name, {'type': 'update_section'})
        await self.channel_layer.group_send('friends', {'type': 'update_friend_list'})
    
    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        read = text_data_json.get('read')
        if read:
            await self.mark_messages_as_read()
            await self.channel_layer.group_send(self.room_name, {'type': 'update_section'})
            await self.channel_layer.group_send('friends', {'type': 'update_friend_list'})
        message = text_data_json.get('message')
        if message:
            sender = self.profile
            friend_message = await self.send_message(sender, message)
    
    async def broadcast(self, event):
        message_id = event.get('message_id', '')
        message = await self.get_message(message_id)
        if await self.is_blocked(message):
            return
        context = {'message': message, 'profile': self.profile}
        rendered_html = await sync_to_async(render_to_string)('friends/social_message.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    async def update_header(self, event):
        current_friend = await self.get_current_friend()
        context = {'current_friend': current_friend}
        friend_header = await sync_to_async(render_to_string)('friends/social_header.html', context)
        await self.send(text_data=json.dumps({'friend_header': friend_header}))
    
    async def update_section(self, event):
        current_friend = await self.get_current_friend()
        messages = await self.get_messages()
        context = {'current_friend': current_friend, 'messages': messages, 'profile': self.profile}
        section = await sync_to_async(render_to_string)('friends/social_section.html', context)
        await self.send(text_data=json.dumps({'section': section}))
    
    @database_sync_to_async
    def get_profile(self):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(user=self.user).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def is_blocked(self, message):
        return self.profile.blocked_profiles.filter(blocked=message.sender).exists()
    
    @database_sync_to_async
    def get_current_friend(self):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.filter(id=self.friendship_id).first()
            if friendship:
                return friendship.get_other(self.profile)
            return None
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_profile_from_alias(self, alias):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(alias=alias).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_message(self, message_id):
        try:
            friendmessage_model = apps.get_model('friends.FriendMessage')
            return friendmessage_model.objects.filter(id=message_id).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_messages(self):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.filter(id=self.friendship_id).first()
            if friendship:
                friendmessage_model = apps.get_model('friends.FriendMessage')
                return friendmessage_model.objects.get_messages(friendship, self.profile)
            return None
        except LookupError:
            return None
    
    @database_sync_to_async
    def send_message(self, sender, message):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.filter(id=self.friendship_id).first()
            if friendship:
                friendmessage_model = apps.get_model('friends.FriendMessage')
                return friendmessage_model.objects.send_message(friendship, sender, message)
        except LookupError:
            return None
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.filter(id=self.friendship_id).first()
            if friendship:
                for message in friendship.messages.filter(receiver=self.profile, read=False).all():
                    if not self.profile.blocked_profiles.filter(blocked=message.sender).exists():
                        message.mark_as_read()
        except LookupError:
            return None

friend_chat_consumer = FriendChatConsumer.as_asgi()