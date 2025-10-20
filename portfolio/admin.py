from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Project, ProjectImage, ProjectStat, ProjectTimeline

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'image_preview', 'alt_text', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        """Show image preview in inline"""
        if obj.image:
            return format_html('<img src="{}" style="max-width: 100px; max-height: 75px;" />', obj.image.url)
        return "No image"
    image_preview.short_description = "Preview"


class ProjectStatInline(admin.TabularInline):
    model = ProjectStat
    extra = 1
    fields = ['label', 'value', 'order']


class ProjectTimelineInline(admin.TabularInline):
    model = ProjectTimeline
    extra = 1
    fields = ['title', 'date', 'description', 'completed', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'year', 'status', 'featured', 'completion_date', 'has_hero_image', 'has_video']
    list_filter = ['category', 'year', 'status', 'featured']
    search_fields = ['title', 'description', 'location', 'lead_architect']
    list_editable = ['featured', 'status']
    date_hierarchy = 'completion_date'
    readonly_fields = ['hero_image_preview', 'video_preview']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Project Details', {
            'fields': ('year', 'location', 'size', 'duration', 'completion_date', 'lead_architect')
        }),
        ('Status & Media', {
            'fields': ('status', 'featured', 'hero_image', 'hero_image_preview', 'video', 'video_preview')
        }),
    )
    
    inlines = [ProjectImageInline, ProjectStatInline, ProjectTimelineInline]
    
    def has_hero_image(self, obj):
        """Show if project has hero image"""
        return "✅" if obj.hero_image else "❌"
    has_hero_image.short_description = "Hero Image"
    
    def has_video(self, obj):
        """Show if project has video"""
        return "✅" if obj.video else "❌"
    has_video.short_description = "Video"


@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'alt_text', 'order']
    list_filter = ['project']
    ordering = ['project', 'order']


@admin.register(ProjectStat)
class ProjectStatAdmin(admin.ModelAdmin):
    list_display = ['project', 'label', 'value', 'order']
    list_filter = ['project', 'label']
    ordering = ['project', 'order']


@admin.register(ProjectTimeline)
class ProjectTimelineAdmin(admin.ModelAdmin):
    list_display = ['project', 'title', 'date', 'completed', 'order']
    list_filter = ['project', 'completed', 'date']
    date_hierarchy = 'date'
    ordering = ['project', 'order']
