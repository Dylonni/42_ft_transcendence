"""
URL configuration for pong project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from . import views

apipatterns = [
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('', views.IndexView.as_view(), name='index'),
    path('api/', include((apipatterns, 'api'), namespace='api')),

    re_path(_(r'^login/?$'), views.LoginView.as_view(), name='login'),
    re_path(_(r'^register/?$'), views.RegisterView.as_view(), name='register'),
	# re_path(_(r'^password-reset/?$'), views.PasswordReset.as_view(), name='password_reset'),
    re_path(_(r'^home/?$'), views.HomeView.as_view(), name='home'),
    re_path(_(r'^profile/?$'), views.ProfileView.as_view(), name='profile'),
    re_path(_(r'^leaderboard/?$'), views.LeaderboardView.as_view(), name='leaderboard'),
	re_path(_(r'^social/?$'), views.SocialView.as_view(), name='social'),
    re_path(_(r'^settings/?$'), views.SettingsView.as_view(), name='settings'),
]