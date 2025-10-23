from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal

class Project(models.Model):
    PROJECT_STATUS = [
        ('pending_approval', 'Pending Approval'),
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, max_length=2000)
    client_name = models.CharField(max_length=100)
    client = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_projects')
    project_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    architect = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='architect_projects')
    location = models.CharField(max_length=300)
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='pending_approval')
    image = models.ImageField(upload_to='project_images/', null=True, blank=True)
    
    # Admin approval fields
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_projects')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection if applicable")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.client_name}"
    
    def clean(self):
        super().clean()
        # Validate dates
        if self.start_date and self.expected_end_date:
            if self.start_date > self.expected_end_date:
                raise ValidationError('Start date cannot be after expected end date.')
        
        if self.actual_end_date and self.start_date:
            if self.actual_end_date < self.start_date:
                raise ValidationError('Actual end date cannot be before start date.')
    
    def get_progress_percentage(self):
        """Get the latest progress percentage from diary entries"""
        try:
            latest_entry = self.diary_entries.order_by('-entry_date').first()
            if latest_entry and latest_entry.progress_percentage is not None:
                return int(latest_entry.progress_percentage)
        except (ValueError, TypeError, AttributeError):
            pass
        
        # Fallback to status-based progress
        status_progress = {
            'pending_approval': 0,
            'planning': 10,
            'active': 50,
            'on_hold': 25,
            'completed': 100,
            'cancelled': 0,
            'rejected': 0,
        }
        return status_progress.get(self.status, 0)

