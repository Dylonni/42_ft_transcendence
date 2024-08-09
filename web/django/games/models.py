import random
from django.core.validators import MaxValueValidator
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
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        null=True,
        blank=True,
    )
    host = models.OneToOneField(
        to='profiles.Profile',
        verbose_name=_('host'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hosted_game',
    )
    player_limit = models.PositiveSmallIntegerField(
        verbose_name=_('player limit'),
        default=1,
        validators=[MaxValueValidator(8)],
    )
    win_score = models.PositiveSmallIntegerField(
        verbose_name=_('score to win'),
        default=5,
        validators=[MaxValueValidator(30)],
    )
    ball_size = models.PositiveSmallIntegerField(
        verbose_name=_('ball size'),
        default=1,
        validators=[MaxValueValidator(2)],
    )
    ball_speed = models.PositiveSmallIntegerField(
        verbose_name=_('ball speed'),
        default=1,
        validators=[MaxValueValidator(2)],
    )
    paddle_length = models.PositiveSmallIntegerField(
        verbose_name=_('paddle length'),
        default=1,
        validators=[MaxValueValidator(2)],
    )
    ai_difficulty = models.PositiveSmallIntegerField(
        verbose_name=_('ai difficulty'),
        default=1,
        validators=[MaxValueValidator(2)],
    )
    map_choice = models.PositiveSmallIntegerField(
        verbose_name=_('map choice'),
        default=0,
        validators=[MaxValueValidator(2)],
    )
    power_ups = models.CharField(
        verbose_name=_('power ups'),
        max_length=255,
        null=True,
        blank=True,
    )
    game_events = models.CharField(
        verbose_name=_('game events'),
        max_length=255,
        null=True,
        blank=True,
    )
    current_order = models.PositiveSmallIntegerField(
        verbose_name=_('current order'),
        default=0,
    )
    winner = models.ForeignKey(
        to='profiles.Profile',
        verbose_name = _('winner'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='won_games',
    )
    started_at = models.DateTimeField(
        verbose_name=_('started at'),
        blank=True,
        null=True,
    )
    ended_at = models.DateTimeField(
        verbose_name=_('ended at'),
        blank=True,
        null=True,
    )
    
    objects = GameManager()
    
    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')
    
    def __str__(self):
        return self.name
    
    def get_player_count(self):
        return self.players.count()
    
    def get_rounds(self):
        return self.rounds
    
    def is_full(self):
        return self.players.count() == self.player_limit
    
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
        verbose_name=_('game'),
        on_delete=models.CASCADE,
        related_name='rounds',
    )
    order = models.PositiveSmallIntegerField(
        verbose_name=_('order'),
        default=0,
    )
    player1 = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('player1'),
        on_delete=models.CASCADE,
        related_name='player1_rounds',
    )
    player2 = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('player2'),
        on_delete=models.CASCADE,
        related_name='player2_rounds',
    )
    score1 = models.PositiveSmallIntegerField(
        verbose_name=_('player1_score'),
        default=0,
    )
    score2 = models.PositiveSmallIntegerField(
        verbose_name=_('player2_score'),
        default=0,
    )
    winner = models.ForeignKey(
        to='profiles.Profile',
        verbose_name = _('winner'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rounds_won',
    )
    next_round = models.ForeignKey(
        to='self',
        verbose_name=_('next round'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_rounds',
    )
    started_at = models.DateTimeField(
        verbose_name=_('started at'),
        blank=True,
        null=True,
    )
    ended_at = models.DateTimeField(
        verbose_name=_('ended at'),
        blank=True,
        null=True,
    )
    
    objects = GameRoundManager()
    
    class Meta:
        verbose_name = _('game round')
        verbose_name_plural = _('game rounds')
    
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
        verbose_name=_('game'),
        on_delete=models.CASCADE,
        related_name='invitations',
    )
    
    objects = GameInviteManager()
    
    class Meta:
        verbose_name = _('game invitation')
        verbose_name_plural = _('game invitations')
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_game_invite_pair')
        ]
    
    def __str__(self):
        return f'Game invitation ({self.id}) from {self.sender} to {self.receiver}'


class GameMessage(BaseModel):
    game = models.ForeignKey(
        to=Game,
        verbose_name=_('game room'),
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='game_messages_sent',
    )
    content = models.TextField(
        verbose_name=_('content'),
        blank=False,
        null=True,
    )
    read = models.BooleanField(
        verbose_name=_('read'),
        default=False,
    )
    
    objects = GameMessageManager()
    
    class Meta:
        verbose_name = _('game message')
        verbose_name_plural = _('game messages')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Game message ({self.id}) from {self.sender}'