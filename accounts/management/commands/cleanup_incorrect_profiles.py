from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, AdminProfile, SiteManagerProfile, SuperAdminProfile


class Command(BaseCommand):
    help = 'Remove incorrect client profiles from Admin and Site Manager users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS('🔍 Scanning for incorrect client profiles...'))
        
        # Find users who have both client profiles AND admin/sitemanager profiles
        incorrect_profiles = []
        
        # Check Admin users with client profiles
        admin_users = User.objects.filter(adminprofile__isnull=False)
        for user in admin_users:
            if hasattr(user, 'profile'):
                incorrect_profiles.append({
                    'user': user,
                    'profile_type': 'Client Profile',
                    'correct_type': 'Admin Profile',
                    'profile': user.profile
                })
        
        # Check Site Manager users with client profiles
        sitemanager_users = User.objects.filter(sitemanagerprofile__isnull=False)
        for user in sitemanager_users:
            if hasattr(user, 'profile'):
                incorrect_profiles.append({
                    'user': user,
                    'profile_type': 'Client Profile',
                    'correct_type': 'Site Manager Profile',
                    'profile': user.profile
                })
        
        # Check Super Admin users with client profiles
        superadmin_users = User.objects.filter(superadminprofile__isnull=False)
        for user in superadmin_users:
            if hasattr(user, 'profile'):
                incorrect_profiles.append({
                    'user': user,
                    'profile_type': 'Client Profile',
                    'correct_type': 'Super Admin Profile',
                    'profile': user.profile
                })
        
        if not incorrect_profiles:
            self.stdout.write(self.style.SUCCESS('✅ No incorrect profiles found!'))
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  Found {len(incorrect_profiles)} incorrect client profiles:')
        )
        
        for item in incorrect_profiles:
            user = item['user']
            self.stdout.write(
                f"   • {user.email} ({user.get_full_name()}) - "
                f"Has {item['profile_type']} but should only have {item['correct_type']}"
            )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 DRY RUN - No profiles were deleted. Run without --dry-run to apply changes.')
            )
            return
        
        # Delete incorrect profiles
        deleted_count = 0
        for item in incorrect_profiles:
            try:
                item['profile'].delete()
                deleted_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"   ✅ Deleted client profile for {item['user'].email}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"   ❌ Failed to delete profile for {item['user'].email}: {e}")
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Successfully cleaned up {deleted_count} incorrect profiles!')
        )
        
        # Verify cleanup
        remaining_issues = []
        for user_type, users in [
            ('Admin', admin_users),
            ('Site Manager', sitemanager_users), 
            ('Super Admin', superadmin_users)
        ]:
            for user in users:
                if hasattr(user, 'profile'):
                    remaining_issues.append(f"{user.email} ({user_type})")
        
        if remaining_issues:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Still have issues with: {", ".join(remaining_issues)}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All profile conflicts resolved!')
            )
