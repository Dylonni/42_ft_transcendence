from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('profiles/', views.profile_list, name='profile_list'),
    path('profiles/search/', views.profile_search, name='profile_search'),
    
    path('profiles/me/', views.my_detail, name='my_detail'),
    path('profiles/me/alias/', views.my_alias, name='my_alias'),
    path('profiles/me/avatar/', views.my_avatar, name='my_avatar'),
    # path('profiles/me/status/', views.my_status, name='my_status'),
	
    path('profiles/<uuid:profile_id>/', views.profile_detail, name='profile_detail'),
	path('profiles/<uuid:profile_id>/invites/', views.profile_invite_list, name='profile_invite_list'),
    path('profiles/<uuid:profile_id>/blocks/', views.profile_block_list, name='profile_block_list'),
	path('profiles/<uuid:profile_id>/requests/', views.profile_request_list, name='profile_request_list'),
    path('profiles/<uuid:profile_id>/friends/', views.profile_friend_list, name='profile_friend_list'),
	
    path('profiles/me/invites/', views.my_invite_list, name='my_invite_list'),
	path('profiles/me/invites/<uuid:invite_id>/', views.my_invite_detail, name='my_invite_detail'),
	path('profiles/me/blocks/', views.my_block_list, name='my_block_list'),
	path('profiles/me/blocks/<uuid:block_id>/', views.my_block_detail, name='my_block_detail'),
    path('profiles/me/requests/', views.my_request_list, name='my_request_list'),
	path('profiles/me/requests/<uuid:request_id>/', views.my_request_detail, name='my_request_detail'),
	path('profiles/me/friends/', views.my_friend_list, name='my_friend_list'),
	path('profiles/me/friends/<uuid:friend_id>/', views.my_friend_detail, name='my_friend_detail'),
	path('profiles/me/friends/<uuid:friend_id>/messages/', views.my_friend_message_list, name='my_friend_message_list'),
	path('profiles/me/friends/<uuid:friend_id>/messages/<uuid:message_id>', views.my_friend_message_detail, name='my_friend_message_detail'),
]