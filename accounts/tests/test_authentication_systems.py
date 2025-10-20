"""
Comprehensive tests for all authentication systems in Triple G BuildHub
Tests Site Manager, Blog Creator, and Client authentication flows.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core import mail
from django.utils import timezone
from datetime import timedelta
import json

from ..models import AdminProfile, OneTimePassword
from ..forms.sitemanager_forms import SiteManagerRegistrationForm, SiteManagerLoginForm
from ..forms.blogcreator_forms import BlogCreatorRegistrationForm, BlogCreatorLoginForm
from ..forms.client_forms import ClientRegistrationForm, ClientLoginForm


class SiteManagerAuthenticationTest(TestCase):
    """Test Site Manager authentication system"""
    
    def setUp(self):
        self.client = Client()
        self.registration_data = {
            'first_name': 'John',
            'last_name': 'Manager',
            'email': 'john.manager@tripleg.com',
            'phone': '+1234567890',
            'company_department': 'Construction Management',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'terms_accepted': True
        }
    
    def test_sitemanager_registration_form_valid(self):
        """Test site manager registration form validation"""
        form = SiteManagerRegistrationForm(data=self.registration_data)
        self.assertTrue(form.is_valid())
    
    def test_sitemanager_registration_form_password_mismatch(self):
        """Test password mismatch validation"""
        data = self.registration_data.copy()
        data['confirm_password'] = 'DifferentPass123!'
        form = SiteManagerRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirm_password', form.errors)
    
    def test_sitemanager_registration_view(self):
        """Test site manager registration view"""
        response = self.client.post(
            reverse('accounts:sitemanager_register'),
            data=self.registration_data
        )
        
        # Should redirect to OTP verification
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:sitemanager_verify_otp'))
        
        # User should be created but inactive
        user = User.objects.get(email=self.registration_data['email'])
        self.assertFalse(user.is_active)
        
        # AdminProfile should be created
        self.assertTrue(hasattr(user, 'adminprofile'))
        self.assertEqual(user.adminprofile.admin_role, 'supervisor')
        self.assertEqual(user.adminprofile.approval_status, 'pending')
        
        # OTP should be generated
        self.assertTrue(OneTimePassword.objects.filter(user=user).exists())
        
        # Email should be sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Site Manager', mail.outbox[0].subject)
    
    def test_sitemanager_otp_verification(self):
        """Test OTP verification process"""
        # First register
        self.client.post(
            reverse('accounts:sitemanager_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        # Verify OTP
        response = self.client.post(
            reverse('accounts:sitemanager_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Should redirect to pending approval
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:sitemanager_pending_approval'))
        
        # User should be active and email verified
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.adminprofile.email_verified)
        
        # OTP should be deleted
        self.assertFalse(OneTimePassword.objects.filter(user=user).exists())
    
    def test_sitemanager_login_before_approval(self):
        """Test login attempt before admin approval"""
        # Create and verify user
        self.client.post(
            reverse('accounts:sitemanager_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        self.client.post(
            reverse('accounts:sitemanager_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Try to login (should fail - pending approval)
        response = self.client.post(
            reverse('accounts:sitemanager_login'),
            data={
                'username': self.registration_data['email'],
                'password': self.registration_data['password']
            }
        )
        
        # Should show error message
        messages = list(response.context['messages'])
        self.assertTrue(any('pending approval' in str(m) for m in messages))
    
    def test_sitemanager_login_after_approval(self):
        """Test successful login after approval"""
        # Create, verify, and approve user
        self.client.post(
            reverse('accounts:sitemanager_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        self.client.post(
            reverse('accounts:sitemanager_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Approve user
        user.adminprofile.approval_status = 'approved'
        user.adminprofile.save()
        
        # Login should succeed
        response = self.client.post(
            reverse('accounts:sitemanager_login'),
            data={
                'username': self.registration_data['email'],
                'password': self.registration_data['password']
            }
        )
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)


class BlogCreatorAuthenticationTest(TestCase):
    """Test Blog Creator authentication system"""
    
    def setUp(self):
        self.client = Client()
        self.registration_data = {
            'first_name': 'Jane',
            'last_name': 'Writer',
            'email': 'jane.writer@tripleg.com',
            'phone': '+1234567891',
            'writing_experience': 'intermediate',
            'specialization': 'Architecture and Design',
            'portfolio_links': 'https://janewriter.com/portfolio',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'terms_accepted': True
        }
    
    def test_blogcreator_registration_form_valid(self):
        """Test blog creator registration form validation"""
        form = BlogCreatorRegistrationForm(data=self.registration_data)
        self.assertTrue(form.is_valid())
    
    def test_blogcreator_registration_view(self):
        """Test blog creator registration view"""
        response = self.client.post(
            reverse('accounts:blogcreator_register'),
            data=self.registration_data
        )
        
        # Should redirect to OTP verification
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:blogcreator_verify_otp'))
        
        # User should be created with staff role
        user = User.objects.get(email=self.registration_data['email'])
        self.assertEqual(user.adminprofile.admin_role, 'staff')
        self.assertEqual(user.adminprofile.writing_experience, 'intermediate')
    
    def test_blogcreator_login_after_approval(self):
        """Test blog creator login after approval"""
        # Create, verify, and approve user
        self.client.post(
            reverse('accounts:blogcreator_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        self.client.post(
            reverse('accounts:blogcreator_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Approve user
        user.adminprofile.approval_status = 'approved'
        user.adminprofile.save()
        
        # Login should succeed
        response = self.client.post(
            reverse('accounts:blogcreator_login'),
            data={
                'username': self.registration_data['email'],
                'password': self.registration_data['password']
            }
        )
        
        self.assertEqual(response.status_code, 302)


class ClientAuthenticationTest(TestCase):
    """Test Client authentication system"""
    
    def setUp(self):
        self.client = Client()
        self.registration_data = {
            'first_name': 'Bob',
            'last_name': 'Client',
            'email': 'bob.client@example.com',
            'phone': '+1234567892',
            'company': 'ABC Corporation',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'terms_accepted': True,
            'newsletter_subscription': True
        }
    
    def test_client_registration_form_valid(self):
        """Test client registration form validation"""
        form = ClientRegistrationForm(data=self.registration_data)
        self.assertTrue(form.is_valid())
    
    def test_client_registration_view(self):
        """Test client registration view"""
        response = self.client.post(
            reverse('accounts:client_register'),
            data=self.registration_data
        )
        
        # Should redirect to OTP verification
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:client_verify_otp'))
        
        # User should be created (no AdminProfile for clients)
        user = User.objects.get(email=self.registration_data['email'])
        self.assertFalse(hasattr(user, 'adminprofile'))
    
    def test_client_otp_verification_auto_login(self):
        """Test client OTP verification with auto-login"""
        # Register
        self.client.post(
            reverse('accounts:client_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        # Verify OTP (should auto-login)
        response = self.client.post(
            reverse('accounts:client_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Should redirect to user settings (auto-approved and logged in)
        self.assertEqual(response.status_code, 302)
        
        # User should be active and logged in
        user.refresh_from_db()
        self.assertTrue(user.is_active)
    
    def test_client_login(self):
        """Test client login"""
        # Create and verify user first
        self.client.post(
            reverse('accounts:client_register'),
            data=self.registration_data
        )
        
        user = User.objects.get(email=self.registration_data['email'])
        otp = OneTimePassword.objects.get(user=user)
        
        self.client.post(
            reverse('accounts:client_verify_otp'),
            data={'otp': otp.code}
        )
        
        # Logout first
        self.client.logout()
        
        # Login should succeed
        response = self.client.post(
            reverse('accounts:client_login'),
            data={
                'username': self.registration_data['email'],
                'password': self.registration_data['password']
            }
        )
        
        self.assertEqual(response.status_code, 302)


class OTPSecurityTest(TestCase):
    """Test OTP security features"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_otp_expiry(self):
        """Test OTP expiration"""
        otp = OneTimePassword.objects.create(
            user=self.user,
            code='123456',
            created_at=timezone.now() - timedelta(minutes=15)
        )
        
        self.assertTrue(otp.is_expired())
    
    def test_otp_rate_limiting(self):
        """Test OTP resend rate limiting"""
        otp = OneTimePassword.objects.create(
            user=self.user,
            code='123456',
            created_at=timezone.now() - timedelta(seconds=30)
        )
        
        # Should not be able to resend yet
        self.assertFalse(otp.can_resend())
        
        # Update created time to allow resend
        otp.created_at = timezone.now() - timedelta(seconds=70)
        otp.save()
        
        # Should be able to resend now
        self.assertTrue(otp.can_resend())


