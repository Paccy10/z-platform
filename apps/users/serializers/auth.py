from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .user import UserSerializer
from ..constants.messages.error import errors
from ..models import User


def generate_tokens(user):
    token = RefreshToken.for_user(user)

    return {
        "access_token": str(token.access_token),
        "refresh_token": str(token),
        "user": UserSerializer(user).data,
    }


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
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(errors["account"]["no_account"])

        if not user.check_password(password):
            raise AuthenticationFailed(errors["account"]["no_account"])

        if not user.is_active:
            raise AuthenticationFailed(errors["account"]["disabled"])

        return user

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = self.authenticate_user(email, password)

        return generate_tokens(user)
