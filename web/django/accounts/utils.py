from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from .tokens import EmailTokenGenerator

def send_activation_mail(request, user):
    current_site = get_current_site(request)
    token_generator = EmailTokenGenerator()
    message = render_to_string('accounts/email_activate.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    })
    to_email = user.email
    send_mail(
        subject='Activate your account',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=message,
    )

def send_password_reset_mail(request, user):
    current_site = get_current_site(request)
    token_generator = EmailTokenGenerator()
    message = render_to_string('accounts/email_password_reset.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
    })
    to_email = user.email
    send_mail(
        subject='Activate your account',
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=message,
    )

def set_jwt_cookies(response, user):
    refresh = RefreshToken.for_user(user)
    response.set_cookie(
        key='access_token',
        value=str(refresh.access_token),
        httponly=True,
        secure=True,
        samesite='Lax'
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh),
        httponly=True,
        secure=True,
        samesite='Lax'
    )
    return str(refresh.access_token), str(refresh)

def unset_jwt_cookies(response):
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

def refresh_access_token(refresh_token):
    try:
        refresh = RefreshToken(refresh_token)
        return str(refresh.access_token), str(refresh)
    except TokenError:
        return None, None
