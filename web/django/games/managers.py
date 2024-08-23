import math
import random
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from notifs.consumers import NotifConsumer


class GameManager(models.Manager):
    def create_game(self, player):
        if player.game:
            raise ValueError(_('Player is already in a game.'))
        game = self.create(name=self.generate_name(), host=player)
        player.join_game(game)
        return game
    
    def search_by_name(self, name):
        return self.filter(name__icontains=name)
    
    def generate_name(self):
        while True:
            number = random.randint(100000, 999999)
            name = f'Game_{number}'
            if not self.filter(name=name).exists():
                return name
    
    def add_player(self, game, player):
        if player.game:
            raise ValueError(_('Player is already in a game.'))
        elif game.is_full():
            raise ValueError(_('Game is full. Unable to join.'))
        player.join_game(game)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_{game.id}',
            {
                'type': 'send_join_message',
                'player_id': str(player.id),
            }
        )
    
    def remove_player(self, game, player):
        player.leave_game()
        if game.host == player:
            new_host = game.players.exclude(id=player.id).first()
            if new_host:
                game.set_host(new_host)
            else:
                game.delete()
        # TODO: remove player from game rounds if game has started
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_{game.id}',
            {
                'type': 'send_leave_message',
                'player_id': str(player.id),
            }
        )


class GameRoundManager(models.Manager):
    def create_round(self, player1, player2):
        round = self.create(player1=player1, player2=player2)
        return round
    
    def prepare_rounds(self, players, game):
        total_players = len(players)
        total_rounds = total_players - 1
        series = math.ceil(math.log2(total_players))
        order = total_rounds + series
        rounds = []
        next_rounds = [None]
        for round_num in range(1, rounds + 1):
            current_serie_rounds = []
            for i in range(2**(round_num - 1)):
                next_round = next_rounds.pop(0)
                if round_num == rounds:
                    if 2 * i + 1 < total_players:
                        player1 = players[2 * i]
                        player2 = players[2 * i + 1]
                        round = self.create_round(player1=player1, player2=player2, order=order, next_round=next_round)
                    else:
                        round = self.create_round(player1=players[2 * i], player2=None, order=order, next_round=next_round)
                else:
                    round = self.create_round(player1=None, player2=None, order=order, next_round=next_round)
                    current_serie_rounds.append(round)
                    current_serie_rounds.append(round)
                rounds.append(round)
                order -= 1
            next_rounds.extend(current_serie_rounds)
        game.current_order = 1
        game.started_at = timezone.now()
        game.save()
        return rounds
    
    def start_game(self, players):
        rounds = self.prepare_rounds(players)
        if rounds:
            first_round = rounds[0]
            first_round.started = True
            first_round.save()
            first_round.player1.set_waiting()
            first_round.player2.set_waiting()
            first_round.player1.save()
            first_round.player2.save()
            for player in players:
                if player != first_round.player1 and player != first_round.player2:
                    player.set_watching()
                    player.save()
        return rounds


# TODO: complete class
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
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError(_('Game invite already sent.'))
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError(_('Game invite already received.'))
        
        game_invite = self.create(sender=sender, receiver=receiver)
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
            f'games_{game.id}',
            {
                'type': 'broadcast',
                'message_id': str(game_message.id),
            }
        )
        return game_message