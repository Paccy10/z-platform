from django.urls import path

from .views import (
    UserSignupView,
    UserConfirmationView,
    UserLoginView,
    MyProfileView,
    VerifyOTPView,
    ForgotPasswordView,
    ResetPasswordView,
    GenerateLoginLinkView,
    VerifyLoginLinkView,
    VerificationRequestView,
    VerificationRequestsView,
    VerificationRequestDetailsView,
    VerificationRequestReviewView,
)

urlpatterns = [
    path("auth/signup/", UserSignupView.as_view(), name="signup"),
    path("auth/confirm/", UserConfirmationView.as_view(), name="confirm"),
    path("auth/login/", UserLoginView.as_view(), name="login"),
    path("auth/otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path(
        "auth/generate-login-link/",
        GenerateLoginLinkView.as_view(),
        name="generate-login-link",
    ),
    path(
        "auth/verify-login-link/",
        VerifyLoginLinkView.as_view(),
        name="verify-login-link",
    ),
    path("profile/me/", MyProfileView.as_view(), name="my-profile"),
    path(
        "profile/me/verify/", VerificationRequestView.as_view(), name="verify-request"
    ),
    path(
        "profile/verification/requests/",
        VerificationRequestsView.as_view(),
        name="get-verification-requests",
    ),
    path(
        "profile/verification/requests/<slug:id>/",
        VerificationRequestDetailsView.as_view(),
        name="get-verification-request-details",
    ),
    path(
        "profile/verification/requests/<slug:id>/review/",
        VerificationRequestReviewView.as_view(),
        name="review-verification-request",
    ),
]
