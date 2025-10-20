"""
Comprehensive test suite for role-based access control system
Tests middleware, decorators, utils, and complete user journeys
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.messages import get_messages
from accounts.models import AdminProfile, Profile
from accounts.utils import get_user_role, get_user_dashboard_url, can_access_path
from accounts.middleware import RoleBasedAccessMiddleware
from unittest.mock import Mock, patch

class RoleBasedAccessControlTests(TestCase):
    """Test role-based access control functionality"""
    
    def setUp(self):
        """Set up test users with different roles"""
        self.client = Client()
        
        # Create superadmin user
        self.superadmin = User.objects.create_superuser(
            username='superadmin@test.com',
            email='superadmin@test.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            admin_role='admin',
            approval_status='approved'
        )
        
        # Create site manager user
        self.site_manager_user = User.objects.create_user(
            username='sitemanager@test.com',
            email='sitemanager@test.com',
            password='testpass123',
            is_staff=True
        )
        self.site_manager_profile = AdminProfile.objects.create(
            user=self.site_manager_user,
            admin_role='supervisor',
            approval_status='approved'
        )
        
        # Create public user
        self.public_user = User.objects.create_user(
            username='client@test.com',
            email='client@test.com',
            password='testpass123'
        )
        self.public_profile = Profile.objects.create(
            user=self.public_user,
            role='customer'
        )

class UtilityFunctionsTests(RoleBasedAccessControlTests):
    """Test utility functions for role detection and access control"""
    
    def test_get_user_role_superadmin(self):
        """Test role detection for superadmin"""
        role = get_user_role(self.superadmin)
        self.assertEqual(role, 'superadmin')
    
    def test_get_user_role_admin(self):
        """Test role detection for admin"""
        role = get_user_role(self.admin_user)
        self.assertEqual(role, 'admin')
    
    def test_get_user_role_site_manager(self):
        """Test role detection for site manager"""
        role = get_user_role(self.site_manager_user)
        self.assertEqual(role, 'site_manager')
    
    def test_get_user_role_public(self):
        """Test role detection for public user"""
        role = get_user_role(self.public_user)
        self.assertEqual(role, 'public')
    
    def test_get_user_role_anonymous(self):
        """Test role detection for anonymous user"""
        from django.contrib.auth.models import AnonymousUser
        role = get_user_role(AnonymousUser())
        self.assertEqual(role, 'anonymous')
    
    def test_get_user_dashboard_url(self):
        """Test dashboard URL generation for different roles"""
        self.assertEqual(get_user_dashboard_url(self.superadmin), '/admin/')
        self.assertEqual(get_user_dashboard_url(self.admin_user), 'admin_side:admin_home')
        self.assertEqual(get_user_dashboard_url(self.site_manager_user), 'admin_side:admin_home')
        self.assertEqual(get_user_dashboard_url(self.public_user), '/user/')
    
    def test_can_access_path_permissions(self):
        """Test path access permissions for different roles"""
        # Public paths - everyone can access
        self.assertTrue(can_access_path(self.public_user, '/'))
        self.assertTrue(can_access_path(self.admin_user, '/'))
        self.assertTrue(can_access_path(self.site_manager_user, '/'))
        
        # Admin paths - only admin and superadmin
        self.assertFalse(can_access_path(self.public_user, '/portfolio/projectmanagement/'))
        self.assertTrue(can_access_path(self.admin_user, '/portfolio/projectmanagement/'))
        self.assertFalse(can_access_path(self.site_manager_user, '/portfolio/projectmanagement/'))
        self.assertTrue(can_access_path(self.superadmin, '/portfolio/projectmanagement/'))
        
        # Client paths - only public users and superadmin
        self.assertTrue(can_access_path(self.public_user, '/usersettings/'))
        self.assertFalse(can_access_path(self.admin_user, '/usersettings/'))
        self.assertFalse(can_access_path(self.site_manager_user, '/usersettings/'))
        self.assertTrue(can_access_path(self.superadmin, '/usersettings/'))

class MiddlewareTests(RoleBasedAccessControlTests):
    """Test middleware functionality"""
    
    def test_middleware_blocks_admin_from_client_areas(self):
        """Test that middleware blocks admin users from client areas"""
        self.client.login(username='admin@test.com', password='testpass123')
        
        # Try to access client settings
        response = self.client.get('/usersettings/')
        
        # Should be redirected
        self.assertEqual(response.status_code, 302)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Admin users cannot access client areas' in str(m) for m in messages))
    
    def test_middleware_blocks_client_from_admin_areas(self):
        """Test that middleware blocks client users from admin areas"""
        self.client.login(username='client@test.com', password='testpass123')
        
        # Try to access admin project management
        response = self.client.get('/portfolio/projectmanagement/')
        
        # Should be redirected
        self.assertEqual(response.status_code, 302)
        
        # Check for error message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('permission' in str(m).lower() for m in messages))
    
    def test_middleware_allows_appropriate_access(self):
        """Test that middleware allows appropriate access"""
        # Admin should access admin areas
        self.client.login(username='admin@test.com', password='testpass123')
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 200)
        
        # Public user should access public areas
        self.client.login(username='client@test.com', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class LoginRoutingTests(RoleBasedAccessControlTests):
    """Test post-login routing based on user roles"""
    
    def test_admin_login_routing(self):
        """Test that admin users are routed to admin dashboard after login"""
        response = self.client.post('/accounts/admin-auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        
        # Should redirect to admin dashboard
        self.assertEqual(response.status_code, 302)
        # The redirect should go to portfolio management (admin dashboard)
        self.assertIn('portfolio', response.url)
    
    def test_client_login_routing(self):
        """Test that client users are routed appropriately after login"""
        response = self.client.post('/accounts/client/login/', {
            'username': 'client@test.com',
            'password': 'testpass123'
        })
        
        # Should redirect (successful login)
        self.assertEqual(response.status_code, 302)

class ViewDecoratorTests(RoleBasedAccessControlTests):
    """Test view decorators for access control"""
    
    def test_require_admin_role_decorator(self):
        """Test that admin role decorator works correctly"""
        # Admin should access
        self.client.login(username='admin@test.com', password='testpass123')
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 200)
        
        # Client should be blocked
        self.client.login(username='client@test.com', password='testpass123')
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_require_public_role_decorator(self):
        """Test that public role decorator works correctly"""
        # Public user should access
        self.client.login(username='client@test.com', password='testpass123')
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 200)
        
        # Admin should be blocked
        self.client.login(username='admin@test.com', password='testpass123')
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 302)  # Redirected
    
    def test_require_site_manager_role_decorator(self):
        """Test that site manager role decorator works correctly"""
        # Site manager should access
        self.client.login(username='sitemanager@test.com', password='testpass123')
        response = self.client.get('/diary/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        # Admin should be blocked
        self.client.login(username='admin@test.com', password='testpass123')
        response = self.client.get('/diary/dashboard/')
        self.assertEqual(response.status_code, 302)  # Redirected

class SecurityTests(RoleBasedAccessControlTests):
    """Test security aspects of access control"""
    
    def test_unauthenticated_access_blocked(self):
        """Test that unauthenticated users are blocked from protected areas"""
        # Try to access admin area without login
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 302)  # Redirected to login
        
        # Try to access client area without login
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 302)  # Redirected to login
    
    def test_inactive_admin_blocked(self):
        """Test that inactive admin users are blocked"""
        # Create inactive admin
        inactive_admin = User.objects.create_user(
            username='inactive@test.com',
            email='inactive@test.com',
            password='testpass123',
            is_staff=True,
            is_active=False
        )
        AdminProfile.objects.create(
            user=inactive_admin,
            admin_role='admin',
            approval_status='approved'
        )
        
        # Try to login
        response = self.client.post('/accounts/admin-auth/login/', {
            'email': 'inactive@test.com',
            'password': 'testpass123'
        })
        
        # Should not be able to login
        self.assertFalse(response.wsgi_request.user.is_authenticated)
    
    def test_pending_admin_blocked(self):
        """Test that pending approval admin users are blocked"""
        # Create pending admin
        pending_admin = User.objects.create_user(
            username='pending@test.com',
            email='pending@test.com',
            password='testpass123',
            is_staff=True
        )
        AdminProfile.objects.create(
            user=pending_admin,
            admin_role='admin',
            approval_status='pending'
        )
        
        # Try to access admin area
        self.client.login(username='pending@test.com', password='testpass123')
        response = self.client.get('/portfolio/projectmanagement/')
        
        # Should be blocked
        self.assertEqual(response.status_code, 302)

class IntegrationTests(RoleBasedAccessControlTests):
    """Test complete user journeys and integration scenarios"""
    
    def test_complete_admin_journey(self):
        """Test complete admin user journey"""
        # Login as admin
        response = self.client.post('/accounts/admin-auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        
        # Should redirect to admin dashboard
        self.assertEqual(response.status_code, 302)
        
        # Should be able to access admin areas
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/blog/blogmanagement/')
        self.assertEqual(response.status_code, 200)
        
        # Should NOT be able to access client areas
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 302)
        
        # Should be able to access public areas
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_complete_client_journey(self):
        """Test complete client user journey"""
        # Login as client
        response = self.client.post('/accounts/client/login/', {
            'username': 'client@test.com',
            'password': 'testpass123'
        })
        
        # Should redirect successfully
        self.assertEqual(response.status_code, 302)
        
        # Should be able to access client areas
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 200)
        
        # Should be able to access public areas
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        
        # Should NOT be able to access admin areas
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 302)
    
    def test_complete_site_manager_journey(self):
        """Test complete site manager user journey"""
        # Login as site manager
        response = self.client.post('/accounts/admin-auth/login/', {
            'email': 'sitemanager@test.com',
            'password': 'testpass123'
        })
        
        # Should redirect to site manager dashboard
        self.assertEqual(response.status_code, 302)
        
        # Should be able to access site manager areas
        response = self.client.get('/diary/dashboard/')
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get('/diary/newproject/')
        self.assertEqual(response.status_code, 200)
        
        # Should NOT be able to access admin areas
        response = self.client.get('/portfolio/projectmanagement/')
        self.assertEqual(response.status_code, 302)
        
        # Should NOT be able to access client areas
        response = self.client.get('/usersettings/')
        self.assertEqual(response.status_code, 302)
        
        # Should be able to access public areas
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

class EdgeCaseTests(RoleBasedAccessControlTests):
    """Test edge cases and error scenarios"""
    
    def test_user_without_admin_profile(self):
        """Test user marked as staff but without AdminProfile"""
        user_no_profile = User.objects.create_user(
            username='noprofile@test.com',
            email='noprofile@test.com',
            password='testpass123',
            is_staff=True
        )
        
        role = get_user_role(user_no_profile)
        self.assertEqual(role, 'public')  # Should default to public
    
    def test_malformed_requests(self):
        """Test handling of malformed requests"""
        # Test with invalid paths
        response = self.client.get('/nonexistent/path/')
        self.assertEqual(response.status_code, 404)
        
        # Test with special characters
        response = self.client.get('/portfolio/../admin/')
        # Should be handled gracefully
        self.assertIn(response.status_code, [302, 404])

if __name__ == '__main__':
    pytest.main([__file__])
