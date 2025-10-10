"""Signals keeping user-related profile data in sync."""

from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.apps import apps

from .models import AdminProfile, SuperAdminProfile, Profile


def _ensure_superuser_profile(user: User) -> None:
    """Guarantee superusers have a SuperAdminProfile."""
    if not user.is_superuser:
        return

    SuperAdminProfile.objects.get_or_create(
        user=user,
        defaults={
            "title": "Super Administrator",
        },
    )


@receiver(post_save, sender=User)
def create_related_profiles(sender, instance: User, created: bool, **kwargs) -> None:
    """Ensure every user has the appropriate profile records."""
    if created and not instance.is_superuser:
        Profile.objects.get_or_create(user=instance)

    _ensure_superuser_profile(instance)


def backfill_superuser_admin_profiles() -> None:
    """Backfill super admin profiles for existing superusers."""
    for user in User.objects.filter(is_superuser=True):
        # Remove any client profiles mistakenly attached to superusers
        Profile.objects.filter(user=user).delete()
        # Remove any admin profiles for superusers (they should be in SuperAdminProfile)
        AdminProfile.objects.filter(user=user).delete()
        _ensure_superuser_profile(user)


@receiver(post_migrate)
def run_backfill_after_migrations(sender, **kwargs) -> None:
    """
    Run backfill after migrations are complete.
    This ensures database is ready and all tables exist.
    """
    # Only run for the accounts app to avoid running multiple times
    if sender.name == 'accounts':
        try:
            backfill_superuser_admin_profiles()
        except Exception as e:
            # Log the error but don't crash the startup
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to backfill superuser profiles: {e}")


# ✅ REMOVED: No longer calling backfill_superuser_admin_profiles() at module import time