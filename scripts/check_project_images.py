#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from site_diary.models import Project

print("PROJECT IMAGES CHECK")
print("=" * 50)

projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])[:10]

for project in projects:
    image_status = "HAS IMAGE" if project.image else "NO IMAGE"
    image_path = project.image.url if project.image else "None"
    print(f"ID: {project.id} | {project.name[:30]} | {image_status} | {image_path}")

print("=" * 50)