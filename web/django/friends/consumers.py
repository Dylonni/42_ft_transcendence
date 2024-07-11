import json
import logging
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('django')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
        self.room_name = f'chat_{self.scope['url_route']['kwargs']['friendship_id']}'
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
        logger.debug(f'Received message from user {self.user}: {message}')
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message,
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        logger.debug(f'Sending message to user {self.user} in room {self.room_name}: {message}')
        await self.send(text_data=json.dumps({'message': message}))