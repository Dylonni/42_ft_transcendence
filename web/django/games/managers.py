import math
import random
from django.db import models
from django.utils import timezone

class TournamentManager(models.Manager):
    def create_tournament(self, name, player_limit=1, win_score=5):
        tournament = self.create(name=name, player_limit=player_limit, win_score=win_score)
        return tournament


class PlayerManager(models.Manager):
    def join_tournament(self, profile, tournament):
        player = self.create(profile=profile, tournament=tournament)
        return player
    
    def leave_tournament(self, profile, tournament):
        try:
            player = self.get(profile=profile, tournament=tournament)
            player.delete()
            return True
        except self.model.DoesNotExist:
            return False
    
    def mark_ready(self, player, ready):
        player.is_ready = ready
        player.save()
        return player
    
    def get_players_by_tournament_id(self, tournament_id):
        return self.filter(tournament__id=tournament_id)
    
    def can_start_tournament(self, tournament_id):
        players = self.get_players_by_tournament_id(tournament_id)
        return all(player.is_ready for player in players)
    
    def shuffle_players_for_tournament(self, tournament_id):
        players = list(self.get_players_by_tournament_id(tournament_id))
        random.shuffle(players)
        return players


class GameManager(models.Manager):
    def create_game(self, player1, player2):
        game = self.create(player1=player1, player2=player2)
        return game
    
    def prepare_games(self, players, tournament):
        total_players = len(players)
        total_games = total_players - 1
        rounds = math.ceil(math.log2(total_players))
        order = total_games + rounds
        games = []
        next_games = [None]
        for round_num in range(1, rounds + 1):
            current_round_games = []
            for i in range(2**(round_num - 1)):
                next_game = next_games.pop(0)
                if round_num == rounds:
                    if 2 * i + 1 < total_players:
                        player1 = players[2 * i]
                        player2 = players[2 * i + 1]
                        game = self.create_game(player1=player1, player2=player2, order=order, next_game=next_game)
                    else:
                        game = self.create_game(player1=players[2 * i], player2=None, order=order, next_game=next_game)
                else:
                    game = self.create_game(player1=None, player2=None, order=order, next_game=next_game)
                    current_round_games.append(game)
                    current_round_games.append(game)
                games.append(game)
                order -= 1
            next_games.extend(current_round_games)
        tournament.current_order = 1
        tournament.started_at = timezone.now()
        tournament.save()
        return games
    
    def start_tournament(self, players):
        games = self.prepare_games(players)
        if games:
            first_game = games[0]
            first_game.started = True
            first_game.save()
            first_game.player1.set_waiting()
            first_game.player2.set_waiting()
            first_game.player1.save()
            first_game.player2.save()
            for player in players:
                if player != first_game.player1 and player != first_game.player2:
                    player.set_watching()
                    player.save()
        return games


class ScoreManager(models.Manager):
    pass