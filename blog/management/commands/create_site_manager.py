from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import SiteManagerProfile

class Command(BaseCommand):
    help = 'Create site manager account'

    def handle(self, *args, **options):
        email = 'rideouts200221@gmail.com'
        password = 'Ernesto!@#'
        
        # Create user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': 'Site',
                'last_name': 'Manager',
                'is_staff': True,
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(f'Created user: {email}')
        else:
            self.stdout.write(f'User already exists: {email}')
        
        # Create site manager profile
        profile, created = SiteManagerProfile.objects.get_or_create(
            user=user,
            defaults={
                'approval_status': 'approved',
                'phone': '+1234567890',
                'department': 'Site Management',
            }
        )
        
        if created:
            self.stdout.write('Created site manager profile')
        else:
            self.stdout.write('Site manager profile already exists')
        
        self.stdout.write(self.style.SUCCESS('Site manager account ready'))