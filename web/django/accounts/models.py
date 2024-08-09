import uuid
from django.apps import apps
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    
    id = models.UUIDField(
        verbose_name=_('id'),
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
    )
    fortytwo_id = models.CharField(
        verbose_name=_('42 id'),
        null=True,
        blank=True,
        editable=False,
    )
    fortytwo_access_token = models.TextField(
        verbose_name=_('42 access token'),
        null=True,
        blank=True,
        editable=False,
    )
    fortytwo_refresh_token = models.TextField(
        verbose_name=_('42 refresh token'),
        null=True,
        blank=True,
        editable=False,
    )
    fortytwo_avatar_url = models.CharField(
        verbose_name=_('42 avatar url'),
        null=True,
        blank=True,
    )
    fortytwo_coalition_cover_url = models.CharField(
        verbose_name=_('42 coalition cover url'),
        null=True,
        blank=True,
    )
    fortytwo_coalition_color = models.CharField(
        verbose_name=_('42 coalition color'),
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
        db_index=True,
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
    )
    is_verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
    )
    groups = models.ManyToManyField(
        to=Group,
        verbose_name=_('groups'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        to=Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    objects = CustomUserManager()
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = _('custom user')
        verbose_name_plural = _('custom users')
    
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
    def update_fortytwo_infos(self, id, access_token, refresh_token, avatar_url, coalition_cover_url, coalition_color):
        self.fortytwo_id = id
        self.fortytwo_access_token = access_token
        self.fortytwo_refresh_token = refresh_token
        self.fortytwo_avatar_url = avatar_url
        self.fortytwo_coalition_cover_url = coalition_cover_url
        self.fortytwo_coalition_color = coalition_color
        self.save()
    
    def set_as_verified(self):
        self.is_verified = True
        self.is_active = True
        self.save()