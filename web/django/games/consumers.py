import asyncio
import json
import logging
import math
import random
import redis
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from django.template.loader import render_to_string

logger = logging.getLogger('django')
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)


class GameChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO: verify if game id is correct and if player is in game
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.profile = await self.get_profile()
        self.room_name = f'games_chat_{self.game_id}'
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
    
    async def broadcast(self, event):
        message_id = event['message_id']
        game = await self.get_game()
        round = await self.get_current_round()
        message = await self.get_message(message_id)
        if await self.is_blocked(message):
            return
        context = {'game': game, 'round': round, 'message': message, 'profile': self.profile}
        rendered_html = await sync_to_async(render_to_string)('games/game_message.html', context)
        await self.send(text_data=json.dumps({'message': rendered_html}))
    
    async def update_header(self, event):
        game = await self.get_game()
        round = await self.get_current_round()
        context = {'game': game, 'round': round}
        rendered_html = await sync_to_async(render_to_string)('games/game_header.html', context)
        await self.send(text_data=json.dumps({'header': rendered_html}))
    
    @database_sync_to_async
    def get_message(self, message_id):
        try:
            gamemessage_model = apps.get_model('games.GameMessage')
            return gamemessage_model.objects.filter(id=message_id).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def send_message(self, game, sender=None, category='Send'):
        try:
            gamemessage_model = apps.get_model('games.GameMessage')
            gamemessage_model.objects.send_message(game=game, sender=sender, category=category)
        except LookupError:
            return None
    
    @database_sync_to_async
    def is_blocked(self, message):
        if message.sender:
            return self.profile.blocked_profiles.filter(blocked=message.sender).exists() and message.category == 'Send'
        return False

    @database_sync_to_async
    def get_profile(self):
        try:
            profile_model = apps.get_model('profiles.Profile')
            return profile_model.objects.filter(user=self.user).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_game(self):
        try:
            game_model = apps.get_model('games.Game')
            return game_model.objects.filter(id=self.game_id).first()
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_round(self, round_id):
        try:
            round_model = apps.get_model('games.GameRound')
            return round_model.objects.filter(id=round_id).first()
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
    
    @database_sync_to_async
    def get_current_round(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                return round
            return None
        except LookupError:
            return None

game_chat_consumer = GameChatConsumer.as_asgi()


class GamePlayConsumer(AsyncWebsocketConsumer):
    FPS = 1/60
    state_lock = asyncio.Lock()

    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.updating_game = False
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_name = f'games_play_{self.game_id}'
        self.player = await self.get_player()
        if not self.player:
            await self.close()
            return
        self.which = await self.check_player()
        if not redis_client.exists(f'{str(self.game_id)}'):
            await self.init_game()
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
    
    async def init_game(self):
        game = await self.get_game(self.game_id)
        if not game:
            return None
        width = 1000
        height = 600
        win_score = await self.get_win_score(game)
        ball_size = await self.get_ball_size(game)
        ball_speed = await self.get_ball_speed(game)
        paddle_height = await self.get_paddle_size(game)
        game_state = {
            'game_running': False,
            'countdown': 0,
            'width': width,
            'height': height,
            'win_score': win_score,
            'ball_size': ball_size,
            'ball_speed': ball_speed,
            'paddle_width': 10,
            'paddle_height': paddle_height,
            'paddle_speed': 8,
            'player1_score': 0,
            'player2_score': 0,
            'player1_y': (height - paddle_height) / 2,
            'player2_y': (height - paddle_height) / 2,
            'ball_x': (width - ball_size) / 2,
            'ball_y': (height - ball_size) / 2,
            'ball_speed_x': 0,
            'ball_speed_y': 0,
        }
        self.set_game_state(game_state)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action', '')
        
        if action in ['move_key', 'move_mouse']:
            await self.handle_player_move(action, text_data_json)
            # asyncio.create_task(self.handle_player_move(action, text_data_json))
        elif action == 'next_round':
            self.channel_layer.task = asyncio.create_task(self.start_loop())
    
    async def handle_player_move(self, action, data):
        direction = data.get('direction', 0)
        position = data.get('position', 0)
        async with GamePlayConsumer.state_lock:
            game_state = self.get_game_state()
            if game_state['game_running']:
                if action == 'move_key':
                    if self.which == 'player1':
                        game_state['player1_y'] = max(0, min(game_state['player1_y'] + direction * game_state['paddle_speed'], game_state['height'] - game_state['paddle_height']))
                    elif self.which == 'player2':
                        game_state['player2_y'] = max(0, min(game_state['player2_y'] + direction * game_state['paddle_speed'], game_state['height'] - game_state['paddle_height']))
                elif action == 'move_mouse':
                    if self.which == 'player1':
                        direction = 1 if game_state['player1_y'] < position - game_state['paddle_height'] / 2 else -1
                        game_state['player1_y'] = max(0, min(game_state['player1_y'] + direction * game_state['paddle_speed'], game_state['height'] - game_state['paddle_height']))
                    elif self.which == 'player2':
                        direction = 1 if game_state['player2_y'] < position - game_state['paddle_height'] / 2 else -1
                        game_state['player2_y'] = max(0, min(game_state['player2_y'] + direction * game_state['paddle_speed'], game_state['height'] - game_state['paddle_height']))
                self.set_game_state(game_state)
                await self.channel_layer.group_send(
                    self.room_name,
                    {
                        'type': 'send_game_state',
                        'game_state': game_state,
                    }
                )
    
    def get_game_state(self):
        game_state = redis_client.get(f'{str(self.game_id)}')
        return json.loads(game_state)
    
    def set_game_state(self, game_state):
        redis_client.set(f'{str(self.game_id)}', json.dumps(game_state))
    
    async def send_game_state(self, event):
        await self.send(text_data=json.dumps({'game_state': event.get('game_state')}))
    
    async def send_countdown(self, event):
        await self.send(text_data=json.dumps({'countdown': event.get('countdown')}))
    
    async def send_home(self, event):
        await self.send(text_data=json.dumps({'redirect': '/home/'}))
    
    async def send_header(self, event):
        game = await self.get_game(self.game_id)
        round = await self.get_round()
        context = {'game': game, 'round': round}
        rendered_html = await sync_to_async(render_to_string)('games/game_header.html', context)
        await self.send(text_data=json.dumps({'header': rendered_html}))
    
    async def terminate(self, event):
        if hasattr(self.channel_layer, 'task') and self.channel_layer.task:
            self.channel_layer.task.cancel()
            try:
                await self.channel_layer.task
            except asyncio.CancelledError:
                pass
        await self.send(text_data=json.dumps({'redirect': '/home/'}))
    
    async def set_players(self, event):
        self.which = await self.check_player()
        game = await self.get_game(self.game_id)
        round = await self.get_round()
        player = await self.get_player()
        context = {'game': game, 'round': round, 'profile': player}
        rendered_html = await sync_to_async(render_to_string)('games/game_ready.html', context)
        await self.send(text_data=json.dumps({'ready': rendered_html}))
    
    async def prepare_next_round(self):
        await self.set_game_start()
        await self.channel_layer.group_send(self.room_name, {'type': 'set_players'})
        time = 3
        countdown = time - self.FPS
        while countdown > 0:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'send_countdown',
                    'countdown': math.ceil(countdown),
                }
            )
            await asyncio.sleep(self.FPS)
            countdown -= self.FPS
        countdown = 0
        await self.channel_layer.group_send(self.room_name, {'type': 'send_header'})
    
    async def start_countdown(self):
        countdown = 3 - self.FPS
        last_value = 4
        while countdown > 0:
            value = math.ceil(countdown)
            if last_value != value:
                last_value = value
                await self.update_game_state('countdown', str(value))
            await asyncio.sleep(self.FPS)
            countdown -= self.FPS
        await self.update_game_state('countdown', None)
    
    async def start_loop(self):
        try:
            await self.prepare_next_round()
            async with GamePlayConsumer.state_lock:
                game_state = self.get_game_state()
                game_state['player1_score'] = 0
                game_state['player2_score'] = 0
                game_state['game_running'] = True
                width = game_state['width']
                height = game_state['height']
                game_state['player1_y'] = (height - game_state['paddle_height']) / 2
                game_state['player2_y'] = (height - game_state['paddle_height']) / 2
                self.set_game_state(game_state)
                ball_speed = game_state['ball_speed']
                ball_speed_x = ball_speed
                ball_speed_y = ball_speed
            await self.set_round_start()
            has_scored = True
            while True:
                if has_scored:
                    async with GamePlayConsumer.state_lock:
                        game_state = self.get_game_state()
                        game_state['ball_x'] = (width - game_state['ball_size']) / 2
                        game_state['ball_y'] = (height - game_state['ball_size']) / 2
                        angle = random.random() * math.pi / 2 - math.pi / 4
                        direction = -1 if ball_speed_x < 0 else 1
                        ball_speed = game_state['ball_speed']
                        ball_speed_x = direction * ball_speed * math.cos(angle)
                        ball_speed_y = ball_speed * math.sin(angle)
                        self.set_game_state(game_state)
                        if game_state['player1_score'] >= game_state['win_score'] or game_state['player2_score'] >= game_state['win_score']:
                            break
                    await self.start_countdown()
                    has_scored = False
                
                async with GamePlayConsumer.state_lock:
                    game_state = self.get_game_state()
                    game_state['ball_x'] += ball_speed_x
                    game_state['ball_y'] += ball_speed_y
                    
                    if game_state['ball_y'] < 0:
                        ball_speed_y = -ball_speed_y
                    elif game_state['ball_y'] > height - game_state['ball_size']:
                        ball_speed_y = -ball_speed_y
                    
                    if game_state['ball_x'] < game_state['paddle_width']:
                        if game_state['player1_y'] - game_state['ball_size'] < game_state['ball_y'] < game_state['player1_y'] + game_state['paddle_height']:
                            ball_speed_x = -ball_speed_x
                            angle = math.atan2(ball_speed_y, ball_speed_x)
                            ball_speed += 1
                            ball_speed_x = ball_speed * math.cos(angle)
                            ball_speed_y = ball_speed * math.sin(angle)
                        else:
                            game_state['player2_score'] += 1
                            await self.update_score(game_state)
                            await self.channel_layer.group_send(self.room_name, {'type': 'send_header'})
                            has_scored = True
                    elif game_state['ball_x'] > width - game_state['ball_size'] - game_state['paddle_width']:
                        if game_state['player2_y'] - game_state['ball_size'] < game_state['ball_y'] < game_state['player2_y'] + game_state['paddle_height']:
                            ball_speed_x = -ball_speed_x
                            angle = math.atan2(ball_speed_y, ball_speed_x)
                            ball_speed += 1
                            ball_speed_x = ball_speed * math.cos(angle)
                            ball_speed_y = ball_speed * math.sin(angle)
                        else:
                            game_state['player1_score'] += 1
                            await self.update_score(game_state)
                            await self.channel_layer.group_send(self.room_name, {'type': 'send_header'})
                            has_scored = True
                    self.set_game_state(game_state)
                    await self.channel_layer.group_send(
                        self.room_name,
                        {
                            'type': 'send_game_state',
                            'game_state': game_state,
                        }
                    )
                await asyncio.sleep(self.FPS)
        
            winner = await self.set_round_winner()
            winner_msg = winner + ' wins!'
            await self.send_win_message()
            await self.update_game_state('countdown', winner_msg)
            countdown = 3 - self.FPS
            while countdown > 0:
                await asyncio.sleep(self.FPS)
                countdown -= self.FPS
            countdown = 0
            await self.update_game_state('countdown', None)
            await self.update_game_state('game_running', False)
            round = await self.get_next_round()
            if round:
                self.channel_layer.task = asyncio.create_task(self.start_loop())
            else:
                await self.end_game()
                await self.channel_layer.group_send(self.room_name, {'type': 'send_home'})
        except asyncio.CancelledError:
            await self.update_game_state('game_running', False)
            await self.channel_layer.group_send(self.room_name, {'type': 'terminate'})
            raise
    
    async def update_game_state(self, key, value):
        async with GamePlayConsumer.state_lock:
            game_state = self.get_game_state()
            game_state[key] = value
            self.set_game_state(game_state)
            await self.channel_layer.group_send(
                self.room_name,
                {
                    'type': 'send_game_state',
                    'game_state': game_state,
                }
            )
    
    @database_sync_to_async
    def get_player(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                if game.ended_at:
                    return None
                profile_model = apps.get_model('profiles.Profile')
                profile = profile_model.objects.filter(user=self.user).first()
                if profile not in game.players.all():
                    return None
            return profile
        except LookupError:
            return None
    
    @database_sync_to_async
    def send_win_message(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                if round:
                    gamemessage_model = apps.get_model('games.GameMessage')
                    gamemessage_model.objects.send_message(game=game, sender=round.winner, category='Win')
        except LookupError:
            return None
    
    @database_sync_to_async
    def check_player(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                if round:
                    if self.player == round.player1:
                        return 'player1'
                    if self.player == round.player2:
                        return 'player2'
            return None
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
    def get_win_score(self, game):
        return game.win_score
    
    @database_sync_to_async
    def get_ball_size(self, game):
        return game.get_ball_size()
    
    @database_sync_to_async
    def get_ball_speed(self, game):
        return game.get_ball_speed()
    
    @database_sync_to_async
    def get_paddle_size(self, game):
        return game.get_paddle_size()
    
    @database_sync_to_async
    def get_round(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                return round
            return None
        except LookupError:
            return None
    
    @database_sync_to_async
    def set_game_start(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                game.start()
        except LookupError:
            return None
    
    @database_sync_to_async
    def set_round_start(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                if round:
                    round.start()
                return round
            return None
        except LookupError:
            return None
    
    @database_sync_to_async
    def update_score(self, game_state):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                if round:
                    round.update_score(game_state['player1_score'], game_state['player2_score'])
                    logger.info(f'round {round.id}: {round.score1} - {round.score2}')
        except LookupError:
            return None
    
    @database_sync_to_async
    def set_round_winner(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                round_model = apps.get_model('games.GameRound')
                round = round_model.objects.filter(game=game, order=game.current_order).first()
                if round:
                    round.end()
                    return round.winner.alias
        except LookupError:
            return None
    
    @database_sync_to_async
    def get_next_round(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                return game_model.objects.get_next_round(game)
        except LookupError:
            return None
    
    @database_sync_to_async
    def end_game(self):
        try:
            game_model = apps.get_model('games.Game')
            game = game_model.objects.filter(id=self.game_id).first()
            if game:
                game.end()
        except LookupError:
            return None

game_play_consumer = GamePlayConsumer.as_asgi()