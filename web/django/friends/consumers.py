import json
import logging
from django.apps import apps
from django.template.loader import render_to_string
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.friendship_id = self.scope['url_route']['kwargs']['friendship_id']
        self.room_name = f"chat_{self.friendship_id}"
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
    
    async def receive(self, text_data=None, bytes_data = None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        logger.info(f'Preparing message to send: {message}')
        sender = await self.get_profile(self.user)
        receiver = await self.get_receiver(sender)
        friend_message = await self.send_message(sender, receiver, message)
        logger.info(f'Broadcasting message from user {sender.alias}: {message}')
    
    async def chat_message(self, event):
        message = event['message']
        profile = await self.get_profile(self.user)
        sender = await self.get_profile_from_alias(message['sender'])
        logger.info(f'Sending message to {message["receiver"]} in room {self.room_name}: {message["content"]}')
        if (str(message['sender']) != str(profile)):
            message = f'<div class="d-flex d-xxl-flex align-items-center align-items-xxl-center" id="template-friend-msg" style="height: auto;width: 100%;padding-bottom: 0px;margin-top: 15px;margin-bottom: 15px;">\
                            <div class="d-xxl-flex justify-content-xxl-center align-items-xxl-center" style="border-radius:0px;width:60px;height:60px;padding-left:0px;margin-left:10px;" href="#"><img width="93" height="135" src="{sender.avatar.url}" style="border-radius:41px;width:100%;height:100%;"></div>\
                            <div class="text-break" style="height: 100%;background: #4c575f;width: 65%;border-radius: 20px;margin-left: 20px;margin-top: 0px;padding-top: 10px;border-bottom-left-radius: 0px;border-top-left-radius: 19px;border-top-right-radius: 19px;border-bottom-right-radius: 19px;font-size: 19px;">\
                                <div class="message-wrapper" style="height:100%;width:90%;margin-left:0px;margin-right:0px;padding-left:10px;padding-right:10px;">\
                                    <p class="wrapbox" style="margin-left:0px;color:var(--bs-body-bg);width:100%;">{message["content"]}</p>\
                                </div>\
                                <div class="d-flex d-xl-flex d-xxl-flex justify-content-end justify-content-xl-end justify-content-xxl-end" style="margin-left: 20px;"><span style="font-size: 18px;color: rgba(255,255,255,0.41);margin-left: 0px;margin-right: 20px;margin-bottom: 5px;">{message["created_at"]}</span></div>\
                            </div>\
                        </div>'
        else:
            # message = render_to_string(path, context, )
            message = f'<div class="d-flex d-xxl-flex justify-content-end align-items-center justify-content-xxl-end align-items-xxl-center" id="template-my-msg" style="height: auto;width: 100%;margin-top: 15px;margin-bottom: 15px;">\
                            <div class="text-break" style="height: 100%;background: #3e7e5b;width: 65%;border-radius: 20px;margin-bottom: 0px;margin-top: 0px;padding-top: 10px;border-bottom-right-radius: 0px;border-top-left-radius: 19px;border-top-right-radius: 19px;border-bottom-left-radius: 19px;margin-right: 20px;font-size: 19px;">\
                                <div class="message-wrapper" style="height:100%;width:90%;margin-left:0px;margin-right:0px;padding-left:10px;padding-right:10px;">\
                                    <p class="wrapbox" style="margin-left: 0px;color: var(--bs-body-bg);width: 100%;">{message["content"]}</p>\
                                </div>\
                                <div class="d-flex d-xl-flex d-xxl-flex justify-content-end justify-content-xl-end justify-content-xxl-end"><span style="font-size: 18px;color: rgba(255,255,255,0.41);margin-right: 20px;margin-bottom: 5px;">{message["created_at"]}</span></div>\
                            </div>\
                        </div>'
        await self.send(text_data=json.dumps({'message': message}))
    
    @database_sync_to_async
    def get_profile(self, user):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.get(user=user)
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
    def get_receiver(self, sender):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            return friendship_model.objects.get_other(self.friendship_id, sender)
        except LookupError:
            return None
    
    @database_sync_to_async
    def send_message(self, sender, receiver, message):
        try:
            friendship_model = apps.get_model('friends.Friendship')
            friendship = friendship_model.objects.get(id=self.friendship_id)
            friendmessage_model = apps.get_model('friends.FriendMessage')
            return friendmessage_model.objects.send_message(sender, receiver, message, friendship)
        except LookupError:
            return None

chat_consumer = ChatConsumer.as_asgi()