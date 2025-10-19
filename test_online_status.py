#!/usr/bin/env python
"""
Simple test script to verify online status tracking works
Run this with: python test_online_status.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.activity_tracker import UserActivityTracker
from django.utils import timezone

def test_online_status():
    print("Testing Online Status Tracking...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    if created:
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Test 1: User should be offline initially
    is_online = UserActivityTracker.is_user_online(user)
    print(f"Initial online status: {is_online} (should be False)")
    
    # Test 2: Mark user as online
    UserActivityTracker.mark_user_online(user)
    is_online = UserActivityTracker.is_user_online(user)
    print(f"After marking online: {is_online} (should be True)")
    
    # Test 3: Mark user as offline
    UserActivityTracker.mark_user_offline(user)
    is_online = UserActivityTracker.is_user_online(user)
    print(f"After marking offline: {is_online} (should be False)")
    
    print("Online status tracking test completed!")

if __name__ == '__main__':
    test_online_status()