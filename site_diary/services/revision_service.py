from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal
from ..models import Project, DiaryEntry, LaborEntry, MaterialEntry, EquipmentEntry

class RevisionImpactService:
    """Service to handle revision impacts on project budgets and dashboard updates"""
    
    @staticmethod
    def calculate_revision_cost_impact(revision_data, diary_entry):
        """Calculate estimated cost impact based on revision type and scope"""
        
        impact_level = revision_data.get('impact_level', 'low_impact')
        revision_type = revision_data.get('revision_type')
        
        # Base cost multipliers by impact level
        impact_multipliers = {
            'no_impact': 0,
            'low_impact': 0.02,      # 2% of daily costs
            'medium_impact': 0.05,   # 5% of daily costs
            'high_impact': 0.10,     # 10% of daily costs
            'critical_impact': 0.20, # 20% of daily costs
        }
        
        # Get daily costs from the diary entry
        daily_labor_cost = sum(labor.total_cost for labor in diary_entry.labor_entries.all())
        daily_material_cost = sum(material.total_cost for material in diary_entry.material_entries.all())
        daily_equipment_cost = sum(equipment.total_rental_cost for equipment in diary_entry.equipment_entries.all())
        
        total_daily_cost = daily_labor_cost + daily_material_cost + daily_equipment_cost
        
        # Apply revision type specific adjustments
        type_multipliers = {
            'materials_adjustment': 1.5,  # Material changes typically cost more
            'work_progress_update': 1.2,  # May require rework
            'quality_safety_update': 1.3, # Safety fixes are expensive
            'milestone_update': 1.1,      # Schedule changes
            'other': 1.0,
        }
        
        base_multiplier = impact_multipliers.get(impact_level, 0.05)
        type_multiplier = type_multipliers.get(revision_type, 1.0)
        
        estimated_cost = total_daily_cost * base_multiplier * type_multiplier
        
        # Minimum cost for non-zero impacts
        if impact_level != 'no_impact' and estimated_cost < 100:
            estimated_cost = 100
        
        return round(estimated_cost, 2)
    
    @staticmethod
    def get_enhanced_dashboard_data(projects):
        """Get enhanced budget data for dashboard including revision impacts"""
        
        dashboard_data = []
        
        for project in projects:
            # Calculate existing costs
            project_entries = DiaryEntry.objects.filter(project=project)
            labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
            material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
            equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
            
            labor_costs = sum(labor.total_cost for labor in labor_entries)
            material_costs = sum(material.total_cost for material in material_entries)
            equipment_costs = sum(equipment.total_rental_cost for equipment in equipment_entries)
            total_spent = labor_costs + material_costs + equipment_costs
            
            # Calculate revision impacts (mock data for now)
            revision_count = project_entries.filter(status='needs_revision').count()
            estimated_revision_cost = revision_count * 5000  # Estimated $5000 per revision
            
            # Calculate adjusted budget
            original_budget = float(project.budget) if project.budget else 0
            adjusted_budget = original_budget + estimated_revision_cost
            remaining_budget = adjusted_budget - float(total_spent)
            
            # Calculate budget health
            if remaining_budget < 0:
                budget_status = 'over_budget'
                budget_health = 'danger'
            elif remaining_budget < (adjusted_budget * 0.1):
                budget_status = 'at_risk'
                budget_health = 'warning'
            else:
                budget_status = 'on_track'
                budget_health = 'good'
            
            # Budget usage percentage
            if adjusted_budget > 0:
                budget_used_percentage = (float(total_spent) / adjusted_budget) * 100
            else:
                budget_used_percentage = 0
            
            # Budget variance from original
            if original_budget > 0:
                budget_variance = ((adjusted_budget - original_budget) / original_budget) * 100
            else:
                budget_variance = 0
            
            dashboard_data.append({
                'project': project,
                'original_budget': original_budget,
                'adjusted_budget': adjusted_budget,
                'total_spent': float(total_spent),
                'remaining_budget': remaining_budget,
                'budget_used_percentage': min(budget_used_percentage, 100),
                'budget_variance_percentage': budget_variance,
                'revision_cost_impact': estimated_revision_cost,
                'budget_status': budget_status,
                'budget_health': budget_health,
                'revision_count': revision_count,
                'labor_costs': float(labor_costs),
                'material_costs': float(material_costs),
                'equipment_costs': float(equipment_costs),
            })
        
        return dashboard_data