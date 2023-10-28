from django.urls import path

from .views import UserSignupView, UserConfirmationView, UserLoginView

urlpatterns = [
    path("auth/signup/", UserSignupView.as_view(), name="signup"),
    path("auth/confirm/", UserConfirmationView.as_view(), name="confirm"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
]
