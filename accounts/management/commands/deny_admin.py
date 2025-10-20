from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import AdminProfile


class Command(BaseCommand):
    help = 'Deny pending admin accounts'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of admin to deny')
        parser.add_argument('--reason', type=str, help='Reason for denial (optional)')
        parser.add_argument('--delete-user', action='store_true', help='Delete the user account entirely')

    @transaction.atomic
    def handle(self, *args, **options):
        if not options['email']:
            self.stdout.write(
                self.style.ERROR('Please specify --email of the admin to deny')
            )
            return

        email = options['email']
        reason = options.get('reason', 'Your admin account application has been reviewed and denied.')
        delete_user = options.get('delete_user', False)

        try:
            user = User.objects.get(email=email, is_staff=True)
            admin_profile = user.admin_profile
            
            if admin_profile.approval_status == 'denied':
                self.stdout.write(
                    self.style.WARNING(f'Admin {email} is already denied.')
                )
                return

            if admin_profile.approval_status == 'approved':
                self.stdout.write(
                    self.style.ERROR(f'Cannot deny approved admin {email}. Use suspend command instead.')
                )
                return

            # Send denial email before deleting
            try:
                send_mail(
                    'Admin Account Application - Triple G BuildHub',
                    f'Thank you for your interest in joining Triple G BuildHub as an admin.\n\n'
                    f'After careful review, we regret to inform you that your admin account application has been denied.\n\n'
                    f'Reason: {reason}\n\n'
                    f'If you believe this is an error or have questions, please contact our support team.\n\n'
                    f'Thank you for your understanding.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                email_sent = True
            except Exception as e:
                email_sent = False
                self.stdout.write(
                    self.style.WARNING(f'Email notification failed: {e}')
                )

            if delete_user:
                # Delete the entire user account
                user_name = user.get_full_name()
                user.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Admin application for {user_name} ({email}) denied and user account deleted.'
                    )
                )
            else:
                # Just mark as denied
                admin_profile.approval_status = 'denied'
                admin_profile.save()
                
                # Deactivate user account
                user.is_active = False
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Admin {user.get_full_name()} ({email}) denied and deactivated.'
                    )
                )

            if email_sent:
                self.stdout.write('  Email notification sent.')
            
            self.stdout.write(f'  Reason: {reason}')

        except User.DoesNotExist:
            raise CommandError(f'Admin user with email {email} not found.')
        except AdminProfile.DoesNotExist:
            raise CommandError(f'Admin profile for {email} not found.')
