from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.common.serializers import BaseSerializer
from apps.common.utils import validate_unique_value
from ..constants.messages.error import errors
from ..models import User


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""

    firstname = serializers.CharField(
        required=True,
        error_messages={
            "required": errors["firstname"]["required"],
            "blank": errors["firstname"]["blank"],
        },
    )
    lastname = serializers.CharField(
        required=True,
        error_messages={
            "required": errors["lastname"]["required"],
            "blank": errors["lastname"]["blank"],
        },
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            "required": errors["email"]["required"],
            "blank": errors["email"]["blank"],
            "invalid": errors["email"]["invalid"],
        },
    )
    password = serializers.CharField(
        required=True,
        min_length=8,
        max_length=100,
        write_only=True,
        validators=[
            RegexValidator(
                regex="^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).+$",
                message=errors["password"]["weak"],
            )
        ],
        error_messages={
            "required": errors["password"]["required"],
            "blank": errors["password"]["blank"],
            "min_length": errors["password"]["min_length"],
        },
    )

    class Meta:
        model = User
        fields = [
            "firstname",
            "lastname",
            "middlename",
            "email",
            "password",
            "is_active",
        ] + BaseSerializer.Meta.fields

    def validate_email(self, email):
        norm_email = email.lower()
        validate_unique_value(
            model=User,
            field="email",
            value=norm_email,
            errors=errors,
            instance=self.instance,
        )

        return norm_email

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