class DiaryEntry(models.Model):
    WEATHER_CONDITIONS = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy'),
        ('windy', 'Windy'),
        ('snowy', 'Snowy'),
    ]
    
    ENTRY_STATUS = [
        ('complete', 'Complete'),
        ('needs_revision', 'Needs Revision'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='diary_entries')
    entry_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Weather Information
    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS, blank=True)
    temperature_high = models.IntegerField(null=True, blank=True, help_text="Temperature in Celsius", validators=[MinValueValidator(-50), MaxValueValidator(60)])
    temperature_low = models.IntegerField(null=True, blank=True, help_text="Temperature in Celsius", validators=[MinValueValidator(-50), MaxValueValidator(60)])
    humidity = models.IntegerField(null=True, blank=True, help_text="Humidity percentage", validators=[MinValueValidator(0), MaxValueValidator(100)])
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Wind speed in km/h", validators=[MinValueValidator(0), MaxValueValidator(500)])
    
    # Work Progress
    work_description = models.TextField(help_text="Description of work performed today", max_length=2000)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Overall project progress percentage", validators=[MinValueValidator(0), MaxValueValidator(100)])
    milestone = models.ForeignKey('Milestone', on_delete=models.SET_NULL, null=True, blank=True, help_text="Current milestone phase")
    
    # Quality and Safety
    quality_issues = models.TextField(blank=True, help_text="Any quality issues encountered", max_length=1000)
    safety_incidents = models.TextField(blank=True, help_text="Any safety incidents or concerns", max_length=1000)
    
    # Notes and Observations
    general_notes = models.TextField(blank=True, max_length=1000)
    photos_taken = models.BooleanField(default=False)
    
    # Review and Status
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_entries')
    status = models.CharField(max_length=20, choices=ENTRY_STATUS, default='complete')
    reviewed_date = models.DateTimeField(null=True, blank=True)
    needs_revision = models.BooleanField(default=False)
    
    draft = models.BooleanField(default=False, help_text="Save as draft without finalizing entry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        super().clean()
        # Validate temperature consistency
        if self.temperature_high is not None and self.temperature_low is not None:
            if self.temperature_low > self.temperature_high:
                raise ValidationError('Low temperature cannot be higher than high temperature.')
    
    class Meta:
        ordering = ['-entry_date', '-created_at']
        unique_together = ['project', 'entry_date']
    
    def __str__(self):
        return f"{self.project.name} - {self.entry_date}"

class LaborEntry(models.Model):
    LABOR_TYPES = [
        ('skilled', 'Skilled Labor'),
        ('unskilled', 'Unskilled Labor'),
        ('supervisor', 'Supervisor'),
        ('engineer', 'Engineer'),
        ('foreman', 'Foreman'),
        ('specialist', 'Specialist'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='labor_entries')
    labor_type = models.CharField(max_length=20, choices=LABOR_TYPES)
    trade_description = models.CharField(max_length=100, help_text="e.g., Carpenter, Electrician, Plumber")
    workers_count = models.PositiveIntegerField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    work_area = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    @property
    def total_cost(self):
        if self.hourly_rate:
            regular_cost = self.hours_worked * self.hourly_rate * self.workers_count
            overtime_cost = self.overtime_hours * (self.hourly_rate * Decimal('1.5')) * self.workers_count
            return regular_cost + overtime_cost
        return 0
    
    def __str__(self):
        return f"{self.trade_description} - {self.workers_count} workers - {self.diary_entry.entry_date}"

class MaterialEntry(models.Model):
    MATERIAL_UNITS = [
        ('kg', 'Kilograms'),
        ('tons', 'Tons'),
        ('m3', 'Cubic Meters'),
        ('m2', 'Square Meters'),
        ('m', 'Meters'),
        ('pcs', 'Pieces'),
        ('bags', 'Bags'),
        ('liters', 'Liters'),
        ('rolls', 'Rolls'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='material_entries')
    material_name = models.CharField(max_length=100)
    quantity_delivered = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit = models.CharField(max_length=10, choices=MATERIAL_UNITS)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    supplier = models.CharField(max_length=100, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    quality_check = models.BooleanField(default=True)
    storage_location = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    @property
    def total_cost(self):
        if self.unit_cost:
            return self.quantity_delivered * self.unit_cost
        return 0
    
    def __str__(self):
        return f"{self.material_name} - {self.quantity_delivered} {self.unit}"

class EquipmentEntry(models.Model):
    EQUIPMENT_STATUS = [
        ('operational', 'Operational'),
        ('maintenance', 'Under Maintenance'),
        ('breakdown', 'Breakdown'),
        ('idle', 'Idle'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='equipment_entries')
    equipment_name = models.CharField(max_length=100)
    equipment_type = models.CharField(max_length=50, help_text="e.g., Excavator, Crane, Mixer")
    operator_name = models.CharField(max_length=100, blank=True)
    hours_operated = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fuel_consumption = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Liters")
    status = models.CharField(max_length=20, choices=EQUIPMENT_STATUS, default='operational')
    maintenance_notes = models.TextField(blank=True)
    breakdown_description = models.TextField(blank=True)
    rental_cost_per_hour = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    work_area = models.CharField(max_length=100, blank=True)
    
    @property
    def total_rental_cost(self):
        if self.rental_cost_per_hour:
            return self.hours_operated * self.rental_cost_per_hour
        return 0
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type}) - {self.diary_entry.entry_date}"

class DelayEntry(models.Model):
    DELAY_CATEGORIES = [
        ('weather', 'Weather Related'),
        ('material', 'Material Shortage'),
        ('equipment', 'Equipment Issues'),
        ('labor', 'Labor Issues'),
        ('permit', 'Permit/Approval Delays'),
        ('design', 'Design Changes'),
        ('client', 'Client Related'),
        ('safety', 'Safety Concerns'),
        ('other', 'Other'),
    ]
    
    IMPACT_LEVELS = [
        ('low', 'Low Impact'),
        ('medium', 'Medium Impact'),
        ('high', 'High Impact'),
        ('critical', 'Critical Impact'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='delay_entries')
    category = models.CharField(max_length=20, choices=DELAY_CATEGORIES)
    description = models.TextField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, help_text="Duration in hours")
    impact_level = models.CharField(max_length=10, choices=IMPACT_LEVELS)
    affected_activities = models.TextField(help_text="Which activities were affected")
    mitigation_actions = models.TextField(blank=True, help_text="Actions taken to mitigate the delay")
    responsible_party = models.CharField(max_length=100, blank=True)
    cost_impact = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.get_category_display()} - {self.duration_hours}h - {self.diary_entry.entry_date}"

class VisitorEntry(models.Model):
    VISITOR_TYPES = [
        ('client', 'Client'),
        ('inspector', 'Inspector'),
        ('consultant', 'Consultant'),
        ('supplier', 'Supplier'),
        ('contractor', 'Sub-contractor'),
        ('official', 'Government Official'),
        ('other', 'Other'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='visitor_entries')
    visitor_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPES)
    arrival_time = models.TimeField()
    departure_time = models.TimeField(null=True, blank=True)
    purpose_of_visit = models.TextField()
    areas_visited = models.CharField(max_length=200, blank=True)
    accompanied_by = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.visitor_name} ({self.company}) - {self.diary_entry.entry_date}"

class Milestone(models.Model):
    name = models.CharField(max_length=200, help_text="Milestone name (e.g., Foundation Work, Structural Framework)")
    description = models.TextField(blank=True, help_text="Detailed description of this milestone phase")
    order = models.PositiveIntegerField(default=1, help_text="Order of milestone in project sequence")
    is_active = models.BooleanField(default=True, help_text="Whether this milestone is available for selection")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class SubcontractorCompany(models.Model):
    COMPANY_TYPES = [
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('hvac', 'HVAC'),
        ('roofing', 'Roofing'),
        ('flooring', 'Flooring'),
        ('painting', 'Painting'),
        ('concrete', 'Concrete'),
        ('steel', 'Steel Work'),
        ('carpentry', 'Carpentry'),
        ('masonry', 'Masonry'),
        ('landscaping', 'Landscaping'),
        ('security', 'Security'),
        ('cleaning', 'Cleaning'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    company_type = models.CharField(max_length=20, choices=COMPANY_TYPES)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Subcontractor Companies'
    
    def __str__(self):
        return f"{self.name} - {self.get_company_type_display()}"

class WorkerType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="Worker type name (e.g., Supervisor, Skilled Labor)")
    description = models.CharField(max_length=200, blank=True, help_text="Brief description of this worker type")
    default_daily_rate = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Default daily rate in PHP")
    is_active = models.BooleanField(default=True, help_text="Whether this worker type is available for selection")
    order = models.PositiveIntegerField(default=1, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class SubcontractorEntry(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='subcontractor_entries')
    company_name = models.CharField(max_length=200)
    work_description = models.TextField()
    daily_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.diary_entry.entry_date}"

class DiaryPhoto(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='diary_photos/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.diary_entry} - {self.caption}"
