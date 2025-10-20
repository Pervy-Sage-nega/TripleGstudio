from django.core.management.base import BaseCommand
from blog.models import BlogPost
from django.contrib.auth.models import User
from accounts.models import SiteManagerProfile

class Command(BaseCommand):
    help = 'Delete all blog posts and site manager account'

    def handle(self, *args, **options):
        # Delete all blog posts
        count = BlogPost.objects.count()
        BlogPost.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} blog posts'))
        
        # Delete site manager account
        try:
            user = User.objects.get(email='rideouts200221@gmail.com')
            user.delete()
            self.stdout.write(self.style.SUCCESS('Deleted site manager account'))
        except User.DoesNotExist:
            self.stdout.write('Site manager account not found')