import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import GameManager, PlayerManager, ScoreManager, TournamentManager


class Tournament(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        verbose_name=_('name'),
        max_length=255,
    )
    player_limit = models.PositiveSmallIntegerField(
        verbose_name=_('player limit'),
        default=1,
    )
    win_score = models.PositiveSmallIntegerField(
        verbose_name=_('score to win'),
        default=5,
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
        related_name='won_tournaments',
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
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
    
    objects = TournamentManager()
    
    def __str__(self):
        return f'Tournament {self.name}'
    
    class Meta:
        verbose_name = _('tournament')
        verbose_name_plural = _('tournaments')


class Player(models.Model):
    class StatusChoices(models.TextChoices):
        WAITING = 'Waiting', _('Waiting')
        READY = 'Ready', _('Ready')
        PLAYING = 'Playing', _('Playing')
        WATCHING = 'Watching', _('Watching')
    
    profile = models.OneToOneField(
        to='Profile',
        verbose_name=_('profile'),
        on_delete=models.CASCADE,
    )
    tournament = models.ForeignKey(
        to=Tournament,
        verbose_name=_('tournament'),
        on_delete=models.CASCADE,
    )
    is_ready = models.BooleanField(
        verbose_name=_('ready'),
        default=False,
    )
    status = models.CharField(
        verbose_name=_('status'),
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.WAITING,
    )
    
    objects = PlayerManager()
    
    def __str__(self):
        return self.profile.alias
    
    class Meta:
        verbose_name = _('player')
        verbose_name_plural = _('players')
    
    def set_waiting(self):
        self.status = self.StatusChoices.WAITING
    
    def set_ready(self):
        self.status = self.StatusChoices.READY
    
    def set_playing(self):
        self.status = self.StatusChoices.PLAYING
    
    def set_watching(self):
        self.status = self.StatusChoices.WATCHING


class Game(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    tournament = models.ForeignKey(
        to=Tournament,
        verbose_name=_('tournament'),
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
        related_name='player1_games',
    )
    player2 = models.ForeignKey(
        to=Player,
        verbose_name=_('player2'),
        on_delete=models.CASCADE,
        related_name='player2_games',
    )
    winner = models.ForeignKey(
        to=Player,
        verbose_name = _('winner'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='won_games',
    )
    next_game = models.ForeignKey(
        to='self',
        verbose_name=_('next game'),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='previous_games',
    )
    started = models.BooleanField(
        verbose_name=_('started'),
        default=False,
    )
    
    objects = GameManager()
    
    def __str__(self):
        return f'{self.player1} VS {self.player2}'
    
    class Meta:
        verbose_name = _('game')
        verbose_name_plural = _('games')


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
    
    def __str__(self):
        return f'{self.player} - {self.points} points'
    
    class Meta:
        verbose_name = _('score')
        verbose_name_plural = _('scores')
        unique_together = ('game', 'player')