import os
from config.supabase_storage import SupabaseStorage
from django.conf import settings

class PortfolioSupabaseStorage(SupabaseStorage):
    def __init__(self):
        super().__init__()
        self.bucket_name = settings.SUPABASE_PORTFOLIO_BUCKET
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"
