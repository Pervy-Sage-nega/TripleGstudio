from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Project(models.Model):
    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=100)
    project_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_projects')
    architect = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='architect_projects')
    location = models.CharField(max_length=300)
    start_date = models.DateField()
    expected_end_date = models.DateField()
    actual_end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.client_name}"

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
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='diary_entries')
    entry_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Weather Information
    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS, blank=True)
    temperature_high = models.IntegerField(null=True, blank=True, help_text="Temperature in Celsius")
    temperature_low = models.IntegerField(null=True, blank=True, help_text="Temperature in Celsius")
    humidity = models.IntegerField(null=True, blank=True, help_text="Humidity percentage")
    wind_speed = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Wind speed in km/h")
    
    # Work Progress
    work_description = models.TextField(help_text="Description of work performed today")
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Overall project progress percentage")
    
    # Quality and Safety
    quality_issues = models.TextField(blank=True, help_text="Any quality issues encountered")
    safety_incidents = models.TextField(blank=True, help_text="Any safety incidents or concerns")
    
    # Notes and Observations
    general_notes = models.TextField(blank=True)
    photos_taken = models.BooleanField(default=False)
    
    # Approval and Review
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_entries')
    approved = models.BooleanField(default=False)
    approval_date = models.DateTimeField(null=True, blank=True)
    
    draft = models.BooleanField(default=False, help_text="Save as draft without finalizing entry")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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

class DiaryPhoto(models.Model):
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='diary_photos/%Y/%m/%d/')
    caption = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Photo for {self.diary_entry} - {self.caption}"
