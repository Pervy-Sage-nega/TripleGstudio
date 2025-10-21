from django import forms
from django.contrib.auth.models import User
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto, SubcontractorCompany
)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'name', 'description', 'client_name', 'project_manager', 
            'architect', 'location', 'start_date', 'expected_end_date', 
            'budget', 'status'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Project description'}),
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Client name'}),
            'project_manager': forms.Select(attrs={'class': 'form-control'}),
            'architect': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project location'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter users for project manager and architect
        self.fields['project_manager'].queryset = User.objects.all()
        self.fields['architect'].queryset = User.objects.all()
        self.fields['architect'].required = False

class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = [
            'project', 'entry_date', 'weather_condition', 'temperature_high', 
            'temperature_low', 'humidity', 'wind_speed', 'work_description', 
            'progress_percentage', 'quality_issues', 'safety_incidents', 
            'general_notes', 'photos_taken'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'weather_condition': forms.Select(attrs={'class': 'form-control'}),
            'temperature_high': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C'}),
            'temperature_low': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C'}),
            'humidity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%', 'min': '0', 'max': '100'}),
            'wind_speed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'km/h'}),
            'work_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe work performed today'}),
            'progress_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '%'}),
            'quality_issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any quality issues encountered'}),
            'safety_incidents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any safety incidents or concerns'}),
            'general_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
            'photos_taken': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # FORCE COMPLETE REFRESH - Delete and recreate the field
        if user:
            from django.utils import timezone
            import uuid
            
            filtered_projects = Project.objects.filter(
                project_manager=user,
                status__in=['planning', 'active', 'on_hold', 'completed']
            )
            print(f"FORM DEBUG: User {user.username} has {filtered_projects.count()} projects")
            for project in filtered_projects:
                print(f"FORM DEBUG: Project {project.id}: {project.name} (Manager: {project.project_manager})")
            
            # Completely replace the field to prevent any caching
            self.fields['project'] = forms.ModelChoiceField(
                queryset=filtered_projects,
                empty_label="Select a project...",
                widget=forms.Select(attrs={
                    'class': 'form-control',
                    'id': f'id_project_{uuid.uuid4().hex[:8]}',
                    'data-refresh': str(timezone.now().timestamp()),
                    'data-user': str(user.id)
                })
            )
        else:
            print("FORM DEBUG: No user provided, showing no projects")
            self.fields['project'].queryset = Project.objects.none()

class LaborEntryForm(forms.ModelForm):
    class Meta:
        model = LaborEntry
        fields = [
            'labor_type', 'trade_description', 'workers_count', 'hours_worked',
            'hourly_rate', 'overtime_hours', 'work_area', 'notes'
        ]
        widgets = {
            'labor_type': forms.Select(attrs={'class': 'form-control'}),
            'trade_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Carpenter, Electrician'}),
            'workers_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'work_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work area/location'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

class MaterialEntryForm(forms.ModelForm):
    class Meta:
        model = MaterialEntry
        fields = [
            'material_name', 'quantity_delivered', 'quantity_used', 'unit',
            'unit_cost', 'supplier', 'delivery_time', 'quality_check',
            'storage_location', 'notes'
        ]
        widgets = {
            'material_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material name'}),
            'quantity_delivered': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'quantity_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name'}),
            'delivery_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'quality_check': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Storage location'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

class EquipmentEntryForm(forms.ModelForm):
    class Meta:
        model = EquipmentEntry
        fields = [
            'equipment_name', 'equipment_type', 'operator_name', 'hours_operated',
            'fuel_consumption', 'status', 'maintenance_notes', 'breakdown_description',
            'rental_cost_per_hour', 'work_area'
        ]
        widgets = {
            'equipment_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Equipment name/ID'}),
            'equipment_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Excavator, Crane'}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operator name'}),
            'hours_operated': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'fuel_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Liters'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Maintenance notes'}),
            'breakdown_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Breakdown description'}),
            'rental_cost_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'work_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work area'}),
        }

class DelayEntryForm(forms.ModelForm):
    class Meta:
        model = DelayEntry
        fields = [
            'category', 'description', 'start_time', 'end_time', 'duration_hours',
            'impact_level', 'affected_activities', 'mitigation_actions',
            'responsible_party', 'cost_impact'
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the delay'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'impact_level': forms.Select(attrs={'class': 'form-control'}),
            'affected_activities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Which activities were affected'}),
            'mitigation_actions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Actions taken to mitigate'}),
            'responsible_party': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Responsible party'}),
            'cost_impact': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }

class VisitorEntryForm(forms.ModelForm):
    class Meta:
        model = VisitorEntry
        fields = [
            'visitor_name', 'company', 'visitor_type', 'arrival_time',
            'departure_time', 'purpose_of_visit', 'areas_visited',
            'accompanied_by', 'notes'
        ]
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Visitor name'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'visitor_type': forms.Select(attrs={'class': 'form-control'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'purpose_of_visit': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Purpose of visit'}),
            'areas_visited': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Areas visited'}),
            'accompanied_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accompanied by'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes'}),
        }

class DiaryPhotoForm(forms.ModelForm):
    class Meta:
        model = DiaryPhoto
        fields = ['photo', 'caption', 'location']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo caption'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo location'}),
        }

# Formsets for handling multiple entries
from django.forms import formset_factory

LaborEntryFormSet = formset_factory(LaborEntryForm, extra=1, can_delete=True)
MaterialEntryFormSet = formset_factory(MaterialEntryForm, extra=1, can_delete=True)
EquipmentEntryFormSet = formset_factory(EquipmentEntryForm, extra=1, can_delete=True)
DelayEntryFormSet = formset_factory(DelayEntryForm, extra=1, can_delete=True)
VisitorEntryFormSet = formset_factory(VisitorEntryForm, extra=1, can_delete=True)
DiaryPhotoFormSet = formset_factory(DiaryPhotoForm, extra=1, can_delete=True)

# Search and Filter Forms
class DiarySearchForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed']),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    weather_condition = forms.ChoiceField(
        choices=[('', 'All Weather')] + DiaryEntry.WEATHER_CONDITIONS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    created_by = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="All Users",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class DiaryEntrySearchForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed']),
        required=False,
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )

class ProjectSearchForm(forms.Form):
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by project name'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Project.PROJECT_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by client name'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by location'})
    )
