import random
from django.apps import apps
from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        if not email:
            raise ValueError('The given email must be set')
        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)
    
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)
    
    def send_mail(self, email, html, subject):
        user = self.filter(email=email).first()
        if not user:
            # raise ValueError('No such user.')
            return
        temp_code = user.code
        if temp_code:
            if not user.has_code_expired():
                # raise ValueError('Code already sent.')
                return
        user.code = ''.join(random.choices('0123456789', k=6))
        user.code_updated_at = timezone.now()
        user.save()
        context = {'user': user}
        html_message = render_to_string(html, context)
        send_mail(
            subject='[42 Transcendence] ' + subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            auth_user=settings.EMAIL_HOST_USER,
            auth_password=settings.EMAIL_HOST_PASSWORD,
            html_message=html_message,
        )
        return user