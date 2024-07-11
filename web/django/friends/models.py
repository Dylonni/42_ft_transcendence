import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import FriendMessageManager, FriendRequestManager, FriendshipManager


class Friendship(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
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
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )
    
    objects = FriendshipManager()
    
    def __str__(self):
        return f'Friendship between {self.profile1} and {self.profile2}'
    
    class Meta:
        verbose_name = _('friendship')
        verbose_name_plural = _('friendships')
        unique_together = ('profile1', 'profile2')


class FriendRequest(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
    )
    receiver = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('receiver'),
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )
    
    objects = FriendRequestManager()
    
    def __str__(self):
        return f'Friend request from {self.sender} to {self.receiver}'
    
    class Meta:
        verbose_name = _('friend request')
        verbose_name_plural = _('friend requests')


class FriendMessage(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    sender = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='sent_friend_messages',
    )
    receiver = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('receiver'),
        on_delete=models.CASCADE,
        related_name='received_friend_messages',
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )
    message = models.TextField(
        verbose_name=_('message'),
        blank=False,
        null=True,
    )
    
    objects = FriendMessageManager()
    
    def __str__(self):
        return f'Friend message from {self.sender} to {self.receiver}'
    
    class Meta:
        verbose_name = _('friend message')
        verbose_name_plural = _('friend messages')
        ordering = ['-created_at']