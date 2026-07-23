from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomerProfile, User, WorkerProfile


@receiver(post_save, sender=User)

#Automatically create the user profile in either Customer or Worker table
def create_user_profile(sender, instance, created, **kwargs):
    """Create a CustomerProfile or WorkerProfile when a new User is created.

    Minimal and safe: only runs on newly created users and avoids overwriting
    any existing profiles. Keeps tests and the registration flow working.
    """
    if not created:
        return

    try:
        if instance.role == "customer":
            CustomerProfile.objects.get_or_create(user=instance)
        elif instance.role == "worker":
            WorkerProfile.objects.get_or_create(user=instance)
    except Exception:
        # Be defensive in signals: don't let profile creation break user save.
        pass
