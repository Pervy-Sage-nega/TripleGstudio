from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import BlogPost, BlogImage
from django.core.files import File
import os
from django.conf import settings
from django.core.files.storage import default_storage
import shutil

class Command(BaseCommand):
    help = 'Add images to existing blog posts from their specific folders'

    def handle(self, *args, **options):
        # Get the author
        try:
            author = User.objects.get(email='rideouts200221@gmail.com')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Author not found'))
            return

        # Blog post folder mapping
        blog_folders = {
            'Beauty Salon: Modern Elegance in Commercial Design': 'Beauty Salon',
            'Crystalline Reckonings: Geometric Precision in Modern Architecture': 'Crystalline Reckonings',
            'Dynamic Urban Continuum: Reshaping City Landscapes': 'Dynamic Urban Continuum',
            'Japanese Village: Harmony Between Tradition and Modernity': 'Japanese Village',
            'Payo ad Apfu: Cultural Heritage in Contemporary Design': 'Payo ad Apfu',
            'Pellucid Reverence: Transparency in Modern Architecture': 'Pellucid Reverence',
            'Shelas Ukay: Sustainable Community Development': 'Shelas Ukay',
            'The Art of Transformation: Adaptive Reuse Excellence': 'The Art of Transformation',
            'The Lasting City: Designing for Urban Resilience': 'The Lasting City',
            'Unorthodox A-Frame: Reimagining Classic Architecture': 'Unorthodox A-Frame'
        }

        # Process each blog post
        for post in BlogPost.objects.filter(author=author):
            folder_name = blog_folders.get(post.title)
            if not folder_name:
                self.stdout.write(f"No folder found for: {post.title}")
                continue
                
            folder_path = os.path.join(settings.BASE_DIR, 'blogpost', folder_name)
            if not os.path.exists(folder_path):
                self.stdout.write(f"Folder not found: {folder_path}")
                continue
            
            # Get all image files from the folder
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if not image_files:
                self.stdout.write(f"No images found in: {folder_path}")
                continue
            
            # Clear existing images
            post.featured_image = None
            post.gallery_images.all().delete()
            
            # Copy images to media directory and assign to post
            for i, image_file in enumerate(image_files):
                src_path = os.path.join(folder_path, image_file)
                
                if i == 0:  # First image as featured
                    dest_path = f'blog/featured_images/{folder_name}_{image_file}'
                    media_dest = os.path.join(settings.MEDIA_ROOT, dest_path)
                    os.makedirs(os.path.dirname(media_dest), exist_ok=True)
                    shutil.copy2(src_path, media_dest)
                    
                    post.featured_image = dest_path
                    post.featured_image_alt = f"Featured image for {post.title}"
                    post.save()
                    self.stdout.write(f"Added featured image to: {post.title}")
                else:  # Rest as gallery images
                    dest_path = f'blog/gallery/{folder_name}_{image_file}'
                    media_dest = os.path.join(settings.MEDIA_ROOT, dest_path)
                    os.makedirs(os.path.dirname(media_dest), exist_ok=True)
                    shutil.copy2(src_path, media_dest)
                    
                    BlogImage.objects.create(
                        blog_post=post,
                        image=dest_path,
                        caption=f'Gallery image for {post.title}',
                        alt_text=f'Gallery image {i}',
                        order=i-1
                    )
            
            self.stdout.write(f"Added {len(image_files)} images to: {post.title}")

        self.stdout.write(self.style.SUCCESS('Successfully added blog-specific images to posts'))