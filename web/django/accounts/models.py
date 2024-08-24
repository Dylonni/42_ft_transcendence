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
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = models.CharField(
        max_length=150,
        unique=True,
    )
    email = models.EmailField(
        unique=True,
    )
    fortytwo_avatar_url = models.CharField(
        null=True,
        blank=True,
    )
    fortytwo_coalition_cover_url = models.CharField(
        null=True,
        blank=True,
    )
    fortytwo_coalition_color = models.CharField(
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        db_index=True,
    )
    is_staff = models.BooleanField(
        default=False,
    )
    is_active = models.BooleanField(
        default=True,
    )
    is_verified = models.BooleanField(
        default=False,
    )
    groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        to=Permission,
        blank=True,
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    objects: CustomUserManager = CustomUserManager()
    
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    class Meta:
        verbose_name = 'custom user'
        verbose_name_plural = 'custom users'
    
    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
    
    def update_fortytwo_infos(self, avatar_url=None, coalition_cover_url=None, coalition_color=None):
        self.fortytwo_avatar_url = avatar_url
        self.fortytwo_coalition_cover_url = coalition_cover_url
        self.fortytwo_coalition_color = coalition_color
        self.save()
    
    def set_as_verified(self):
        self.is_verified = True
        self.is_active = True
        self.save()