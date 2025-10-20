from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portfolio.models import Category, Project, ProjectImage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from portfolio.views import create_project
import tempfile
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Test project creation with image gallery to verify database saving'

    def handle(self, *args, **options):
        try:
            # Get the admin user
            admin_user = User.objects.get(email='triplegotp@gmail.com')
            
            # Get or create a category
            category, _ = Category.objects.get_or_create(name='Test Category')
            
            # Create a test image
            def create_test_image(name='test_image.jpg'):
                # Create a simple test image
                img = Image.new('RGB', (100, 100), color='red')
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                img_io.seek(0)
                return SimpleUploadedFile(name, img_io.getvalue(), content_type='image/jpeg')
            
            # Test 1: Check current project count
            initial_count = Project.objects.count()
            initial_image_count = ProjectImage.objects.count()
            
            self.stdout.write(f"Initial project count: {initial_count}")
            self.stdout.write(f"Initial image count: {initial_image_count}")
            
            # Test 2: Create a test project with images
            self.stdout.write("\nTesting project creation with images...")
            
            # Create request factory
            factory = RequestFactory()
            
            # Create test images
            test_images = [
                create_test_image('gallery_1.jpg'),
                create_test_image('gallery_2.jpg'),
                create_test_image('gallery_3.jpg')
            ]
            
            # Prepare POST data
            post_data = {
                'title': 'Test Project with Gallery',
                'description': 'This is a test project to verify image gallery functionality',
                'category': category.id,
                'year': 2024,
                'location': 'Test Location',
                'size': '100 m²',
                'duration': '6 Months',
                'completion_date': '2024-12-31',
                'lead_architect': 'Test Architect',
                'status': 'planned',
                'featured': 'on',
                'seo_meta_title': 'Test SEO Title',
                'seo_meta_description': 'Test SEO Description',
                'hero_image_alt': 'Test Hero Alt Text'
            }
            
            # Create hero image
            hero_image = create_test_image('hero.jpg')
            
            # Create POST request with files
            request = factory.post('/portfolio/create/', data=post_data)
            request.user = admin_user
            request.FILES = {
                'hero_image': hero_image,
                'gallery_images': test_images
            }
            
            # Simulate the create_project view logic
            try:
                from django.db import transaction
                
                with transaction.atomic():
                    # Create the main project
                    project = Project.objects.create(
                        title=post_data['title'],
                        description=post_data['description'],
                        category_id=post_data['category'],
                        year=int(post_data['year']),
                        location=post_data['location'],
                        size=post_data['size'],
                        duration=post_data['duration'],
                        completion_date=post_data['completion_date'],
                        lead_architect=post_data['lead_architect'],
                        status=post_data['status'],
                        featured=post_data.get('featured') == 'on',
                        seo_meta_title=post_data.get('seo_meta_title', ''),
                        seo_meta_description=post_data.get('seo_meta_description', ''),
                        hero_image_alt=post_data.get('hero_image_alt', ''),
                    )
                    # Handle hero image
                    if hero_image:
                        project.hero_image = hero_image
                        project.save()
                    
                    # Handle gallery images
                    for i, image in enumerate(test_images):
                        project_image = ProjectImage.objects.create(
                            project=project,
                            image=image,
                            alt_text=f"{project.title} - Gallery Image {i+1}",
                            order=i
                        )
                        self.stdout.write(f"  Created gallery image {i+1}: {project_image.alt_text}")
                    
                    self.stdout.write(f"\n[SUCCESS] Created test project: {project.title}")
                    
                    # Verify the project was created
                    final_count = Project.objects.count()
                    final_image_count = ProjectImage.objects.count()
                    
                    self.stdout.write(f"\nVerification:")
                    self.stdout.write(f"  Projects before: {initial_count}")
                    self.stdout.write(f"  Projects after: {final_count}")
                    self.stdout.write(f"  Images before: {initial_image_count}")
                    self.stdout.write(f"  Images after: {final_image_count}")
                    
                    # Check the created project
                    created_project = Project.objects.get(id=project.id)
                    gallery_images = ProjectImage.objects.filter(project=created_project)
                    
                    self.stdout.write(f"\nProject Details:")
                    self.stdout.write(f"  Title: {created_project.title}")
                    self.stdout.write(f"  Has hero image: {'Yes' if created_project.hero_image else 'No'}")
                    self.stdout.write(f"  Gallery images count: {gallery_images.count()}")
                    
                    for img in gallery_images:
                        self.stdout.write(f"    - {img.alt_text} (Order: {img.order})")
                    
                    # Test 3: Verify database integrity
                    self.stdout.write(f"\nDatabase Integrity Check:")
                    if gallery_images.count() == len(test_images):
                        self.stdout.write(f"  [OK] All gallery images saved correctly")
                    else:
                        self.stdout.write(f"  [ERROR] Expected {len(test_images)} images, found {gallery_images.count()}")
                    
                    if created_project.hero_image:
                        self.stdout.write(f"  [OK] Hero image saved correctly")
                    else:
                        self.stdout.write(f"  [ERROR] Hero image not saved")
                    
                    # Clean up test project
                    self.stdout.write(f"\nCleaning up test project...")
                    created_project.delete()
                    self.stdout.write(f"  [OK] Test project deleted")
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error during project creation test: {str(e)}")
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Admin user triplegotp@gmail.com not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running test: {str(e)}')
            )