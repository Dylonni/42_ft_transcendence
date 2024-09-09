import logging
import math
import random
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel, BaseInteraction
from .managers import (
    GameManager,
    GameRoundManager,
    GameInviteManager,
    GameMessageManager,
)


class Game(BaseModel):
    class SizeChoices(models.TextChoices):
        SMALL = 'Small', _('Small')
        MEDIUM = 'Medium', _('Medium')
        LARGE = 'Large', _('Large')
    
    class SpeedChoices(models.TextChoices):
        SLOW = 'Slow', _('Slow')
        NORMAL = 'Normal', _('Normal')
        FAST = 'Fast', _('Fast')
    
    class DifficultyChoices(models.TextChoices):
        EASY = 'Easy', _('Easy')
        NORMAL = 'Normal', _('Normal')
        HARD = 'Hard', _('Hard')
    
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    host = models.OneToOneField(
        to='profiles.Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hosted_game',
    )
    player_limit = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(8)],
    )
    win_score = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    ball_size = models.CharField(
        choices=SizeChoices.choices,
        default=SizeChoices.MEDIUM,
    )
    ball_speed = models.CharField(
        choices=SpeedChoices.choices,
        default=SpeedChoices.NORMAL,
    )
    paddle_size = models.CharField(
        choices=SizeChoices.choices,
        default=SizeChoices.MEDIUM,
    )
    ai_difficulty = models.CharField(
        choices=DifficultyChoices.choices,
        default=DifficultyChoices.NORMAL,
    )
    map_choice = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(2)],
    )
    power_ups = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    game_events = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    current_order = models.IntegerField(
        default=-1,
    )
    winner = models.ForeignKey(
        to='profiles.Profile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='won_games',
    )
    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    ended_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    
    objects: GameManager = GameManager()
    
    class Meta:
        verbose_name = 'game'
        verbose_name_plural = 'games'
    
    def __str__(self):
        return self.name
    
    def get_current_round(self):
        return self.rounds.filter(order=self.current_order).first()

    def get_ball_size(self):
        if self.ball_size == self.SizeChoices.SMALL:
            return 10
        elif self.ball_size == self.SizeChoices.MEDIUM:
            return 15
        return 20
    
    def get_ball_speed(self):
        if self.ball_speed == self.SpeedChoices.SLOW:
            return 4
        elif self.ball_speed == self.SpeedChoices.NORMAL:
            return 6
        return 8
    
    def get_paddle_size(self):
        if self.paddle_size == self.SizeChoices.SMALL:
            return 70
        elif self.paddle_size == self.SizeChoices.MEDIUM:
            return 85
        return 100
    
    def get_player_count(self):
        return self.players.count()
    
    def get_rounds(self):
        return self.rounds.all()
    
    def is_full(self):
        return self.players.count() == self.player_limit
    
    def has_player(self, player):
        return player in self.players.all()
    
    def can_join(self, player):
        return player not in self.players
    
    def can_start(self, player):
        is_host = player == self.host
        is_full = self.is_full()
        return is_host and is_full
    
    def set_host(self, new_host):
        self.host = new_host
        self.save()
        return self
    
    def start(self):
        if self.started_at:
            return
        self.started_at = timezone.now()
        self.save()
    
    def end(self):
        self.ended_at = timezone.now()
        self.host = None
        last_round = self.rounds.order_by('order').last()
        if last_round and last_round.winner:
            self.winner = last_round.winner
        self.save()
        for player in self.players.all():
            self.__class__.objects.remove_player(self, player)
        self.messages.all().delete()
    
    def get_currently_playing(self):
        round = self.rounds.filter(order=self.current_order).first()
        if round:
            return [round.player1, round.player2]
        return None


