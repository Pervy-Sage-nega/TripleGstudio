from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.urls import reverse
from datetime import datetime

# Create your models here.

class Category(models.Model):
    """Category model for organizing projects"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Project(models.Model):
    """Main project model - no client information for privacy"""
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='projects')
    year = models.IntegerField(
        validators=[
            MinValueValidator(2000),
            MaxValueValidator(datetime.now().year + 5)
        ]
    )
    location = models.CharField(max_length=255)
    size = models.CharField(max_length=50, help_text="e.g., 350 m², 2500 sq ft")
    duration = models.CharField(max_length=50, help_text="e.g., 14 Months, 2 Years")
    completion_date = models.DateField()
    lead_architect = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    featured = models.BooleanField(default=False, help_text="Show in featured projects section")
    hero_image = models.ImageField(upload_to='projects/hero/', blank=True, null=True)
    video = models.FileField(upload_to='projects/videos/', blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-completion_date', '-created_at']
    
    def get_absolute_url(self):
        return reverse('portfolio:project_detail', kwargs={'project_id': self.id})
    
    def __str__(self):
        return f"{self.title} ({self.year})"
    
    def hero_image_preview(self):
        """Return HTML for hero image preview in admin"""
        if self.hero_image:
            return f'<img src="{self.hero_image.url}" style="max-width: 200px; max-height: 150px;" />'
        return "No hero image"
    hero_image_preview.allow_tags = True
    hero_image_preview.short_description = "Hero Image Preview"
    
    def video_preview(self):
        """Return HTML for video preview in admin"""
        if self.video:
            return f'<video controls style="max-width: 200px; max-height: 150px;"><source src="{self.video.url}" type="video/mp4"></video>'
        return "No video"
    video_preview.allow_tags = True
    video_preview.short_description = "Video Preview"


class ProjectImage(models.Model):
    """Gallery images for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    alt_text = models.CharField(max_length=255, help_text="Descriptive text for accessibility")
    order = models.PositiveIntegerField(default=0, help_text="Display order in gallery")
    
    class Meta:
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.project.title} - Image {self.id}"


class ProjectStat(models.Model):
    """Key statistics/facts about projects - no client info"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='stats')
    label = models.CharField(max_length=100, help_text="e.g., 'Total Area', 'Floors', 'Rooms'")
    value = models.CharField(max_length=255, help_text="e.g., '350 m²', '3', '5 Bedrooms'")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'id']
        unique_together = ['project', 'label']
    
    def __str__(self):
        return f"{self.project.title} - {self.label}: {self.value}"


class ProjectTimeline(models.Model):
    """Timeline/milestones for projects"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='timeline')
    title = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField()
    completed = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0, help_text="Display order in timeline")
    
    class Meta:
        ordering = ['order', 'date']
    
    def __str__(self):
        return f"{self.project.title} - {self.title} ({self.date})"
