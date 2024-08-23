from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel, BaseInteraction
from .managers import FriendMessageManager, FriendRequestManager, FriendshipManager


class Friendship(BaseModel):
    profile1 = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='friendships_as_profile1',
    )
    profile2 = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.CASCADE,
        related_name='friendships_as_profile2',
    )
    removed_by = models.ForeignKey(
        to='profiles.Profile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='removed_friendships',
    )
    
    objects: FriendshipManager = FriendshipManager()
    
    class Meta:
        verbose_name = 'friendship'
        verbose_name_plural = 'friendships'
        constraints = [
            models.UniqueConstraint(fields=['profile1', 'profile2'], name='unique_friendship_pair')
        ]
    
    def __str__(self):
        return f'Friendship ({self.id}) between {self.profile1} and {self.profile2}'
    
    def get_last_message(self):
        last_message = self.messages.order_by('-created_at').first()
        if last_message:
            return last_message.content
        return None
    
    def get_last_speaker(self):
        last_message = self.messages.order_by('-created_at').first()
        if last_message:
            return last_message.sender
        return None
    
    def get_other(self, profile):
        if profile == self.profile1:
            return self.profile2
        elif profile == self.profile2:
            return self.profile1
        return None


class FriendRequest(BaseInteraction):
    objects: FriendRequestManager = FriendRequestManager()
    
    class Meta:
        verbose_name = 'friend request'
        verbose_name_plural = 'friend requests'
        constraints = [
            models.UniqueConstraint(fields=['sender', 'receiver'], name='unique_friend_request_pair')
        ]
    
    def __str__(self):
        return f'Friend request ({self.id}) from {self.sender} to {self.receiver}'


class FriendMessage(BaseInteraction):
    friendship = models.ForeignKey(
        to='Friendship',
        on_delete=models.CASCADE,
        related_name='messages',
    )
    content = models.TextField(
        blank=False,
        null=True,
    )
    read = models.BooleanField(
        default=False,
    )
    
    objects: FriendMessageManager = FriendMessageManager()
    
    class Meta:
        verbose_name = 'friend message'
        verbose_name_plural = 'friend messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Friend message ({self.id}) from {self.sender} to {self.receiver}'