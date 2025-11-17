from config.supabase_storage import SupabaseStorage

class BlogSupabaseStorage(SupabaseStorage):
    """Supabase storage backend for blog images"""
    def __init__(self):
        super().__init__()
        self.bucket_name = 'blog_images'
        self.base_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/"
