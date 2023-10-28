from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from ..common.models import BaseModel
from .managers import UserManager


class User(AbstractBaseUser, BaseModel):
    """Custom user model"""

    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    middlename = models.CharField(max_length=255, null=True)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    otp = models.CharField(max_length=255, null=True)
    otp_expired_at = models.DateTimeField(null=True)

    USERNAME_FIELD = "email"

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=["firstname"]),
            models.Index(fields=["lastname"]),
            models.Index(fields=["middlename"]),
        ]

    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.firstname}{f' {self.middlename }'if self.middlename else ''} {self.lastname}"
