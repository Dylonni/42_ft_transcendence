import math
import random
from django.db import models
from django.db.models import Q
from django.utils import timezone

class GameManager(models.Manager):
    def create_game(self, name='', player_limit=5, win_score=5):
        game = self.create(
            name=self._generate_name(),
            player_limit=player_limit,
            win_score=win_score,
        )
        return game
    
    def search_by_name(self, name):
        return self.filter(name__icontains=name)
    
    def _generate_name(self):
        while True:
            number = random.randint(100000, 999999)
            name = f'Game_{number}'
            if not self.filter(name=name).exists():
                return name


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
            raise ValueError('Cannot send a game invite to yourself.')
        if self.filter(sender=sender, receiver=receiver).exists():
            raise ValueError('Game invite already sent.')
        if self.filter(sender=receiver, receiver=sender).exists():
            raise ValueError('Game invite already received.')
        
        game_invite = self.create(sender=sender, receiver=receiver)
        return game_invite
    
    def accept_invite(self, invite_id):
        game_invite = self.get(id=invite_id)
        # Add logic to add receiver in game_invite.game.id
        game_invite.delete()
    
    def decline_invite(self, invite_id):
        game_invite = self.get(id=invite_id)
        game_invite.delete()


class PlayerManager(models.Manager):
    def join_game(self, profile, game):
        player = self.create(profile=profile, game=game)
        return player
    
    def leave_game(self, profile, game):
        try:
            player = self.get(profile=profile, game=game)
            player.delete()
            return True
        except self.model.DoesNotExist:
            return False
    
    def mark_ready(self, player, ready):
        player.is_ready = ready
        player.save()
        return player
    
    def get_players_by_game_id(self, game_id):
        return self.filter(game__id=game_id)
    
    def can_start_game(self, game_id):
        players = self.get_players_by_game_id(game_id)
        return all(player.is_ready for player in players)
    
    def shuffle_players_for_game(self, game_id):
        players = list(self.get_players_by_game_id(game_id))
        random.shuffle(players)
        return players


# TODO: complete class
class RoundManager(models.Manager):
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
class ScoreManager(models.Manager):
    pass


# TODO: complete class
class GameMessageManager(models.Manager):
    pass