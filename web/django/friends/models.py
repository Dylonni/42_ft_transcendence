from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel, BaseInteraction
from .managers import FriendMessageManager, FriendRequestManager, FriendshipManager


class Friendship(BaseModel):
    profile1 = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('profile1'),
        on_delete=models.CASCADE,
        related_name='friendships_as_profile1',
    )
    profile2 = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('profile2'),
        on_delete=models.CASCADE,
        related_name='friendships_as_profile2',
    )
    removed_by = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('removed by'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='removed_friendships',
    )
    
    objects = FriendshipManager()
    
    class Meta:
        verbose_name = _('friendship')
        verbose_name_plural = _('friendships')
        constraints = [
            models.UniqueConstraint(fields=['profile1', 'profile2'], name='unique_friendship_pair')
        ]
    
    def __str__(self):
        return f'Friendship ({self.id}) between {self.profile1} and {self.profile2}'


class FriendRequest(BaseInteraction):
    objects = FriendRequestManager()
    
    class Meta:
        verbose_name = _('friend request')
        verbose_name_plural = _('friend requests')
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_friend_request_pair')
        ]
    
    def __str__(self):
        return f'Friend request ({self.id}) from {self.sender} to {self.receiver}'


class FriendMessage(BaseInteraction):
    friendship = models.ForeignKey(
        to='Friendship',
        verbose_name=_('friendship'),
        on_delete=models.CASCADE,
        related_name='messages',
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
    
    objects = FriendMessageManager()
    
    class Meta:
        verbose_name = _('friend message')
        verbose_name_plural = _('friend messages')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Friend message ({self.id}) from {self.sender} to {self.receiver}'