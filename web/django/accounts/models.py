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
        help_text=_('Unique identifier for the user, automatically generated.'),
    )
    username = models.CharField(
        verbose_name=_('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        ),
        validators=[username_validator],
        error_messages={
            'max_length': _('The username must be 150 characters or fewer.'),
            'invalid': _('This value may contain only letters, numbers, and @/./+/-/_ characters.'),
        },
    )
    email = models.EmailField(
        verbose_name=_('email address'),
        unique=True,
        help_text=_('Required. A valid email address.'),
        error_messages={
            'invalid': _('Enter a valid email address.'),
        },
    )
    fortytwo_id = models.CharField(
        verbose_name=_('42 id'),
        null=True,
        blank=True,
        editable=False,
        help_text=_('Unique identifier for the user from 42.'),
    )
    fortytwo_access_token = models.TextField(
        verbose_name=_('42 access token'),
        null=True,
        blank=True,
        editable=False,
        help_text=_('Access token for 42 API.'),
    )
    fortytwo_refresh_token = models.TextField(
        verbose_name=_('42 refresh token'),
        null=True,
        blank=True,
        editable=False,
        help_text=_('Refresh token for 42 API.'),
    )
    fortytwo_image_url = models.CharField(
        verbose_name=_('42 image url'),
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        verbose_name=_('date joined'),
        default=timezone.now,
        db_index=True,
        help_text=_('The date and time when the user joined.'),
    )
    is_staff = models.BooleanField(
        verbose_name=_('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        verbose_name=_('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_verified = models.BooleanField(
        verbose_name=_('verified'),
        default=False,
        help_text=_('Designates whether the user has verified their email.'),
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
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