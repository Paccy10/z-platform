from django.urls import path

from .views import UserSignupView, UserConfirmationView

urlpatterns = [
    path("auth/signup/", UserSignupView.as_view(), name="signup"),
    path("auth/confirm/", UserConfirmationView.as_view(), name="confirm"),
]