class AccountLockingTest(TestCase):
    """Test account locking functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_profile = AdminProfile.objects.create(
            user=self.user,
            admin_role='supervisor',
            approval_status='approved'
        )
    
    def test_account_locking(self):
        """Test account locking mechanism"""
        # Lock account
        self.admin_profile.lock_account(duration_minutes=30)
        
        # Account should be locked
        self.assertTrue(self.admin_profile.is_account_locked())
        self.assertFalse(self.admin_profile.can_login())
    
    def test_failed_login_attempts(self):
        """Test failed login attempt tracking"""
        # Simulate failed login attempts
        for i in range(5):
            self.admin_profile.failed_login_attempts += 1
            self.admin_profile.save()
        
        # Should trigger account lock
        if self.admin_profile.failed_login_attempts >= 5:
            self.admin_profile.lock_account()
        
        self.assertTrue(self.admin_profile.is_account_locked())


class IntegrationTest(TestCase):
    """Integration tests for role-based access"""
    
    def test_role_detection(self):
        """Test role detection for different user types"""
        # Site Manager
        site_manager = User.objects.create_user(
            username='sitemanager',
            email='sm@tripleg.com',
            password='testpass123'
        )
        AdminProfile.objects.create(
            user=site_manager,
            admin_role='supervisor',
            approval_status='approved'
        )
        
        # Blog Creator
        blog_creator = User.objects.create_user(
            username='blogcreator',
            email='bc@tripleg.com',
            password='testpass123'
        )
        AdminProfile.objects.create(
            user=blog_creator,
            admin_role='staff',
            approval_status='approved'
        )
        
        # Client (no AdminProfile)
        client = User.objects.create_user(
            username='client',
            email='client@example.com',
            password='testpass123'
        )
        
        # Test role detection
        self.assertEqual(site_manager.adminprofile.admin_role, 'supervisor')
        self.assertEqual(blog_creator.adminprofile.admin_role, 'staff')
        self.assertFalse(hasattr(client, 'adminprofile'))
    
    def test_cross_authentication_prevention(self):
        """Test that users can't login to wrong authentication systems"""
        # Create a site manager
        site_manager = User.objects.create_user(
            username='sitemanager',
            email='sm@tripleg.com',
            password='testpass123'
        )
        AdminProfile.objects.create(
            user=site_manager,
            admin_role='supervisor',
            approval_status='approved'
        )
        
        # Try to login as blog creator (should fail)
        response = self.client.post(
            reverse('accounts:blogcreator_login'),
            data={
                'username': 'sm@tripleg.com',
                'password': 'testpass123'
            }
        )
        
        # Should show error message about wrong account type
        messages = list(response.context['messages'])
        self.assertTrue(any('not authorized' in str(m) for m in messages))
