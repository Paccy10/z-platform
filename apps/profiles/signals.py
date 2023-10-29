from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User
from .models import Profile, AccountVerification
from .constants.status import VerificationStatus


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=AccountVerification)
def change_user_prrofile_status(sender, instance, created, **kwargs):
    if created:
        profile = instance.user.profile
        profile.status = VerificationStatus.VERIFICATION_PENDING.value
        profile.save()
