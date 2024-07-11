import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from rest_framework_simplejwt.tokens import AccessToken
from profiles.models import Profile

UserModel = get_user_model()
logger = logging.getLogger('django')

def redirect_not_ajax(request, path, context):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = set_profile_context(request, context)
        html = render_to_string(path, context, request)
        return HttpResponse(html)
    context = set_profile_context(request, context)
    sub_template = render_to_string(path, context, request)
    context = {
        'sub_template': sub_template,
        'title': _('Transcendence'),
    }
    return render(request, 'index.html', context)

def set_profile_context(request, context):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer '):
        access_token = auth_header.split(' ')[1]
        try:
            access_token_obj = AccessToken(access_token)
            user_id = access_token_obj['user_id']
            user = UserModel.objects.get(id=user_id)
            profile = Profile.objects.get(user=user)
            context['profile'] = profile
            return context
        except Exception as e:
            return context
    return context

def index(request):
    sub_template = render_to_string('accounts/login.html', request=request)
    context = {
        'sub_template': sub_template,
        'title': _('Login'),
    }
    return render(request, 'index.html', context)

def login(request):
    return redirect_not_ajax(request, 'accounts/login.html', {'title': _('Login')})

def register(request):
    return redirect_not_ajax(request, 'accounts/register.html', {'title': _('Register')})

def home(request):
    return redirect_not_ajax(request, 'home.html', {'title': _('Home')})

def profile(request):
    return redirect_not_ajax(request, 'profile.html', {'title': _('Profile')})

def leaderboard(request):
    return redirect_not_ajax(request, 'leaderboard.html', {'title': _('Leaderboard')})

def social(request):
    return redirect_not_ajax(request, 'social.html', {'title': _('Social')})

def settings(request):
    return redirect_not_ajax(request, 'settings.html', {'title': _('Settings')})