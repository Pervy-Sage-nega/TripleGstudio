import os
import requests
from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible
from urllib.parse import urljoin

@deconstructible
class SupabaseStorage(Storage):
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_KEY'))
        self.bucket_name = os.getenv('SUPABASE_BUCKET', 'project-images')
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"
        
    def _save(self, name, content):
        # Convert Windows backslashes to forward slashes for Supabase
        name = name.replace('\\', '/')
        
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
        headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': content.content_type if hasattr(content, 'content_type') else 'application/octet-stream'
        }
        
        response = requests.post(url, headers=headers, data=content.read())
        
        if response.status_code in [200, 201]:
            return name
        else:
            raise Exception(f"Failed to upload to Supabase: {response.text}")
    
    def url(self, name):
        # Convert Windows backslashes to forward slashes
        name = name.replace('\\', '/')
        return urljoin(self.base_url, name)
    
    def exists(self, name):
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
        headers = {'Authorization': f'Bearer {self.supabase_key}'}
        response = requests.head(url, headers=headers)
        return response.status_code == 200
    
    def delete(self, name):
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
        headers = {'Authorization': f'Bearer {self.supabase_key}'}
        requests.delete(url, headers=headers)
    
    def size(self, name):
        url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{name}"
        headers = {'Authorization': f'Bearer {self.supabase_key}'}
        response = requests.head(url, headers=headers)
        return int(response.headers.get('Content-Length', 0))
