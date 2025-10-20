from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import AdminProfile


class Command(BaseCommand):
    help = 'Approve pending admin accounts'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of admin to approve')
        parser.add_argument('--all-pending', action='store_true', help='Approve all pending admins')
        parser.add_argument('--list-pending', action='store_true', help='List all pending admins')
        parser.add_argument('--approver-email', type=str, help='Email of the approving superuser')

    @transaction.atomic
    def handle(self, *args, **options):
        if options['list_pending']:
            self.list_pending_admins()
            return

        if options['all_pending']:
            self.approve_all_pending(options.get('approver_email'))
            return

        if options['email']:
            self.approve_single_admin(options['email'], options.get('approver_email'))
            return

        self.stdout.write(
            self.style.ERROR('Please specify --email, --all-pending, or --list-pending')
        )

    def list_pending_admins(self):
        """List all pending admin accounts"""
        pending_admins = AdminProfile.objects.filter(
            approval_status='pending'
        ).select_related('user')

        if not pending_admins.exists():
            self.stdout.write(self.style.SUCCESS('No pending admin accounts found.'))
            return

        self.stdout.write(self.style.WARNING(f'Found {pending_admins.count()} pending admin accounts:'))
        self.stdout.write('')
        
        for admin_profile in pending_admins:
            user = admin_profile.user
            self.stdout.write(f'  • {user.get_full_name()} ({user.email})')
            self.stdout.write(f'    Role: {admin_profile.get_admin_role_display()}')
            self.stdout.write(f'    Department: {admin_profile.department or "Not specified"}')
            self.stdout.write(f'    Employee ID: {admin_profile.employee_id or "Not specified"}')
            self.stdout.write(f'    Registered: {admin_profile.created_at.strftime("%Y-%m-%d %H:%M")}')
            self.stdout.write('')

    def approve_single_admin(self, email, approver_email=None):
        """Approve a single admin account"""
        try:
            user = User.objects.get(email=email, is_staff=True)
            admin_profile = user.admin_profile
            
            if admin_profile.approval_status == 'approved':
                self.stdout.write(
                    self.style.WARNING(f'Admin {email} is already approved.')
                )
                return

            # Get approver
            approver = None
            if approver_email:
                try:
                    approver = User.objects.get(email=approver_email, is_superuser=True)
                except User.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Approver {approver_email} not found or not a superuser.')
                    )
                    return

            # Approve the admin
            admin_profile.approval_status = 'approved'
            admin_profile.approved_by = approver
            admin_profile.approved_at = timezone.now()
            admin_profile.save()

            # Send approval email
            try:
                send_mail(
                    'Admin Account Approved - Triple G BuildHub',
                    f'Congratulations! Your admin account has been approved.\n\n'
                    f'You can now log in to the admin panel at: {settings.SITE_URL}/accounts/admin-auth/login/\n\n'
                    f'Your account details:\n'
                    f'- Name: {user.get_full_name()}\n'
                    f'- Email: {user.email}\n'
                    f'- Role: {admin_profile.get_admin_role_display()}\n'
                    f'- Department: {admin_profile.department or "Not specified"}\n\n'
                    f'Welcome to the Triple G BuildHub team!',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                email_sent = False
                self.stdout.write(
                    self.style.WARNING(f'Admin approved but email failed to send: {e}')
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Admin {user.get_full_name()} ({email}) approved successfully!'
                )
            )
            
            if email_sent:
                self.stdout.write('  Email notification sent.')
            
            if approver:
                self.stdout.write(f'  Approved by: {approver.get_full_name()}')

        except User.DoesNotExist:
            raise CommandError(f'Admin user with email {email} not found.')
        except AdminProfile.DoesNotExist:
            raise CommandError(f'Admin profile for {email} not found.')

    def approve_all_pending(self, approver_email=None):
        """Approve all pending admin accounts"""
        pending_admins = AdminProfile.objects.filter(
            approval_status='pending'
        ).select_related('user')

        if not pending_admins.exists():
            self.stdout.write(self.style.SUCCESS('No pending admin accounts to approve.'))
            return

        # Get approver
        approver = None
        if approver_email:
            try:
                approver = User.objects.get(email=approver_email, is_superuser=True)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Approver {approver_email} not found or not a superuser.')
                )
                return

        approved_count = 0
        failed_emails = []

        for admin_profile in pending_admins:
            user = admin_profile.user
            
            # Approve the admin
            admin_profile.approval_status = 'approved'
            admin_profile.approved_by = approver
            admin_profile.approved_at = timezone.now()
            admin_profile.save()

            # Send approval email
            try:
                send_mail(
                    'Admin Account Approved - Triple G BuildHub',
                    f'Congratulations! Your admin account has been approved.\n\n'
                    f'You can now log in to the admin panel.\n\n'
                    f'Your account details:\n'
                    f'- Name: {user.get_full_name()}\n'
                    f'- Email: {user.email}\n'
                    f'- Role: {admin_profile.get_admin_role_display()}\n\n'
                    f'Welcome to the Triple G BuildHub team!',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                failed_emails.append(f'{user.email}: {e}')

            approved_count += 1
            self.stdout.write(f'  ✓ {user.get_full_name()} ({user.email})')

        self.stdout.write('')
        self.stdout.write(
            self.style.SUCCESS(f'Successfully approved {approved_count} admin accounts!')
        )

        if failed_emails:
            self.stdout.write(self.style.WARNING('Email notifications failed for:'))
            for failed in failed_emails:
                self.stdout.write(f'  • {failed}')

        if approver:
            self.stdout.write(f'All approvals by: {approver.get_full_name()}')
