import asyncio
import json
import logging
import math
import random
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
        game = await self.get_game_by_player(player_id)
        context = {'game': game}
        rendered_html = await sync_to_async(render_to_string)('games/game_player.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    async def send_leave_message(self, event):
        game_id = event['game_id']
        game = await self.get_game(game_id)
        context = {'game': game}
        rendered_html = await sync_to_async(render_to_string)('games/game_player.html', context)
        await self.send(text_data=json.dumps({'element': rendered_html}))
    
    async def send_prepare_message(self, event):
        game_id = event['game_id']
        game = await self.get_game(game_id)
        context = {'game': game}
        rendered_html = await sync_to_async(render_to_string)('games/game_player.html', context)
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
    
    @database_sync_to_async
    def get_game(self, game_id):
        try:
            game_model = apps.get_model('games.Game')
            return game_model.objects.filter(id=game_id).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_game_by_player(self, profile_id):
        try:
            profile_model = apps.get_model('profiles.Profile')
            player = profile_model.objects.filter(id=profile_id).first()
            if player and player.game:
                return player.game
            return None
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
        logger.info(text_data_json)
        action = text_data_json.get('action', '')
        if action == 'start_game':
            self.updating_game = True
            self.game_state = await self.init_game_state(self.game_id)
            asyncio.create_task(self.update_game_state())
        if action == 'move_paddle':
            position = text_data_json.get('position', 0)
            player = text_data_json.get('player', None)
            if player == 'player1':
                self.game_state['player1_y'] = position - self.paddle_halfheight
            elif player == 'player2':
                self.game_state['player2_y'] = position - self.paddle_halfheight
    
    async def update_game_state(self):
        while self.updating_game:
            if not self.game_state['game_running']:
                break
            
            self.game_state['ball_x'] += self.game_state['ball_speed_x']
            self.game_state['ball_y'] += self.game_state['ball_speed_y']
            
            if self.game_state['ball_y'] <= 0 or self.game_state['ball_y'] >= self.height - self.ball_size:
                self.game_state['ball_speed_y'] = -self.game_state['ball_speed_y']
            
            if self.game_state['ball_x'] <= self.paddle_width:
                if self.game_state['player1_y'] <= self.game_state['ball_y'] <= self.game_state['player1_y'] + self.paddle_height:
                    self.game_state['ball_x'] = self.paddle_width
                    self.game_state['ball_speed_x'] = -self.game_state['ball_speed_x']
                else:
                    self.game_state['player2_score'] += 1
                    if self.game_state['player1_score'] >= self.win_score:
                        break
                    self.reset_ball()
            if self.game_state['ball_x'] >= self.width - self.paddle_width - self.ball_size:
                if self.game_state['player2_y'] <= self.game_state['ball_y'] <= self.game_state['player2_y'] + self.paddle_height:
                    self.game_state['ball_x'] = self.width - self.paddle_width - self.ball_size
                    self.game_state['ball_speed_x'] = -self.game_state['ball_speed_x']
                else:
                    self.game_state['player1_score'] += 1
                    if self.game_state['player1_score'] >= self.win_score:
                        break
                    self.reset_ball()
            
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'send_game_state',
                    'game_state': self.game_state,
                }
            )
            await asyncio.sleep(1/60)
    
    async def send_game_state(self, event):
        game_state = event['game_state']
        await self.send(text_data=json.dumps({
            'action': 'update_state',
            'game_state': game_state,
        }))
    
    def reset_ball(self):
        self.game_state['ball_x'] = (self.width - self.ball_size) / 2
        self.game_state['ball_y'] = (self.height - self.ball_size) / 2
        angle = random.random() * math.pi / 2 - math.pi / 4
        self.game_state['ball_speed_x'] *= -1 * self.ball_speed * math.cos(angle)
        self.game_state['ball_speed_y'] = self.ball_speed * math.sin(angle)
    
    @database_sync_to_async
    def init_game_state(self, game_id):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=game_id).first()
            if not game:
                return None
            self.win_score = game.win_score
            self.width = 1000
            self.height = 600
            self.halfwidth = self.width / 2
            self.halfheight = self.height / 2
            self.ball_size = game.get_ball_size()
            self.ball_speed = game.get_ball_speed()
            angle = random.random() * math.pi / 2 - math.pi / 4
            self.paddle_width = 10
            self.paddle_height = game.get_paddle_size()
            self.paddle_halfheight = self.paddle_height / 2
            self.paddle_speed = 8
            game_state = {
                'player1_y': (self.height - self.paddle_height) / 2,
                'player2_y': (self.height - self.paddle_height) / 2,
                'ball_x': (self.width - self.ball_size) / 2,
                'ball_y': (self.height - self.ball_size) / 2,
                'ball_speed_x': self.ball_speed * math.cos(angle),
                'ball_speed_y': self.ball_speed * math.sin(angle),
                'player1_score': 0,
                'player2_score': 0,
                'game_running': True,
            }
            return game_state
        except LookupError:
            return None

game_play_consumer = GamePlayConsumer.as_asgi()