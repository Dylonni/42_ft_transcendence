import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name=_('created at'),
        default=timezone.now,
    )
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f'{self.__class__.__name__} ({self.id})'


class BaseInteraction(BaseModel):
    sender = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='%(class)s_sent',
    )
    receiver = models.ForeignKey(
        to='profiles.Profile',
        verbose_name=_('receiver'),
        on_delete=models.CASCADE,
        related_name='%(class)s_received',
    )
    
    class Meta:
        abstract = True
        unique_together = ('sender', 'receiver')
    
    def __str__(self):
        return f'Interaction ({self.id}) from {self.sender} to {self.receiver}'