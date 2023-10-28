from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from django.core.validators import RegexValidator
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from .user import UserSerializer
from ..constants.messages.error import errors
from ..constants.messages.success import OTP_SENT
from ..models import User


def generate_tokens(user):
    token = RefreshToken.for_user(user)

    return {
        "access_token": str(token.access_token),
        "refresh_token": str(token),
        "user": UserSerializer(user).data,
    }


def get_user_by_email(email):
    try:
        user = User.objects.get(email=email)

        return user
    except User.DoesNotExist:
        raise AuthenticationFailed(errors["account"]["no_account"])


class LoginSerializer(serializers.ModelSerializer):
    """User login serializer"""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        error_messages={
            "required": errors["password"]["required"],
        },
    )

    class Meta:
        model = User
        fields = ["email", "password"]

    def authenticate_user(self, email, password):
        user = get_user_by_email(email)

        if not user.check_password(password):
            raise AuthenticationFailed(errors["account"]["no_account"])

        if not user.is_active:
            raise AuthenticationFailed(errors["account"]["disabled"])

        return user

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = self.authenticate_user(email, password)

        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{6}$",
                message=errors["otp"]["length"],
            )
        ],
        error_messages={
            "required": errors["otp"]["required"],
            "blank": errors["otp"]["blank"],
        },
    )

    def validate(self, attrs):
        email = attrs.get("email")
        otp = attrs.get("otp")
        user = get_user_by_email(email)

        if not user.otp or not check_password(otp, user.otp):
            raise serializers.ValidationError({"otp": errors["otp"]["invalid"]})

        if user.otp_expired_at and user.otp_expired_at < timezone.now():
            raise serializers.ValidationError({"otp": errors["otp"]["expired"]})

        tokens = generate_tokens(user)

        user.otp_expired_at = timezone.now()
        user.save()

        return tokens
