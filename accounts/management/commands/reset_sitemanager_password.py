from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile

class Command(BaseCommand):
    help = 'Reset site manager password for testing'

    def handle(self, *args, **options):
        try:
            # Get site manager
            sm = AdminProfile.objects.filter(admin_role='site_manager').first()
            if sm:
                user = sm.user
                # Set password to 'test123'
                user.set_password('test123')
                user.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Password reset for {user.email} to "test123"')
                )
                
                # Test authentication
                from django.contrib.auth import authenticate
                auth_result = authenticate(username=user.username, password='test123')
                if auth_result:
                    self.stdout.write(
                        self.style.SUCCESS('Authentication test: SUCCESS')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('Authentication test: FAILED')
                    )
            else:
                self.stdout.write(
                    self.style.ERROR('No site manager found')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
