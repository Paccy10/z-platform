from django.urls import path

from .views import (
    UserSignupView,
    UserConfirmationView,
    UserLoginView,
    MyProfileView,
    VerifyOTPView,
)

urlpatterns = [
    path("auth/signup/", UserSignupView.as_view(), name="signup"),
    path("auth/confirm/", UserConfirmationView.as_view(), name="confirm"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
]
