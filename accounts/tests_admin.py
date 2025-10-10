from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from datetime import date, timedelta
from django.utils import timezone
from .models import AdminProfile, OneTimePassword
from .forms import AdminRegisterForm, AdminLoginForm, AdminOTPForm


class AdminAuthenticationTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create a test admin user
        self.admin_user = User.objects.create_user(
            username='admin@test.com',
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_active=True
        )
        
        # Create admin profile
        self.admin_profile = AdminProfile.objects.create(
            user=self.admin_user,
            admin_role='admin',
            approval_status='approved',
            department='IT',
            employee_id='EMP001'
        )

    def test_admin_register_view_get(self):
        """Test admin registration page loads"""
        url = reverse('accounts:admin_register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create an Account')
        self.assertIsInstance(response.context['form'], AdminRegisterForm)

    def test_admin_register_valid_data(self):
        """Test admin registration with valid data"""
        url = reverse('accounts:admin_register')
        data = {
            'first_name': 'New',
            'last_name': 'Admin',
            'email': 'newadmin@test.com',
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
            'terms': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect to OTP verification
        
        # Check user was created
        user = User.objects.get(email='newadmin@test.com')
        self.assertFalse(user.is_active)  # Should be inactive until verification
        self.assertTrue(user.is_staff)    # Should be marked as staff
        
        # Check admin profile was created
        self.assertTrue(hasattr(user, 'admin_profile'))
        self.assertEqual(user.admin_profile.approval_status, 'pending')
        
        # Check OTP was created
        self.assertTrue(OneTimePassword.objects.filter(user=user).exists())
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verification code', mail.outbox[0].body)

    def test_admin_register_duplicate_email(self):
        """Test admin registration with duplicate email"""
        url = reverse('accounts:admin_register')
        data = {
            'first_name': 'Duplicate',
            'last_name': 'Admin',
            'email': 'admin@test.com',  # Already exists
            'password1': 'complexpass123!',
            'password2': 'complexpass123!',
            'terms': True
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Should stay on form
        self.assertFormError(response, 'form', 'email', 'This email is already registered.')

    def test_admin_login_view_get(self):
        """Test admin login page loads"""
        url = reverse('accounts:admin_login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')
        self.assertIsInstance(response.context['form'], AdminLoginForm)

    def test_admin_login_valid_credentials(self):
        """Test admin login with valid credentials"""
        url = reverse('accounts:admin_login')
        data = {
            'email': 'admin@test.com',
            'password': 'testpass123',
            'remember': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        
        # Check user is logged in
        user = User.objects.get(email='admin@test.com')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.id)

    def test_admin_login_invalid_credentials(self):
        """Test admin login with invalid credentials"""
        url = reverse('accounts:admin_login')
        data = {
            'email': 'admin@test.com',
            'password': 'wrongpassword',
            'remember': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Should stay on form
        
        # Check failed login attempts incremented
        self.admin_profile.refresh_from_db()
        self.assertEqual(self.admin_profile.failed_login_attempts, 1)

    def test_admin_login_pending_approval(self):
        """Test admin login with pending approval"""
        # Set admin profile to pending
        self.admin_profile.approval_status = 'pending'
        self.admin_profile.save()
        
        url = reverse('accounts:admin_login')
        data = {
            'email': 'admin@test.com',
            'password': 'testpass123',
            'remember': False
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Should stay on form
        # Check that user is not logged in
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_admin_login_account_lockout(self):
        """Test admin account lockout after failed attempts"""
        url = reverse('accounts:admin_login')
        data = {
            'email': 'admin@test.com',
            'password': 'wrongpassword',
            'remember': False
        }
        
        # Make 5 failed attempts
        for i in range(5):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, 200)
        
        # Check account is locked
        self.admin_profile.refresh_from_db()
        self.assertEqual(self.admin_profile.failed_login_attempts, 5)
        self.assertIsNotNone(self.admin_profile.account_locked_until)
        self.assertTrue(self.admin_profile.is_account_locked())

    def test_admin_otp_verification(self):
        """Test admin OTP verification"""
        # Create pending admin user
        user = User.objects.create_user(
            username='pending@test.com',
            email='pending@test.com',
            password='testpass123',
            is_staff=True,
            is_active=False
        )
        AdminProfile.objects.create(
            user=user,
            approval_status='pending'
        )
        
        # Create OTP
        otp = OneTimePassword.objects.create(user=user, code='123456')
        
        # Set session
        session = self.client.session
        session['pending_admin_id'] = user.id
        session.save()
        
        url = reverse('accounts:admin_verify_otp')
        data = {'otp': '123456'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Check user is activated
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Check OTP is deleted
        self.assertFalse(OneTimePassword.objects.filter(user=user).exists())

    def test_admin_otp_verification_invalid_code(self):
        """Test admin OTP verification with invalid code"""
        # Create pending admin user
        user = User.objects.create_user(
            username='pending2@test.com',
            email='pending2@test.com',
            password='testpass123',
            is_staff=True,
            is_active=False
        )
        AdminProfile.objects.create(
            user=user,
            approval_status='pending'
        )
        
        # Create OTP
        otp = OneTimePassword.objects.create(user=user, code='123456')
        
        # Set session
        session = self.client.session
        session['pending_admin_id'] = user.id
        session.save()
        
        url = reverse('accounts:admin_verify_otp')
        data = {'otp': '999999'}  # Wrong code
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)  # Should stay on form
        
        # Check user is still inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)
        
        # Check OTP still exists
        self.assertTrue(OneTimePassword.objects.filter(user=user).exists())

    def test_admin_resend_otp(self):
        """Test admin OTP resend functionality"""
        # Create pending admin user
        user = User.objects.create_user(
            username='resend@test.com',
            email='resend@test.com',
            password='testpass123',
            is_staff=True,
            is_active=False
        )
        
        # Set session
        session = self.client.session
        session['pending_admin_id'] = user.id
        session.save()
        
        url = reverse('accounts:admin_resend_otp')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to verify OTP
        
        # Check new OTP was created
        self.assertTrue(OneTimePassword.objects.filter(user=user).exists())
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('new admin verification code', mail.outbox[0].body)

    def test_admin_logout(self):
        """Test admin logout"""
        # Login first
        self.client.login(username='admin@test.com', password='testpass123')
        
        url = reverse('accounts:admin_logout')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Check user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)


class AdminProfileModelTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='test@test.com',
            email='test@test.com',
            password='testpass123',
            is_staff=True
        )
        
        self.admin_profile = AdminProfile.objects.create(
            user=self.user,
            admin_role='staff',
            approval_status='approved'
        )

    def test_admin_profile_creation(self):
        """Test admin profile creation"""
        self.assertEqual(self.admin_profile.user, self.user)
        self.assertEqual(self.admin_profile.admin_role, 'staff')
        self.assertEqual(self.admin_profile.approval_status, 'approved')
        self.assertIsNotNone(self.admin_profile.created_at)

    def test_is_approved(self):
        """Test is_approved method"""
        self.assertTrue(self.admin_profile.is_approved())
        
        self.admin_profile.approval_status = 'pending'
        self.assertFalse(self.admin_profile.is_approved())

    def test_is_account_locked(self):
        """Test is_account_locked method"""
        self.assertFalse(self.admin_profile.is_account_locked())
        
        # Lock account for 30 minutes
        self.admin_profile.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.admin_profile.save()
        self.assertTrue(self.admin_profile.is_account_locked())
        
        # Set lock time in the past
        self.admin_profile.account_locked_until = timezone.now() - timedelta(minutes=30)
        self.admin_profile.save()
        self.assertFalse(self.admin_profile.is_account_locked())

    def test_can_login(self):
        """Test can_login method"""
        self.assertTrue(self.admin_profile.can_login())
        
        # Test inactive user
        self.user.is_active = False
        self.user.save()
        self.assertFalse(self.admin_profile.can_login())
        
        # Reset user
        self.user.is_active = True
        self.user.save()
        
        # Test pending approval
        self.admin_profile.approval_status = 'pending'
        self.admin_profile.save()
        self.assertFalse(self.admin_profile.can_login())
        
        # Test suspended
        self.admin_profile.approval_status = 'suspended'
        self.admin_profile.save()
        self.assertFalse(self.admin_profile.can_login())

    def test_str_method(self):
        """Test string representation"""
        expected = f"{self.user.get_full_name()} - Staff"
        self.assertEqual(str(self.admin_profile), expected)