class GameRound(BaseModel):
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='rounds',
    )
    order = models.PositiveSmallIntegerField(
        default=0,
    )
    player1 = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.SET_NULL,
        related_name='player1_rounds',
        null=True,
    )
    player2 = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.SET_NULL,
        related_name='player2_rounds',
        null=True,
    )
    score1 = models.PositiveSmallIntegerField(
        default=0,
    )
    score2 = models.PositiveSmallIntegerField(
        default=0,
    )
    elo_win = models.IntegerField(
        default=0,
    )
    elo_lose = models.IntegerField(
        default=0,
    )
    winner = models.ForeignKey(
        to='profiles.Profile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rounds_won',
    )
    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    ended_at = models.DateTimeField(
        blank=True,
        null=True,
    )
    
    objects: GameRoundManager = GameRoundManager()
    
    class Meta:
        verbose_name = 'game round'
        verbose_name_plural = 'game rounds'
    
    def __str__(self):
        return f'{self.player1} VS {self.player2}'
    
    def get_duration(self):
        return self.ended_at - self.started_at
    
    def get_loser(self):
        if self.winner:
            return self.player2 if self.winner == self.player1 else self.player1
        return None
    
    def is_over(self):
        return self.score1 == self.game.win_score or self.score2 == self.game.win_score
    
    def set_winner(self, winner):
        self.winner = winner
        self.save()
    
    def update_score(self, score1, score2):
        self.score1 = score1
        self.score2 = score2
        self.save()
    
    def calculate_elo(self):
        gain = max(min(int(abs(self.player1.elo - self.player2.elo) // 4), 30), 10)
        loss = -gain
        serie = math.ceil(math.log2(self.game.player_limit))
        if serie:
            current_serie = 0
            for i in range(serie):
                if self.order >= 2**i - 1:
                    current_serie = i
                    break
            bonus = 2**current_serie
        if self.winner.get_total_games() <= 5:
            gain = max(min(int(abs(self.player1.elo - self.player2.elo) // 4), 50), 25)
        if self.get_loser().get_total_games() <= 5:
            loss = -5
        self.winner.update_elo(gain + bonus)
        self.get_loser().update_elo(loss)
        self.elo_win = gain + bonus
        self.elo_lose = loss
        self.save()
    
    def start(self):
        self.started_at = timezone.now()
        self.save()
    
    def end(self):
        self.ended_at = timezone.now()
        if self.score1 == self.game.win_score:
            self.winner = self.player1
        elif self.score2 == self.game.win_score:
            self.winner = self.player2
        self.save()
        self.calculate_elo()
        # Move winner to next round
        rounds = self.game.rounds.order_by('order')
        for round in rounds:
            if not round.player1:
                round.player1 = self.winner
                round.save()
                break
            elif not round.player2:
                round.player2 = self.winner
                round.save()
                break


class GameInvite(BaseInteraction):
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='invitations',
    )
    
    objects: GameInviteManager = GameInviteManager()
    
    class Meta:
        verbose_name = 'game invitation'
        verbose_name_plural = 'game invitations'
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_game_invite_pair')
        ]
    
    def __str__(self):
        return f'Game invitation ({self.id}) from {self.sender} to {self.receiver}'


class GameMessage(BaseModel):
    class GameMessageCategories(models.TextChoices):
        SEND = 'Send', _('Send')
        JOIN = 'Join', _('Join')
        LEAVE = 'Leave', _('Leave')
        PREPARE = 'Prepare', _('Prepare')
        ELIMINATE = 'Eliminate', _('Eliminate')
        WIN = 'Win', _('Win')
    
    category = models.CharField(
        max_length=20,
        choices=GameMessageCategories.choices,
        default=GameMessageCategories.SEND,
    )
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='game_messages_sent',
        null=True,
    )
    content = models.TextField(
        blank=False,
        null=True,
    )
    
    objects: GameMessageManager = GameMessageManager()
    
    class Meta:
        verbose_name = 'game message'
        verbose_name_plural = 'game messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Game message ({self.id}) from {self.sender}'