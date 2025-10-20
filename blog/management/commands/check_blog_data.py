from django.core.management.base import BaseCommand
from blog.models import BlogPost, BlogImage
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Check blog data in the database'

    def handle(self, *args, **options):
        # Check blog posts
        posts = BlogPost.objects.all()
        self.stdout.write(f"BlogPost records: {posts.count()}")
        
        for post in posts:
            self.stdout.write(f"- {post.title}")
            self.stdout.write(f"  Author: {post.author.email}")
            self.stdout.write(f"  Status: {post.status}")
            self.stdout.write(f"  Featured Image: {post.featured_image}")
            
            # Check gallery images
            gallery_images = post.gallery_images.all()
            self.stdout.write(f"  Gallery Images: {gallery_images.count()}")
            for img in gallery_images:
                self.stdout.write(f"    - {img.image}")
            self.stdout.write("")