from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .tokens import EmailTokenGenerator

def send_activation_mail(request, user):
    current_site = get_current_site(request)
    token_generator = EmailTokenGenerator()
    html_message = render_to_string('accounts/email_activate.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    })
    send_mail(
        subject='Activate your account',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        html_message=html_message,
    )

def send_password_reset_mail(request, user):
    current_site = get_current_site(request)
    token_generator = EmailTokenGenerator()
    html_message = render_to_string('accounts/email_reset_password.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    })
    send_mail(
        subject='Reset your password',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
        auth_user=settings.EMAIL_HOST_USER,
        auth_password=settings.EMAIL_HOST_PASSWORD,
        html_message=html_message,
    )

def set_jwt_cookies_for_user(response, user):
    refresh = RefreshToken.for_user(user)
    set_jwt_as_cookies(response, str(refresh.access_token), str(refresh))
    return str(refresh.access_token), str(refresh)

def set_jwt_as_cookies(response: HttpResponse, access_token, refresh_token):
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        # secure=True,
        # samesite='Lax',
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        # secure=True,
        # samesite='Lax',
    )

def unset_jwt_cookies(response: HttpResponse):
    response.delete_cookie(
        key='access_token',
    )
    response.delete_cookie(
        key='refresh_token',
    )

def is_token_valid(token):
    try:
        AccessToken(token)
        return True
    except TokenError:
        return False

def get_jwt_from_refresh(refresh_token):
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token), str(refresh)
    except TokenError:
        return None, None