from django.db import models
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel
from .managers import NotificationManager


class Notification(BaseModel):
    class NotificationChoices(models.TextChoices):
        # ACHIEVEMENT = 'Achievement', _('Achievement')
        FRIEND_REQUEST = 'Friend Request', _('Friend Request')
        FRIEND_MESSAGE = 'Friend Message', _('Friend Message')
        GAME_INVITATION = 'Game Invitation', _('Game Invitation')
        GAME_MESSAGE = 'Game Message', _('Game Message')
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationChoices.choices,
        default=NotificationChoices.MESSAGE,
    )
    receiver = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('receiver'),
        on_delete=models.CASCADE,
        related_name='notifications_received',
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
    
    objects = NotificationManager()
    
    class Meta:
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        ordering = ['created_at']
    
    def __str__(self):
        return f'Notification ({self.id}) for a {self.notification_type} to {self.receiver}'