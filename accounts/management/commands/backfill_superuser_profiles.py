"""
Management command to manually backfill superuser profiles.
This can be run manually if needed: python manage.py backfill_superuser_profiles
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import AdminProfile, SuperAdminProfile, Profile


class Command(BaseCommand):
    help = 'Backfill SuperAdminProfile for existing superusers and clean up incorrect profiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
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
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )
        
        superusers = User.objects.filter(is_superuser=True)
        
        if not superusers.exists():
            self.stdout.write(
                self.style.SUCCESS('No superusers found in the system.')
            )
            return
        
        self.stdout.write(f'Found {superusers.count()} superuser(s)')
        
        for user in superusers:
            if verbose:
                self.stdout.write(f'\nProcessing superuser: {user.username} ({user.email})')
            
            # Check for incorrect Profile records
            client_profiles = Profile.objects.filter(user=user)
            if client_profiles.exists():
                if verbose:
                    self.stdout.write(f'  - Found {client_profiles.count()} client profile(s) to remove')
                if not dry_run:
                    client_profiles.delete()
            
            # Check for incorrect AdminProfile records
            admin_profiles = AdminProfile.objects.filter(user=user)
            if admin_profiles.exists():
                if verbose:
                    self.stdout.write(f'  - Found {admin_profiles.count()} admin profile(s) to remove')
                if not dry_run:
                    admin_profiles.delete()
            
            # Ensure SuperAdminProfile exists
            super_profile, created = SuperAdminProfile.objects.get_or_create(
                user=user,
                defaults={'title': 'Super Administrator'}
            ) if not dry_run else (None, False)
            
            if dry_run:
                existing_super = SuperAdminProfile.objects.filter(user=user).exists()
                if not existing_super:
                    if verbose:
                        self.stdout.write(f'  - Would create SuperAdminProfile')
                else:
                    if verbose:
                        self.stdout.write(f'  - SuperAdminProfile already exists')
            else:
                if created:
                    if verbose:
                        self.stdout.write(f'  - Created SuperAdminProfile')
                else:
                    if verbose:
                        self.stdout.write(f'  - SuperAdminProfile already exists')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nDRY RUN COMPLETE - Run without --dry-run to apply changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nBackfill complete for {superusers.count()} superuser(s)')
            )
