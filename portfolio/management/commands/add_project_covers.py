from django.core.management.base import BaseCommand
from portfolio.models import Project
from django.core.files.base import ContentFile
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Add cover images (hero images) to projects from project folders'

    def handle(self, *args, **options):
        try:
            # Base path to project images
            project_base_path = Path('d:/tripleG/project')
            
            if not project_base_path.exists():
                self.stdout.write(
                    self.style.ERROR(f'Project directory not found: {project_base_path}')
                )
                return
            
            # Get all projects
            projects = Project.objects.all()
            updated_count = 0
            
            for project in projects:
                self.stdout.write(f"\nProcessing project: {project.title}")
                
                # Check if project already has hero image
                if project.hero_image:
                    self.stdout.write(f"  Already has cover image: {project.hero_image.name}")
                    continue
                
                # Find project folder
                project_folder = None
                for folder in project_base_path.iterdir():
                    if folder.is_dir() and project.title.lower() in folder.name.lower():
                        project_folder = folder
                        break
                
                if not project_folder:
                    self.stdout.write(f"  [WARNING] No matching folder found")
                    continue
                
                # Look for the first image to use as cover
                image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
                cover_image = None
                
                # Try to find image1 first, then any image
                for img_name in ['image1.jpg', 'image.jpg', 'cover.jpg', 'hero.jpg']:
                    img_path = project_folder / img_name
                    if img_path.exists():
                        cover_image = img_path
                        break
                
                # If no specific cover image found, use the first available image
                if not cover_image:
                    for ext in image_extensions:
                        images = list(project_folder.glob(f'*{ext}')) + list(project_folder.glob(f'*{ext.upper()}'))
                        if images:
                            cover_image = images[0]
                            break
                
                if cover_image:
                    try:
                        # Read image file
                        with open(cover_image, 'rb') as f:
                            image_content = f.read()
                        
                        # Save as hero image
                        project.hero_image.save(
                            f"{project.title.replace(' ', '_')}_cover{cover_image.suffix}",
                            ContentFile(image_content),
                            save=True
                        )
                        
                        # Update hero image alt text
                        project.hero_image_alt = f"{project.title} - Cover Image"
                        project.save()
                        
                        updated_count += 1
                        self.stdout.write(f"  [OK] Added cover image: {cover_image.name}")
                        
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"  [ERROR] Failed to add cover image: {str(e)}")
                        )
                else:
                    self.stdout.write(f"  [WARNING] No images found in folder")
            
            # Summary
            self.stdout.write(f"\n" + "="*50)
            self.stdout.write("COVER IMAGE SUMMARY:")
            self.stdout.write(f"Total projects processed: {projects.count()}")
            self.stdout.write(f"Cover images added: {updated_count}")
            
            # Final check
            projects_with_covers = Project.objects.exclude(hero_image='').count()
            self.stdout.write(f"Projects with cover images: {projects_with_covers}")
            
            # List projects and their cover status
            self.stdout.write(f"\nProject Cover Status:")
            for project in Project.objects.all():
                status = "[HAS COVER]" if project.hero_image else "[NO COVER]"
                self.stdout.write(f"  {status} {project.title}")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error adding cover images: {str(e)}')
            )