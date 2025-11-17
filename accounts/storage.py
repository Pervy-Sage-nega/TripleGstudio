import os
from config.supabase_storage import SupabaseStorage
from django.conf import settings

class AdminProfileStorage(SupabaseStorage):
    def __init__(self):
        super().__init__()
        self.bucket_name = 'admin-profiles'
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"

class SiteManagerProfileStorage(SupabaseStorage):
    def __init__(self):
        super().__init__()
        self.bucket_name = 'sitemanager-profiles'
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"

class ClientProfileStorage(SupabaseStorage):
    def __init__(self):
        super().__init__()
        self.bucket_name = 'client-profiles'
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"