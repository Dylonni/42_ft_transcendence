import logging
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from pong.models import BaseModel
from .managers import ProfileManager, ProfileBlockManager
from .storage import OverwriteStorage

UserModel = get_user_model()
logger = logging.getLogger('django')


class Profile(BaseModel):
    class StatusChoices(models.TextChoices):
        CONNECTED = 'Connected', _('Connected')
        OCCUPIED = 'Occupied', _('Occupied')
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
        upload_to='avatars',
        storage=OverwriteStorage(), 
    )
    status = models.CharField(
        verbose_name=_('status'),
        choices=StatusChoices.choices,
        default=StatusChoices.DISCONNECTED,
    )
    default_lang = models.CharField(
        verbose_name=_('default language'),
        max_length=40,
    )
    
    objects = ProfileManager()
    
    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
    
    def __str__(self):
        return self.alias


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