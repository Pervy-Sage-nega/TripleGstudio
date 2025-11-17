from django.core.management.base import BaseCommand
from accounts.models import AdminProfile

class Command(BaseCommand):
    help = 'Test admin profile image URLs'

    def handle(self, *args, **options):
        self.stdout.write('Testing admin profile images...')
        
        for profile in AdminProfile.objects.all():
            self.stdout.write(f'\nAdmin: {profile.user.get_full_name()}')
            
            if profile.profile_pic:
                self.stdout.write(f'  Profile pic field: {profile.profile_pic.name}')
                self.stdout.write(f'  Profile pic URL: {profile.profile_pic.url}')
                self.stdout.write(f'  get_profile_image_url(): {profile.get_profile_image_url()}')
                
                # Check if it's Supabase URL
                if 'supabase.co' in profile.profile_pic.url:
                    self.stdout.write(self.style.SUCCESS('  ✓ Using Supabase storage'))
                else:
                    self.stdout.write(self.style.WARNING('  ⚠ Using local storage'))
            else:
                self.stdout.write('  No profile picture')
                self.stdout.write(f'  get_profile_image_url(): {profile.get_profile_image_url()}')