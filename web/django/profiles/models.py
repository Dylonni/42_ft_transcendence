import logging
import requests
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
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
        ONLINE = 'Online', _('Online')
        WAITING = 'Waiting', _('Waiting')
        PLAYING = 'Playing', _('Playing')
        OFFLINE = 'Offline', _('Offline')
    
    user = models.OneToOneField(
        to=UserModel,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    alias = models.CharField(
        max_length=150,
        unique=True,
    )
    avatar = models.ImageField(
        null=True,
        upload_to=upload_avatar,
        storage=OverwriteStorage(), 
    )
    avatar_url = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )
    status = models.CharField(
        choices=StatusChoices.choices,
        default=StatusChoices.OFFLINE,
    )
    default_lang = models.CharField(
        max_length=40,
        default='en',
    )
    game = models.ForeignKey(
        to='games.Game',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='players',
    )
    elo = models.IntegerField(
        default=1000,
    )
    is_ready = models.BooleanField(
        default=False,
    )
    
    objects: ProfileManager = ProfileManager()
    
    class Meta:
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    
    def __str__(self):
        return self.alias
    
    def get_avatar_url(self):
        if self.avatar_url.startswith('http'):
            return self.avatar_url
        return self.avatar_url + '?' + str(timezone.now().timestamp())
    
    def get_blocked_profiles(self):
        return self.blocked_profiles.all()
    
    def get_invited_profiles(self):
        if self.game:
            return self.game.gameinvite_sent.filter(sender=self)
        return None
    
    def set_avatar_url(self, id='1', path=''):
        if id == 'fortytwo':
            self.avatar_url = path
        else:
            if id not in ['1', '2', '3', '4']:
                id = '1'
            self.avatar_url = f'/media/defaults/avatar{id}.webp'
        self.save()
    
    def set_default_lang(self, lang='en'):
        if lang not in dict(settings.LANGUAGES):
            lang = 'en'
        self.default_lang = lang
        self.save()
    
    def update_elo(self, value):
        self.elo = max(self.elo + value, 0)
        self.save()
    
    def is_friend(self, profile):
        is_profile1_friend = self.friendships_as_profile1.filter(profile1=self, profile2=profile, removed_by__isnull=True).exists()
        is_profile2_friend = self.friendships_as_profile2.filter(profile1=profile, profile2=self, removed_by__isnull=True).exists()
        return is_profile1_friend or is_profile2_friend
    
    def has_blocked(self, profile):
        return self.blocked_profiles.filter(blocker=self, blocked=profile).exists()
    
    def get_block(self, profile):
        return self.blocked_profiles.filter(blocker=self, blocked=profile).first()
    
    def is_host(self):
        return self.game and self.game.host == self
    
    def has_unread_messages(self):
        return self.friendmessage_sent.filter(read=False).exists()
    
    def join_game(self, game):
        self.game = game
        if game.started_at:
            self.set_status(self.StatusChoices.PLAYING)
        else:
            self.set_status(self.StatusChoices.WAITING)
        self.save()
    
    def leave_game(self):
        if self.game.started_at:
            self.update_elo(-50)
        self.game = None
        self.set_status(self.StatusChoices.ONLINE)
        self.save()
    
    def set_status(self, status: StatusChoices):
        self.status = status
        self.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('friends', {'type': 'update_friend_list'})
        friendships_as_profile1 = self.friendships_as_profile1.all()
        for friendship in friendships_as_profile1:
            async_to_sync(channel_layer.group_send)(f'friends_{friendship.id}', {'type': 'update_header'})
        friendships_as_profile2 = self.friendships_as_profile2.all()
        for friendship in friendships_as_profile2:
            async_to_sync(channel_layer.group_send)(f'friends_{friendship.id}', {'type': 'update_header'})
    
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
        on_delete=models.CASCADE,
        related_name='blocked_profiles',
    )
    blocked = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='blocking_profiles',
    )
    
    objects: ProfileBlockManager = ProfileBlockManager()
    
    class Meta:
        verbose_name = 'profile block'
        verbose_name_plural = 'profile blocks'
    
    def __str__(self):
        return f'{self.blocker} blocked {self.blocked}'