from config.supabase_storage import SupabaseStorage
from django.conf import settings


class BlogSupabaseStorage(SupabaseStorage):
    """Supabase storage backend for blog images"""
    bucket_name = settings.SUPABASE_BLOG_BUCKET
