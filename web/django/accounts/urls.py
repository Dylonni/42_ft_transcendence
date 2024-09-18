from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

authpatterns = [
    path('login/', views.user_login, name='user_login'),
	path('twofa/', views.user_twofa, name='user_twofa'),
	path('logout/', views.user_logout, name='user_logout'),
	
    path('register/', views.user_register, name='user_register'),
    path('activate/', views.user_activate, name='user_activate'),
	
	path('password/request/', views.password_request, name='password_request'),
	path('password/reset/', views.password_reset, name='password_reset'),
	path('password/confirm/', views.password_confirm, name='password_confirm'),
]

oauthpatterns = [
	path('42/login/', views.fortytwo_login, name='fortytwo_login'),
	path('42/unlink/', views.fortytwo_unlink, name='fortytwo_unlink'),
	path('42/callback/', views.fortytwo_callback, name='fortytwo_callback'),
]

tknpatterns = [
	path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', views.token_verify, name='token_verify'),
]

urlpatterns = [
	path('auth/', include((authpatterns, 'auth'), namespace='auth')),
	path('oauth/', include((oauthpatterns, 'oauth'), namespace='oauth')),
    path('token/', include((tknpatterns, 'token'), namespace='token')),
]