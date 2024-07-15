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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import render
from . import views

apipatterns = [
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('', include(('friends.urls', 'friends'), namespace='friends')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('', views.index, name='index'),
    path('api/', include((apipatterns, 'api'), namespace='api')),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
	# path('password-reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
	path('profile/<uuid:profile_id>/', views.profile_other, name='profile_other'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
	path('social/', views.social, name='social'),
    path('settings/', views.settings, name='settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)