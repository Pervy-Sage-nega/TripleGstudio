from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile, SiteManagerProfile, AdminProfile


class Command(BaseCommand):
    help = 'Remove duplicate profiles - keeps highest privilege profile (Admin > Site Manager > Client)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        total_deleted = 0
        
        # 1. Remove client profiles for users who have admin profiles
        admin_users = AdminProfile.objects.select_related('user').all()
        admin_client_profiles = []
        
        for admin_profile in admin_users:
            try:
                client_profile = Profile.objects.get(user=admin_profile.user)
                admin_client_profiles.append(client_profile)
                if verbose:
                    self.stdout.write(f'Found admin user with client profile: {admin_profile.user.email}')
            except Profile.DoesNotExist:
                continue
        
        if admin_client_profiles:
            if not dry_run:
                deleted_count = len(admin_client_profiles)
                Profile.objects.filter(id__in=[p.id for p in admin_client_profiles]).delete()
                total_deleted += deleted_count
                self.stdout.write(
                    self.style.SUCCESS(f'Removed {deleted_count} client profiles for admin users')
                )
            else:
                self.stdout.write(f'Would remove {len(admin_client_profiles)} client profiles for admin users')
        
        # 2. Remove client profiles for users who have site manager profiles
        sm_users = SiteManagerProfile.objects.select_related('user').all()
        sm_client_profiles = []
        
        for sm_profile in sm_users:
            try:
                client_profile = Profile.objects.get(user=sm_profile.user)
                sm_client_profiles.append(client_profile)
                if verbose:
                    self.stdout.write(f'Found site manager with client profile: {sm_profile.user.email}')
            except Profile.DoesNotExist:
                continue
        
        if sm_client_profiles:
            if not dry_run:
                deleted_count = len(sm_client_profiles)
                Profile.objects.filter(id__in=[p.id for p in sm_client_profiles]).delete()
                total_deleted += deleted_count
                self.stdout.write(
                    self.style.SUCCESS(f'Removed {deleted_count} client profiles for site manager users')
                )
            else:
                self.stdout.write(f'Would remove {len(sm_client_profiles)} client profiles for site manager users')
        
        # 3. Remove site manager profiles for users who have admin profiles
        admin_sm_profiles = []
        
        for admin_profile in admin_users:
            try:
                sm_profile = SiteManagerProfile.objects.get(user=admin_profile.user)
                admin_sm_profiles.append(sm_profile)
                if verbose:
                    self.stdout.write(f'Found admin user with site manager profile: {admin_profile.user.email}')
            except SiteManagerProfile.DoesNotExist:
                continue
        
        if admin_sm_profiles:
            if not dry_run:
                deleted_count = len(admin_sm_profiles)
                SiteManagerProfile.objects.filter(id__in=[p.id for p in admin_sm_profiles]).delete()
                total_deleted += deleted_count
                self.stdout.write(
                    self.style.SUCCESS(f'Removed {deleted_count} site manager profiles for admin users')
                )
            else:
                self.stdout.write(f'Would remove {len(admin_sm_profiles)} site manager profiles for admin users')
        
        # 4. Summary
        if dry_run:
            total_would_delete = len(admin_client_profiles) + len(sm_client_profiles) + len(admin_sm_profiles)
            if total_would_delete == 0:
                self.stdout.write(self.style.SUCCESS('No duplicate profiles found!'))
            else:
                self.stdout.write(
                    self.style.WARNING(f'Would remove {total_would_delete} duplicate profiles in total')
                )
                self.stdout.write('Run without --dry-run to apply changes')
        else:
            if total_deleted == 0:
                self.stdout.write(self.style.SUCCESS('No duplicate profiles found!'))
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully cleaned up {total_deleted} duplicate profiles!')
                )
        
        # 5. Show current profile counts
        client_count = Profile.objects.count()
        admin_count = AdminProfile.objects.count()
        sm_count = SiteManagerProfile.objects.count()
        
        self.stdout.write('\nCurrent profile counts:')
        self.stdout.write(f'  Client Profiles: {client_count}')
        self.stdout.write(f'  Admin Profiles: {admin_count}')
        self.stdout.write(f'  Site Manager Profiles: {sm_count}')
