from django.urls import path
from .views import MeView, ChangePasswordView, ForgotPasswordView, ResetPasswordView

urlpatterns = [
    path("me/", MeView.as_view()),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path('reset-password/<uuid:token>/', ResetPasswordView.as_view(), name='reset-password')
]
