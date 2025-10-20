from django.core.management.base import BaseCommand
from portfolio.models import Project
from django.core.files.base import ContentFile
from pathlib import Path


class Command(BaseCommand):
    help = 'Fix cover image for 4-Storey Dormitel project'

    def handle(self, *args, **options):
        try:
            # Find the project
            project = Project.objects.get(title='4-Storey Dormitel')
            
            # Path to the folder (note the spelling difference)
            project_folder = Path('d:/tripleG/project/4-Storey Dormetil')
            
            if not project_folder.exists():
                self.stdout.write(
                    self.style.ERROR(f'Project folder not found: {project_folder}')
                )
                return
            
            # Find the first image
            image_path = project_folder / 'image1.jpg'
            
            if image_path.exists():
                # Read image file
                with open(image_path, 'rb') as f:
                    image_content = f.read()
                
                # Save as hero image
                project.hero_image.save(
                    f"4_Storey_Dormitel_cover.jpg",
                    ContentFile(image_content),
                    save=True
                )
                
                # Update hero image alt text
                project.hero_image_alt = f"{project.title} - Cover Image"
                project.save()
                
                self.stdout.write(f"[OK] Added cover image to {project.title}")
                
            else:
                self.stdout.write(
                    self.style.ERROR(f'Image not found: {image_path}')
                )
            
        except Project.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('4-Storey Dormitel project not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {str(e)}')
            )