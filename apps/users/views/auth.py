import jwt
import random
import string
import datetime
from rest_framework import generics, mixins, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.urls import reverse
from django.template.loader import get_template
from django_rq import enqueue
from django.contrib.auth.hashers import make_password
from django.core.signing import dumps, loads
from django.utils.encoding import force_bytes, smart_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from apps.users.models import User
from apps.users.serializers import (
    UserSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    generate_tokens,
)
from apps.users.constants.messages.error import USER_NOT_FOUND, errors
from apps.users.constants.messages.success import (
    OTP_SENT,
    PASSWORD_RESET_LINK_SENT,
    PASSWORD_RESET,
    LOGIN_LINK_SENT,
)
from apps.common.utils import send_email
from core.settings.base import env


class UserSignupView(mixins.CreateModelMixin, generics.GenericAPIView):
    """User signup view"""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        response = self.create(request, *args, **kwargs)

        # Send verification email
        user = User.objects.get(id=response.data["id"])
        token = RefreshToken.for_user(user).access_token
        current_path = reverse("confirm")
        url = (
            f"{request.scheme}://{request.get_host()}{current_path}?token={str(token)}"
        )
        subject = "Email Confirmation"
        message = get_template("confirmation.html").render({"user": user, "url": url})
        enqueue(send_email, subject, message, [user.email])

        return response


class UserConfirmationView(generics.GenericAPIView):
    """User confirmation view"""

    def get(self, request):
        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, env("SECRET_KEY"), algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            if not user.is_active:
                user.is_active = True
                user.save()

            return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"token": [errors["token"]["expired"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.DecodeError:
            return Response(
                {"token": [errors["token"]["invalid"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserLoginView(generics.GenericAPIView):
    """User login view"""

    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Send OTP
        user = serializer.validated_data
        otp = "".join(random.choice(string.digits) for _ in range(6))
        user.otp = make_password(otp)
        user.otp_expired_at = datetime.datetime.now() + datetime.timedelta(minutes=5)
        user.save()

        subject = "Login OTP"
        message = get_template("otp.html").render({"user": user, "otp": otp})
        enqueue(send_email, subject, message, [user.email])

        return Response({"detail": OTP_SENT}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    """Verify OTP view"""

    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ForgotPasswordView(generics.GenericAPIView):
    """Forgot password view"""

    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            raise NotFound(USER_NOT_FOUND)

        token = RefreshToken.for_user(user).access_token
        current_path = reverse("reset-password")
        url = (
            f"{request.scheme}://{request.get_host()}{current_path}?token={str(token)}"
        )
        subject = "Forgot Password"
        message = get_template("forgot-password.html").render(
            {"user": user, "url": url}
        )
        enqueue(send_email, subject, message, [user.email])

        return Response({"detail": PASSWORD_RESET_LINK_SENT}, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    """Reset password view"""

    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = request.GET.get("token")
        try:
            payload = jwt.decode(token, env("SECRET_KEY"), algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            user.set_password(serializer.validated_data["password"])
            user.save()

            return Response({"detail": PASSWORD_RESET}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"token": [errors["token"]["expired"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.DecodeError:
            return Response(
                {"token": [errors["token"]["invalid"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GenerateLoginLinkView(generics.GenericAPIView):
    """Generate login link view"""

    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if not user:
            raise NotFound(USER_NOT_FOUND)

        token = RefreshToken.for_user(user).access_token
        signed_token = urlsafe_base64_encode(force_bytes(dumps({"token": str(token)})))
        current_path = reverse("verify-login-link")
        url = f"{request.scheme}://{request.get_host()}{current_path}?token={signed_token}"
        subject = "Login Link"
        message = get_template("login-link.html").render({"user": user, "url": url})
        enqueue(send_email, subject, message, [user.email])

        return Response({"detail": LOGIN_LINK_SENT}, status=status.HTTP_200_OK)


class VerifyLoginLinkView(generics.GenericAPIView):
    """Verify login link view"""

    serializer_class = ForgotPasswordSerializer

    def get(self, request):
        signed_token = request.GET.get("token")

        try:
            token_payload = loads(smart_str(urlsafe_base64_decode(signed_token)))
        except Exception:
            return Response(
                {"token": [errors["token"]["invalid"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = token_payload.get("token")
        try:
            payload = jwt.decode(token, env("SECRET_KEY"), algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])

            return Response(generate_tokens(user), status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response(
                {"token": [errors["token"]["expired"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.DecodeError:
            return Response(
                {"token": [errors["token"]["invalid"]]},
                status=status.HTTP_400_BAD_REQUEST,
            )
