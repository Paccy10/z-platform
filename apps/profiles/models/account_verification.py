from django.contrib.auth import get_user_model
from django.db import models

from ...common.models import BaseModel
from ..constants.status import RequestStatus
from ..utils import verification_document_upload_to

User = get_user_model()


class AccountVerification(BaseModel):
    """Account verification requests model"""

    user = models.OneToOneField(
        User, related_name="account_verification", on_delete=models.CASCADE
    )
    id_document_number = models.CharField(max_length=20, null=True)
    id_document_image = models.ImageField(
        upload_to=verification_document_upload_to, null=True
    )
    status = models.CharField(
        max_length=40,
        default=RequestStatus.PENDING.value,
        choices=[(status.value, status.value) for status in RequestStatus],
    )
