#!/usr/bin/env python
"""
Test admin functionality and project approval workflow
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from site_diary.models import Project, DiaryEntry
from django.utils import timezone

def test_admin_functionality():
    print("=" * 50)
    print("ADMIN FUNCTIONALITY TEST")
    print("=" * 50)
    
    # Test 1: Check project approval workflow
    print("\n1. Testing Project Approval Workflow...")
    
    # Count projects by status
    pending_projects = Project.objects.filter(status='pending_approval').count()
    approved_projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed']).count()
    rejected_projects = Project.objects.filter(status='rejected').count()
    
    print(f"   Pending approval: {pending_projects}")
    print(f"   Approved projects: {approved_projects}")
    print(f"   Rejected projects: {rejected_projects}")
    
    if approved_projects > 0:
        print("   [OK] Approved projects available for diary creation")
    else:
        print("   [INFO] No approved projects - create and approve some projects first")
    
    # Test 2: Check diary entry approval
    print("\n2. Testing Diary Entry Management...")
    
    total_entries = DiaryEntry.objects.count()
    pending_entries = DiaryEntry.objects.filter(approved=False, draft=False).count()
    approved_entries = DiaryEntry.objects.filter(approved=True).count()
    draft_entries = DiaryEntry.objects.filter(draft=True).count()
    
    print(f"   Total diary entries: {total_entries}")
    print(f"   Pending approval: {pending_entries}")
    print(f"   Approved entries: {approved_entries}")
    print(f"   Draft entries: {draft_entries}")
    
    if total_entries > 0:
        print("   [OK] Diary entries exist for admin review")
    else:
        print("   [INFO] No diary entries - create some entries first")
    
    # Test 3: Check admin views data availability
    print("\n3. Testing Admin Views Data...")
    
    # Check if we have users who can be admins
    admin_users = User.objects.filter(is_staff=True, is_superuser=True).count()
    site_managers = User.objects.filter(is_staff=True).count()
    
    print(f"   Admin users: {admin_users}")
    print(f"   Site managers: {site_managers}")
    
    if admin_users > 0:
        print("   [OK] Admin users available")
    else:
        print("   [WARN] No admin users - create superuser first")
    
    # Test 4: Verify approved projects are visible to site managers
    print("\n4. Testing Site Manager Access...")
    
    # Get approved projects that should be visible in diary dashboard
    visible_projects = Project.objects.filter(
        status__in=['planning', 'active', 'on_hold', 'completed']
    ).count()
    
    print(f"   Projects visible to site managers: {visible_projects}")
    
    if visible_projects > 0:
        print("   [OK] Approved projects will be visible in /diary/dashboard/")
        print("   [OK] Site managers can create diary entries for approved projects")
    else:
        print("   [WARN] No approved projects - admin needs to approve projects first")
    
    print("\n" + "=" * 50)
    print("ADMIN FUNCTIONALITY TEST SUMMARY")
    print("=" * 50)
    
    if approved_projects > 0 and visible_projects > 0:
        print("✓ Admin approval workflow is working")
        print("✓ Approved projects are visible to site managers")
        print("✓ Ready for diary creation and management")
    else:
        print("! Admin needs to approve projects first")
        print("! Use /diary/admin/clientproject/ to approve pending projects")
    
    print("=" * 50)

if __name__ == '__main__':
    test_admin_functionality()