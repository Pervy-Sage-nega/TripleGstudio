from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import AdminProfile


class Command(BaseCommand):
    help = 'Suspend or unsuspend admin accounts'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of admin to suspend/unsuspend')
        parser.add_argument('--unsuspend', action='store_true', help='Unsuspend the admin account')
        parser.add_argument('--reason', type=str, help='Reason for suspension (optional)')

    @transaction.atomic
    def handle(self, *args, **options):
        if not options['email']:
            self.stdout.write(
                self.style.ERROR('Please specify --email of the admin to suspend/unsuspend')
            )
            return

        email = options['email']
        unsuspend = options.get('unsuspend', False)
        reason = options.get('reason', 'Your admin account has been suspended.')

        try:
            user = User.objects.get(email=email, is_staff=True)
            admin_profile = user.admin_profile
            
            if unsuspend:
                if admin_profile.approval_status != 'suspended':
                    self.stdout.write(
                        self.style.WARNING(f'Admin {email} is not currently suspended.')
                    )
                    return

                # Unsuspend the admin
                admin_profile.approval_status = 'approved'
                admin_profile.failed_login_attempts = 0  # Reset failed attempts
                admin_profile.account_locked_until = None  # Remove any locks
                admin_profile.save()

                # Reactivate user account
                user.is_active = True
                user.save()

                # Send unsuspension email
                try:
                    send_mail(
                        'Admin Account Reactivated - Triple G BuildHub',
                        f'Good news! Your admin account has been reactivated.\n\n'
                        f'You can now log in to the admin panel again.\n\n'
                        f'Your account details:\n'
                        f'- Name: {user.get_full_name()}\n'
                        f'- Email: {user.email}\n'
                        f'- Role: {admin_profile.get_admin_role_display()}\n\n'
                        f'Welcome back to the Triple G BuildHub team!',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    email_sent = True
                except Exception as e:
                    email_sent = False
                    self.stdout.write(
                        self.style.WARNING(f'Admin unsuspended but email failed to send: {e}')
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Admin {user.get_full_name()} ({email}) unsuspended successfully!'
                    )
                )

            else:
                if admin_profile.approval_status == 'suspended':
                    self.stdout.write(
                        self.style.WARNING(f'Admin {email} is already suspended.')
                    )
                    return

                if admin_profile.approval_status != 'approved':
                    self.stdout.write(
                        self.style.ERROR(f'Cannot suspend admin {email} - account is not approved.')
                    )
                    return

                # Suspend the admin
                admin_profile.approval_status = 'suspended'
                admin_profile.save()

                # Deactivate user account
                user.is_active = False
                user.save()

                # Send suspension email
                try:
                    send_mail(
                        'Admin Account Suspended - Triple G BuildHub',
                        f'We regret to inform you that your admin account has been suspended.\n\n'
                        f'Reason: {reason}\n\n'
                        f'Your access to the admin panel has been temporarily revoked. '
                        f'If you believe this is an error or have questions, please contact our support team.\n\n'
                        f'Account details:\n'
                        f'- Name: {user.get_full_name()}\n'
                        f'- Email: {user.email}\n'
                        f'- Role: {admin_profile.get_admin_role_display()}',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    email_sent = True
                except Exception as e:
                    email_sent = False
                    self.stdout.write(
                        self.style.WARNING(f'Admin suspended but email failed to send: {e}')
                    )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Admin {user.get_full_name()} ({email}) suspended successfully!'
                    )
                )

            if email_sent:
                self.stdout.write('  Email notification sent.')
            
            if not unsuspend:
                self.stdout.write(f'  Reason: {reason}')

        except User.DoesNotExist:
            raise CommandError(f'Admin user with email {email} not found.')
        except AdminProfile.DoesNotExist:
            raise CommandError(f'Admin profile for {email} not found.')
