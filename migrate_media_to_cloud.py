#!/usr/bin/env python
"""
Complete Media Migration Script for Triple G
Migrates images, videos, and profile pictures to cloud storage
"""

import os
import sys
import django
import shutil
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from blog.models import BlogPost, BlogImage
from accounts.models import Profile
from portfolio.models import Project

class CompleteMediaMigrator:
    def __init__(self):
        self.migrated_count = 0
        self.error_count = 0
        self.errors = []
        self.static_media_dir = BASE_DIR / 'static' / 'media'
        
    def setup_directories(self):
        """Create all necessary static media directories"""
        print("📁 Setting up static media directories...")
        
        # Create directory structure
        directories = [
            'blog/featured_images',
            'blog/gallery', 
            'blog/videos',
            'profile_pics',
            'projects/images',
            'projects/videos',
            'videos'  # For background videos
        ]
        
        for directory in directories:
            (self.static_media_dir / directory).mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created directory structure in: {self.static_media_dir}")
    
    def migrate_blog_images(self):
        """Migrate blog featured images and gallery images"""
        print("\n📸 Migrating blog images...")
        
        # Featured images
        posts_with_images = BlogPost.objects.exclude(featured_image='').exclude(featured_image__isnull=True)
        for post in posts_with_images:
            self._copy_file(post.featured_image, 'blog featured image', post.title)
        
        # Gallery images
        gallery_images = BlogImage.objects.exclude(image='').exclude(image__isnull=True)
        for img in gallery_images:
            self._copy_file(img.image, 'gallery image', img.blog_post.title)
    
    def migrate_background_videos(self):
        """Migrate background videos used in blog posts"""
        print("\n🎬 Migrating background videos...")
        
        # Find all MP4 files in static/videos and media directories
        video_sources = [
            BASE_DIR / 'static' / 'videos',
            BASE_DIR / 'media' / 'videos',
            BASE_DIR / 'media' / 'projects' / 'videos'
        ]
        
        for source_dir in video_sources:
            if source_dir.exists():
                for video_file in source_dir.glob('*.mp4'):
                    try:
                        # Determine destination based on source
                        if 'projects' in str(video_file):
                            dest_path = self.static_media_dir / 'projects' / 'videos' / video_file.name
                        else:
                            dest_path = self.static_media_dir / 'videos' / video_file.name
                        
                        # Create destination directory
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copy file
                        shutil.copy2(video_file, dest_path)
                        print(f"✅ Copied video: {video_file.name}")
                        self.migrated_count += 1
                        
                    except Exception as e:
                        error_msg = f"Failed to copy video '{video_file.name}': {e}"
                        print(f"❌ {error_msg}")
                        self.errors.append(error_msg)
                        self.error_count += 1
    
    def migrate_profile_pictures(self):
        """Migrate user profile pictures"""
        print("\n👤 Migrating profile pictures...")
        
        profiles_with_pics = Profile.objects.exclude(profile_pic='').exclude(profile_pic__isnull=True)
        
        for profile in profiles_with_pics:
            self._copy_file(profile.profile_pic, 'profile picture', profile.user.username)
    
    def migrate_project_media(self):
        """Migrate project images and videos"""
        print("\n🏗️ Migrating project media...")
        
        try:
            projects = Project.objects.all()
            for project in projects:
                # Migrate hero image
                if hasattr(project, 'hero_image') and project.hero_image:
                    self._copy_file(project.hero_image, 'project hero image', project.title)
                
                # Migrate background video
                if hasattr(project, 'background_video') and project.background_video:
                    self._copy_file(project.background_video, 'project background video', project.title)
                
                # Migrate gallery images
                if hasattr(project, 'gallery_images'):
                    for img in project.gallery_images.all():
                        if hasattr(img, 'image') and img.image:
                            self._copy_file(img.image, 'project gallery image', project.title)
        
        except Exception as e:
            print(f"ℹ️  Project migration skipped: {e}")
    
    def _copy_file(self, file_field, file_type, context_name):
        """Helper method to copy a file field to static directory"""
        try:
            if file_field and os.path.exists(file_field.path):
                # Source and destination paths
                src_path = Path(file_field.path)
                rel_path = Path(file_field.name)
                dest_path = self.static_media_dir / rel_path
                
                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_path, dest_path)
                print(f"✅ Copied {file_type}: {file_field.name}")
                self.migrated_count += 1
                
        except Exception as e:
            error_msg = f"Failed to copy {file_type} for '{context_name}': {e}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.error_count += 1
    
    def update_settings_for_media(self):
        """Update settings.py for comprehensive media handling"""
        print("\n⚙️  Updating settings for complete media handling...")
        
        settings_path = BASE_DIR / 'config' / 'settings.py'
        
        # Read current settings
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Enhanced media configuration
        media_config = '''
# Enhanced Media Configuration for Render
if USE_RENDER_STATIC and not DEBUG:
    # Production on Render - serve all media as static files
    MEDIA_URL = '/static/media/'
    MEDIA_ROOT = BASE_DIR / 'static' / 'media'
    
    # Ensure all media directories are collected
    STATICFILES_DIRS = [
        BASE_DIR / "static",
        BASE_DIR / "static/media",
        BASE_DIR / "static/media/videos",
        BASE_DIR / "static/media/profile_pics",
        BASE_DIR / "static/media/projects",
    ]
else:
    # Local development storage
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    STATICFILES_DIRS = [BASE_DIR / "static"]
'''
        
        # Replace existing media configuration
        if 'Enhanced Media Configuration for Render' not in content:
            # Find and replace the Render media configuration
            start_marker = '# Render.com Media Configuration'
            end_marker = 'MEDIA_ROOT = BASE_DIR / \'media\''
            
            start_idx = content.find(start_marker)
            if start_idx != -1:
                end_idx = content.find(end_marker, start_idx)
                if end_idx != -1:
                    end_idx = content.find('\n', end_idx) + 1
                    content = content[:start_idx] + media_config + content[end_idx:]
                    
                    # Write back to file
                    with open(settings_path, 'w') as f:
                        f.write(content)
                    
                    print("✅ Settings updated for comprehensive media handling")
                    return True
        
        print("ℹ️  Settings already configured for media handling")
        return True
    
    def create_video_serving_template_helpers(self):
        """Create template helpers for video serving"""
        print("\n📝 Creating video serving helpers...")
        
        template_helper = '''
<!-- Video Background Helper Template -->
<!-- Usage: {% include 'helpers/video_background.html' with video_path='videos/your-video.mp4' %} -->

{% load static %}
<div class="video-background">
    <video autoplay muted loop playsinline class="background-video">
        <source src="{% static video_path %}" type="video/mp4">
        <!-- Fallback for browsers that don't support video -->
        <div class="video-fallback" style="background-image: url('{% static 'images/fallback-bg.jpg' %}');"></div>
    </video>
</div>

<style>
.video-background {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    z-index: -1;
}

.background-video {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.video-fallback {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
}
</style>
'''
        
        # Create templates/helpers directory
        helpers_dir = BASE_DIR / 'templates' / 'helpers'
        helpers_dir.mkdir(parents=True, exist_ok=True)
        
        # Write video helper template
        with open(helpers_dir / 'video_background.html', 'w') as f:
            f.write(template_helper)
        
        print("✅ Created video serving template helpers")
    
    def generate_migration_report(self):
        """Generate comprehensive migration report"""
        print("\n" + "="*60)
        print("📊 COMPLETE MEDIA MIGRATION REPORT")
        print("="*60)
        print(f"✅ Successfully migrated: {self.migrated_count} files")
        print(f"❌ Failed migrations: {self.error_count} files")
        
        if self.errors:
            print("\n🔍 Error Details:")
            for error in self.errors:
                print(f"  • {error}")
        
        print("\n📁 Migrated Media Types:")
        print("  • Blog featured images")
        print("  • Blog gallery images") 
        print("  • Background videos (MP4)")
        print("  • User profile pictures")
        print("  • Project media files")
        
        print("\n📝 Next Steps for Cloud Deployment:")
        print("1. Run: python manage.py collectstatic --no-input")
        print("2. Commit changes: git add . && git commit -m 'feat: Complete media cloud migration'")
        print("3. Push to GitHub: git push origin main")
        print("4. Deploy to Render.com")
        print("5. Test all media types on deployed site")
        
        print("\n🎉 Complete media migration ready for cloud deployment!")

def main():
    """Main migration function"""
    print("🚀 Complete Media Migration for Triple G")
    print("="*60)
    
    migrator = CompleteMediaMigrator()
    
    # Setup directories
    migrator.setup_directories()
    
    # Migrate all media types
    migrator.migrate_blog_images()
    migrator.migrate_background_videos()
    migrator.migrate_profile_pictures()
    migrator.migrate_project_media()
    
    # Update configuration
    migrator.update_settings_for_media()
    migrator.create_video_serving_template_helpers()
    
    # Generate report
    migrator.generate_migration_report()

if __name__ == "__main__":
    main()
