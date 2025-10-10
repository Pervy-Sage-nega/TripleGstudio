from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import AdminProfile


class Command(BaseCommand):
    help = 'List admin accounts with various filters'

    def add_arguments(self, parser):
        parser.add_argument('--status', type=str, choices=['pending', 'approved', 'denied', 'suspended'], 
                          help='Filter by approval status')
        parser.add_argument('--role', type=str, choices=['admin', 'manager', 'supervisor', 'staff'],
                          help='Filter by admin role')
        parser.add_argument('--locked', action='store_true', help='Show only locked accounts')
        parser.add_argument('--detailed', action='store_true', help='Show detailed information')

    def handle(self, *args, **options):
        # Build queryset
        queryset = AdminProfile.objects.select_related('user', 'approved_by').all()
        
        # Apply filters
        if options['status']:
            queryset = queryset.filter(approval_status=options['status'])
        
        if options['role']:
            queryset = queryset.filter(admin_role=options['role'])
        
        if options['locked']:
            now = timezone.now()
            queryset = queryset.filter(account_locked_until__gt=now)
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        if not queryset.exists():
            self.stdout.write(self.style.SUCCESS('No admin accounts found matching the criteria.'))
            return
        
        # Display results
        self.stdout.write(self.style.SUCCESS(f'Found {queryset.count()} admin account(s):'))
        self.stdout.write('')
        
        for admin_profile in queryset:
            user = admin_profile.user
            
            # Basic info
            status_color = self.get_status_color(admin_profile.approval_status)
            self.stdout.write(
                f'• {user.get_full_name()} ({user.email}) - '
                f'{status_color(admin_profile.get_approval_status_display())}'
            )
            
            if options['detailed']:
                self.show_detailed_info(admin_profile)
            else:
                self.show_basic_info(admin_profile)
            
            self.stdout.write('')

    def show_basic_info(self, admin_profile):
        """Show basic admin information"""
        user = admin_profile.user
        
        self.stdout.write(f'  Role: {admin_profile.get_admin_role_display()}')
        if admin_profile.department:
            self.stdout.write(f'  Department: {admin_profile.department}')
        
        self.stdout.write(f'  Active: {"Yes" if user.is_active else "No"}')
        self.stdout.write(f'  Registered: {admin_profile.created_at.strftime("%Y-%m-%d %H:%M")}')
        
        if admin_profile.is_account_locked():
            self.stdout.write(
                self.style.ERROR(f'  🔒 LOCKED until {admin_profile.account_locked_until.strftime("%Y-%m-%d %H:%M")}')
            )

    def show_detailed_info(self, admin_profile):
        """Show detailed admin information"""
        user = admin_profile.user
        
        self.stdout.write(f'  Role: {admin_profile.get_admin_role_display()}')
        self.stdout.write(f'  Department: {admin_profile.department or "Not specified"}')
        self.stdout.write(f'  Employee ID: {admin_profile.employee_id or "Not specified"}')
        self.stdout.write(f'  Phone: {admin_profile.phone or "Not specified"}')
        self.stdout.write(f'  Emergency Contact: {admin_profile.emergency_contact or "Not specified"}')
        
        if admin_profile.hire_date:
            self.stdout.write(f'  Hire Date: {admin_profile.hire_date.strftime("%Y-%m-%d")}')
        
        self.stdout.write(f'  Active: {"Yes" if user.is_active else "No"}')
        self.stdout.write(f'  Last Login: {user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Never"}')
        
        if admin_profile.last_login_ip:
            self.stdout.write(f'  Last Login IP: {admin_profile.last_login_ip}')
        
        self.stdout.write(f'  Failed Login Attempts: {admin_profile.failed_login_attempts}')
        
        if admin_profile.is_account_locked():
            self.stdout.write(
                self.style.ERROR(f'  🔒 LOCKED until {admin_profile.account_locked_until.strftime("%Y-%m-%d %H:%M")}')
            )
        
        self.stdout.write(f'  Registered: {admin_profile.created_at.strftime("%Y-%m-%d %H:%M")}')
        self.stdout.write(f'  Last Updated: {admin_profile.updated_at.strftime("%Y-%m-%d %H:%M")}')
        
        if admin_profile.approved_by:
            self.stdout.write(f'  Approved By: {admin_profile.approved_by.get_full_name()}')
            if admin_profile.approved_at:
                self.stdout.write(f'  Approved At: {admin_profile.approved_at.strftime("%Y-%m-%d %H:%M")}')

    def get_status_color(self, status):
        """Get appropriate color styling for status"""
        colors = {
            'pending': self.style.WARNING,
            'approved': self.style.SUCCESS,
            'denied': self.style.ERROR,
            'suspended': self.style.ERROR,
        }
        return colors.get(status, self.style.NOTICE)
