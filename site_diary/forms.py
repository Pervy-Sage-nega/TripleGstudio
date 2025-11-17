from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.html import escape
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto, SubcontractorCompany, Milestone
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
            'project', 'entry_date', 'milestone', 'weather_condition', 'temperature_high', 
            'temperature_low', 'humidity', 'wind_speed', 'work_description', 
            'progress_percentage', 'quality_issues', 'safety_incidents', 
            'general_notes', 'photos_taken'
        ]
        widgets = {
            'project': forms.Select(attrs={'class': 'form-control'}),
            'entry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'weather_condition': forms.Select(attrs={'class': 'form-control'}),
            'temperature_high': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C', 'min': '-50', 'max': '60'}),
            'temperature_low': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '°C', 'min': '-50', 'max': '60'}),
            'humidity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '%', 'min': '0', 'max': '100'}),
            'wind_speed': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'km/h', 'min': '0', 'max': '500'}),
            'work_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe work performed today', 'maxlength': '2000'}),
            'progress_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': '%'}),
            'quality_issues': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any quality issues encountered', 'maxlength': '1000'}),
            'safety_incidents': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Any safety incidents or concerns', 'maxlength': '1000'}),
            'general_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes', 'maxlength': '1000'}),
            'photos_taken': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'milestone': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter projects to show user's projects including ProjectAssignment assignments
            from admin_side.models import ProjectAssignment
            from django.db.models import Q
            
            # Get projects through assignments or direct assignment
            assigned_project_ids = ProjectAssignment.objects.filter(
                user=user, is_active=True
            ).values_list('project_id', flat=True)
            
            self.fields['project'].queryset = Project.objects.filter(
                Q(id__in=assigned_project_ids) | 
                Q(project_manager=user) | 
                Q(architect=user),
                status__in=['planning', 'active', 'on_hold', 'completed']
            )
        
        # Set up milestone field with active milestones
        self.fields['milestone'].queryset = Milestone.objects.filter(is_active=True).order_by('order', 'name')
        self.fields['milestone'].empty_label = "Select Current Phase"
        self.fields['milestone'].required = False
    
    def clean_temperature_high(self):
        temp = self.cleaned_data.get('temperature_high')
        if temp is not None and (temp < -50 or temp > 60):
            raise ValidationError('Temperature must be between -50°C and 60°C')
        return temp
    
    def clean_temperature_low(self):
        temp = self.cleaned_data.get('temperature_low')
        if temp is not None and (temp < -50 or temp > 60):
            raise ValidationError('Temperature must be between -50°C and 60°C')
        return temp
    
    def clean_humidity(self):
        humidity = self.cleaned_data.get('humidity')
        if humidity is not None and (humidity < 0 or humidity > 100):
            raise ValidationError('Humidity must be between 0% and 100%')
        return humidity
    
    def clean_wind_speed(self):
        speed = self.cleaned_data.get('wind_speed')
        if speed is not None and (speed < 0 or speed > 500):
            raise ValidationError('Wind speed must be between 0 and 500 km/h')
        return speed
    
    def clean_progress_percentage(self):
        progress = self.cleaned_data.get('progress_percentage')
        if progress is not None and (progress < 0 or progress > 100):
            raise ValidationError('Progress must be between 0% and 100%')
        return progress

class LaborEntryForm(forms.ModelForm):
    class Meta:
        model = LaborEntry
        fields = [
            'labor_type', 'trade_description', 'workers_count', 'hours_worked',
            'hourly_rate', 'overtime_hours', 'work_area', 'notes'
        ]
        widgets = {
            'labor_type': forms.Select(attrs={'class': 'form-control'}),
            'trade_description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Carpenter, Electrician', 'maxlength': '100'}),
            'workers_count': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '1000'}),
            'hours_worked': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'hourly_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'min': '0', 'max': '10000'}),
            'overtime_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'work_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work area/location', 'maxlength': '100'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes', 'maxlength': '500'}),
        }
    
    def clean_workers_count(self):
        count = self.cleaned_data.get('workers_count')
        if count is not None and (count < 1 or count > 1000):
            raise ValidationError('Workers count must be between 1 and 1000')
        return count
    
    def clean_hours_worked(self):
        hours = self.cleaned_data.get('hours_worked')
        if hours is not None and (hours < 0 or hours > 24):
            raise ValidationError('Hours worked must be between 0 and 24')
        return hours
    
    def clean_overtime_hours(self):
        hours = self.cleaned_data.get('overtime_hours')
        if hours is not None and (hours < 0 or hours > 24):
            raise ValidationError('Overtime hours must be between 0 and 24')
        return hours

