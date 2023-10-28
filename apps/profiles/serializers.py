from rest_framework import serializers

from .models import Profile
from apps.common.serializers import BaseSerializer
from apps.users.constants.messages.error import errors as user_errors
from .constants.messages.error import errors as profile_errors
from .constants.gender import Gender
from .constants.marital_status import MaritalStatus


class ProfileDisplaySerializer(serializers.ModelSerializer):
    """User profile display serializer"""

    firstname = serializers.CharField(source="user.firstname")
    lastname = serializers.CharField(source="user.lastname")
    middlename = serializers.CharField(source="user.middlename")
    email = serializers.CharField(source="user.email")

    class Meta:
        model = Profile
        fields = [
            "firstname",
            "lastname",
            "middlename",
            "email",
            "photo",
            "gender",
            "age",
            "date_of_birth",
            "marital_status",
            "nationality",
            "status",
        ] + BaseSerializer.Meta.fields


class EditProfileSerializer(serializers.Serializer):
    """Edit user profile serializer"""

    firstname = serializers.CharField(
        error_messages={
            "required": user_errors["firstname"]["required"],
            "blank": user_errors["firstname"]["blank"],
        },
    )
    lastname = serializers.CharField(
        error_messages={
            "required": user_errors["lastname"]["required"],
            "blank": user_errors["lastname"]["blank"],
        }
    )
    middlename = serializers.CharField(required=False)
    photo = serializers.ImageField(required=False)
    gender = serializers.ChoiceField(
        choices=[(gender.value, gender.value) for gender in Gender],
        error_messages={
            "required": profile_errors["gender"]["required"],
            "blank": profile_errors["gender"]["blank"],
        },
    )
    date_of_birth = serializers.DateField(
        error_messages={
            "required": profile_errors["date_of_birth"]["required"],
            "blank": profile_errors["date_of_birth"]["blank"],
        },
    )
    marital_status = serializers.ChoiceField(
        choices=[
            (marital_status.value, marital_status.value)
            for marital_status in MaritalStatus
        ],
        error_messages={
            "required": profile_errors["marital_status"]["required"],
            "blank": profile_errors["marital_status"]["blank"],
        },
    )
    nationality = serializers.CharField(
        error_messages={
            "required": profile_errors["nationality"]["required"],
            "blank": profile_errors["nationality"]["blank"],
        }
    )

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "middle_name",
            "phone_number",
            "about_me",
            "avatar",
            "gender",
            "country",
            "city",
        ]
