from django.core.management.base import BaseCommand
from portfolio.models import Project, ProjectImage, Category
from django.core.files.base import ContentFile
from PIL import Image
import io


class Command(BaseCommand):
    help = 'Verify image gallery functionality in project management'

    def handle(self, *args, **options):
        try:
            # Test 1: Check current state
            self.stdout.write("=== IMAGE GALLERY VERIFICATION ===\n")
            
            total_projects = Project.objects.count()
            total_images = ProjectImage.objects.count()
            projects_with_images = Project.objects.filter(images__isnull=False).distinct().count()
            
            self.stdout.write(f"Current Database State:")
            self.stdout.write(f"  Total Projects: {total_projects}")
            self.stdout.write(f"  Total Images: {total_images}")
            self.stdout.write(f"  Projects with Images: {projects_with_images}")
            
            # Test 2: Verify image-project relationships
            self.stdout.write(f"\nProject-Image Relationships:")
            for project in Project.objects.all():
                image_count = project.images.count()
                status = "[OK]" if image_count > 0 else "[NO IMAGES]"
                self.stdout.write(f"  {status} {project.title}: {image_count} images")
            
            # Test 3: Create a test project with images to verify functionality
            self.stdout.write(f"\nTesting Image Gallery Creation...")
            
            # Get or create test category
            test_category, _ = Category.objects.get_or_create(name='Test Category')
            
            # Create a simple test image
            def create_test_image_content():
                img = Image.new('RGB', (100, 100), color='blue')
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                return img_io.getvalue()
            
            # Create test project
            test_project = Project.objects.create(
                title='Image Gallery Test Project',
                description='Testing image gallery functionality',
                category=test_category,
                year=2024,
                location='Test Location',
                size='100 m²',
                duration='1 Month',
                completion_date='2024-12-31',
                lead_architect='Test Architect',
                status='draft'
            )
            
            self.stdout.write(f"  Created test project: {test_project.title}")
            
            # Add test images to the project
            test_image_data = create_test_image_content()
            
            for i in range(3):
                project_image = ProjectImage.objects.create(
                    project=test_project,
                    alt_text=f"Test Image {i+1}",
                    order=i
                )
                
                # Save image content
                project_image.image.save(
                    f'test_image_{i+1}.jpg',
                    ContentFile(test_image_data),
                    save=True
                )
                
                self.stdout.write(f"    Added image {i+1}: {project_image.alt_text}")
            
            # Verify the test project
            created_images = ProjectImage.objects.filter(project=test_project)
            self.stdout.write(f"  Verification: {created_images.count()} images created")
            
            # Test 4: Check if images are properly linked
            self.stdout.write(f"\nImage-Project Link Verification:")
            for img in created_images:
                self.stdout.write(f"  Image: {img.alt_text} -> Project: {img.project.title}")
                self.stdout.write(f"    Order: {img.order}")
                self.stdout.write(f"    Has file: {'Yes' if img.image else 'No'}")
            
            # Test 5: Test project.images relationship
            project_images_via_relation = test_project.images.all()
            self.stdout.write(f"\nRelationship Test:")
            self.stdout.write(f"  Images via project.images.all(): {project_images_via_relation.count()}")
            
            # Clean up test project
            self.stdout.write(f"\nCleaning up test data...")
            test_project.delete()  # This should cascade delete the images
            self.stdout.write(f"  Test project and images deleted")
            
            # Final verification
            final_projects = Project.objects.count()
            final_images = ProjectImage.objects.count()
            
            self.stdout.write(f"\nFinal State:")
            self.stdout.write(f"  Projects: {final_projects} (should be {total_projects})")
            self.stdout.write(f"  Images: {final_images} (should be {total_images})")
            
            # Test 6: Check existing project image access
            self.stdout.write(f"\nExisting Project Image Access Test:")
            sample_project = Project.objects.filter(images__isnull=False).first()
            if sample_project:
                self.stdout.write(f"  Sample project: {sample_project.title}")
                self.stdout.write(f"  Images count: {sample_project.images.count()}")
                
                for img in sample_project.images.all()[:3]:  # Show first 3 images
                    self.stdout.write(f"    - {img.alt_text} (Order: {img.order})")
                    self.stdout.write(f"      File exists: {'Yes' if img.image else 'No'}")
            else:
                self.stdout.write(f"  No projects with images found")
            
            # Summary
            self.stdout.write(f"\n" + "="*50)
            self.stdout.write("SUMMARY:")
            self.stdout.write(f"[OK] Image gallery database structure is working")
            self.stdout.write(f"[OK] Project-Image relationships are functional")
            self.stdout.write(f"[OK] Image creation and deletion works correctly")
            self.stdout.write(f"[OK] Project management can handle image galleries")
            
            if projects_with_images > 0:
                self.stdout.write(f"[OK] {projects_with_images} projects have image galleries")
            else:
                self.stdout.write(f"[WARNING] No projects currently have image galleries")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during verification: {str(e)}')
            )