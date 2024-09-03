from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('friends/', views.friend_list, name='friend_list'),
]