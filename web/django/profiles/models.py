import logging
import requests
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel
from .managers import ProfileManager, ProfileBlockManager
from .storage import OverwriteStorage

UserModel = get_user_model()
logger = logging.getLogger('django')

def upload_avatar(instance, filename):
    ext = filename.split('.')[-1]
    return f"avatars/{instance.id}.{ext}"


class Profile(BaseModel):
    class StatusChoices(models.TextChoices):
        CONNECTED = 'Connected', _('Connected')
        PLAYING = 'Playing', _('Playing')
        DISCONNECTED = 'Disconnected', _('Disconnected')
    
    user = models.OneToOneField(
        to=UserModel,
        verbose_name=_('user'),
        on_delete=models.CASCADE,
        related_name='profile',
    )
    alias = models.CharField(
        verbose_name=_('alias'),
        max_length=150,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name=_('avatar'),
        null=True,
        upload_to=upload_avatar,
        storage=OverwriteStorage(), 
    )
    avatar_url = models.CharField(
        verbose_name=_('avatar url'),
        max_length=150,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name=_('status'),
        choices=StatusChoices.choices,
        default=StatusChoices.DISCONNECTED,
    )
    default_lang = models.CharField(
        verbose_name=_('default language'),
        max_length=40,
        default='en',
    )
    game = models.ForeignKey(
        to='games.Game',
        verbose_name=_('game'),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='players',
    )
    elo = models.PositiveSmallIntegerField(
        verbose_name=_('elo'),
        default=1000,
    )
    is_ready = models.BooleanField(
        verbose_name=_('ready'),
        default=False,
    )
    
    objects = ProfileManager()
    
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
    
    def __str__(self):
        return self.alias
    
    def set_default_avatar_url(self, id='1'):
        if id not in ['1', '2', '3']:
            id = '1'
        self.avatar_url = f'/media/defaults/avatar{id}.webp'
        self.save()
    
    def is_host(self):
        return self.game and self.game.host == self
    
    def join_game(self, game):
        self.game = game
        self.save()
    
    def leave_game(self):
        self.game = None
        self.save()
    
    def update_elo(self, new_elo):
        self.elo = new_elo
        self.save()
    
    def toggle_ready(self):
        self.is_ready = not self.is_ready
        self.save()
        return self.is_ready
    
    def get_total_games(self):
        return self.player1_rounds.count() + self.player2_rounds.count()
    
    def get_won_tournaments(self):
        return self.won_games.count()
    
    def get_won_games(self):
        return self.rounds_won.count()
    
    def get_lost_games(self):
        return self.get_total_games() - self.get_won_games()
    
    def get_rank(self):
        higher_elo_count = self.__class__.objects.filter(elo__gt=self.elo).count()
        return higher_elo_count + 1


class ProfileBlock(BaseModel):
    blocker = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('blocker'),
        on_delete=models.CASCADE,
        related_name='blocked_profiles',
    )
    blocked = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('blocked'),
        on_delete=models.CASCADE,
        related_name='blockers',
    )
    
    objects = ProfileBlockManager()
    
    class Meta:
        verbose_name = _("profile block")
        verbose_name_plural = _("profile blocks")
    
    def __str__(self):
        return f'{self.blocker} blocked {self.blocked}'