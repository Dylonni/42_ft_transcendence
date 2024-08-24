import random
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
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
    current_order = models.PositiveSmallIntegerField(
        default=0,
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
    
    def get_player_count(self):
        return self.players.count()
    
    def get_rounds(self):
        return self.rounds
    
    def is_full(self):
        return self.players.count() == self.player_limit
    
    def has_player(self, player):
        return player in self.players.all()
    
    def can_join(self, player):
        return player not in self.players
    
    def can_start(self, player):
        is_host = player == self.host
        is_full = self.is_full()
        all_ready = all(player.is_ready for player in self.players)
        return is_host and is_full and all_ready
    
    def set_host(self, new_host):
        self.host = new_host
        self.save()
        return self
    
    def shuffle_players(self):
        players = self.players
        random.shuffle(self.players)
        return players


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
        on_delete=models.CASCADE,
        related_name='player1_rounds',
    )
    player2 = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='player2_rounds',
    )
    score1 = models.PositiveSmallIntegerField(
        default=0,
    )
    score2 = models.PositiveSmallIntegerField(
        default=0,
    )
    winner = models.ForeignKey(
        to='profiles.Profile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rounds_won',
    )
    next_round = models.ForeignKey(
        to='self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_rounds',
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
    
    def get_loser(self):
        if self.winner:
            return self.player2 if self.winner == self.player1 else self.player1
        return None
    
    def is_over(self):
        return self.score1 == self.game.win_score or self.score2 == self.game.win_score
    
    def set_winner(self, winner):
        self.winner = winner
        self.save()


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
    game = models.ForeignKey(
        to=Game,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='game_messages_sent',
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