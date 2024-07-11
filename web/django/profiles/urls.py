from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/<uuid:profile_id>/', views.profile_detail, name='profile_detail'),
    path('profiles/<uuid:profile_id>/block/', views.profile_block, name='profile_block'),
    path('profiles/me/', views.profile_me, name='profile_me'),
    path('profiles/me/alias/', views.profile_alias, name='profile_me_alias'),
    path('profiles/me/avatar/', views.profile_avatar, name='profile_me_avatar'),
    path('profiles/me/status/', views.profile_status, name='profile_me_status'),
    path('profiles/search/', views.profile_search, name='profile_search'),
]