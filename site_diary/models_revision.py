from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import DiaryEntry, Project

class RevisionRequest(models.Model):
    REVISION_TYPES = [
        ('weather_correction', 'Weather Data Correction'),
        ('personnel_update', 'Personnel Update'),
        ('materials_adjustment', 'Materials/Equipment Adjustment'),
        ('work_progress_update', 'Work Progress Update'),
        ('quality_safety_update', 'Quality/Safety Update'),
        ('milestone_update', 'Milestone Update'),
        ('documentation_correction', 'Documentation Correction'),
        ('budget_adjustment', 'Budget Adjustment'),
        ('other', 'Other'),
    ]
    
    REVISION_STATUS = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    
    IMPACT_LEVELS = [
        ('no_impact', 'No Impact - Minor correction'),
        ('low_impact', 'Low Impact - Small adjustments'),
        ('medium_impact', 'Medium Impact - Moderate changes'),
        ('high_impact', 'High Impact - Significant changes'),
        ('critical_impact', 'Critical Impact - Major revisions'),
    ]
    
    diary_entry = models.ForeignKey(DiaryEntry, on_delete=models.CASCADE, related_name='revision_requests')
    revision_type = models.CharField(max_length=30, choices=REVISION_TYPES)
    revision_reason = models.CharField(max_length=50)
    description = models.TextField(help_text="Detailed description of changes")
    impact_level = models.CharField(max_length=20, choices=IMPACT_LEVELS)
    
    # Budget Impact Fields
    estimated_cost_impact = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Estimated additional cost")
    actual_cost_impact = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Actual cost after implementation")
    
    # Approval workflow
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='revision_requests')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_revisions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_revisions')
    
    status = models.CharField(max_length=20, choices=REVISION_STATUS, default='pending')
    rejection_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Revision {self.id} - {self.diary_entry.project.name} - {self.get_revision_type_display()}"
    
    @property
    def project(self):
        return self.diary_entry.project
    
    def approve(self, approved_by_user):
        """Approve the revision and update project budget"""
        self.status = 'approved'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()
        
        # Update project budget if there's cost impact
        if self.estimated_cost_impact > 0:
            self.update_project_budget()
    
    def implement(self, implemented_by_user, actual_cost=None):
        """Mark revision as implemented and update actual costs"""
        self.status = 'implemented'
        self.implemented_at = timezone.now()
        if actual_cost is not None:
            self.actual_cost_impact = actual_cost
        self.save()
        
        # Update project budget with actual costs
        self.update_project_budget(use_actual=True)
    
    def update_project_budget(self, use_actual=False):
        """Update project budget based on revision impact"""
        cost_impact = self.actual_cost_impact if use_actual and self.actual_cost_impact else self.estimated_cost_impact
        
        if cost_impact > 0:
            project = self.diary_entry.project
            # Create budget adjustment record
            BudgetAdjustment.objects.create(
                project=project,
                revision_request=self,
                adjustment_amount=cost_impact,
                adjustment_type='revision_impact',
                description=f"Budget adjustment due to revision: {self.description[:100]}",
                created_by=self.approved_by or self.requested_by
            )

class BudgetAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('revision_impact', 'Revision Impact'),
        ('scope_change', 'Scope Change'),
        ('material_price_change', 'Material Price Change'),
        ('labor_rate_change', 'Labor Rate Change'),
        ('equipment_cost_change', 'Equipment Cost Change'),
        ('delay_penalty', 'Delay Penalty'),
        ('bonus_payment', 'Bonus Payment'),
        ('other', 'Other'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budget_adjustments')
    revision_request = models.ForeignKey(RevisionRequest, on_delete=models.SET_NULL, null=True, blank=True)
    
    adjustment_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="Positive for increase, negative for decrease")
    adjustment_type = models.CharField(max_length=30, choices=ADJUSTMENT_TYPES)
    description = models.TextField()
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Budget Adjustment: {self.project.name} - {self.adjustment_amount}"

class ProjectBudgetSummary(models.Model):
    """Cached budget summary for performance"""
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='budget_summary')
    
    # Original budget
    original_budget = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Actual costs from diary entries
    labor_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    material_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    equipment_costs = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Revision impacts
    revision_adjustments = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Calculated fields
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    adjusted_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    remaining_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_variance_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    def update_summary(self):
        """Recalculate budget summary from actual data"""
        from .models import LaborEntry, MaterialEntry, EquipmentEntry
        
        # Get all diary entries for this project
        project_entries = DiaryEntry.objects.filter(project=self.project)
        
        # Calculate actual costs
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        self.labor_costs = sum(labor.total_cost for labor in labor_entries)
        self.material_costs = sum(material.total_cost for material in material_entries)
        self.equipment_costs = sum(equipment.total_rental_cost for equipment in equipment_entries)
        
        # Calculate revision adjustments
        adjustments = BudgetAdjustment.objects.filter(project=self.project)
        self.revision_adjustments = sum(adj.adjustment_amount for adj in adjustments)
        
        # Calculate totals
        self.total_spent = self.labor_costs + self.material_costs + self.equipment_costs
        self.adjusted_budget = self.original_budget + self.revision_adjustments
        self.remaining_budget = self.adjusted_budget - self.total_spent
        
        # Calculate variance percentage
        if self.original_budget > 0:
            self.budget_variance_percentage = ((self.adjusted_budget - self.original_budget) / self.original_budget) * 100
        
        self.save()
    
    def __str__(self):
        return f"Budget Summary: {self.project.name}"