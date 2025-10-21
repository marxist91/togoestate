from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def set_role_for_superuser(sender, instance, created, **kwargs):
    """
    Si un superuser est créé, on force son rôle à admin_platform.
    """
    if created and instance.is_superuser:
        if instance.role != User.Roles.ADMIN_PLATFORM:
            instance.role = User.Roles.ADMIN_PLATFORM
            instance.save()