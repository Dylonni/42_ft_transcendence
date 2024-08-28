import math
import random
import string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from notifs.consumers import NotifConsumer


class GameManager(models.Manager):
    def set_game_infos(self, game, player):
        if player.game:
            raise ValueError(_('Player is already in a game.'))
        name = self._generate_name()
        if not name:
            raise ValueError(_('Server is full. Try to create a game later.'))
        game.name = name
        game.host = player
        game.save()
        player.join_game(game)
        return game
    
    def search_by_name(self, name):
        return self.filter(name__icontains=name)
    
    def add_player(self, game, player):
        if player.game:
            raise ValueError(_('Player is already in a game.'))
        elif game.is_full():
            raise ValueError(_('Game is full. Unable to join.'))
        elif game.started_at:
            raise ValueError(_('Game has already started.'))
        player.join_game(game)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_chat_{game.id}',
            {
                'type': 'send_join_message',
                'player_id': str(player.id),
            }
        )
    
    def remove_player(self, game, player):
        if player not in game.players.all():
            raise ValueError(_('Player is not in the game.'))
        player.leave_game()
        if game.players.count() == 0:
            game.delete()
            return
        if game.host == player:
            new_host = game.players.first()
            if new_host:
                game.set_host(new_host)
        # TODO: remove player from game rounds if game has started
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_chat_{game.id}',
            {
                'type': 'send_leave_message',
                'player_id': str(player.id),
                'game_id': str(game.id),
            }
        )
    
    def get_next_round(self, game):
        game.current_order += 1
        game.save()
        return game.rounds.filter(order=game.current_order).first()
    
    def _generate_name(self):
        if self.filter(started_at=None).count() > 100:
            return None
        while True:
            number = ''.join(random.choices(string.digits, k=6))
            name = f'Game_{number}'
            if not self.filter(name=name, started_at=None).exists():
                return name


class GameRoundManager(models.Manager):
    def get_last_matches(self, player):
        return self.filter(Q(player1=player) | Q(player2=player), ended_at__isnull=False).order_by('-started_at')[:20]
    
    def prepare_rounds(self, game):
        players = list(game.players.all())
        random.shuffle(players)
        total_players = len(players)
        total_rounds = total_players - 1
        rounds = []
        for round_num in range(total_rounds):
            round = self.create(game=game, order=round_num)
            rounds.append(round)
        round_num = 0
        for player in players:
            if not rounds[round_num].player1:
                rounds[round_num].player1 = player
                rounds[round_num].save()
            elif not rounds[round_num].player2:
                rounds[round_num].player2 = player
                rounds[round_num].save()
            else:
                round_num += 1
        return rounds
    
    def start_game(self, game):
        if game.started_at:
            raise ValueError(_('Game has already started.'))
        self.prepare_rounds(game)
        # TODO: send prepare message


class GameInviteManager(models.Manager):
    def get_invite(self, sender, receiver):
        return self.filter(
            Q(sender=sender, receiver=receiver) | 
            Q(sender=receiver, receiver=sender)
        ).first()
    
    def get_invites(self, profile):
        return self.filter(Q(sender=profile) | Q(receiver=profile))
    
    def get_received_invites(self, profile):
        return self.filter(receiver=profile)
    
    def create_invite(self, sender, receiver):
        if sender == receiver:
            raise ValueError(_('Cannot send a game invite to yourself.'))
        if not sender.game:
            raise ValueError(_('Sender is not in a game.'))
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError(_('Game invite already sent.'))
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError(_('Game invite already received.'))
        
        game_invite = self.create(sender=sender, receiver=receiver, game=sender.game)
        consumer = NotifConsumer()
        async_to_sync(consumer.notify_profile)(
            sender=game_invite.sender,
            receiver=game_invite.receiver,
            category='Game Invitation',
            object_id=game_invite.id,
        )
        return game_invite
    
    def accept_invite(self, game_invite):
        player = game_invite.receiver
        game = game_invite.game
        if player.game:
            raise ValueError(_('Player is already in a game.'))
        elif game.is_full():
            raise ValueError(_('Game is full. Unable to join.'))
        player.join_game(game)
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Game Invite',
            object_id=game_invite.id,
        )
        game_invite.delete()
    
    def decline_invite(self, game_invite):
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Game Invite',
            object_id=game_invite.id,
        )
        game_invite.delete()


class GameMessageManager(models.Manager):
    def send_message(self, game, sender, content):
        game_message = self.create(game=game, sender=sender, content=content)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_chat_{game.id}',
            {
                'type': 'broadcast',
                'message_id': str(game_message.id),
            }
        )
        return game_message