class MaterialEntryForm(forms.ModelForm):
    class Meta:
        model = MaterialEntry
        fields = [
            'material_name', 'quantity_delivered', 'quantity_used', 'unit',
            'unit_cost', 'supplier', 'delivery_time', 'quality_check',
            'storage_location', 'notes'
        ]
        widgets = {
            'material_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Material name', 'maxlength': '100'}),
            'quantity_delivered': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '999999'}),
            'quantity_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '999999'}),
            'unit': forms.Select(attrs={'class': 'form-control'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'min': '0', 'max': '999999'}),
            'supplier': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier name', 'maxlength': '100'}),
            'delivery_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'quality_check': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Storage location', 'maxlength': '100'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes', 'maxlength': '500'}),
        }
    
    def clean_quantity_delivered(self):
        qty = self.cleaned_data.get('quantity_delivered')
        if qty is not None and qty < 0:
            raise ValidationError('Quantity delivered cannot be negative')
        return qty
    
    def clean_quantity_used(self):
        qty = self.cleaned_data.get('quantity_used')
        if qty is not None and qty < 0:
            raise ValidationError('Quantity used cannot be negative')
        return qty
    
    def clean(self):
        cleaned_data = super().clean()
        delivered = cleaned_data.get('quantity_delivered')
        used = cleaned_data.get('quantity_used')
        
        if delivered is not None and used is not None and used > delivered:
            raise ValidationError('Quantity used cannot exceed quantity delivered')
        
        return cleaned_data

class EquipmentEntryForm(forms.ModelForm):
    class Meta:
        model = EquipmentEntry
        fields = [
            'equipment_name', 'equipment_type', 'operator_name', 'hours_operated',
            'fuel_consumption', 'status', 'maintenance_notes', 'breakdown_description',
            'rental_cost_per_hour', 'work_area'
        ]
        widgets = {
            'equipment_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Equipment name/ID', 'maxlength': '100'}),
            'equipment_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Excavator, Crane', 'maxlength': '50'}),
            'operator_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Operator name', 'maxlength': '100'}),
            'hours_operated': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '24'}),
            'fuel_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Liters', 'min': '0', 'max': '10000'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Maintenance notes', 'maxlength': '500'}),
            'breakdown_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Breakdown description', 'maxlength': '500'}),
            'rental_cost_per_hour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'min': '0', 'max': '10000'}),
            'work_area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work area', 'maxlength': '100'}),
        }
    
    def clean_hours_operated(self):
        hours = self.cleaned_data.get('hours_operated')
        if hours is not None and (hours < 0 or hours > 24):
            raise ValidationError('Hours operated must be between 0 and 24')
        return hours

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
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe the delay', 'maxlength': '1000'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'duration_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0', 'max': '168'}),
            'impact_level': forms.Select(attrs={'class': 'form-control'}),
            'affected_activities': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Which activities were affected', 'maxlength': '500'}),
            'mitigation_actions': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Actions taken to mitigate', 'maxlength': '500'}),
            'responsible_party': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Responsible party', 'maxlength': '100'}),
            'cost_impact': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00', 'min': '0', 'max': '999999'}),
        }
    
    def clean_duration_hours(self):
        hours = self.cleaned_data.get('duration_hours')
        if hours is not None and (hours < 0 or hours > 168):  # Max 1 week
            raise ValidationError('Duration must be between 0 and 168 hours (1 week)')
        return hours

class VisitorEntryForm(forms.ModelForm):
    class Meta:
        model = VisitorEntry
        fields = [
            'visitor_name', 'company', 'visitor_type', 'arrival_time',
            'departure_time', 'purpose_of_visit', 'areas_visited',
            'accompanied_by', 'notes'
        ]
        widgets = {
            'visitor_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Visitor name', 'maxlength': '100'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name', 'maxlength': '100'}),
            'visitor_type': forms.Select(attrs={'class': 'form-control'}),
            'arrival_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'departure_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'purpose_of_visit': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Purpose of visit', 'maxlength': '500'}),
            'areas_visited': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Areas visited', 'maxlength': '200'}),
            'accompanied_by': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Accompanied by', 'maxlength': '100'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Additional notes', 'maxlength': '500'}),
        }

class DiaryPhotoForm(forms.ModelForm):
    class Meta:
        model = DiaryPhoto
        fields = ['photo', 'caption', 'location']
        widgets = {
            'photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo caption', 'maxlength': '200'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Photo location', 'maxlength': '100'}),
        }
    
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            # Validate file type
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if photo.content_type not in allowed_types:
                raise ValidationError('Invalid file type. Please upload JPEG, PNG, or GIF.')
            
            # Validate file size (max 10MB)
            if photo.size > 10 * 1024 * 1024:
                raise ValidationError('File too large. Maximum size is 10MB.')
        
        return photo

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
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by project name', 'maxlength': '200'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Project.PROJECT_STATUS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    client_name = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by client name', 'maxlength': '100'})
    )
    location = forms.CharField(
        required=False,
        max_length=300,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search by location', 'maxlength': '300'})
    )
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            return name.strip()
        return name
    
    def clean_client_name(self):
        client_name = self.cleaned_data.get('client_name')
        if client_name:
            return client_name.strip()
        return client_name
    
    def clean_location(self):
        location = self.cleaned_data.get('location')
        if location:
            return location.strip()
        return location
