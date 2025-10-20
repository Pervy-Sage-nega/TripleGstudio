from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.utils import get_user_role

class Command(BaseCommand):
    help = 'Check user role and profile status'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='User email to check')

    def handle(self, *args, **options):
        email = options['email']
        
        try:
            user = User.objects.get(email=email)
            role = get_user_role(user)
            
            self.stdout.write(f"User: {user.username} ({user.email})")
            self.stdout.write(f"Role: {role}")
            self.stdout.write(f"Is Active: {user.is_active}")
            self.stdout.write(f"Is Staff: {user.is_staff}")
            self.stdout.write(f"Is Superuser: {user.is_superuser}")
            
            # Check profiles
            if hasattr(user, 'sitemanagerprofile'):
                profile = user.sitemanagerprofile
                self.stdout.write(f"Site Manager Profile:")
                self.stdout.write(f"  - Approval Status: {profile.approval_status}")
                self.stdout.write(f"  - Can Login: {profile.can_login()}")
                self.stdout.write(f"  - Is Approved: {profile.is_approved()}")
                self.stdout.write(f"  - Is Account Locked: {profile.is_account_locked()}")
            
            if hasattr(user, 'adminprofile'):
                profile = user.adminprofile
                self.stdout.write(f"Admin Profile:")
                self.stdout.write(f"  - Admin Role: {profile.admin_role}")
                self.stdout.write(f"  - Approval Status: {profile.approval_status}")
                self.stdout.write(f"  - Can Login: {profile.can_login()}")
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with email {email} not found'))