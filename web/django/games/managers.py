import random
import string
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from notifs.consumers import NotifConsumer
from .consumers import GameChatConsumer, GamePlayConsumer


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
        async_to_sync(channel_layer.group_send)(f'games_chat_{game.id}', {'type': 'update_header'})
        consumer = GameChatConsumer()
        async_to_sync(consumer.send_message)(game=game, sender=player, category='Join')
    
    def remove_player(self, game, player):
        if player not in game.players.all():
            raise ValueError(_('Player is not in the game.'))
        player.leave_game()
        current_round = game.rounds.filter(Q(player1=player) | Q(player2=player), order=game.current_order)
        empty_round = game.rounds.filter(Q(player1=player) | Q(player2=player), started_at__isnull=False)
        game_terminated = False
        channel_layer = get_channel_layer()
        if current_round.exists() or empty_round.exists():
            game.ended_at = timezone.now()
            game.host = None
            game.save()
            for player in game.players.all():
                self.remove_player(game, player)
            game.messages.all().delete()
            remaining_rounds = game.rounds.filter(order__gt=game.current_order)
            remaining_rounds.delete()
            if empty_round.exists():
                empty_round.delete()
            if current_round.exists():
                current_round.delete()
            game_terminated = True
            async_to_sync(channel_layer.group_send)(f'games_play_{game.id}', {'type': 'terminate'})
        if game.players.count() == 0:
            if not game.ended_at:
                game.delete()
            return
        if game.host == player:
            new_host = game.players.first()
            if new_host:
                game.set_host(new_host)
        if not game_terminated:
            consumer = GameChatConsumer()
            async_to_sync(consumer.send_message)(game=game, sender=player, category='Leave')
            async_to_sync(channel_layer.group_send)(f'games_chat_{game.id}', {'type': 'update_header'})
            async_to_sync(channel_layer.group_send)(f'games_play_{game.id}', {'type': 'set_players'})
    
    def get_next_round(self, game):
        game.current_order += 1
        game.save()
        round = game.rounds.filter(order=game.current_order).first()
        if round:
            consumer = GameChatConsumer()
            async_to_sync(consumer.send_message)(game=game, category='Prepare')
        return round
    
    def start(self, game):
        if game.started_at:
            raise ValueError(_('Game has already started.'))
        game.started_at = timezone.now()
        game.save()
        for player in game.players.all():
            player.set_status(player.StatusChoices.PLAYING)
    
    def _generate_name(self):
        if self.filter(started_at=None).count() > 100:
            return None
        while True:
            number = ''.join(random.choices(string.digits, k=6))
            name = f'Game_{number}'
            if not self.filter(name=name, started_at=None).exists():
                return name


class GameRoundManager(models.Manager):
    def get_current_round(self, game):
        return self.filter(game=game, order=game.current_order).first()

    def get_last_matches(self, player):
        return self.filter(Q(player1=player) | Q(player2=player), ended_at__isnull=False).order_by('-started_at')[:20]
    
    def prepare_rounds(self, game):
        if game.started_at:
            raise ValueError(_('Game has already started.'))
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
                round_num += 1
        return rounds


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
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Game Invitation',
            object_id=game_invite.id,
        )
        game_invite.delete()
        return game, player
    
    def decline_invite(self, game_invite):
        consumer = NotifConsumer()
        async_to_sync(consumer.remove_notification)(
            category='Game Invitation',
            object_id=game_invite.id,
        )
        game_invite.delete()


class GameMessageManager(models.Manager):
    def get_messages(self, game, profile):
        blocked_profiles = profile.blocked_profiles.values_list('blocked', flat=True)
        return self.filter(game=game).exclude(
            models.Q(sender__in=blocked_profiles) & models.Q(category=self.model.GameMessageCategories.SEND)
        )
    
    def send_message(self, game, sender=None, content=None, category='Send'):
        if not content and category == 'Send':
            return
        game_message = self.create(game=game, sender=sender, content=content, category=category)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'games_chat_{game.id}',
            {
                'type': 'broadcast',
                'message_id': str(game_message.id),
            }
        )
        return game_message