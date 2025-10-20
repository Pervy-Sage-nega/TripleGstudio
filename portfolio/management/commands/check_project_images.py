from django.core.management.base import BaseCommand
from portfolio.models import Project, ProjectImage
from django.core.files.base import ContentFile
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Check project image gallery state and add images from project folders'

    def handle(self, *args, **options):
        try:
            # Base path to project images
            project_base_path = Path('d:/tripleG/project')
            
            if not project_base_path.exists():
                self.stdout.write(
                    self.style.ERROR(f'Project directory not found: {project_base_path}')
                )
                return
            
            # Check each project
            projects = Project.objects.all()
            
            for project in projects:
                self.stdout.write(f"\nChecking project: {project.title}")
                
                # Check current image count
                current_images = ProjectImage.objects.filter(project=project)
                self.stdout.write(f"  Current images in database: {current_images.count()}")
                
                # List current images
                for img in current_images:
                    self.stdout.write(f"    - {img.alt_text} (Order: {img.order})")
                
                # Try to find project folder
                project_folder = None
                for folder in project_base_path.iterdir():
                    if folder.is_dir() and project.title.lower() in folder.name.lower():
                        project_folder = folder
                        break
                
                if project_folder:
                    self.stdout.write(f"  Found project folder: {project_folder.name}")
                    
                    # Count image files in folder
                    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                    image_files = []
                    
                    for ext in image_extensions:
                        image_files.extend(project_folder.glob(f'*{ext}'))
                        image_files.extend(project_folder.glob(f'*{ext.upper()}'))
                    
                    self.stdout.write(f"  Images found in folder: {len(image_files)}")
                    
                    # List image files
                    for img_file in image_files:
                        self.stdout.write(f"    - {img_file.name}")
                    
                    # Add missing images to database (if any)
                    if image_files and current_images.count() == 0:
                        self.stdout.write(f"  Adding {len(image_files)} images to database...")
                        
                        for i, img_file in enumerate(image_files):
                            try:
                                # Read image file
                                with open(img_file, 'rb') as f:
                                    image_content = f.read()
                                
                                # Create ProjectImage
                                project_image = ProjectImage.objects.create(
                                    project=project,
                                    alt_text=f"{project.title} - {img_file.stem}",
                                    order=i
                                )
                                
                                # Save image file
                                project_image.image.save(
                                    img_file.name,
                                    ContentFile(image_content),
                                    save=True
                                )
                                
                                self.stdout.write(f"    [OK] Added: {img_file.name}")
                                
                            except Exception as e:
                                self.stdout.write(
                                    self.style.ERROR(f"    [ERROR] Error adding {img_file.name}: {str(e)}")
                                )
                    
                else:
                    self.stdout.write(f"  [WARNING] No matching folder found for project")
            
            # Summary
            self.stdout.write(f"\n" + "="*50)
            self.stdout.write("SUMMARY:")
            
            total_projects = Project.objects.count()
            projects_with_images = Project.objects.filter(images__isnull=False).distinct().count()
            total_images = ProjectImage.objects.count()
            
            self.stdout.write(f"Total projects: {total_projects}")
            self.stdout.write(f"Projects with images: {projects_with_images}")
            self.stdout.write(f"Total images in database: {total_images}")
            
            # Check database integrity
            self.stdout.write(f"\nDatabase integrity check:")
            for project in Project.objects.all():
                image_count = project.images.count()
                if image_count > 0:
                    self.stdout.write(f"  [OK] {project.title}: {image_count} images")
                else:
                    self.stdout.write(f"  [NO IMAGES] {project.title}: No images")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking project images: {str(e)}')
            )