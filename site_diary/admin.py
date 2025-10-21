from django.contrib import admin
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto, SubcontractorCompany, Milestone
)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_name', 'project_manager', 'status', 'start_date', 'expected_end_date']
    list_filter = ['status', 'start_date', 'project_manager']
    search_fields = ['name', 'client_name', 'location']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']

class LaborEntryInline(admin.TabularInline):
    model = LaborEntry
    extra = 1

class MaterialEntryInline(admin.TabularInline):
    model = MaterialEntry
    extra = 1

class EquipmentEntryInline(admin.TabularInline):
    model = EquipmentEntry
    extra = 1

class DelayEntryInline(admin.TabularInline):
    model = DelayEntry
    extra = 1

class VisitorEntryInline(admin.TabularInline):
    model = VisitorEntry
    extra = 1

class DiaryPhotoInline(admin.TabularInline):
    model = DiaryPhoto
    extra = 1

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ['project', 'entry_date', 'created_by', 'weather_condition', 'approved', 'reviewed_by']
    list_filter = ['approved', 'weather_condition', 'entry_date', 'project__status']
    search_fields = ['project__name', 'work_description', 'created_by__username']
    date_hierarchy = 'entry_date'
    ordering = ['-entry_date']
    readonly_fields = ['created_at', 'updated_at']
    
    inlines = [
        LaborEntryInline,
        MaterialEntryInline,
        EquipmentEntryInline,
        DelayEntryInline,
        VisitorEntryInline,
        DiaryPhotoInline,
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('project', 'entry_date', 'created_by')
        }),
        ('Weather Information', {
            'fields': ('weather_condition', 'temperature_high', 'temperature_low', 'humidity', 'wind_speed'),
            'classes': ('collapse',)
        }),
        ('Work Progress', {
            'fields': ('work_description', 'progress_percentage', 'milestone')
        }),
        ('Quality & Safety', {
            'fields': ('quality_issues', 'safety_incidents'),
            'classes': ('collapse',)
        }),
        ('Notes & Media', {
            'fields': ('general_notes', 'photos_taken'),
            'classes': ('collapse',)
        }),
        ('Approval', {
            'fields': ('approved', 'reviewed_by', 'approval_date'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(LaborEntry)
class LaborEntryAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'labor_type', 'trade_description', 'workers_count', 'hours_worked', 'total_cost']
    list_filter = ['labor_type', 'diary_entry__entry_date']
    search_fields = ['trade_description', 'diary_entry__project__name']
    ordering = ['-diary_entry__entry_date']

@admin.register(MaterialEntry)
class MaterialEntryAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'material_name', 'quantity_delivered', 'quantity_used', 'unit', 'supplier', 'total_cost']
    list_filter = ['unit', 'quality_check', 'diary_entry__entry_date']
    search_fields = ['material_name', 'supplier', 'diary_entry__project__name']
    ordering = ['-diary_entry__entry_date']

@admin.register(EquipmentEntry)
class EquipmentEntryAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'equipment_name', 'equipment_type', 'operator_name', 'hours_operated', 'status', 'total_rental_cost']
    list_filter = ['status', 'equipment_type', 'diary_entry__entry_date']
    search_fields = ['equipment_name', 'equipment_type', 'operator_name', 'diary_entry__project__name']
    ordering = ['-diary_entry__entry_date']

@admin.register(DelayEntry)
class DelayEntryAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'category', 'duration_hours', 'impact_level', 'responsible_party', 'cost_impact']
    list_filter = ['category', 'impact_level', 'diary_entry__entry_date']
    search_fields = ['description', 'responsible_party', 'diary_entry__project__name']
    ordering = ['-diary_entry__entry_date']

@admin.register(VisitorEntry)
class VisitorEntryAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'visitor_name', 'company', 'visitor_type', 'arrival_time', 'departure_time']
    list_filter = ['visitor_type', 'diary_entry__entry_date']
    search_fields = ['visitor_name', 'company', 'diary_entry__project__name']
    ordering = ['-diary_entry__entry_date']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']

@admin.register(SubcontractorCompany)
class SubcontractorCompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'company_type', 'contact_person', 'phone', 'is_active']
    list_filter = ['company_type', 'is_active']
    search_fields = ['name', 'contact_person', 'phone']
    ordering = ['name']

@admin.register(DiaryPhoto)
class DiaryPhotoAdmin(admin.ModelAdmin):
    list_display = ['diary_entry', 'caption', 'location', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['caption', 'location', 'diary_entry__project__name']
    ordering = ['-uploaded_at']
