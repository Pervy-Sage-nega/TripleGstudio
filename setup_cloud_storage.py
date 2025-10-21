#!/usr/bin/env python
"""
Automated AWS S3 Setup Script for Triple G Blog
This script helps you set up AWS S3 bucket and configure credentials automatically.
"""

import boto3
import os
import json
from botocore.exceptions import ClientError, NoCredentialsError

class AWSSetupManager:
    def __init__(self):
        self.bucket_name = "tripleg-media-bucket"
        self.region = "us-east-1"
        
    def check_aws_cli(self):
        """Check if AWS CLI is configured"""
        try:
            session = boto3.Session()
            credentials = session.get_credentials()
            if credentials:
                print("✅ AWS credentials found")
                return True
            else:
                print("❌ No AWS credentials found")
                return False
        except Exception as e:
            print(f"❌ Error checking AWS credentials: {e}")
            return False
    
    def create_s3_bucket(self):
        """Create S3 bucket for media storage"""
        print(f"\n📦 Creating S3 bucket: {self.bucket_name}")
        
        try:
            s3_client = boto3.client('s3', region_name=self.region)
            
            # Check if bucket already exists
            try:
                s3_client.head_bucket(Bucket=self.bucket_name)
                print(f"ℹ️  Bucket {self.bucket_name} already exists")
                return True
            except ClientError:
                pass  # Bucket doesn't exist, continue with creation
            
            # Create bucket
            if self.region == 'us-east-1':
                s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            
            print(f"✅ Successfully created bucket: {self.bucket_name}")
            return True
            
        except ClientError as e:
            print(f"❌ Failed to create bucket: {e}")
            return False
    
    def configure_bucket_policy(self):
        """Configure bucket policy for public read access"""
        print("\n🔐 Configuring bucket policy...")
        
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/media/*"
                }
            ]
        }
        
        try:
            s3_client = boto3.client('s3')
            s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print("✅ Bucket policy configured for public read access")
            return True
        except ClientError as e:
            print(f"❌ Failed to configure bucket policy: {e}")
            return False
    
    def configure_cors(self):
        """Configure CORS for web access"""
        print("\n🌐 Configuring CORS...")
        
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedHeaders': ['*'],
                    'AllowedMethods': ['GET', 'PUT', 'POST', 'DELETE'],
                    'AllowedOrigins': ['*'],
                    'ExposeHeaders': ['ETag'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }
        
        try:
            s3_client = boto3.client('s3')
            s3_client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
            print("✅ CORS configured successfully")
            return True
        except ClientError as e:
            print(f"❌ Failed to configure CORS: {e}")
            return False
    
    def update_env_file(self):
        """Update .env file with AWS credentials"""
        print("\n📝 Updating .env file...")
        
        try:
            # Get current AWS credentials
            session = boto3.Session()
            credentials = session.get_credentials()
            
            if not credentials:
                print("❌ No AWS credentials found")
                return False
            
            env_path = "d:\\tripleG\\TripleG\\.env"
            
            # Read current .env content
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            # Update AWS settings
            updated_lines = []
            aws_settings_updated = {
                'USE_S3': False,
                'AWS_ACCESS_KEY_ID': False,
                'AWS_SECRET_ACCESS_KEY': False,
                'AWS_STORAGE_BUCKET_NAME': False,
                'AWS_S3_REGION_NAME': False
            }
            
            for line in lines:
                if line.startswith('USE_S3='):
                    updated_lines.append('USE_S3=True\n')
                    aws_settings_updated['USE_S3'] = True
                elif line.startswith('AWS_ACCESS_KEY_ID='):
                    updated_lines.append(f'AWS_ACCESS_KEY_ID={credentials.access_key}\n')
                    aws_settings_updated['AWS_ACCESS_KEY_ID'] = True
                elif line.startswith('AWS_SECRET_ACCESS_KEY='):
                    updated_lines.append(f'AWS_SECRET_ACCESS_KEY={credentials.secret_key}\n')
                    aws_settings_updated['AWS_SECRET_ACCESS_KEY'] = True
                elif line.startswith('AWS_STORAGE_BUCKET_NAME='):
                    updated_lines.append(f'AWS_STORAGE_BUCKET_NAME={self.bucket_name}\n')
                    aws_settings_updated['AWS_STORAGE_BUCKET_NAME'] = True
                elif line.startswith('AWS_S3_REGION_NAME='):
                    updated_lines.append(f'AWS_S3_REGION_NAME={self.region}\n')
                    aws_settings_updated['AWS_S3_REGION_NAME'] = True
                else:
                    updated_lines.append(line)
            
            # Add missing AWS settings
            if not aws_settings_updated['USE_S3']:
                updated_lines.append('USE_S3=True\n')
            if not aws_settings_updated['AWS_ACCESS_KEY_ID']:
                updated_lines.append(f'AWS_ACCESS_KEY_ID={credentials.access_key}\n')
            if not aws_settings_updated['AWS_SECRET_ACCESS_KEY']:
                updated_lines.append(f'AWS_SECRET_ACCESS_KEY={credentials.secret_key}\n')
            if not aws_settings_updated['AWS_STORAGE_BUCKET_NAME']:
                updated_lines.append(f'AWS_STORAGE_BUCKET_NAME={self.bucket_name}\n')
            if not aws_settings_updated['AWS_S3_REGION_NAME']:
                updated_lines.append(f'AWS_S3_REGION_NAME={self.region}\n')
            
            # Write back to .env
            with open(env_path, 'w') as f:
                f.writelines(updated_lines)
            
            print("✅ .env file updated with AWS credentials")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update .env file: {e}")
            return False
    
    def test_setup(self):
        """Test the complete setup"""
        print("\n🧪 Testing S3 setup...")
        
        try:
            s3_client = boto3.client('s3')
            
            # Test upload
            test_content = b"Test file for Triple G Blog"
            s3_client.put_object(
                Bucket=self.bucket_name,
                Key="media/test/test.txt",
                Body=test_content,
                ContentType="text/plain"
            )
            
            # Test public access
            test_url = f"https://{self.bucket_name}.s3.amazonaws.com/media/test/test.txt"
            print(f"✅ Test file uploaded successfully")
            print(f"🔗 Test URL: {test_url}")
            
            # Clean up test file
            s3_client.delete_object(Bucket=self.bucket_name, Key="media/test/test.txt")
            
            return True
            
        except ClientError as e:
            print(f"❌ Setup test failed: {e}")
            return False

def main():
    """Main setup function"""
    print("🚀 AWS S3 Setup for Triple G Blog")
    print("="*50)
    
    setup_manager = AWSSetupManager()
    
    # Check AWS credentials
    if not setup_manager.check_aws_cli():
        print("\n❌ Setup aborted. Please configure AWS CLI first:")
        print("1. Install AWS CLI: https://aws.amazon.com/cli/")
        print("2. Run: aws configure")
        print("3. Enter your AWS Access Key ID and Secret Access Key")
        return
    
    # Create and configure S3 bucket
    if not setup_manager.create_s3_bucket():
        print("\n❌ Failed to create S3 bucket")
        return
    
    if not setup_manager.configure_bucket_policy():
        print("\n⚠️  Warning: Failed to configure bucket policy")
    
    if not setup_manager.configure_cors():
        print("\n⚠️  Warning: Failed to configure CORS")
    
    # Update environment file
    if not setup_manager.update_env_file():
        print("\n❌ Failed to update .env file")
        return
    
    # Test setup
    if setup_manager.test_setup():
        print("\n🎉 AWS S3 setup completed successfully!")
        print("\n📝 Next steps:")
        print("1. Run: python migrate_to_cloud.py")
        print("2. Restart your Django server")
        print("3. Test image uploads in your blog")
    else:
        print("\n❌ Setup test failed. Please check your configuration.")

if __name__ == "__main__":
    main()
