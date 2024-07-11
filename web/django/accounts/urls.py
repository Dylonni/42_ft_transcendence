from django.urls import include, path
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

authpatterns = [
    path('login/', views.user_login, name='user_login'),
	path('logout/', views.user_logout, name='user_logout'),
	
    path('register/', views.user_register, name='user_register'),
    path('activate/<uidb64>/<token>/', views.user_activate, name='user_activate'),
	
	path('reset-password/request/', views.password_reset_request, name='password_reset_request'),
	path('reset-password/<uidb64>/<token>/', views.password_reset, name='password_reset'),
	path('reset-password/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]

oauthpatterns = [
	path('42/login/', views.fortytwo_login, name='fortytwo_login'),
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
    # path('update-email/', views.UserUpdateEmailView.as_view(), name='update_email'),