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
from . import views

apipatterns = [
    path('', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('', include(('profiles.urls', 'profiles'), namespace='profiles')),
    path('', include(('friends.urls', 'friends'), namespace='friends')),
    path('lang/<str:lang>/', views.lang_reload, name='lang_reload'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django_prometheus.urls')),
    path('', views.index, name='index'),
    path('api/', include((apipatterns, 'api'), namespace='api')),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
	path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('home/', views.home, name='home'),
    path('profiles/me/', views.profile, name='profile'),
	path('profiles/<uuid:profile_id>/', views.profile_other, name='profile_other'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
	path('friends/', views.social, name='social'),
    path('friends/<uuid:friend_id>/', views.social_friend, name='social_friend'),
    path('settings/', views.settings, name='settings'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)\
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)