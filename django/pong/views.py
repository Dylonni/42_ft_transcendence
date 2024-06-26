from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

def index(request):
    context = {'title': _('Transcendence')}
    return render(request, 'index.html', context)

def login(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {'title': _('Login')}
        html = render_to_string('accounts/login.html', context, request)
        return HttpResponse(html)
    return index(request)

def register(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {'title': _('Register')}
        html = render_to_string('accounts/register.html', context, request)
        return HttpResponse(html)
    return index(request)

def user_settings(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {'title': _('Settings')}
        html = render_to_string('settings.html', context, request)
        return HttpResponse(html)
    return index(request)