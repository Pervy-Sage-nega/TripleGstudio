#!/usr/bin/env python
"""
Automated Cloud Migration Script for Triple G Blog Images
This script migrates all blog images from local storage to AWS S3 cloud storage.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from blog.models import BlogPost, BlogImage
import boto3
from botocore.exceptions import ClientError

class CloudMigrationManager:
    def __init__(self):
        self.migrated_count = 0
        self.error_count = 0
        self.errors = []
        
    def setup_aws_credentials(self):
        """Setup AWS credentials for S3 access"""
        print("🔧 Setting up AWS credentials...")
        
        # Check if AWS credentials are set
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        
        if not all([access_key, secret_key, bucket_name]):
            print("❌ AWS credentials not found in environment variables!")
            print("Please set the following in your .env file:")
            print("- AWS_ACCESS_KEY_ID")
            print("- AWS_SECRET_ACCESS_KEY") 
            print("- AWS_STORAGE_BUCKET_NAME")
            return False
            
        # Test S3 connection
        try:
            s3_client = boto3.client('s3')
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Successfully connected to S3 bucket: {bucket_name}")
            return True
        except ClientError as e:
            print(f"❌ Failed to connect to S3: {e}")
            return False
    
    def migrate_featured_images(self):
        """Migrate all featured images to cloud storage"""
        print("\n📸 Migrating featured images...")
        
        posts_with_images = BlogPost.objects.exclude(featured_image='').exclude(featured_image__isnull=True)
        total_posts = posts_with_images.count()
        
        if total_posts == 0:
            print("ℹ️  No featured images found to migrate.")
            return
            
        print(f"Found {total_posts} posts with featured images")
        
        for i, post in enumerate(posts_with_images, 1):
            try:
                print(f"[{i}/{total_posts}] Migrating: {post.title}")
                
                # Check if file exists locally
                local_path = post.featured_image.path
                if not os.path.exists(local_path):
                    print(f"⚠️  Local file not found: {local_path}")
                    self.error_count += 1
                    continue
                
                # Read file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                
                # Save to cloud storage
                file_name = post.featured_image.name
                saved_name = default_storage.save(file_name, ContentFile(file_content))
                
                # Update database with new path
                post.featured_image.name = saved_name
                post.save(update_fields=['featured_image'])
                
                print(f"✅ Migrated: {file_name}")
                self.migrated_count += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate featured image for post '{post.title}': {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                self.error_count += 1
    
    def migrate_gallery_images(self):
        """Migrate all gallery images to cloud storage"""
        print("\n🖼️  Migrating gallery images...")
        
        gallery_images = BlogImage.objects.exclude(image='').exclude(image__isnull=True)
        total_images = gallery_images.count()
        
        if total_images == 0:
            print("ℹ️  No gallery images found to migrate.")
            return
            
        print(f"Found {total_images} gallery images")
        
        for i, img in enumerate(gallery_images, 1):
            try:
                print(f"[{i}/{total_images}] Migrating gallery image for: {img.blog_post.title}")
                
                # Check if file exists locally
                local_path = img.image.path
                if not os.path.exists(local_path):
                    print(f"⚠️  Local file not found: {local_path}")
                    self.error_count += 1
                    continue
                
                # Read file content
                with open(local_path, 'rb') as f:
                    file_content = f.read()
                
                # Save to cloud storage
                file_name = img.image.name
                saved_name = default_storage.save(file_name, ContentFile(file_content))
                
                # Update database with new path
                img.image.name = saved_name
                img.save(update_fields=['image'])
                
                print(f"✅ Migrated: {file_name}")
                self.migrated_count += 1
                
            except Exception as e:
                error_msg = f"Failed to migrate gallery image for post '{img.blog_post.title}': {e}"
                print(f"❌ {error_msg}")
                self.errors.append(error_msg)
                self.error_count += 1
    
    def enable_cloud_storage(self):
        """Enable cloud storage in environment settings"""
        print("\n⚙️  Enabling cloud storage...")
        
        env_path = BASE_DIR / '.env'
        if not env_path.exists():
            print("❌ .env file not found!")
            return False
            
        # Read current .env content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Update USE_S3 to True
        if 'USE_S3=False' in content:
            content = content.replace('USE_S3=False', 'USE_S3=True')
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.write(content)
            
            print("✅ Cloud storage enabled in .env file")
            print("🔄 Please restart your Django server to apply changes")
            return True
        elif 'USE_S3=True' in content:
            print("ℹ️  Cloud storage already enabled")
            return True
        else:
            print("❌ USE_S3 setting not found in .env file")
            return False
    
    def generate_migration_report(self):
        """Generate a detailed migration report"""
        print("\n" + "="*60)
        print("📊 MIGRATION REPORT")
        print("="*60)
        print(f"✅ Successfully migrated: {self.migrated_count} files")
        print(f"❌ Failed migrations: {self.error_count} files")
        
        if self.errors:
            print("\n🔍 Error Details:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.migrated_count > 0:
            print("\n🎉 Migration completed successfully!")
            print("Your blog images are now stored in the cloud and will be accessible from any device.")
        else:
            print("\n⚠️  No files were migrated. Please check the errors above.")
        
        print("\n📝 Next Steps:")
        print("1. Verify images are accessible on other devices")
        print("2. Test blog functionality with cloud storage")
        print("3. Consider removing local media files after verification")

def main():
    """Main migration function"""
    print("🚀 Starting Triple G Blog Cloud Migration")
    print("="*60)
    
    migrator = CloudMigrationManager()
    
    # Step 1: Setup AWS credentials
    if not migrator.setup_aws_credentials():
        print("\n❌ Migration aborted due to AWS setup issues")
        return
    
    # Step 2: Migrate images
    migrator.migrate_featured_images()
    migrator.migrate_gallery_images()
    
    # Step 3: Enable cloud storage
    migrator.enable_cloud_storage()
    
    # Step 4: Generate report
    migrator.generate_migration_report()

if __name__ == "__main__":
    main()
