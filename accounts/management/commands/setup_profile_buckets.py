from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Setup Supabase storage buckets for profile images'

    def handle(self, *args, **options):
        if not (settings.SUPABASE_URL and settings.SUPABASE_KEY):
            self.stdout.write(self.style.ERROR('Supabase credentials not configured'))
            return
        
        buckets_to_create = [
            'admin-profiles',
            'sitemanager-profiles', 
            'client-profiles'
        ]
        
        for bucket_name in buckets_to_create:
            self.create_bucket(bucket_name)

    def create_bucket(self, bucket_name):
        """Create a Supabase storage bucket if it doesn't exist"""
        url = f"{settings.SUPABASE_URL}/storage/v1/bucket"
        service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', settings.SUPABASE_KEY)
        headers = {
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json'
        }
        
        # Check if bucket exists
        list_url = f"{settings.SUPABASE_URL}/storage/v1/bucket"
        response = requests.get(list_url, headers=headers)
        
        if response.status_code == 200:
            existing_buckets = [bucket['name'] for bucket in response.json()]
            if bucket_name in existing_buckets:
                self.stdout.write(f'  ✓ Bucket "{bucket_name}" already exists')
                return
        
        # Create bucket
        data = {
            'name': bucket_name,
            'public': True,
            'file_size_limit': 10485760,  # 10MB
            'allowed_mime_types': ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Created bucket "{bucket_name}"'))
        else:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Failed to create bucket "{bucket_name}": {response.text}')
            )