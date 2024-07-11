from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from . import views

urlpatterns = [
    path('friends/', views.friend_list, name='friend_list'),
    path('friends/<uuid:profile_id>/', views.friend_detail, name='friend_detail'),
	path('friends/<uuid:profile_id>/chat/', views.friend_conversation, name='friend_conversation'),
	path('friends/<uuid:profile_id>/send/', views.friend_message, name='friend_message'),
	path('friends/requests/', views.friend_request_list_create, name='friend_request_list_create'),
    path('friends/requests/<uuid:request_id>/', views.friend_request_detail, name='friend_request_detail'),
	path('friends/search/', views.friend_search, name='friend_search'),
]