from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Check if diary_photos bucket exists in Supabase'

    def handle(self, *args, **options):
        if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
            self.stdout.write(self.style.ERROR('Supabase credentials not configured'))
            return
        
        url = f"{settings.SUPABASE_URL}/storage/v1/bucket"
        headers = {
            'Authorization': f'Bearer {settings.SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            buckets = response.json()
            bucket_names = [bucket['name'] for bucket in buckets]
            
            if 'diary_photos' in bucket_names:
                self.stdout.write(self.style.SUCCESS('✓ diary_photos bucket exists'))
            else:
                self.stdout.write(self.style.ERROR('X diary_photos bucket not found'))
                self.stdout.write(f'Available buckets: {", ".join(bucket_names)}')
        else:
            self.stdout.write(self.style.ERROR(f'Failed to check buckets: {response.text}'))