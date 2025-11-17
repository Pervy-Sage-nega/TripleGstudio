from django.core.management.base import BaseCommand
from blog.models import BlogPost, BlogImage, ContentImage

class Command(BaseCommand):
    help = 'Test blog storage configuration'

    def handle(self, *args, **options):
        self.stdout.write('Testing blog storage configuration...')
        
        # Test blog posts with featured images
        posts_with_images = BlogPost.objects.filter(featured_image__isnull=False)
        self.stdout.write(f'Blog posts with featured images: {posts_with_images.count()}')
        
        if posts_with_images.exists():
            sample_post = posts_with_images.first()
            self.stdout.write(f'Sample post: {sample_post.title}')
            try:
                self.stdout.write(f'Featured image URL: {sample_post.featured_image.url}')
                
                # Check if URL contains the correct bucket
                if 'blog_images' in sample_post.featured_image.url:
                    self.stdout.write(self.style.SUCCESS('Using blog_images bucket'))
                else:
                    self.stdout.write(self.style.WARNING('Not using blog_images bucket'))
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Featured image field error: {e}'))
                # Try to find a post with a working featured image
                for post in posts_with_images:
                    try:
                        self.stdout.write(f'Trying post: {post.title}')
                        self.stdout.write(f'Featured image URL: {post.featured_image.url}')
                        if 'blog_images' in post.featured_image.url:
                            self.stdout.write(self.style.SUCCESS('Using blog_images bucket'))
                        else:
                            self.stdout.write(self.style.WARNING('Not using blog_images bucket'))
                        break
                    except ValueError:
                        continue
        
        # Test gallery images
        gallery_images = BlogImage.objects.all()
        self.stdout.write(f'Gallery images: {gallery_images.count()}')
        
        if gallery_images.exists():
            sample_gallery = gallery_images.first()
            try:
                self.stdout.write(f'Sample gallery image URL: {sample_gallery.image.url}')
                
                if 'blog_images' in sample_gallery.image.url:
                    self.stdout.write(self.style.SUCCESS('Gallery using blog_images bucket'))
                else:
                    self.stdout.write(self.style.WARNING('Gallery not using blog_images bucket'))
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Gallery image field error: {e}'))
        
        # Test content images
        content_images = ContentImage.objects.all()
        self.stdout.write(f'Content images: {content_images.count()}')
        
        if content_images.exists():
            sample_content = content_images.first()
            try:
                self.stdout.write(f'Sample content image URL: {sample_content.image.url}')
                
                if 'blog_images' in sample_content.image.url:
                    self.stdout.write(self.style.SUCCESS('Content images using blog_images bucket'))
                else:
                    self.stdout.write(self.style.WARNING('Content images not using blog_images bucket'))
            except ValueError as e:
                self.stdout.write(self.style.ERROR(f'Content image field error: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Blog storage test completed!'))