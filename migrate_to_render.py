#!/usr/bin/env python
"""
Migrate Blog Images to Render Static Files
Since you're already using Render PostgreSQL, this script prepares your images 
for Render's static file serving or Cloudinary integration.
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

class RenderMigrationManager:
    def __init__(self):
        self.migrated_count = 0
        self.error_count = 0
        self.errors = []
        self.static_media_dir = BASE_DIR / 'static' / 'media'
        
    def setup_static_media_directory(self):
        """Create static media directory structure"""
        print("📁 Setting up static media directories...")
        
        # Create directories
        (self.static_media_dir / 'blog' / 'featured_images').mkdir(parents=True, exist_ok=True)
        (self.static_media_dir / 'blog' / 'gallery').mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Created directories in: {self.static_media_dir}")
        
    def copy_images_to_static(self):
        """Copy all blog images to static directory"""
        print("\n📸 Copying images to static directory...")
        
        # Copy featured images
        posts_with_images = BlogPost.objects.exclude(featured_image='').exclude(featured_image__isnull=True)
        
        for post in posts_with_images:
            try:
                if post.featured_image and os.path.exists(post.featured_image.path):
                    # Source and destination paths
                    src_path = Path(post.featured_image.path)
                    rel_path = Path(post.featured_image.name)
                    dest_path = self.static_media_dir / rel_path
                    
                    # Create destination directory if it doesn't exist
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Copied: {post.featured_image.name}")
                    self.migrated_count += 1
                    
            except Exception as e:
                error_msg = f"Failed to copy featured image for '{post.title}': {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                self.error_count += 1
        
        # Copy gallery images
        gallery_images = BlogImage.objects.exclude(image='').exclude(image__isnull=True)
        
        for img in gallery_images:
            try:
                if img.image and os.path.exists(img.image.path):
                    # Source and destination paths
                    src_path = Path(img.image.path)
                    rel_path = Path(img.image.name)
                    dest_path = self.static_media_dir / rel_path
                    
                    # Create destination directory if it doesn't exist
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Copy file
                    shutil.copy2(src_path, dest_path)
                    print(f"✅ Copied: {img.image.name}")
                    self.migrated_count += 1
                    
            except Exception as e:
                error_msg = f"Failed to copy gallery image for '{img.blog_post.title}': {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                self.error_count += 1
    
    def update_settings_for_render(self):
        """Update settings.py for Render deployment"""
        print("\n⚙️  Updating settings for Render...")
        
        settings_path = BASE_DIR / 'config' / 'settings.py'
        
        # Read current settings
        with open(settings_path, 'r') as f:
            content = f.read()
        
        # Add Render-specific media configuration
        render_config = '''
# Render.com Media Configuration
if not DEBUG:  # Production on Render
    # Serve media files from static directory
    MEDIA_URL = '/static/media/'
    MEDIA_ROOT = BASE_DIR / 'static' / 'media'
    
    # Add media to staticfiles dirs for collection
    STATICFILES_DIRS.append(BASE_DIR / 'static' / 'media')
'''
        
        # Insert before the existing media configuration
        if 'Render.com Media Configuration' not in content:
            # Find the media files section
            media_section_start = content.find('# Media files')
            if media_section_start != -1:
                # Insert the Render config before the existing media config
                content = content[:media_section_start] + render_config + '\n' + content[media_section_start:]
                
                # Write back to file
                with open(settings_path, 'w') as f:
                    f.write(content)
                
                print("✅ Settings updated for Render deployment")
                return True
        
        print("ℹ️  Settings already configured for Render")
        return True
    
    def create_render_build_script(self):
        """Create build script for Render deployment"""
        print("\n📝 Creating Render build script...")
        
        build_script = '''#!/usr/bin/env bash
# Render.com build script for Triple G Blog

set -o errexit  # exit on error

# Install dependencies
pip install -r requirements.txt

# Collect static files (including media)
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

echo "✅ Build completed successfully!"
'''
        
        build_path = BASE_DIR / 'build.sh'
        with open(build_path, 'w', encoding='utf-8') as f:
            f.write(build_script)
        
        # Make script executable (on Unix systems)
        try:
            os.chmod(build_path, 0o755)
        except:
            pass  # Windows doesn't need chmod
        
        print(f"✅ Created build script: {build_path}")
    
    def create_render_yaml(self):
        """Create render.yaml for easy deployment"""
        print("\n📄 Creating render.yaml configuration...")
        
        render_yaml = '''services:
  - type: web
    name: tripleg-blog
    env: python
    buildCommand: "./build.sh"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DEBUG
        value: False
      - key: USE_S3
        value: False
    staticPublishPath: ./staticfiles
'''
        
        yaml_path = BASE_DIR / 'render.yaml'
        with open(yaml_path, 'w', encoding='utf-8') as f:
            f.write(render_yaml)
        
        print(f"✅ Created render.yaml: {yaml_path}")
    
    def generate_migration_report(self):
        """Generate migration report"""
        print("\n" + "="*60)
        print("📊 RENDER MIGRATION REPORT")
        print("="*60)
        print(f"✅ Successfully copied: {self.migrated_count} files")
        print(f"❌ Failed copies: {self.error_count} files")
        
        if self.errors:
            print("\n🔍 Error Details:")
            for error in self.errors:
                print(f"  • {error}")
        
        print("\n📝 Next Steps for Render Deployment:")
        print("1. Commit all changes to your Git repository")
        print("2. Push to GitHub/GitLab")
        print("3. Connect your repository to Render.com")
        print("4. Deploy using the render.yaml configuration")
        print("5. Your images will be served from static files")
        
        print("\n🎉 Migration to Render-compatible format completed!")

def main():
    """Main migration function"""
    print("🚀 Migrating Triple G Blog to Render.com")
    print("="*60)
    
    migrator = RenderMigrationManager()
    
    # Setup directories
    migrator.setup_static_media_directory()
    
    # Copy images to static directory
    migrator.copy_images_to_static()
    
    # Update settings for Render
    migrator.update_settings_for_render()
    
    # Create deployment files
    migrator.create_render_build_script()
    migrator.create_render_yaml()
    
    # Generate report
    migrator.generate_migration_report()

if __name__ == "__main__":
    main()
