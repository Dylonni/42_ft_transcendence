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
    path('accounts/', include('accounts.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((apipatterns, 'api'), namespace='api')),
    
    re_path(_(r'^login/?$'), views.login, name='login'),
    re_path(_(r'^register/?$'), views.register, name='register'),
    re_path(_(r'^settings/?$'), views.user_settings, name='settings'),
    
    path('', views.index, name='index'),
]