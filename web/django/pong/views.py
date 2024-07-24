from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils import translation

def redirect_not_ajax(request, title, path):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        context = {'title': title}
        html = render_to_string(path, context, request)
        return HttpResponse(html)
    return redirect('index')


class IndexView(APIView):
    def get(self, request, *args, **kwargs):
        context = {'title': _('Transcendence')}
        return render(request, 'index.html', context)


class LoginView(APIView):
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Login'), 'accounts/login.html')


class RegisterView(APIView):
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Register'), 'accounts/register.html')


class HomeView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Home'), 'home.html')


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Profile'), 'profile.html')


class SocialView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Social'), 'social.html')


class SettingsView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        # translation.activate("ja")
        return redirect_not_ajax(request, _('Settings'), 'settings.html')