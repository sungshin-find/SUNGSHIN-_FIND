from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView, EmailSendView, EmailVerifyView

urlpatterns = [
    path('email/send-code/', EmailSendView.as_view(), name='user-email-send'),
    path('email/verify-code/', EmailVerifyView.as_view(), name='user-email-verify'),
    path('signup/', SignupView.as_view(), name='user-signup'),
    path('login/', TokenObtainPairView.as_view(), name='user-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='user-token-refresh'),
]