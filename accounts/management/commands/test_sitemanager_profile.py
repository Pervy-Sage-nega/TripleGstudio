from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import SiteManagerProfile

class Command(BaseCommand):
    help = 'Test SiteManagerProfile database operations'

    def handle(self, *args, **options):
        self.stdout.write('Testing SiteManagerProfile database operations...')
        
        # Find a site manager user
        site_managers = SiteManagerProfile.objects.all()
        self.stdout.write(f'Found {site_managers.count()} site manager profiles')
        
        for profile in site_managers:
            self.stdout.write(f'Site Manager: {profile.user.username}')
            self.stdout.write(f'  - Phone: {profile.phone}')
            self.stdout.write(f'  - Emergency Contact: {profile.emergency_contact}')
            self.stdout.write(f'  - Profile Pic: {profile.profile_pic}')
            self.stdout.write(f'  - Department: {profile.department}')
            self.stdout.write('---')
        
        # Test saving data
        if site_managers.exists():
            test_profile = site_managers.first()
            original_phone = test_profile.phone
            
            # Test update
            test_profile.phone = 'TEST-123-456'
            test_profile.save()
            
            # Verify update
            test_profile.refresh_from_db()
            if test_profile.phone == 'TEST-123-456':
                self.stdout.write(self.style.SUCCESS('✅ Database save/update working correctly'))
            else:
                self.stdout.write(self.style.ERROR('❌ Database save/update failed'))
            
            # Restore original value
            test_profile.phone = original_phone
            test_profile.save()
            
        self.stdout.write('Test completed.')
