from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile

class Command(BaseCommand):
    help = 'Check admin user access for blog management'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to check')

    def handle(self, *args, **options):
        username = options['username']
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f"\n=== USER DETAILS ==="))
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Email: {user.email}")
            self.stdout.write(f"Active: {user.is_active}")
            self.stdout.write(f"Staff: {user.is_staff}")
            self.stdout.write(f"Superuser: {user.is_superuser}")
            
            # Check adminprofile (correct related_name)
            self.stdout.write(self.style.SUCCESS(f"\n=== ADMIN PROFILE CHECK ==="))
            has_adminprofile = hasattr(user, 'adminprofile')
            self.stdout.write(f"hasattr(user, 'adminprofile'): {has_adminprofile}")
            
            if has_adminprofile:
                try:
                    admin_profile = user.adminprofile
                    self.stdout.write(self.style.SUCCESS(f"✓ AdminProfile found!"))
                    self.stdout.write(f"  Admin Role: {admin_profile.admin_role}")
                    self.stdout.write(f"  Approval Status: {admin_profile.approval_status}")
                    self.stdout.write(f"  Email Verified: {admin_profile.email_verified}")
                    self.stdout.write(f"  Account Locked: {admin_profile.is_account_locked()}")
                    self.stdout.write(f"  Can Login: {admin_profile.can_login()}")
                    
                    # Check if role is in allowed list
                    allowed_roles = ['admin', 'manager', 'supervisor', 'staff']
                    role_allowed = admin_profile.admin_role in allowed_roles
                    self.stdout.write(f"  Role in allowed list: {role_allowed}")
                    
                    # Final access check
                    self.stdout.write(self.style.SUCCESS(f"\n=== ACCESS CHECK ==="))
                    if user.is_superuser:
                        self.stdout.write(self.style.SUCCESS("✓ SUPERUSER - Access granted"))
                    elif (admin_profile.approval_status == 'approved' and 
                          admin_profile.admin_role in allowed_roles and
                          admin_profile.can_login()):
                        self.stdout.write(self.style.SUCCESS("✓ ADMIN PROFILE - Access granted"))
                    else:
                        self.stdout.write(self.style.ERROR("✗ ACCESS DENIED"))
                        if admin_profile.approval_status != 'approved':
                            self.stdout.write(f"  Reason: Approval status is '{admin_profile.approval_status}' (needs 'approved')")
                        if admin_profile.admin_role not in allowed_roles:
                            self.stdout.write(f"  Reason: Role is '{admin_profile.admin_role}' (needs admin/manager/supervisor)")
                        if not admin_profile.can_login():
                            self.stdout.write(f"  Reason: can_login() returned False")
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Error accessing adminprofile: {e}"))
            else:
                self.stdout.write(self.style.WARNING("✗ No AdminProfile found for this user"))
                
            # Check SiteManagerProfile
            self.stdout.write(self.style.SUCCESS(f"\n=== SITE MANAGER PROFILE CHECK ==="))
            has_sitemanagerprofile = hasattr(user, 'sitemanagerprofile')
            self.stdout.write(f"hasattr(user, 'sitemanagerprofile'): {has_sitemanagerprofile}")
            
            if has_sitemanagerprofile:
                site_manager = user.sitemanagerprofile
                self.stdout.write(f"  Approval Status: {site_manager.approval_status}")
                self.stdout.write(f"  Can Login: {site_manager.can_login()}")
                
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User '{username}' not found"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            import traceback
            traceback.print_exc()
