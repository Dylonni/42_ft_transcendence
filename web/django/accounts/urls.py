from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from . import views

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('register/', views.UserRegisterView.as_view(), name='user_register'),
    path('activate/<uidb64>/<token>/', views.UserActivateView.as_view(), name='user_activate'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('update-email/', views.UserUpdateEmailView.as_view(), name='update_email'),
]