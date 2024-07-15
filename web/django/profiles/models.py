import logging
import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import ProfileManager
from .storage import OverwriteStorage

UserModel = get_user_model()
logger = logging.getLogger('django')


class Profile(models.Model):
    class StatusChoices(models.TextChoices):
        CONNECTED = 'Connected', _('Connected')
        OCCUPIED = 'Occupied', _('Occupied')
        DISCONNECTED = 'Disconnected', _('Disconnected')
    
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
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
        upload_to='avatars',
        storage=OverwriteStorage(), 
    )
    status = models.CharField(
        verbose_name=_('status'),
        choices=StatusChoices.choices,
        default=StatusChoices.DISCONNECTED,
    )
    blocked_profiles = models.ManyToManyField(
        to='self',
        verbose_name=_('blocked profiles'),
        blank=True,
        symmetrical=False,
        related_name='blocked_by',
    )
    
    objects = ProfileManager()
    
    def __str__(self):
        return self.alias
    
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")