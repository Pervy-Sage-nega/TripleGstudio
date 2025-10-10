from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random


class Profile(models.Model):
    USER_ROLES = [
        ('guest', 'Guest'),
        ('customer', 'Customer'),
        ('architect', 'Architect'),
        # ('admin', 'Admin'),  # use is_staff / is_superuser instead
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=USER_ROLES, default='guest')
    phone = models.CharField(max_length=20, blank=True, null=True)
    assigned_architect = models.CharField(max_length=100, blank=True, null=True)
    project_name = models.CharField(max_length=200, blank=True, null=True)
    project_start = models.DateField(blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    class Meta:
        verbose_name = 'Client Profile'
        verbose_name_plural = 'Client Profiles'
        
    def __str__(self):
        return f"{self.user.username} - {self.role}"


class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    def can_resend(self):
        """Check if user can request a new OTP (rate limiting)"""
        return timezone.now() > self.created_at + timedelta(seconds=60)

    @staticmethod
    def generate_code():
        return str(random.randint(100000, 999999))

    def __str__(self):
        return f"OTP for {self.user.username} - {self.code}"


class AdminProfile(models.Model):
    ADMIN_ROLES = [
        ('admin', 'Administrator'),
        ('manager', 'Project Manager'),
        ('supervisor', 'Site Supervisor'),
        ('staff', 'Staff'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='adminprofile')
    admin_role = models.CharField(max_length=20, choices=ADMIN_ROLES, default='staff')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    department = models.CharField(max_length=100, blank=True, null=True)
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    
    # Site Manager specific fields
    company_department = models.CharField(max_length=100, blank=True, null=True)
    
    # Blog Creator specific fields
    writing_experience = models.CharField(max_length=20, blank=True, null=True)
    portfolio_links = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=200, blank=True, null=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_admins'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
        
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_admin_role_display()}"
    
    def is_approved(self):
        return self.approval_status == 'approved'
    
    def is_account_locked(self):
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def can_login(self):
        return (
            self.user.is_active and 
            self.is_approved() and 
            not self.is_account_locked() and
            self.approval_status != 'suspended'
        )
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()


class SiteManagerProfile(models.Model):
    APPROVAL_STATUS = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sitemanagerprofile')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    department = models.CharField(max_length=100, blank=True, null=True, default='Site Management')
    employee_id = models.CharField(max_length=50, blank=True, null=True, unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(blank=True, null=True)
    company_department = models.CharField(max_length=100, blank=True, null=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(blank=True, null=True)
    
    approved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='approved_sitemanagers'
    )
    approved_at = models.DateTimeField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Manager Profile'
        verbose_name_plural = 'Site Manager Profiles'
        
    def __str__(self):
        return f"{self.user.get_full_name()} - Site Manager"
    
    def is_approved(self):
        return self.approval_status == 'approved'
    
    def is_account_locked(self):
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def can_login(self):
        return (
            self.user.is_active and 
            self.is_approved() and 
            not self.is_account_locked() and
            self.approval_status != 'suspended'
        )
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration"""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save()


class SuperAdminProfile(models.Model):
    """Profile for Django superusers."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='superadminprofile')
    title = models.CharField(max_length=100, default='Super Administrator')
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Super Admin Profile'
        verbose_name_plural = 'Super Admin Profiles'
        
    def __str__(self):
        return f"{self.user.get_full_name()} - Super Admin"


# Signal to send email notifications when approval status changes
@receiver(pre_save, sender=AdminProfile)
def track_approval_status_change(sender, instance, **kwargs):
    """Track approval status changes to send appropriate emails"""
    if instance.pk:  # Only for existing instances
        try:
            old_instance = AdminProfile.objects.get(pk=instance.pk)
            instance._old_approval_status = old_instance.approval_status
        except AdminProfile.DoesNotExist:
            instance._old_approval_status = None
    else:
        instance._old_approval_status = None


@receiver(post_save, sender=AdminProfile)
def send_approval_status_email(sender, instance, created, **kwargs):
    """Send email when approval status changes"""
    if created:
        return  # Don't send email for new profiles
    
    old_status = getattr(instance, '_old_approval_status', None)
    new_status = instance.approval_status
    
    # Only send email if status actually changed
    if old_status and old_status != new_status:
        from .utils import send_admin_approval_email, send_admin_denial_email, send_admin_suspension_email
        
        if new_status == 'approved':
            send_admin_approval_email(instance, instance.approved_by)
        elif new_status == 'denied':
            send_admin_denial_email(instance)
        elif new_status == 'suspended':
            send_admin_suspension_email(instance)


# Signal to send email notifications when SiteManager approval status changes
@receiver(pre_save, sender=SiteManagerProfile)
def track_sitemanager_approval_status_change(sender, instance, **kwargs):
    """Track approval status changes to send appropriate emails"""
    if instance.pk:  # Only for existing instances
        try:
            old_instance = SiteManagerProfile.objects.get(pk=instance.pk)
            instance._old_approval_status = old_instance.approval_status
        except SiteManagerProfile.DoesNotExist:
            instance._old_approval_status = None
    else:
        instance._old_approval_status = None


@receiver(post_save, sender=SiteManagerProfile)
def send_sitemanager_approval_status_email(sender, instance, created, **kwargs):
    """Send email when approval status changes"""
    if created:
        return  # Don't send email for new profiles
    
    old_status = getattr(instance, '_old_approval_status', None)
    new_status = instance.approval_status
    
    # Only send email if status actually changed
    if old_status and old_status != new_status:
        from .utils import send_admin_approval_email, send_admin_denial_email, send_admin_suspension_email
        
        if new_status == 'approved':
            send_admin_approval_email(instance, instance.approved_by)
        elif new_status == 'denied':
            send_admin_denial_email(instance)
        elif new_status == 'suspended':
            send_admin_suspension_email(instance)


# 🔔 Signals outside the model class - TEMPORARILY DISABLED
# @receiver(post_save, sender=User)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # Use get_or_create to prevent IntegrityError from race conditions
#         Profile.objects.get_or_create(
#             user=instance, 
#             defaults={'role': 'customer'}
#         )
#     else:
#         # Only save if profile exists
#         if hasattr(instance, 'profile'):
#             instance.profile.save()