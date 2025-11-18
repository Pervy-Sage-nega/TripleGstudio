#!/usr/bin/env python
"""
Test script to verify admin interface setup
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from accounts.models import AdminProfile

def test_admin_urls():
    """Test if admin URLs are properly configured"""
    try:
        # Test URL reversal
        admin_home_url = reverse('admin_side:admin_home')
        admin_settings_url = reverse('admin_side:admin_settings')
        admin_logout_url = reverse('admin_side:admin_logout')
        
        print("✅ Admin URLs are properly configured:")
        print(f"   - Admin Home: {admin_home_url}")
        print(f"   - Admin Settings: {admin_settings_url}")
        print(f"   - Admin Logout: {admin_logout_url}")
        return True
    except Exception as e:
        print(f"❌ Admin URL configuration error: {e}")
        return False

def test_admin_views():
    """Test if admin views are accessible"""
    try:
        # Create test client
        client = Client()
        
        # Test admin home (should redirect to login)
        response = client.get(reverse('admin_side:admin_home'))
        if response.status_code in [200, 302]:
            print("✅ Admin home view is accessible")
        else:
            print(f"❌ Admin home view returned status {response.status_code}")
            return False
            
        # Test admin settings (should redirect to login)
        response = client.get(reverse('admin_side:admin_settings'))
        if response.status_code in [200, 302]:
            print("✅ Admin settings view is accessible")
        else:
            print(f"❌ Admin settings view returned status {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Admin view test error: {e}")
        return False

def test_models():
    """Test if required models exist"""
    try:
        # Test AdminProfile model
        admin_count = AdminProfile.objects.count()
        user_count = User.objects.count()
        
        print(f"✅ Models are accessible:")
        print(f"   - Total users: {user_count}")
        print(f"   - Admin profiles: {admin_count}")
        return True
    except Exception as e:
        print(f"❌ Model test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Admin Interface Setup...")
    print("=" * 50)
    
    tests = [
        ("URL Configuration", test_admin_urls),
        ("View Accessibility", test_admin_views),
        ("Model Access", test_models),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Admin interface is ready for testing.")
        print("\n🚀 Next steps:")
        print("   1. Start the Django server: python manage.py runserver")
        print("   2. Login as site manager at: /accounts/sitemanager/login/")
        print("   3. Access admin panel at: /admin-panel/")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
