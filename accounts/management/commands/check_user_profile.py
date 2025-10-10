from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile

class Command(BaseCommand):
    help = 'Check specific user profile details'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to check')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f"=== USER DETAILS ===")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Active: {user.is_active}")
            self.stdout.write(f"Staff: {user.is_staff}")
            self.stdout.write(f"Superuser: {user.is_superuser}")
            
            # Check if hasattr works
            has_admin_attr = hasattr(user, 'admin_profile')
            self.stdout.write(f"hasattr(user, 'admin_profile'): {has_admin_attr}")
            
            # Try to access admin_profile directly
            try:
                admin_profile = user.admin_profile
                self.stdout.write(f"Direct access successful: {admin_profile}")
                self.stdout.write(f"Admin Role: {admin_profile.admin_role}")
                self.stdout.write(f"Approval Status: {admin_profile.approval_status}")
            except Exception as e:
                self.stdout.write(f"Direct access failed: {e}")
            
            # Check AdminProfile table directly
            admin_profiles = AdminProfile.objects.filter(user=user)
            self.stdout.write(f"AdminProfile count for user: {admin_profiles.count()}")
            
            for ap in admin_profiles:
                self.stdout.write(f"Found AdminProfile: Role={ap.admin_role}, Status={ap.approval_status}")
                
        except User.DoesNotExist:
            self.stdout.write(f"User with email {email} not found")
        except Exception as e:
            self.stdout.write(f"Error: {e}")
