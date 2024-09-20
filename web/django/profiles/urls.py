from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/search/', views.profile_search, name='profile_search'),
    
    path('profiles/me/', views.my_detail, name='my_detail'),
    path('profiles/me/alias/', views.my_alias, name='my_alias'),
    path('profiles/me/avatar/', views.my_avatar, name='my_avatar'),
	path('profiles/me/lang/<str:lang>/', views.my_lang, name='my_lang'),
	path('profiles/me/email/', views.my_email, name='my_email'),
	path('profiles/me/password/', views.my_password, name='my_password'),
	path('profiles/me/twofa/', views.my_twofa, name='my_twofa'),
    path('profiles/me/code/', views.my_code, name='my_code'),
	
    path('profiles/<uuid:profile_id>/', views.profile_detail, name='profile_detail'),
	path('profiles/<uuid:profile_id>/invites/', views.profile_invite_list, name='profile_invite_list'),
    path('profiles/<uuid:profile_id>/blocks/', views.profile_block_list, name='profile_block_list'),
	path('profiles/<uuid:profile_id>/requests/', views.profile_request_list, name='profile_request_list'),
    path('profiles/<uuid:profile_id>/friends/', views.profile_friend_list, name='profile_friend_list'),
	path('profiles/<uuid:profile_id>/elos/', views.profile_elo_list, name='profile_elo_list'),
	
    path('profiles/me/invites/', views.my_invite_list, name='my_invite_list'),
	path('profiles/me/invites/<uuid:invite_id>/', views.my_invite_detail, name='my_invite_detail'),
	path('profiles/me/blocks/', views.my_block_list, name='my_block_list'),
	path('profiles/me/blocks/<uuid:block_id>/', views.my_block_detail, name='my_block_detail'),
    path('profiles/me/requests/', views.my_request_list, name='my_request_list'),
	path('profiles/me/requests/<uuid:request_id>/', views.my_request_detail, name='my_request_detail'),
    
	path('profiles/me/elos/', views.my_elo_list, name='my_elo_list'),
    
	path('profiles/me/friends/', views.my_friend_list, name='my_friend_list'),
	path('profiles/me/friends/<uuid:friendship_id>/', views.my_friend_detail, name='my_friend_detail'),
	path('profiles/me/friends/<uuid:friendship_id>/messages/', views.my_friend_message_list, name='my_friend_message_list'),
]