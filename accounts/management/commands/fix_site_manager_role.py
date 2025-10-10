from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile

class Command(BaseCommand):
    help = 'Fix site manager admin role'

    def handle(self, *args, **options):
        try:
            # Get user
            user = User.objects.get(email='rideouts191@gmail.com')
            self.stdout.write(f"Found user: {user.email}")
            
            # Get AdminProfile
            admin_profile = AdminProfile.objects.get(user=user)
            self.stdout.write(f"Current admin role: {admin_profile.admin_role}")
            self.stdout.write(f"Current approval status: {admin_profile.approval_status}")
            
            # Update to site_manager
            admin_profile.admin_role = 'site_manager'
            admin_profile.approval_status = 'approved'
            admin_profile.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated {user.email} to site_manager role with approved status')
            )
            
            # Test hasattr
            self.stdout.write(f'hasattr test: {hasattr(user, "adminprofile")}')
            
            # Refresh from database
            user.refresh_from_db()
            admin_profile.refresh_from_db()
            
            self.stdout.write(f'Final admin role: {admin_profile.admin_role}')
            self.stdout.write(f'Final approval status: {admin_profile.approval_status}')
            
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('User not found'))
        except AdminProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR('AdminProfile not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
