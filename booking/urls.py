from django.urls import path
from .views import *


urlpatterns = [
    path('register', RegisterView.as_view(),name = 'register'),
    path('login', LoginAPIView.as_view(),name = 'login'),
    path('email-verify/', VerifyEmail.as_view(),name = 'email-verify'),
    path('reset-email-request/', RequestPasswordResetEmail.as_view(), name="reset-email-request"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenViewAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

]