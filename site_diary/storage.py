from config.supabase_storage import SupabaseStorage

class DiaryPhotoStorage(SupabaseStorage):
    """Storage class for diary photo uploads"""
    bucket_name = 'diary_photos'