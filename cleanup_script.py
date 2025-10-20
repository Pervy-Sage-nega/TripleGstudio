#!/usr/bin/env python
"""
Direct cleanup script for orphaned users
Run with: python manage.py shell < cleanup_script.py
"""

from django.contrib.auth.models import User
from accounts.models import Profile, AdminProfile, SiteManagerProfile
from django.db import transaction

print("=== Before Cleanup ===")
all_users = User.objects.all()
print(f"Total users: {all_users.count()}")

for user in all_users:
    profiles = []
    if hasattr(user, 'profile'):
        profiles.append(f"Profile({user.profile.role})")
    if hasattr(user, 'adminprofile'):
        profiles.append(f"AdminProfile({user.adminprofile.admin_role})")
    if hasattr(user, 'sitemanagerprofile'):
        profiles.append(f"SiteManagerProfile({user.sitemanagerprofile.approval_status})")
    
    profile_info = " | ".join(profiles) if profiles else "NO PROFILE"
    user_type = "SUPERUSER" if user.is_superuser else "REGULAR"
    status = "ACTIVE" if user.is_active else "INACTIVE"
    
    print(f"ID: {user.id} | {user.username} | {user.email} | {status} | {user_type} | {profile_info}")

print("\n=== Starting Cleanup ===")

# Delete all non-superuser users
with transaction.atomic():
    regular_users = User.objects.filter(is_superuser=False)
    deleted_count = 0
    
    for user in regular_users:
        try:
            # Delete associated profiles first
            Profile.objects.filter(user=user).delete()
            AdminProfile.objects.filter(user=user).delete() 
            SiteManagerProfile.objects.filter(user=user).delete()
            
            username = user.username
            user.delete()
            deleted_count += 1
            print(f"✓ Deleted user: {username}")
            
        except Exception as e:
            print(f"✗ Failed to delete {user.username}: {e}")

print(f"\n=== Cleanup Complete ===")
print(f"Deleted {deleted_count} users")

print("\n=== After Cleanup ===")
remaining_users = User.objects.all()
print(f"Remaining users: {remaining_users.count()}")

for user in remaining_users:
    user_type = "SUPERUSER" if user.is_superuser else "REGULAR"
    print(f"ID: {user.id} | {user.username} | {user.email} | {user_type}")
