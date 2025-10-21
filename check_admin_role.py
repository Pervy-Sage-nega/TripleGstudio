#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('.')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TripleG.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import AdminProfile

# Get user
try:
    user = User.objects.get(email='rideouts191@gmail.com')
    print(f'User found: {user.email}')
    
    # Check AdminProfile
    admin_profiles = AdminProfile.objects.filter(user=user)
    print(f'AdminProfile count: {admin_profiles.count()}')
    
    for ap in admin_profiles:
        print(f'Admin Role: {ap.admin_role}')
        print(f'Approval Status: {ap.approval_status}')
        print(f'User Active: {user.is_active}')
        
        # Test hasattr
        print(f'hasattr(user, "adminprofile"): {hasattr(user, "adminprofile")}')
        
        # Test direct access
        try:
            direct_ap = user.adminprofile
            print(f'Direct access works: {direct_ap.admin_role}')
        except Exception as e:
            print(f'Direct access failed: {e}')
            
except User.DoesNotExist:
    print('User not found')
except Exception as e:
    print(f'Error: {e}')
