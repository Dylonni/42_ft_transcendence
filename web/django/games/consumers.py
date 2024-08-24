import asyncio
import json
import logging
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.template.loader import render_to_string

logger = logging.getLogger('django')


class GameChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO: verify if game id is correct and if player is in game
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'games_chat_{self.game_id}'
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
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        # TODO: handle player joining/leaving/chatting
        message = text_data_json['message']
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'broadcast',
                'message': message,
            }
        )
    
    async def broadcast(self, event):
        message_id = event['message_id']
        message = await self.get_message(message_id)
        context = {'message': message}
        rendered_html = await sync_to_async(render_to_string)('games/game_send.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    async def send_join_message(self, event):
        player_id = event['player_id']
        player = await self.get_profile(player_id)
        context = {'player': player}
        rendered_html = await sync_to_async(render_to_string)('games/game_wait.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    async def send_leave_message(self, event):
        player_id = event['player_id']
        player = await self.get_profile(player_id)
        context = {'player': player}
        rendered_html = await sync_to_async(render_to_string)('games/game_wait.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    @database_sync_to_async
    def get_message(self, message_id):
        try:
            gamemessage_model = apps.get_model('games.GameMessage')
            return gamemessage_model.objects.filter(id=message_id).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_profile(self, profile_id):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(id=profile_id).first()
        except LookupError:
            return None

game_chat_consumer = GameChatConsumer.as_asgi()


class GamePlayConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO: verify if game id is correct and if player is in game
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'games_play_{self.game_id}'
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
        action = text_data_json.get('action', '')
        if action == 'start_game':
            self.updating_game = True
            # TODO: set initial state
            self.game_state = {
                'player1_y': 250,
                'player2_y': 250,
                'ball_x': 400,
                'ball_y': 300,
                'paddle_height': 100,
                'paddle_width': 10,
                'ball_radius': 10,
            }
            asyncio.create_task(self.update_game_state())
        if action == 'move_paddle':
            position = text_data_json.get('position', 0)
            player = text_data_json.get('player', None)
            if player == 'player1':
                self.game_state['player1_y'] = position
            elif player == 'player2':
                self.game_state['player2_y'] = position
    
    async def update_game_state(self):
        while self.updating_game:
            # TODO: update ball position
            # TODO: check collision with top and bottom and update ball position
            # TODO: check collision with paddles and update ball position
            # TODO: check ball position and update score if necessary
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'game_state',
                    'game_state': self.game_state,
                }
            )
            await asyncio.sleep(1/60)
    
    async def game_state(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps({
            'action': 'update_state',
            'game_state': game_state,
        }))

game_play_consumer = GamePlayConsumer.as_asgi()