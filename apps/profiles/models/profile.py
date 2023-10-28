from django.contrib.auth import get_user_model
from django.db import models

from ...common.models import BaseModel
from ..constants.gender import Gender
from ..constants.marital_status import MaritalStatus
from ..constants.status import VerificationStatus
from ..utils import profile_photo_upload_to

User = get_user_model()


class Profile(BaseModel):
    """Profile model"""

    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    photo = models.ImageField(upload_to=profile_photo_upload_to, null=True)
    gender = models.CharField(
        max_length=20,
        null=True,
        choices=[(gender.value, gender.value) for gender in Gender],
    )
    age = models.IntegerField(null=True)
    date_of_birth = models.DateField(null=True)
    marital_status = models.CharField(
        max_length=20,
        null=True,
        choices=[
            (marital_status.value, marital_status.value)
            for marital_status in MaritalStatus
        ],
    )
    nationality = models.CharField(max_length=100, null=True)
    status = models.CharField(
        max_length=40,
        default=VerificationStatus.UNVERIFIED.value,
        choices=[(status.value, status.value) for status in VerificationStatus],
    )

    class Meta:
        indexes = [
            models.Index(fields=["date_of_birth"]),
            models.Index(fields=["nationality"]),
        ]

    def __str__(self):
        return f"{self.user.email}'s profile"
