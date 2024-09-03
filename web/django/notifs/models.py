from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pong.models import BaseInteraction
from .managers import NotificationManager


class Notification(BaseInteraction):
    class NotificationCategories(models.TextChoices):
        FRIEND_REQUEST = 'Friend Request', _('Friend Request')
        FRIEND_MESSAGE = 'Friend Message', _('Friend Message')
        GAME_INVITATION = 'Game Invitation', _('Game Invitation')
        GAME_MESSAGE = 'Game Message', _('Game Message')
    
    category = models.CharField(
        max_length=20,
        choices=NotificationCategories.choices,
        default=NotificationCategories.GAME_INVITATION,
    )
    object_id = models.UUIDField(
        null=True,
        blank=True,
    )
    read = models.BooleanField(
        default=False,
    )
    
    objects: NotificationManager = NotificationManager()
    
    class Meta:
        verbose_name = 'notification'
        verbose_name_plural = 'notifications'
        ordering = ['created_at']
    
    def __str__(self):
        return f'Notification ({self.id}) for a {self.notification_type} to {self.receiver}'
    
    def mark_as_read(self):
        self.read = True
        self.save()

    def get_time_since(self):
        return timezone.now() - self.created_at