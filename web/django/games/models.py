from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel, BaseInteraction
from .managers import (
    GameManager,
    GameInviteManager,
    PlayerManager,
    RoundManager,
    ScoreManager,
    GameMessageManager,
    BaseGameManager,
)


class BaseGame(BaseModel):
    win_score = models.PositiveSmallIntegerField(
        verbose_name=_('score to win'),
        default=5,
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
    
    objects = BaseGameManager()
    
    class Meta:
        verbose_name = _('base game')
        verbose_name_plural = _('base games')
    
    def __str__(self):
        return f'Base Game'


class Game(BaseGame):
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
        null=True,
        blank=True,
    )
    player_limit = models.PositiveSmallIntegerField(
        verbose_name=_('player limit'),
        default=1,
    )
    current_order = models.PositiveSmallIntegerField(
        verbose_name=_('current order'),
        default=0,
    )
    winner = models.ForeignKey(
        to='Player',
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
        return f'Game {self.name}'


class GameInvite(BaseInteraction):
    objects = GameInviteManager()
    
    class Meta:
        verbose_name = _('game invitation')
        verbose_name_plural = _('game invitations')
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_game_invite_pair')
        ]
    
    def __str__(self):
        return f'Game invitation ({self.id}) from {self.sender} to {self.receiver}'


class Player(models.Model):
    class StatusChoices(models.TextChoices):
        WAITING = 'Waiting', _('Waiting')
        READY = 'Ready', _('Ready')
        PLAYING = 'Playing', _('Playing')
        WATCHING = 'Watching', _('Watching')
    
    profile = models.OneToOneField(
        to='profiles.Profile',
        verbose_name=_('profile'),
        on_delete=models.CASCADE,
    )
    game = models.ForeignKey(
        to=Game,
        verbose_name=_('game'),
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.WAITING,
    )
    is_host = models.BooleanField(
        verbose_name=_('is host'),
        default=False,
    )
    
    objects = PlayerManager()
    
    class Meta:
        verbose_name = _('player')
        verbose_name_plural = _('players')
    
    def __str__(self):
        return self.profile.alias
    
    def set_waiting(self):
        self.status = self.StatusChoices.WAITING
        self.save()
    
    def set_ready(self):
        self.status = self.StatusChoices.READY
        self.save()
    
    def set_playing(self):
        self.status = self.StatusChoices.PLAYING
        self.save()
    
    def set_watching(self):
        self.status = self.StatusChoices.WATCHING
        self.save()


class Round(BaseModel):
    game = models.ForeignKey(
        to=Game,
        verbose_name=_('game'),
        on_delete=models.CASCADE,
    )
    order = models.PositiveSmallIntegerField(
        verbose_name=_('order'),
        default=0,
    )
    player1 = models.ForeignKey(
        to=Player,
        verbose_name=_('player1'),
        on_delete=models.CASCADE,
        related_name='player1_rounds',
    )
    player2 = models.ForeignKey(
        to=Player,
        verbose_name=_('player2'),
        on_delete=models.CASCADE,
        related_name='player2_rounds',
    )
    winner = models.ForeignKey(
        to=Player,
        verbose_name = _('winner'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='won_rounds',
    )
    next_round = models.ForeignKey(
        to='self',
        verbose_name=_('next round'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_rounds',
    )
    started = models.BooleanField(
        verbose_name=_('started'),
        default=False,
    )
    
    objects = RoundManager()
    
    class Meta:
        verbose_name = _('round')
        verbose_name_plural = _('rounds')
    
    def __str__(self):
        return f'{self.player1} VS {self.player2}'


class Score(models.Model):
    game = models.ForeignKey(
        to=Game,
        related_name='scores',
        on_delete=models.CASCADE,
    )
    player = models.ForeignKey(
        to=Player,
        verbose_name=_('player'),
        on_delete=models.CASCADE,
        related_name='scores',
    )
    points = models.PositiveSmallIntegerField(
        verbose_name=_('points'),
        default=0,
    )
    
    objects = ScoreManager()
    
    class Meta:
        verbose_name = _('score')
        verbose_name_plural = _('scores')
        unique_together = ('game', 'player')
    
    def __str__(self):
        return f'{self.player} - {self.points} points'


class GameMessage(BaseModel):
    game = models.ForeignKey(
        to=Game,
        verbose_name=_('game'),
        on_delete=models.CASCADE,
        related_name='messages',
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='%(class)s_sent',
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