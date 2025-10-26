from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Sum, Avg, Count, Max, Min
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import csv
import json
from django.core.cache import cache
from accounts.decorators import require_site_manager_role, require_admin_role
from .models import (
    Project, DiaryEntry, LaborEntry, MaterialEntry, 
    EquipmentEntry, DelayEntry, VisitorEntry, DiaryPhoto, SubcontractorCompany, Milestone, SubcontractorEntry
)
from .forms import (
    ProjectForm, DiaryEntryForm, LaborEntryFormSet, MaterialEntryFormSet,
    EquipmentEntryFormSet, DelayEntryFormSet, VisitorEntryFormSet, 
    DiaryPhotoFormSet, DiarySearchForm, DiaryEntrySearchForm, ProjectSearchForm
)
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.utils.html import escape
import requests
import logging

OPENWEATHERMAP_API_KEY = "0c461dd2b831a59146501773674950cd"
logger = logging.getLogger(__name__)

# Create your views here.
@login_required
@require_site_manager_role
@csrf_protect
def diary(request):
    """Create new diary entry with all related data, including Save as Draft support"""
    # Initialize draft_data to prevent UnboundLocalError
    draft_data = None
    
    # Get user's assigned projects only - very strict filtering
    user_projects = Project.objects.filter(
        project_manager=request.user,
        status__in=['planning', 'active', 'on_hold', 'completed']
    )
    
    if request.method == 'POST':
        save_as_draft = request.POST.get('save_as_draft') == '1'
        logger.info(f"POST request received - save_as_draft: {save_as_draft}")
        logger.info(f"POST data keys: {list(request.POST.keys())}")
        
        diary_form = DiaryEntryForm(request.POST, user=request.user)
        
        # Make work_description not required when saving as draft
        if save_as_draft:
            diary_form.fields['work_description'].required = False
        
        labor_formset = LaborEntryFormSet(request.POST, prefix='labor')
        material_formset = MaterialEntryFormSet(request.POST, prefix='material')
        equipment_formset = EquipmentEntryFormSet(request.POST, prefix='equipment')
        delay_formset = DelayEntryFormSet(request.POST, prefix='delay')
        visitor_formset = VisitorEntryFormSet(request.POST, prefix='visitor')
        photo_formset = DiaryPhotoFormSet(request.POST, request.FILES, prefix='photo')
        
        # Validate forms
        if not diary_form.is_valid():
            logger.warning(f"Diary form validation failed for user {request.user.id}: {diary_form.errors}")
        if not labor_formset.is_valid():
            logger.warning(f"Labor formset validation failed for user {request.user.id}: {labor_formset.errors}")
        if not material_formset.is_valid():
            logger.warning(f"Material formset validation failed for user {request.user.id}: {material_formset.errors}")
        if not equipment_formset.is_valid():
            logger.warning(f"Equipment formset validation failed for user {request.user.id}: {equipment_formset.errors}")
        if not delay_formset.is_valid():
            logger.warning(f"Delay formset validation failed for user {request.user.id}: {delay_formset.errors}")
        
        # Check if editing existing draft with proper validation
        edit_draft_id = request.POST.get('edit_draft_id') or request.GET.get('edit')
        editing_draft = None
        
        if edit_draft_id:
            try:
                # Validate draft_id is numeric to prevent injection
                draft_id = int(edit_draft_id)
                editing_draft = DiaryEntry.objects.get(
                    id=draft_id,
                    created_by=request.user,
                    draft=True
                )
            except (ValueError, TypeError, DiaryEntry.DoesNotExist):
                messages.error(request, 'Draft not found or access denied.')
                return redirect('site_diary:sitedraft')
        
        # For drafts, only require project and entry_date
        if save_as_draft:
            logger.info(f"Processing draft save request")
            
            # Get project and entry_date directly from POST data for drafts
            try:
                project_id = request.POST.get('project')
                entry_date = request.POST.get('entry_date')
                
                logger.info(f"Draft data - Project ID: {project_id}, Entry Date: {entry_date}")
                
                if not project_id or not entry_date:
                    error_msg = 'Please select a project and entry date to save as draft.'
                    logger.warning(f"Draft save failed - missing data: project_id={project_id}, entry_date={entry_date}")
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'message': error_msg}, status=400)
                    
                    messages.error(request, error_msg)
                    return render(request, 'site_diary/diary.html', {
                        'diary_form': diary_form,
                        'labor_formset': labor_formset,
                        'material_formset': material_formset,
                        'equipment_formset': equipment_formset,
                        'delay_formset': delay_formset,
                        'visitor_formset': visitor_formset,
                        'photo_formset': photo_formset,
                        'user_projects': user_projects,
                        'project_data': [],
                        'subcontractor_companies': SubcontractorCompany.objects.filter(is_active=True).order_by('name'),
                        'milestones': Milestone.objects.filter(is_active=True).order_by('order', 'name'),
                    })
                
                # Get project object
                project = Project.objects.get(id=project_id, project_manager=request.user)
                
            except (Project.DoesNotExist, ValueError):
                error_msg = 'Invalid project selected.'
                logger.warning(f"Draft save failed - invalid project: {project_id}")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': error_msg}, status=400)
                
                messages.error(request, error_msg)
                return redirect('site_diary:diary')
            
            # Check if draft already exists for this project and date (avoid duplicates)
            existing_draft = DiaryEntry.objects.filter(
                project=project,
                entry_date=entry_date,
                created_by=request.user,
                draft=True
            ).first()
            
            # Get milestone if provided
            milestone_id = request.POST.get('milestone')
            milestone = None
            if milestone_id:
                try:
                    milestone = Milestone.objects.get(id=milestone_id)
                except Milestone.DoesNotExist:
                    pass
            
            if existing_draft:
                # Update existing draft with all POST data
                existing_draft.milestone = milestone
                existing_draft.work_description = request.POST.get('work_description', '')
                existing_draft.progress_percentage = request.POST.get('progress_percentage', 0) or 0
                existing_draft.weather_condition = request.POST.get('weather_condition', '')
                existing_draft.temperature_high = request.POST.get('temperature_high') or None
                existing_draft.temperature_low = request.POST.get('temperature_low') or None
                existing_draft.humidity = request.POST.get('humidity') or None
                existing_draft.wind_speed = request.POST.get('wind_speed') or None
                existing_draft.quality_issues = request.POST.get('quality_issues', '')
                existing_draft.safety_incidents = request.POST.get('safety_incidents', '')
                existing_draft.general_notes = request.POST.get('general_notes', '')
                existing_draft.photos_taken = request.POST.get('photos_taken') == 'on'
                existing_draft.save()
                diary_entry = existing_draft
                logger.info(f"Updated existing draft {diary_entry.id} for user {request.user.id}")
            else:
                # Create new draft with all POST data
                diary_entry = DiaryEntry.objects.create(
                    project=project,
                    entry_date=entry_date,
                    created_by=request.user,
                    draft=True,
                    milestone=milestone,
                    work_description=request.POST.get('work_description', ''),
                    progress_percentage=request.POST.get('progress_percentage', 0) or 0,
                    weather_condition=request.POST.get('weather_condition', ''),
                    temperature_high=request.POST.get('temperature_high') or None,
                    temperature_low=request.POST.get('temperature_low') or None,
                    humidity=request.POST.get('humidity') or None,
                    wind_speed=request.POST.get('wind_speed') or None,
                    quality_issues=request.POST.get('quality_issues', ''),
                    safety_incidents=request.POST.get('safety_incidents', ''),
                    general_notes=request.POST.get('general_notes', ''),
                    photos_taken=request.POST.get('photos_taken') == 'on'
                )
                logger.info(f"Created new draft {diary_entry.id} for user {request.user.id}")
            
            # Save labor, materials, equipment, and delays data for drafts
            # Handle dynamic worker types
            from .models import WorkerType
            worker_types = WorkerType.objects.filter(is_active=True)
            
            # Clear existing labor entries for this draft (except overtime)
            LaborEntry.objects.filter(diary_entry=diary_entry).exclude(labor_type='overtime').delete()
            
            # Process each worker type dynamically
            for worker_type in worker_types:
                worker_slug = worker_type.name.lower().replace(' ', '-')
                count_field = f"{worker_slug}Count"
                rate_field = f"{worker_slug}Rate"
                
                worker_count = request.POST.get(count_field, 0)
                worker_rate = request.POST.get(rate_field, 0)
                
                if int(worker_count or 0) > 0:
                    LaborEntry.objects.create(
                        diary_entry=diary_entry,
                        labor_type=worker_slug,
                        trade_description=worker_type.name,
                        workers_count=worker_count,
                        hours_worked=8,
                        overtime_hours=0,
                        hourly_rate=worker_rate or worker_type.default_daily_rate or 0
                    )
            
            # Handle JSON data from frontend
            materials_json = request.POST.get('materials_json')
            if materials_json:
                MaterialEntry.objects.filter(diary_entry=diary_entry).delete()
                materials_data = json.loads(materials_json)
                for material_data in materials_data:
                    MaterialEntry.objects.create(
                        diary_entry=diary_entry,
                        material_name=material_data['name'],
                        quantity_delivered=material_data['quantity'],
                        unit=material_data['unit'],
                        unit_cost=material_data['cost'] / material_data['quantity'] if material_data['quantity'] > 0 else 0,
                        supplier=material_data.get('supplier', ''),
                        delivery_time=material_data.get('delivery_time')
                    )
            
            equipment_json = request.POST.get('equipment_json')
            if equipment_json:
                EquipmentEntry.objects.filter(diary_entry=diary_entry).delete()
                equipment_data = json.loads(equipment_json)
                for equip_data in equipment_data:
                    EquipmentEntry.objects.create(
                        diary_entry=diary_entry,
                        equipment_name=equip_data['name'],
                        equipment_type=equip_data['name'],
                        hours_operated=equip_data['hours'],
                        rental_cost_per_hour=equip_data['cost'] / equip_data['hours'] if equip_data['hours'] > 0 else 0,
                        operator_name=equip_data.get('operator', ''),
                        fuel_consumption=equip_data.get('fuel', 0)
                    )
            
            delays_json = request.POST.get('delays_json')
            if delays_json:
                DelayEntry.objects.filter(diary_entry=diary_entry).delete()
                delays_data = json.loads(delays_json)
                for delay_data in delays_data:
                    DelayEntry.objects.create(
                        diary_entry=diary_entry,
                        category=delay_data['type'],
                        description=delay_data['description'],
                        start_time=delay_data.get('start_time') if delay_data.get('start_time') else None,
                        end_time=delay_data.get('end_time') if delay_data.get('end_time') else None,
                        duration_hours=delay_data.get('duration', 0),
                        impact_level=delay_data['impact'],
                        mitigation_actions=delay_data.get('solution', ''),
                        affected_activities='General work activities'
                    )
            
            # Handle overtime JSON data
            overtime_json = request.POST.get('overtime_json')
            if overtime_json:
                # Clear existing overtime entries for this draft
                LaborEntry.objects.filter(diary_entry=diary_entry, labor_type='overtime').delete()
                overtime_data = json.loads(overtime_json)
                for overtime_entry in overtime_data:
                    LaborEntry.objects.create(
                        diary_entry=diary_entry,
                        labor_type='overtime',
                        trade_description=f"{overtime_entry['personnel']} {overtime_entry['role']} personnel",
                        workers_count=overtime_entry['personnel'],
                        hours_worked=overtime_entry['hours'],
                        overtime_hours=overtime_entry['hours'],
                        hourly_rate=overtime_entry['rate']
                    )
            
            # Handle subcontractor JSON data
            subcontractor_json = request.POST.get('subcontractor_json')
            print(f"DEBUG: Draft save - subcontractor_json: {subcontractor_json}")
            if subcontractor_json:
                SubcontractorEntry.objects.filter(diary_entry=diary_entry).delete()
                subcontractor_data = json.loads(subcontractor_json)
                print(f"DEBUG: Draft save - parsed subcontractor_data: {subcontractor_data}")
                for sub_data in subcontractor_data:
                    created_sub = SubcontractorEntry.objects.create(
                        diary_entry=diary_entry,
                        company_name=sub_data['name'],
                        work_description=sub_data['work'],
                        daily_cost=sub_data.get('cost', 0)
                    )
                    print(f"DEBUG: Draft save - created subcontractor: {created_sub.company_name} - {created_sub.work_description} (₱{created_sub.daily_cost})")
            else:
                print(f"DEBUG: Draft save - no subcontractor_json found in POST data")
            
            logger.info(f"Draft saved successfully with ID: {diary_entry.id}")
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Draft saved successfully!', 'draft_id': diary_entry.id})
            
            messages.success(request, 'Diary draft saved successfully!')
            return redirect('site_diary:sitedraft')
        
        # Full validation for final submission
        elif diary_form.is_valid() and material_formset.is_valid() and equipment_formset.is_valid() and labor_formset.is_valid():
            # Debug: Log all POST data
            print(f"DEBUG: Final submission - POST data keys: {list(request.POST.keys())}")
            print(f"DEBUG: Final submission - subcontractor_json: {request.POST.get('subcontractor_json')}")
            for key, value in request.POST.items():
                if 'subcontractor' in key.lower():
                    print(f"DEBUG: Final submission - {key} = {value}")
            
            # Save diary entry
            diary_entry = diary_form.save(commit=False)
            diary_entry.created_by = request.user
            diary_entry.draft = False
            diary_entry.save()
            print(f"DEBUG: Final submission - Diary entry saved with ID: {diary_entry.id}")
            
            # Handle JSON data from frontend
            materials_json = request.POST.get('materials_json')
            if materials_json:
                materials_data = json.loads(materials_json)
                for material_data in materials_data:
                    MaterialEntry.objects.create(
                        diary_entry=diary_entry,
                        material_name=material_data['name'],
                        quantity_delivered=material_data['quantity'],
                        unit=material_data['unit'],
                        unit_cost=material_data['cost'] / material_data['quantity'] if material_data['quantity'] > 0 else 0,
                        supplier=material_data.get('supplier', ''),
                        delivery_time=material_data.get('delivery_time')
                    )
            
            equipment_json = request.POST.get('equipment_json')
            if equipment_json:
                equipment_data = json.loads(equipment_json)
                for equip_data in equipment_data:
                    EquipmentEntry.objects.create(
                        diary_entry=diary_entry,
                        equipment_name=equip_data['name'],
                        equipment_type=equip_data['name'],
                        hours_operated=equip_data['hours'],
                        rental_cost_per_hour=equip_data['cost'] / equip_data['hours'] if equip_data['hours'] > 0 else 0,
                        operator_name=equip_data.get('operator', ''),
                        fuel_consumption=equip_data.get('fuel', 0)
                    )
            
            # Handle delays data
            delays_json = request.POST.get('delays_json')
            if delays_json:
                delays_data = json.loads(delays_json)
                for delay_data in delays_data:
                    DelayEntry.objects.create(
                        diary_entry=diary_entry,
                        category=delay_data['type'],
                        description=delay_data['description'],
                        start_time=delay_data.get('start_time') if delay_data.get('start_time') else None,
                        end_time=delay_data.get('end_time') if delay_data.get('end_time') else None,
                        duration_hours=delay_data.get('duration', 0),
                        impact_level=delay_data['impact'],
                        mitigation_actions=delay_data.get('solution', ''),
                        affected_activities='General work activities'
                    )
            
            # Handle overtime JSON data
            overtime_json = request.POST.get('overtime_json')
            if overtime_json:
                overtime_data = json.loads(overtime_json)
                for overtime_entry in overtime_data:
                    LaborEntry.objects.create(
                        diary_entry=diary_entry,
                        labor_type='overtime',
                        trade_description=f"{overtime_entry['personnel']} {overtime_entry['role']} personnel",
                        workers_count=overtime_entry['personnel'],
                        hours_worked=overtime_entry['hours'],
                        overtime_hours=overtime_entry['hours'],
                        hourly_rate=overtime_entry['rate']
                    )
            
            # Handle subcontractor JSON data
            subcontractor_json = request.POST.get('subcontractor_json')
            print(f"DEBUG: Main diary - subcontractor_json: {subcontractor_json}")
            if subcontractor_json:
                subcontractor_data = json.loads(subcontractor_json)
                print(f"DEBUG: Main diary - parsed subcontractor_data: {subcontractor_data}")
                for sub_data in subcontractor_data:
                    created_sub = SubcontractorEntry.objects.create(
                        diary_entry=diary_entry,
                        company_name=sub_data['name'],
                        work_description=sub_data['work'],
                        daily_cost=sub_data.get('cost', 0)
                    )
                    print(f"DEBUG: Main diary - created subcontractor: {created_sub.company_name} - {created_sub.work_description} (₱{created_sub.daily_cost})")
            else:
                print(f"DEBUG: Main diary - no subcontractor_json found in POST data")
                print(f"DEBUG: Main diary - POST keys: {list(request.POST.keys())}")
            
            # Handle dynamic worker types
            from .models import WorkerType
            worker_types = WorkerType.objects.filter(is_active=True)
            
            # Process each worker type dynamically
            for worker_type in worker_types:
                worker_slug = worker_type.name.lower().replace(' ', '-')
                count_field = f"{worker_slug}Count"
                rate_field = f"{worker_slug}Rate"
                
                worker_count = request.POST.get(count_field, 0)
                worker_rate = request.POST.get(rate_field, 0)
                
                if int(worker_count or 0) > 0:
                    LaborEntry.objects.create(
                        diary_entry=diary_entry,
                        labor_type=worker_slug,
                        trade_description=worker_type.name,
                        workers_count=worker_count,
                        hours_worked=8,
                        overtime_hours=0,
                        hourly_rate=worker_rate or worker_type.default_daily_rate or 0
                    )
            
            # Process formsets
            material_formset.instance = diary_entry
            equipment_formset.instance = diary_entry
            labor_formset.instance = diary_entry
            
            material_count = 0
            equipment_count = 0
            labor_count = 0
            
            if material_formset.is_valid():
                for form in material_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        material = form.save(commit=False)
                        material.diary_entry = diary_entry
                        material.total_cost = material.quantity_delivered * material.unit_cost
                        material.save()
                        material_count += 1
            
            if equipment_formset.is_valid():
                for form in equipment_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        equipment = form.save(commit=False)
                        equipment.diary_entry = diary_entry
                        equipment.total_rental_cost = equipment.hours_operated * equipment.rental_cost_per_hour
                        equipment.save()
                        equipment_count += 1
            
            if labor_formset.is_valid():
                for form in labor_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        labor = form.save(commit=False)
                        labor.diary_entry = diary_entry
                        labor.total_cost = labor.workers_count * labor.hours_worked * labor.hourly_rate
                        labor.save()
                        labor_count += 1
            
            logger.info(f"Saved {material_count} materials, {equipment_count} equipment, {labor_count} labor entries for diary {diary_entry.id}")
            
            if material_count > 0 or equipment_count > 0 or labor_count > 0:
                messages.success(request, f'Diary entry created successfully! Saved {material_count} materials, {equipment_count} equipment, {labor_count} labor entries.')
            else:
                messages.success(request, 'Diary entry created successfully!')
            return redirect('site_diary:history')
        else:
            # Form validation failed
            logger.warning(f"Form validation failed for user {request.user.id}")
            
            # Collect specific error messages
            error_messages = []
            if diary_form.errors:
                for field, errors in diary_form.errors.items():
                    if field == '__all__':
                        error_messages.append(f"Form errors: {', '.join(errors)}")
                    else:
                        field_name = diary_form.fields[field].label or field.replace('_', ' ').title()
                        error_messages.append(f"{field_name}: {', '.join(errors)}")
            
            if material_formset.errors:
                error_messages.append("Materials section has errors")
            
            if equipment_formset.errors:
                error_messages.append("Equipment section has errors")
                
            if labor_formset.errors:
                error_messages.append("Labor section has errors")
            
            if delay_formset.errors:
                error_messages.append("Delays section has errors")
            
            if visitor_formset.errors:
                error_messages.append("Visitors section has errors")
            
            if photo_formset.errors:
                error_messages.append("Photos section has errors")
            
            if error_messages:
                messages.error(request, 'Please fix the following errors: ' + '; '.join(error_messages))
            else:
                messages.error(request, 'Please correct the form errors and try again.')
    else:
        
        # Check if editing an existing draft with proper validation
        edit_draft_id = request.GET.get('edit')
        draft_instance = None
        draft_data = None
        
        if edit_draft_id:
            try:
                # Validate draft_id is numeric to prevent injection
                draft_id = int(edit_draft_id)
                draft_instance = DiaryEntry.objects.get(
                    id=draft_id,
                    created_by=request.user,
                    draft=True
                )
                logger.info(f"Editing draft {draft_instance.id} for user {request.user.id}")
                
                # Get all related data for the draft
                labor_entries = LaborEntry.objects.filter(diary_entry=draft_instance)
                material_entries = MaterialEntry.objects.filter(diary_entry=draft_instance)
                equipment_entries = EquipmentEntry.objects.filter(diary_entry=draft_instance)
                delay_entries = DelayEntry.objects.filter(diary_entry=draft_instance)
                subcontractor_entries = SubcontractorEntry.objects.filter(diary_entry=draft_instance)
                
                # Prepare draft data for JavaScript
                from django.core.serializers.json import DjangoJSONEncoder
                
                draft_data = {
                    'id': draft_instance.id,
                    'project_id': draft_instance.project.id,
                    'entry_date': draft_instance.entry_date.strftime('%Y-%m-%d'),
                    'work_description': draft_instance.work_description or '',
                    'progress_percentage': float(draft_instance.progress_percentage) if draft_instance.progress_percentage else 0,
                    'milestone_id': draft_instance.milestone.id if draft_instance.milestone else None,
                    'weather_condition': draft_instance.weather_condition or '',
                    'temperature_high': float(draft_instance.temperature_high) if draft_instance.temperature_high else None,
                    'temperature_low': float(draft_instance.temperature_low) if draft_instance.temperature_low else None,
                    'humidity': float(draft_instance.humidity) if draft_instance.humidity else None,
                    'wind_speed': float(draft_instance.wind_speed) if draft_instance.wind_speed else None,
                    'quality_issues': draft_instance.quality_issues or '',
                    'safety_incidents': draft_instance.safety_incidents or '',
                    'general_notes': draft_instance.general_notes or '',
                    'photos_taken': draft_instance.photos_taken,
                    
                    # Related data
                    'materials': [{
                        'name': m.material_name,
                        'quantity': float(m.quantity_delivered),
                        'unit': m.unit,
                        'cost': float(m.total_cost),
                        'supplier': m.supplier,
                        'delivery_time': m.delivery_time.strftime('%H:%M') if m.delivery_time else ''
                    } for m in material_entries],
                    
                    'equipment': [{
                        'name': e.equipment_name,
                        'operator': e.operator_name,
                        'hours': float(e.hours_operated),
                        'fuel': float(e.fuel_consumption) if e.fuel_consumption else 0,
                        'cost': float(e.total_rental_cost)
                    } for e in equipment_entries],
                    
                    'delays': [{
                        'type': d.category,
                        'impact': d.impact_level,
                        'description': d.description,
                        'start_time': d.start_time.strftime('%H:%M') if d.start_time else '',
                        'end_time': d.end_time.strftime('%H:%M') if d.end_time else '',
                        'duration': float(d.duration_hours),
                        'solution': d.mitigation_actions
                    } for d in delay_entries],
                    
                    'subcontractors': [{
                        'name': s.company_name,
                        'work': s.work_description,
                        'cost': float(s.daily_cost)
                    } for s in subcontractor_entries],
                    
                    'labor': {},
                    'overtime': []
                }
                
                # Process labor entries by type
                for labor in labor_entries:
                    if labor.labor_type == 'overtime':
                        # Parse overtime data from trade_description
                        # Format: "X role personnel"
                        parts = labor.trade_description.split(' ')
                        personnel = labor.workers_count
                        role = ' '.join(parts[1:-1]) if len(parts) > 2 else 'worker'
                        
                        draft_data['overtime'].append({
                            'personnel': personnel,
                            'role': role,
                            'hours': labor.hours_worked,
                            'rate': float(labor.hourly_rate)
                        })
                    else:
                        # Regular labor type
                        draft_data['labor'][labor.labor_type] = {
                            'count': labor.workers_count,
                            'rate': float(labor.hourly_rate)
                        }
                
            except (ValueError, TypeError, DiaryEntry.DoesNotExist):
                messages.error(request, 'Draft not found or access denied.')
                return redirect('site_diary:sitedraft')
        
        diary_form = DiaryEntryForm(instance=draft_instance, user=request.user)
        
        # Make work_description not required when editing draft
        if draft_instance:
            diary_form.fields['work_description'].required = False
        
        labor_formset = LaborEntryFormSet(prefix='labor')
        material_formset = MaterialEntryFormSet(prefix='material')
        equipment_formset = EquipmentEntryFormSet(prefix='equipment')
        delay_formset = DelayEntryFormSet(prefix='delay')
        visitor_formset = VisitorEntryFormSet(prefix='visitor')
        photo_formset = DiaryPhotoFormSet(prefix='photo')
    
    # Get project data for budget calculations
    project_data = []
    for project in user_projects:
        # Calculate existing costs for this project
        project_entries = DiaryEntry.objects.filter(project=project)
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        total_spent = (
            sum(labor.total_cost for labor in labor_entries) +
            sum(material.total_cost for material in material_entries) +
            sum(equipment.total_rental_cost for equipment in equipment_entries)
        )
        
        project_data.append({
            'id': project.id,
            'name': project.name,
            'location': project.location,
            'budget': float(project.budget) if project.budget else 0,
            'spent': float(total_spent),
            'remaining': float(project.budget) - float(total_spent) if project.budget else -float(total_spent)
        })
    
    # Get active subcontractor companies for dropdown
    subcontractor_companies = SubcontractorCompany.objects.filter(is_active=True).order_by('name')
    
    # Get active milestones for dropdown
    milestones = Milestone.objects.filter(is_active=True).order_by('order', 'name')
    
    # Get active worker types for dynamic form generation
    from .models import WorkerType
    worker_types = WorkerType.objects.filter(is_active=True).order_by('order', 'name')
    
    context = {
        'diary_form': diary_form,
        'labor_formset': labor_formset,
        'material_formset': material_formset,
        'equipment_formset': equipment_formset,
        'delay_formset': delay_formset,
        'visitor_formset': visitor_formset,
        'photo_formset': photo_formset,
        'user_projects': user_projects,
        'project_data': project_data,
        'subcontractor_companies': subcontractor_companies,
        'milestones': milestones,
        'worker_types': worker_types,
        'draft_data_json': json.dumps(draft_data, cls=DjangoJSONEncoder) if draft_data else None,
        'draft_data': draft_data,
        'editing_draft': draft_instance is not None,
        'edit_draft_id': draft_instance.id if draft_instance else None,
    }
    return render(request, 'site_diary/diary.html', context)

@login_required
@require_site_manager_role
def dashboard(request):
    """Site Manager Enhanced dashboard with comprehensive project overview"""
    # Check for success modal flag
    success_modal_data = request.session.pop('show_success_modal', None)
    approval_modal_data = success_modal_data  # For template compatibility
    # Get user's approved projects only
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Enhanced project data with progress and analytics
    project_data = []
    
    for project in projects:
        # Get latest non-draft diary entry for progress
        latest_entry = DiaryEntry.objects.filter(project=project, draft=False).order_by('-entry_date').first()
        
        # Calculate project analytics
        project_entries = DiaryEntry.objects.filter(project=project, draft=False)
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
        
        # Calculate milestone-based progress
        if latest_entry and latest_entry.milestone and latest_entry.progress_percentage is not None:
            # Use milestone + percentage completion of that milestone
            milestone_progress = float(latest_entry.progress_percentage)
            current_milestone = latest_entry.milestone
            print(f"DEBUG: Project {project.name} - Milestone: {current_milestone.name}, Completion: {milestone_progress}%")
            progress = milestone_progress
        elif latest_entry and latest_entry.progress_percentage is not None:
            # Fallback to direct progress percentage
            progress = float(latest_entry.progress_percentage)
            current_milestone = None
            print(f"DEBUG: Project {project.name} - Direct progress: {progress}%")
        else:
            # Default progress calculation
            progress = float(project.get_progress_percentage())
            current_milestone = None
            print(f"DEBUG: Project {project.name} - Default progress: {progress}%")
        
        # Budget calculations with revision impact analysis
        total_labor_cost = sum(float(labor.total_cost) for labor in labor_entries if labor.total_cost)
        total_material_cost = sum(float(material.total_cost) for material in material_entries if material.total_cost)
        total_equipment_cost = sum(float(equipment.total_rental_cost) for equipment in equipment_entries if equipment.total_rental_cost)
        subcontractor_entries = SubcontractorEntry.objects.filter(diary_entry__in=project_entries)
        delay_cost_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
        total_subcontractor_cost = sum(float(sub.daily_cost) for sub in subcontractor_entries if sub.daily_cost)
        total_delay_cost = sum(float(delay.cost_impact) for delay in delay_cost_entries if delay.cost_impact)
        total_spent = total_labor_cost + total_material_cost + total_equipment_cost + total_subcontractor_cost + total_delay_cost
        
        # Calculate revision impacts
        revision_entries = project_entries.filter(status='needs_revision')
        revision_count = revision_entries.count()
        
        # Estimate revision cost impact based on project complexity and revision count (PHP)
        base_revision_cost = 100000  # Base cost per revision ₱100,000
        complexity_multiplier = 1.0
        if total_spent > 5000000:  # Large project ₱5M+
            complexity_multiplier = 1.5
        elif total_spent > 2500000:  # Medium project ₱2.5M+
            complexity_multiplier = 1.2
        
        estimated_revision_cost = revision_count * base_revision_cost * complexity_multiplier
        
        # Calculate adjusted budget including revision impacts
        original_budget = float(project.budget) if project.budget else 0
        adjusted_budget = original_budget + estimated_revision_cost
        remaining_budget = adjusted_budget - total_spent
        
        # Budget health assessment
        if remaining_budget < 0:
            budget_health = 'danger'
        elif remaining_budget < (adjusted_budget * 0.1):  # Less than 10% remaining
            budget_health = 'warning'
        else:
            budget_health = 'good'
        
        # Calculate budget usage percentage based on original budget
        if original_budget > 0:
            budget_used_percentage = min((total_spent / original_budget) * 100, 100)
        else:
            budget_used_percentage = 0
        
        # Debug output
        print(f"DEBUG Budget: Project={project.name}, Budget={original_budget}, Spent={total_spent}, Percentage={budget_used_percentage}%")
        
        # Budget variance from original
        if original_budget > 0:
            budget_variance = ((adjusted_budget - original_budget) / original_budget) * 100
        else:
            budget_variance = 0
        
        # Determine current phase based on progress
        if progress < 25:
            phase_name = "Planning"
        elif progress < 50:
            phase_name = "Foundation"
        elif progress < 75:
            phase_name = "Structure"
        else:
            phase_name = "Finishing"
        
        # Calculate schedule status based on actual delays
        delay_count = delay_entries.count()
        if delay_count == 0:
            schedule_status = 'On Track'
        elif delay_count < 3:
            schedule_status = 'Minor Delays'
        else:
            schedule_status = 'At Risk'
            
        # Get project milestones with proper progression logic
        milestones = Milestone.objects.filter(is_active=True).order_by('order')[:4]
        project_milestones = []
        current_milestone_order = None
        
        # Find current milestone order
        if latest_entry and latest_entry.milestone:
            current_milestone_order = latest_entry.milestone.order
        
        for i, milestone in enumerate(milestones):
            milestone.threshold = (i + 1) * 25  # 25%, 50%, 75%, 100%
            
            if current_milestone_order is not None:
                if milestone.order < current_milestone_order:
                    # Previous milestones are completed (100%)
                    milestone.is_completed = True
                    milestone.is_current = False
                    milestone.completion_percentage = 100
                elif milestone.order == current_milestone_order:
                    # Current milestone in progress
                    milestone.is_completed = False
                    milestone.is_current = True
                    milestone.completion_percentage = float(latest_entry.progress_percentage) if latest_entry.progress_percentage else 0
                else:
                    # Future milestones not started
                    milestone.is_completed = False
                    milestone.is_current = False
                    milestone.completion_percentage = 0
            else:
                # No milestone set
                milestone.is_completed = False
                milestone.is_current = False
                milestone.completion_percentage = 0
            
            project_milestones.append(milestone)
        
        # Get current milestone info
        current_milestone_id = latest_entry.milestone.id if latest_entry and latest_entry.milestone else None
        current_milestone_name = latest_entry.milestone.name if latest_entry and latest_entry.milestone else 'Not Set'
        
        # Add calculated fields directly to project object
        project.progress = progress
        project.current_phase = f"Phase {min(int(progress/25) + 1, 4)} - {phase_name}"
        project.current_milestone = current_milestone_name
        project.milestone_completion = float(latest_entry.progress_percentage) if latest_entry and latest_entry.progress_percentage else 0
        project.budget_used = budget_used_percentage
        project.schedule_status = schedule_status
        project.milestones = project_milestones
        project.current_milestone_id = current_milestone_id
        
        # Add revision impact data - only if there are actual revisions
        project.original_budget = original_budget
        project.adjusted_budget = adjusted_budget
        project.remaining_budget = remaining_budget
        project.budget_health = budget_health
        project.budget_variance = budget_variance
        project.revision_count = revision_count if revision_count > 0 else 0
        project.revision_cost_impact = estimated_revision_cost if revision_count > 0 else 0
        project.total_spent = total_spent
        
        project_data.append(project)
    
    # Dashboard statistics
    total_projects = projects.count()
    active_projects = projects.filter(status='active').count()
    at_risk_projects = projects.filter(status='on_hold').count()
    total_entries = DiaryEntry.objects.filter(project__in=projects).count()
    draft_entries = DiaryEntry.objects.filter(project__in=projects, draft=True).count()
    
    # Recent delays
    recent_delays = DelayEntry.objects.filter(
        diary_entry__project__in=projects
    ).select_related('diary_entry__project').order_by('-diary_entry__entry_date')[:5]
    
    # Get recent diary entries
    recent_entries = DiaryEntry.objects.filter(
        project__in=projects
    ).select_related('project', 'created_by').order_by('-entry_date')[:5]
    
    context = {
        'projects': project_data[:5],  # Show only 5 recent projects with enhanced data
        'recent_entries': recent_entries,
        'recent_delays': recent_delays,
        'stats': {
            'total_projects': total_projects,
            'active_projects': active_projects,
            'at_risk': at_risk_projects,
            'draft_entries': draft_entries,
        },
        'success_modal_data': success_modal_data,
        'approval_modal_data': approval_modal_data
    }
    return render(request, 'site_diary/dashboard.html', context)

@login_required
@require_site_manager_role
def diary_logs(request):
    """Diary logs view - shows diary entries for specific project"""
    project_id = request.GET.get('project')
    if not project_id:
        messages.error(request, 'No project specified.')
        return redirect('site_diary:dashboard')
    
    project = get_object_or_404(Project, id=project_id)
    
    if not request.user.is_staff:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
        if project not in user_projects:
            messages.error(request, 'Access denied.')
            return redirect('site_diary:dashboard')
    
    entries = DiaryEntry.objects.filter(project=project, draft=False).select_related(
        'created_by', 'milestone'
    ).order_by('-entry_date')
    
    paginator = Paginator(entries, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'project': project,
        'total_entries': entries.count(),
    }
    return render(request, 'site_diary/diary_logs.html', context)

@require_site_manager_role
@require_http_methods(["GET"])
def weather_api(request):
    """Weather API endpoint for fetching weather data"""
    location = request.GET.get('location', '').strip()
    
    # Validate location input
    if not location or len(location) > 100:
        return JsonResponse({'error': 'Invalid location parameter'}, status=400)
    
    # Sanitize location input to prevent injection
    location = escape(location)
    
    try:
        from django.conf import settings
        
        # Use OpenWeatherMap API
        api_key = getattr(settings, 'WEATHER_API_KEY', OPENWEATHERMAP_API_KEY)
        api_url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': location,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(api_url, params=params, timeout=10)
                
        if response.status_code == 200:
            data = response.json()
            
            # Validate API response structure
            if not all(key in data for key in ['main', 'weather', 'wind']):
                return JsonResponse({'error': 'Invalid weather data received'}, status=500)
            
            weather_data = {
                'temperature': round(float(data['main']['temp'])),
                'temperature_high': round(float(data['main']['temp_max'])),
                'temperature_low': round(float(data['main']['temp_min'])),
                'humidity': int(data['main']['humidity']),
                'wind_speed': round(float(data['wind']['speed']) * 3.6),  # Convert m/s to km/h
                'description': escape(data['weather'][0]['description']),
                'condition': escape(data['weather'][0]['main']),
                'icon': escape(data['weather'][0]['icon']),
                'location': location
            }
            return JsonResponse(weather_data)
        else:
            logger.warning(f"Weather API failed for location {location}: {response.status_code}")
            return JsonResponse({'error': 'Weather data not found'}, status=404)
                    
    except requests.RequestException as e:
        logger.error(f"Weather API request failed: {str(e)}")
        # Fallback to mock data if API fails
        weather_data = {
            'temperature': 28,
            'temperature_high': 32,
            'temperature_low': 24,
            'humidity': 65,
            'wind_speed': 12,
            'description': 'Partly Cloudy',
            'condition': 'Clouds',
            'icon': '02d',
            'location': location
        }
        return JsonResponse(weather_data)
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Weather data parsing error: {str(e)}")
        return JsonResponse({'error': 'Weather service error'}, status=500)
    except Exception as e:
        logger.error(f"Unexpected weather API error: {str(e)}")
        return JsonResponse({'error': 'Weather service error'}, status=500)

@require_site_manager_role
def print_preview(request, project_id):
    """Print preview for project"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                messages.error(request, 'Access denied.')
                return redirect('site_diary:dashboard')
        
        return render(request, 'site_diary/print_preview.html', {'project': project})
    except (ValueError, TypeError):
        messages.error(request, 'Invalid project ID.')
        return redirect('site_diary:dashboard')

@require_site_manager_role
def diary_entry_pdf(request, entry_id):
    """Generate PDF for specific diary entry using printlayout template"""
    try:
        entry_id = int(entry_id)
        diary_entry = get_object_or_404(DiaryEntry, id=entry_id)
        
        # Verify user has access to this entry's project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if diary_entry.project not in user_projects:
                messages.error(request, 'Access denied.')
                return redirect('site_diary:history')
        
        # Get the project
        project = diary_entry.project
        
        # Render the printlayout template with all necessary data
        context = {
            'project': project,
            'diary_entry': diary_entry,
        }
        
        return render(request, 'site_diary/printlayout.html', context)
        
    except (ValueError, TypeError):
        messages.error(request, 'Invalid entry ID.')
        return redirect('site_diary:history')
    except Exception as e:
        logger.error(f"PDF generation error for entry {entry_id}: {str(e)}")
        messages.error(request, 'Error generating PDF.')
        return redirect('site_diary:history')

@require_site_manager_role
def sample_print(request):
    """Sample print view"""
    return render(request, 'site_diary/sample_print.html')

@require_site_manager_role
@require_http_methods(["POST"])
@csrf_protect
def generate_project_report(request, project_id):
    """Generate project report API"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Generate report logic here
        report_data = {
            'status': 'success',
            'report_url': f'/reports/{project_id}/',
            'project_name': escape(project.name)
        }
        return JsonResponse(report_data)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return JsonResponse({'error': 'Report generation failed'}, status=500)

@require_site_manager_role
@require_http_methods(["GET"])
def api_filter_projects(request):
    """API for filtering projects"""
    status = request.GET.get('status', '').strip()
    category = request.GET.get('category', '').strip()
    
    # Get user's projects only
    if request.user.is_staff:
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
    
    # Validate and apply filters
    if status and status in dict(Project.PROJECT_STATUS):
        projects = projects.filter(status=status)
    if category:
        # Assuming category field exists, validate against allowed values
        projects = projects.filter(category=escape(category))
        
    project_data = []
    for project in projects[:50]:  # Limit results to prevent DoS
        project_data.append({
            'id': project.id,
            'name': escape(project.name),
            'status': project.status,
            'client_name': escape(project.client_name),
        })
    
    return JsonResponse({'projects': project_data})

@require_site_manager_role
def adminclientproject(request):
    """Admin client project management"""
    return render(request, 'site_diary/admin/clientproject.html')

@require_site_manager_role
def admindiary(request):
    """Admin diary management"""
    return render(request, 'site_diary/admin/diary.html')



@require_admin_role
def adminhistory(request):
    """Admin history view"""
    return render(request, 'site_diary/admin/history.html')

@require_admin_role
def adminreports(request):
    """Admin reports view with comprehensive analytics and dynamic data - shows ALL projects"""
    from django.db.models import Sum, Avg, Count, Max, Min
    from decimal import Decimal
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_project = request.GET.get('project')
    selected_architect = request.GET.get('architect')
    selected_location = request.GET.get('location')
    selected_client = request.GET.get('client')
    
    # Get ALL projects (admin sees everything)
    projects = Project.objects.all()
    
    # Apply filters to projects
    if selected_project:
        try:
            projects = projects.filter(id=int(selected_project))
        except (ValueError, TypeError):
            pass
    
    if selected_architect:
        try:
            projects = projects.filter(project_manager_id=int(selected_architect))
        except (ValueError, TypeError):
            pass
    
    if selected_location:
        projects = projects.filter(location__icontains=selected_location)
    
    if selected_client:
        projects = projects.filter(client_name__icontains=selected_client)
    
    # Get diary entries for the filtered projects
    entries = DiaryEntry.objects.filter(project__in=projects, draft=False)
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Overall summary statistics for ALL projects
    total_projects = Project.objects.count()
    total_entries = entries.count()
    total_delays = DelayEntry.objects.filter(diary_entry__in=entries).count()
    active_projects = Project.objects.filter(status='active').count()
    
    # Budget analysis across ALL projects
    total_budget = Project.objects.aggregate(total=Sum('budget'))['total'] or 0
    
    # Calculate total spent across ALL projects
    labor_entries = LaborEntry.objects.filter(diary_entry__in=entries)
    material_entries = MaterialEntry.objects.filter(diary_entry__in=entries)
    equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=entries)
    
    total_labor_cost = sum(labor.total_cost for labor in labor_entries)
    total_material_cost = sum(material.total_cost for material in material_entries)
    total_equipment_cost = sum(equipment.total_rental_cost for equipment in equipment_entries)
    total_spent = total_labor_cost + total_material_cost + total_equipment_cost
    
    budget_usage_percentage = (float(total_spent) / float(total_budget) * 100) if total_budget > 0 else 0
    
    # Project statistics for reports table - ALL projects with approved entries count
    project_stats = []
    
    try:
        for project in projects.order_by('-created_at'):
            project_entries = DiaryEntry.objects.filter(project=project, draft=False)
            
            # Calculate project costs
            project_labor = LaborEntry.objects.filter(diary_entry__in=project_entries)
            project_materials = MaterialEntry.objects.filter(diary_entry__in=project_entries)
            project_equipment = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
            project_delays = DelayEntry.objects.filter(diary_entry__in=project_entries)
            
            project_total_cost = (
                sum(labor.total_cost for labor in project_labor) +
                sum(material.total_cost for material in project_materials) +
                sum(equipment.total_rental_cost for equipment in project_equipment)
            )
            
            # Determine status based on delays and progress
            delay_count = project_delays.count()
            latest_entry = project_entries.order_by('-entry_date').first()
            progress = float(latest_entry.progress_percentage) if latest_entry and latest_entry.progress_percentage else 0
            
            if progress >= 100:
                status = 'Completed'
            elif delay_count > 3:
                status = 'Delayed'
            else:
                status = 'In Progress'
            
            # Count approved entries (status='complete')
            approved_entries = project_entries.filter(status='complete').count()
            
            # Use a simple dictionary with explicit structure
            project_stat = {
                'project': project,
                'entries_count': project_entries.count(),
                'approved_entries': approved_entries,
                'total_delays': delay_count,
                'total_cost': project_total_cost,
                'status': status,
                'progress': progress
            }
            project_stats.append(project_stat)
    except Exception as e:
        # If there's an error, provide empty list to prevent template errors
        logger.error(f"Error building project stats: {str(e)}")
        project_stats = []
    
    # Labor distribution analysis
    labor_stats = LaborEntry.objects.filter(
        diary_entry__in=entries
    ).values('labor_type').annotate(
        total_workers=Sum('workers_count'),
        total_hours=Sum('hours_worked'),
        total_cost=Sum('hourly_rate'),
        entry_count=Count('id')
    ).order_by('-total_hours')
    
    # Material analysis
    material_stats = MaterialEntry.objects.filter(
        diary_entry__in=entries
    ).values('material_name').annotate(
        total_delivered=Sum('quantity_delivered'),
        total_cost=Sum('unit_cost'),
        entry_count=Count('id')
    ).order_by('-total_delivered')[:10]
    
    # Delay analysis
    delay_stats = DelayEntry.objects.filter(
        diary_entry__in=entries
    ).values('category').annotate(
        count=Count('id'),
        total_hours=Sum('duration_hours'),
        avg_impact=Avg('cost_impact')
    ).order_by('-total_hours')
    
    # Weather analysis
    weather_stats = entries.exclude(weather_condition='').values('weather_condition').annotate(
        count=Count('id'),
        avg_temp_high=Avg('temperature_high'),
        avg_temp_low=Avg('temperature_low')
    ).order_by('-count')
    
    # Equipment utilization
    equipment_stats = EquipmentEntry.objects.filter(
        diary_entry__in=entries
    ).values('equipment_type').annotate(
        total_hours=Sum('hours_operated'),
        total_cost=Sum('rental_cost_per_hour'),
        utilization_days=Count('diary_entry__entry_date', distinct=True)
    ).order_by('-total_hours')
    
    # Budget forecast analysis
    budget_forecast_data = []
    for project in Project.objects.filter(budget__gt=0)[:5]:  # Top 5 projects by budget
        project_entries = DiaryEntry.objects.filter(project=project, draft=False)
        project_labor = LaborEntry.objects.filter(diary_entry__in=project_entries)
        project_materials = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        project_equipment = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        actual_cost = (
            sum(labor.total_cost for labor in project_labor) +
            sum(material.total_cost for material in project_materials) +
            sum(equipment.total_rental_cost for equipment in project_equipment)
        )
        
        budget_forecast_data.append({
            'project_name': project.name,
            'budget': float(project.budget),
            'actual': float(actual_cost),
            'variance': float(project.budget) - float(actual_cost)
        })
    
    # Get unique values for filters
    all_projects = Project.objects.all().order_by('name')
    all_architects = User.objects.filter(
        managed_projects__isnull=False
    ).distinct().order_by('first_name', 'last_name')
    all_locations = Project.objects.values_list('location', flat=True).distinct()
    all_clients = Project.objects.values_list('client_name', flat=True).distinct()
    
    # Serialize data for JavaScript
    def serialize_data(data):
        if isinstance(data, list):
            return [serialize_data(item) for item in data]
        elif isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key == 'project' and hasattr(value, 'id'):
                    # Serialize Project objects to basic info
                    result[key] = {
                        'id': value.id,
                        'name': value.name,
                        'budget': float(value.budget) if value.budget else 0
                    }
                else:
                    result[key] = serialize_data(value)
            return result
        elif isinstance(data, Decimal):
            return float(data)
        elif hasattr(data, 'isoformat'):
            return data.isoformat()
        else:
            return data
    
    # Debug: Check project_stats structure before passing to template
    logger.info(f"Project stats count: {len(project_stats)}")
    for i, stat in enumerate(project_stats[:3]):  # Check first 3 items
        logger.info(f"Stat {i}: type={type(stat)}, keys={list(stat.keys()) if isinstance(stat, dict) else 'not dict'}")
    
    context = {
        # Summary data
        'overall_summary': {
            'total_projects': total_projects,
            'total_entries': total_entries,
            'total_delays': total_delays,
            'budget_usage': round(budget_usage_percentage, 1),
        },
        
        # Statistics - ensure it's a clean list
        'project_stats': project_stats if isinstance(project_stats, list) else [],
        'labor_stats': list(labor_stats) if labor_stats else [],
        'material_stats': list(material_stats) if material_stats else [],
        'delay_stats': list(delay_stats) if delay_stats else [],
        'weather_stats': list(weather_stats) if weather_stats else [],
        'equipment_stats': list(equipment_stats) if equipment_stats else [],
        'budget_forecast_data': budget_forecast_data if isinstance(budget_forecast_data, list) else [],
        
        # Filter options
        'projects': all_projects,
        'architects': all_architects,
        'locations': list(all_locations) if all_locations else [],
        'clients': list(all_clients) if all_clients else [],
        
        # Current filter values
        'selected_project': selected_project or '',
        'selected_architect': selected_architect or '',
        'selected_location': selected_location or '',
        'selected_client': selected_client or '',
        'start_date': start_date or '',
        'end_date': end_date or '',
        
        # JSON data for charts
        'labor_stats_json': json.dumps(serialize_data(list(labor_stats)) if labor_stats else [], cls=DjangoJSONEncoder),
        'project_stats_json': json.dumps(serialize_data(project_stats) if project_stats else [], cls=DjangoJSONEncoder),
        'delay_stats_json': json.dumps(serialize_data(list(delay_stats)) if delay_stats else [], cls=DjangoJSONEncoder),
        'weather_stats_json': json.dumps(serialize_data(list(weather_stats)) if weather_stats else [], cls=DjangoJSONEncoder),
        'equipment_stats_json': json.dumps(serialize_data(list(equipment_stats)) if equipment_stats else [], cls=DjangoJSONEncoder),
        'overall_summary_json': json.dumps(serialize_data({
            'total_projects': total_projects,
            'total_entries': total_entries,
            'total_delays': total_delays,
            'budget_usage': round(budget_usage_percentage, 1),
        }), cls=DjangoJSONEncoder),
        'budget_forecast_json': json.dumps(serialize_data(budget_forecast_data) if budget_forecast_data else [], cls=DjangoJSONEncoder),
    }
    
    return render(request, 'admin/adminreports.html', context)

@require_site_manager_role
def chatbot(request):
    return render(request, 'chatbot/chatbot.html')

@require_site_manager_role
@csrf_protect
def newproject(request):
    """Create new project - requires admin approval"""
    if request.method == 'POST':
        try:
            # Validate and sanitize inputs
            client_name = request.POST.get('client_name', '').strip()
            client_email = request.POST.get('client_email', '').strip()
            project_name = request.POST.get('name', '').strip()
            location = request.POST.get('location', '').strip()
            description = request.POST.get('description', '').strip()
            
            # Basic validation
            if not client_name or len(client_name) > 100:
                messages.error(request, 'Valid client name is required.')
                return redirect('site_diary:newproject')
            
            if not project_name or len(project_name) > 200:
                messages.error(request, 'Valid project name is required.')
                return redirect('site_diary:newproject')
            
            if not location or len(location) > 300:
                messages.error(request, 'Valid location is required.')
                return redirect('site_diary:newproject')
            
            # Validate budget
            try:
                budget = float(request.POST.get('budget', 0)) if request.POST.get('budget') else 0
                if budget < 0:
                    messages.error(request, 'Budget cannot be negative.')
                    return redirect('site_diary:newproject')
                # Check if budget exceeds database limit (10^10 - 1)
                if budget >= 10000000000:  # 10 billion
                    messages.error(request, 'Budget amount is too large. Maximum allowed is ₱9,999,999,999.99.')
                    return redirect('site_diary:newproject')
            except (ValueError, TypeError):
                messages.error(request, 'Invalid budget amount.')
                return redirect('site_diary:newproject')
            
            # Validate dates
            start_date = request.POST.get('start_date')
            expected_end_date = request.POST.get('expected_end_date')
            
            if not start_date or not expected_end_date:
                messages.error(request, 'Start date and expected end date are required.')
                return redirect('site_diary:newproject')
            
            # Try to find existing client by email
            client_user = None
            if client_email:
                try:
                    from django.contrib.auth.models import User
                    from django.core.validators import validate_email
                    validate_email(client_email)
                    client_user = User.objects.get(email=client_email)
                except (User.DoesNotExist, ValidationError):
                    pass
            
            # Validate image file if provided
            image_file = None
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                # Validate file type and size
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
                if image_file.content_type not in allowed_types:
                    messages.error(request, 'Invalid image type. Please upload JPEG, PNG, or GIF.')
                    return redirect('site_diary:newproject')
                
                if image_file.size > 5 * 1024 * 1024:  # 5MB limit
                    messages.error(request, 'Image file too large. Maximum size is 5MB.')
                    return redirect('site_diary:newproject')
            
            # Create project with pending approval status
            project = Project.objects.create(
                name=project_name,
                client_name=client_name,
                client=client_user,
                location=location,
                description=description,
                budget=budget,
                start_date=start_date,
                expected_end_date=expected_end_date,
                project_manager=request.user,
                status='pending_approval',  # Project needs admin approval
                image=image_file
            )
            
            # Update client's profile if linked
            if client_user:
                try:
                    from accounts.models import Profile
                    profile, created = Profile.objects.get_or_create(user=client_user)
                    if not profile.project_name:
                        profile.project_name = project.name
                        profile.project_start = project.start_date
                        profile.save()
                        messages.info(request, f'Client account linked and updated for {client_user.get_full_name() or client_user.username}')
                except Exception as e:
                    logger.error(f"Error updating client profile: {str(e)}")
            
            # Set session flag for success modal
            request.session['show_success_modal'] = {
                'project_name': project.name,
                'project_id': project.id
            }
            logger.info(f"Project {project.id} created by user {request.user.id}")
            return redirect('site_diary:dashboard')
        except Exception as e:
            logger.error(f"Error creating project for user {request.user.id}: {str(e)}")
            messages.error(request, 'Error creating project. Please try again.')
    
    context = {
        'page_title': 'Create New Project'
    }
    return render(request, 'site_diary/newproject.html', context)

@login_required
def project_list(request):
    """List approved projects with filtering and search capabilities"""
    # Get user's approved projects only
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Apply filters
    search_form = ProjectSearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data.get('name'):
            projects = projects.filter(name__icontains=search_form.cleaned_data['name'])
        if search_form.cleaned_data.get('status'):
            projects = projects.filter(status=search_form.cleaned_data['status'])
        if search_form.cleaned_data.get('client_name'):
            projects = projects.filter(client_name__icontains=search_form.cleaned_data['client_name'])
        if search_form.cleaned_data.get('location'):
            projects = projects.filter(location__icontains=search_form.cleaned_data['location'])
    
    # Pagination
    paginator = Paginator(projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'page_title': 'Project List'
    }
    return render(request, 'site_diary/project_list.html', context)



@login_required
def project_edit(request, project_id):
    """Edit an existing project"""
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user has permission to edit this project
    if not request.user.is_staff and project.project_manager != request.user:
        messages.error(request, 'You do not have permission to edit this project.')
        return redirect('site_diary:project_detail', project_id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" updated successfully!')
            return redirect('site_diary:project_detail', project_id=project_id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProjectForm(instance=project)
    
    context = {
        'form': form,
        'project': project,
        'page_title': f'Edit Project: {project.name}'
    }
    return render(request, 'site_diary/project_edit.html', context)



@login_required
@require_site_manager_role
def revision_diary(request, entry_id):
    """Revision diary page for specific entry with complete data"""
    entry = get_object_or_404(DiaryEntry, id=entry_id)
    
    # Verify user has access to this entry's project
    if not request.user.is_staff:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
        if entry.project not in user_projects:
            messages.error(request, 'Access denied.')
            return redirect('site_diary:history')
    
    if request.method == 'POST':
        # Handle revision form submission
        from .models_revision import RevisionRequest
        
        try:
            # Handle dynamic worker types data
            from .models import WorkerType
            worker_types = WorkerType.objects.filter(is_active=True)
            
            # Clear existing labor entries for this entry (except overtime)
            LaborEntry.objects.filter(diary_entry=entry).exclude(labor_type='overtime').delete()
            
            # Process each worker type dynamically
            for worker_type in worker_types:
                worker_slug = worker_type.name.lower().replace(' ', '-')
                count_field = f"{worker_slug}Count"
                rate_field = f"{worker_slug}Rate"
                
                worker_count = request.POST.get(count_field, 0)
                worker_rate = request.POST.get(rate_field, 0)
                
                if int(worker_count or 0) > 0:
                    LaborEntry.objects.create(
                        diary_entry=entry,
                        labor_type=worker_slug,
                        trade_description=worker_type.name,
                        workers_count=worker_count,
                        hours_worked=8,
                        overtime_hours=0,
                        hourly_rate=worker_rate or worker_type.default_daily_rate or 0
                    )
            
            # Handle materials JSON data
            materials_json = request.POST.get('materials_json')
            if materials_json:
                MaterialEntry.objects.filter(diary_entry=entry).delete()
                materials_data = json.loads(materials_json)
                for material_data in materials_data:
                    MaterialEntry.objects.create(
                        diary_entry=entry,
                        material_name=material_data['name'],
                        quantity_delivered=material_data['quantity'],
                        unit=material_data['unit'],
                        unit_cost=material_data['cost'] / material_data['quantity'] if material_data['quantity'] > 0 else 0,
                        supplier='',
                        delivery_time=None
                    )
            
            # Handle equipment JSON data
            equipment_json = request.POST.get('equipment_json')
            if equipment_json:
                EquipmentEntry.objects.filter(diary_entry=entry).delete()
                equipment_data = json.loads(equipment_json)
                for equip_data in equipment_data:
                    EquipmentEntry.objects.create(
                        diary_entry=entry,
                        equipment_name=equip_data['name'],
                        equipment_type=equip_data['name'],
                        hours_operated=equip_data['hours'],
                        rental_cost_per_hour=equip_data['cost'] / equip_data['hours'] if equip_data['hours'] > 0 else 0,
                        operator_name='',
                        fuel_consumption=0
                    )
            
            # Handle overtime JSON data if provided
            overtime_json = request.POST.get('overtime_json')
            if overtime_json:
                # Clear existing overtime entries for this entry
                LaborEntry.objects.filter(diary_entry=entry, labor_type='overtime').delete()
                overtime_data = json.loads(overtime_json)
                for overtime_entry in overtime_data:
                    LaborEntry.objects.create(
                        diary_entry=entry,
                        labor_type='overtime',
                        trade_description=f"{overtime_entry['personnel']} {overtime_entry['role']} personnel",
                        workers_count=overtime_entry['personnel'],
                        hours_worked=overtime_entry['hours'],
                        overtime_hours=overtime_entry['hours'],
                        hourly_rate=overtime_entry['rate']
                    )
            
            # Handle delays JSON data
            delays_json = request.POST.get('delays_json')
            if delays_json:
                DelayEntry.objects.filter(diary_entry=entry).delete()
                delays_data = json.loads(delays_json)
                for delay_data in delays_data:
                    DelayEntry.objects.create(
                        diary_entry=entry,
                        category=delay_data['type'],
                        description=delay_data['description'],
                        start_time=None,
                        end_time=None,
                        duration_hours=delay_data.get('duration', 0),
                        impact_level=delay_data['impact'],
                        mitigation_actions='',
                        affected_activities='General work activities'
                    )
            
            # Handle subcontractor JSON data if provided
            subcontractor_json = request.POST.get('subcontractor_json')
            if subcontractor_json:
                SubcontractorEntry.objects.filter(diary_entry=entry).delete()
                subcontractor_data = json.loads(subcontractor_json)
                for sub_data in subcontractor_data:
                    SubcontractorEntry.objects.create(
                        diary_entry=entry,
                        company_name=sub_data['name'],
                        work_description=sub_data['work'],
                        daily_cost=sub_data.get('cost', 0)
                    )
            
            # Update diary entry fields if provided
            if request.POST.get('revised_work_description'):
                entry.work_description = request.POST.get('revised_work_description')
            if request.POST.get('revised_progress_percentage'):
                entry.progress_percentage = request.POST.get('revised_progress_percentage')
            if request.POST.get('revised_quality_issues'):
                entry.quality_issues = request.POST.get('revised_quality_issues')
            if request.POST.get('revised_safety_incidents'):
                entry.safety_incidents = request.POST.get('revised_safety_incidents')
            if request.POST.get('revised_general_notes'):
                entry.general_notes = request.POST.get('revised_general_notes')
            
            entry.save()
            
            # Create revision request
            revision_request = RevisionRequest.objects.create(
                diary_entry=entry,
                revision_type=request.POST.get('revisionType'),
                revision_reason=request.POST.get('revisionReason'),
                description=request.POST.get('revisionDescription'),
                impact_level=request.POST.get('revisionImpact', 'no_impact'),
                estimated_cost_impact=request.POST.get('actualCostImpact', 0),
                requested_by=request.user
            )
            messages.success(request, f'Revision request #{revision_request.id} submitted successfully!')
        except Exception as e:
            messages.error(request, f'Error submitting revision request: {str(e)}')
        
        return redirect('site_diary:history')
    
    # Get all related data for the entry
    labor_entries = LaborEntry.objects.filter(diary_entry=entry).order_by('id')
    material_entries = MaterialEntry.objects.filter(diary_entry=entry).order_by('id')
    equipment_entries = EquipmentEntry.objects.filter(diary_entry=entry).order_by('id')
    delay_entries = DelayEntry.objects.filter(diary_entry=entry).order_by('id')
    visitor_entries = VisitorEntry.objects.filter(diary_entry=entry).order_by('id')
    photo_entries = DiaryPhoto.objects.filter(diary_entry=entry).order_by('id')
    subcontractor_entries = SubcontractorEntry.objects.filter(diary_entry=entry).order_by('id')
    
    # Debug: Print what data we're fetching
    print(f"DEBUG: Revision diary for entry {entry.id}: {labor_entries.count()} labor, {material_entries.count()} materials, {equipment_entries.count()} equipment, {delay_entries.count()} delays, {visitor_entries.count()} visitors, {photo_entries.count()} photos, {subcontractor_entries.count()} subcontractors")
    
    # Debug subcontractor data specifically
    print(f"DEBUG: Subcontractor entries for entry {entry.id}:")
    for sub in subcontractor_entries:
        print(f"DEBUG:   - {sub.company_name}: {sub.work_description} (₱{sub.daily_cost})")
    
    # Also check if there are any VisitorEntry records with visitor_type='contractor'
    contractor_visitors = VisitorEntry.objects.filter(diary_entry=entry, visitor_type='contractor')
    print(f"DEBUG: Found {contractor_visitors.count()} contractor visitor entries for entry {entry.id}:")
    for cv in contractor_visitors:
        print(f"DEBUG:   - {cv.visitor_name}: {cv.company} - {cv.purpose}")
    
    # Get milestone and subcontractor data for dropdowns
    milestones = Milestone.objects.filter(is_active=True).order_by('order', 'name')
    subcontractor_companies = SubcontractorCompany.objects.filter(is_active=True).order_by('name')
    
    # Debug: Check if we have any SubcontractorEntry records at all
    all_subcontractor_entries = SubcontractorEntry.objects.all()
    print(f"DEBUG: Total SubcontractorEntry records in database: {all_subcontractor_entries.count()}")
    for sub in all_subcontractor_entries:
        print(f"DEBUG:   - Entry {sub.diary_entry.id}: {sub.company_name} - {sub.work_description} (₱{sub.daily_cost})")
    

    
    # Get active worker types for dynamic form generation
    from .models import WorkerType
    worker_types = WorkerType.objects.filter(is_active=True).order_by('order', 'name')
    
    # Populate worker types with existing values
    for worker_type in worker_types:
        worker_slug = worker_type.name.lower().replace(' ', '-')
        # Find existing labor entry for this worker type
        existing_labor = labor_entries.filter(labor_type=worker_slug).first()
        worker_type.current_count = existing_labor.workers_count if existing_labor else 0
        worker_type.current_rate = existing_labor.hourly_rate if existing_labor else (worker_type.default_daily_rate or 0)
    
    context = {
        'entry_id': entry.id,
        'entry': entry,
        'project_name': entry.project.name,
        'entry_date': entry.entry_date.strftime('%B %d, %Y'),
        'labor_entries': labor_entries,
        'material_entries': material_entries,
        'equipment_entries': equipment_entries,
        'delay_entries': delay_entries,
        'visitor_entries': visitor_entries,
        'photo_entries': photo_entries,
        'subcontractor_entries': subcontractor_entries,
        'milestones': milestones,
        'subcontractor_companies': subcontractor_companies,
        'worker_types': worker_types,
    }
    

    # Final debug before rendering
    print(f"DEBUG: Context subcontractor_entries count: {len(context['subcontractor_entries'])}")
    print(f"DEBUG: Subcontractor entries found: {subcontractor_entries.count()}")
    
    return render(request, 'site_diary/revision_diary.html', context)

@login_required
@require_site_manager_role
def history(request):
    """View diary entry history with search and filtering"""
    # Get user's approved projects
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Get diary entries with comprehensive prefetch for all related data
    entries = DiaryEntry.objects.filter(project__in=projects).select_related(
        'project', 'created_by', 'reviewed_by', 'milestone'
    ).prefetch_related(
        'labor_entries', 'material_entries', 'equipment_entries', 
        'delay_entries', 'visitor_entries', 'subcontractor_entries', 'photos'
    )
    
    # Add budget impact data to projects
    for project in projects:
        # Calculate revision impacts
        project_entries = DiaryEntry.objects.filter(project=project)
        revision_count = project_entries.filter(status='needs_revision').count()
        
        # Calculate budget impact
        base_revision_cost = 100000  # ₱100,000 per revision
        complexity_multiplier = 1.0
        
        # Get total spent for complexity calculation  
        from .models import LaborEntry, MaterialEntry, EquipmentEntry
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        total_spent = (
            sum(labor.total_cost for labor in labor_entries) +
            sum(material.total_cost for material in material_entries) +
            sum(equipment.total_rental_cost for equipment in equipment_entries)
        )
        
        if total_spent > 5000000:  # Large project ₱5M+
            complexity_multiplier = 1.5
        elif total_spent > 2500000:  # Medium project ₱2.5M+
            complexity_multiplier = 1.2
        
        estimated_revision_cost = revision_count * base_revision_cost * complexity_multiplier
        
        # Calculate budget health
        original_budget = float(project.budget) if project.budget else 0
        adjusted_budget = original_budget + estimated_revision_cost
        remaining_budget = adjusted_budget - float(total_spent)
        
        if remaining_budget < 0:
            budget_health = 'danger'
        elif remaining_budget < (adjusted_budget * 0.1):
            budget_health = 'warning'
        else:
            budget_health = 'good'
        
        # Add calculated fields to project
        project.revision_count = revision_count
        project.revision_cost_impact = estimated_revision_cost
        project.adjusted_budget = adjusted_budget
        project.budget_health = budget_health
        project.total_spent = total_spent
    
    # Prefetch diary entries for projects
    projects = projects.prefetch_related('diary_entries')
    
    # Apply search filters
    search_form = DiarySearchForm(request.GET)
    if search_form.is_valid():
        if search_form.cleaned_data['project']:
            entries = entries.filter(project=search_form.cleaned_data['project'])
        if search_form.cleaned_data['start_date']:
            entries = entries.filter(entry_date__gte=search_form.cleaned_data['start_date'])
        if search_form.cleaned_data['end_date']:
            entries = entries.filter(entry_date__lte=search_form.cleaned_data['end_date'])
        if search_form.cleaned_data['weather_condition']:
            entries = entries.filter(weather_condition=search_form.cleaned_data['weather_condition'])
        if search_form.cleaned_data['created_by']:
            entries = entries.filter(created_by=search_form.cleaned_data['created_by'])
    
    # Pagination
    paginator = Paginator(entries.order_by('-entry_date'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
    }
    return render(request, 'site_diary/history.html', context)

@login_required
@require_site_manager_role
def reports(request):
    """Generate comprehensive reports and analytics with database data"""
    # Get user's approved projects
    if request.user.is_staff:
        projects = Project.objects.filter(status__in=['planning', 'active', 'on_hold', 'completed'])
    else:
        projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
    
    # Date filtering
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_project = request.GET.get('project')
    report_type = request.GET.get('report_type', 'summary')
    
    # Filter projects if specific project selected
    if selected_project:
        try:
            projects = projects.filter(id=int(selected_project))
        except (ValueError, TypeError):
            pass
    
    # Get diary entries for the period
    entries = DiaryEntry.objects.filter(project__in=projects)
    if start_date:
        entries = entries.filter(entry_date__gte=start_date)
    if end_date:
        entries = entries.filter(entry_date__lte=end_date)
    
    # Project statistics with comprehensive data from database
    project_stats = []
    for project in projects:
        project_entries = entries.filter(project=project)
        
        # Get all related data for this project from database
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
        visitor_entries = VisitorEntry.objects.filter(diary_entry__in=project_entries)
        
        # Calculate costs from database
        total_labor_cost = sum(labor.total_cost for labor in labor_entries)
        total_material_cost = sum(material.total_cost for material in material_entries)
        total_equipment_cost = sum(equipment.total_rental_cost for equipment in equipment_entries)
        total_delay_impact = delay_entries.aggregate(total=Sum('cost_impact'))['total'] or 0
        
        # Progress tracking from database
        progress_data = project_entries.aggregate(
            avg_progress=Avg('progress_percentage'),
            max_progress=Max('progress_percentage'),
            min_progress=Min('progress_percentage')
        )
        
        # Safety and quality metrics from database
        safety_incidents = project_entries.exclude(safety_incidents='').count()
        quality_issues = project_entries.exclude(quality_issues='').count()
        
        project_stats.append({
            'project': project,
            'entries_count': project_entries.count(),
            'total_delays': delay_entries.count(),
            'total_delay_hours': delay_entries.aggregate(total=Sum('duration_hours'))['total'] or 0,
            'total_labor_cost': total_labor_cost,
            'total_material_cost': total_material_cost,
            'total_equipment_cost': total_equipment_cost,
            'total_project_cost': total_labor_cost + total_material_cost + total_equipment_cost,
            'total_delay_impact': total_delay_impact,
            'avg_progress': progress_data['avg_progress'] or 0,
            'max_progress': progress_data['max_progress'] or 0,
            'min_progress': progress_data['min_progress'] or 0,
            'approved_entries': project_entries.filter(status='complete').count(),
            'pending_entries': project_entries.filter(status='needs_revision').count(),
            'safety_incidents': safety_incidents,
            'quality_issues': quality_issues,
            'visitor_count': visitor_entries.count(),
            'photos_count': project_entries.filter(photos_taken=True).count(),
        })
    
    # Delay analysis by category from database
    delay_categories = DelayEntry.objects.filter(
        diary_entry__in=entries
    ).values('category').annotate(
        count=Count('id'),
        total_hours=Sum('duration_hours'),
        avg_impact=Avg('cost_impact'),
        total_cost_impact=Sum('cost_impact')
    ).order_by('-total_hours')
    
    # Weather analysis from database
    weather_stats = entries.exclude(weather_condition='').values('weather_condition').annotate(
        count=Count('id'),
        avg_temp_high=Avg('temperature_high'),
        avg_temp_low=Avg('temperature_low'),
        avg_humidity=Avg('humidity'),
        avg_wind_speed=Avg('wind_speed')
    ).order_by('-count')
    
    # Labor analysis from database
    labor_stats = LaborEntry.objects.filter(
        diary_entry__in=entries
    ).values('labor_type').annotate(
        total_workers=Sum('workers_count'),
        total_hours=Sum('hours_worked'),
        total_overtime=Sum('overtime_hours'),
        avg_hourly_rate=Avg('hourly_rate'),
        entry_count=Count('id')
    ).order_by('-total_hours')
    
    # Material analysis from database
    material_stats = MaterialEntry.objects.filter(
        diary_entry__in=entries
    ).values('material_name').annotate(
        total_delivered=Sum('quantity_delivered'),
        total_used=Sum('quantity_used'),
        avg_unit_cost=Avg('unit_cost'),
        total_entries=Count('id')
    ).order_by('-total_delivered')[:15]  # Top 15 materials
    
    # Equipment utilization from database
    equipment_stats = EquipmentEntry.objects.filter(
        diary_entry__in=entries
    ).values('equipment_type').annotate(
        total_hours=Sum('hours_operated'),
        avg_hourly_rate=Avg('rental_cost_per_hour'),
        total_fuel=Sum('fuel_consumption'),
        utilization_days=Count('diary_entry__entry_date', distinct=True),
        breakdown_count=Count('id', filter=Q(status='breakdown'))
    ).order_by('-total_hours')
    
    # Monthly progress tracking from database
    monthly_progress = entries.extra(
        select={'month': "DATE_TRUNC('month', entry_date)"}
    ).values('month').annotate(
        avg_progress=Avg('progress_percentage'),
        entry_count=Count('id'),
        total_delays=Count('delay_entries'),
        avg_temp=Avg('temperature_high')
    ).order_by('month')
    
    # Overall summary from database
    overall_summary = {
        'total_projects': projects.count(),
        'total_entries': entries.count(),
        'total_approved': entries.filter(status='complete').count(),
        'total_pending': entries.filter(status='needs_revision').count(),
        'total_labor_entries': LaborEntry.objects.filter(diary_entry__in=entries).count(),
        'total_material_entries': MaterialEntry.objects.filter(diary_entry__in=entries).count(),
        'total_equipment_entries': EquipmentEntry.objects.filter(diary_entry__in=entries).count(),
        'total_delays': DelayEntry.objects.filter(diary_entry__in=entries).count(),
        'total_visitors': VisitorEntry.objects.filter(diary_entry__in=entries).count(),
        'date_range': {
            'start': start_date,
            'end': end_date,
        }
    }
    
    # Ensure we have data even if no entries exist
    if not project_stats:
        project_stats = []
    if not delay_categories:
        delay_categories = []
    if not labor_stats:
        labor_stats = []
    if not material_stats:
        material_stats = []
    
    # Convert data to JSON-serializable format
    import json
    from decimal import Decimal
    from django.core.serializers.json import DjangoJSONEncoder
    
    def serialize_data(data):
        """Convert data to JSON-serializable format"""
        if isinstance(data, list):
            return [serialize_data(item) for item in data]
        elif hasattr(data, '__dict__'):
            result = {}
            for key, value in data.__dict__.items():
                if not key.startswith('_'):
                    result[key] = serialize_data(value)
            return result
        elif isinstance(data, Decimal):
            return float(data)
        elif hasattr(data, 'isoformat'):  # datetime objects
            return data.isoformat()
        else:
            return data
    
    # Serialize project stats with progress tracking data
    serialized_project_stats = []
    for stat in project_stats:
        # Get all diary entries for this project with progress data
        project_entries = entries.filter(project=stat['project']).order_by('entry_date')
        progress_entries = []
        for entry in project_entries:
            progress_entries.append({
                'date': entry.entry_date.strftime('%Y-%m-%d'),
                'progress': float(entry.progress_percentage) if entry.progress_percentage else 0
            })
        
        serialized_stat = {
            'project': {
                'id': stat['project'].id,
                'name': stat['project'].name,
                'budget': float(stat['project'].budget) if stat['project'].budget else 0
            },
            'entries_count': stat['entries_count'],
            'total_delays': stat['total_delays'],
            'total_labor_cost': float(stat['total_labor_cost']),
            'total_material_cost': float(stat['total_material_cost']),
            'total_equipment_cost': float(stat['total_equipment_cost']),
            'avg_progress': float(stat['avg_progress']) if stat['avg_progress'] else 0,
            'safety_incidents': stat['safety_incidents'],
            'quality_issues': stat['quality_issues'],
            'approved_entries': stat['approved_entries'],
            'progress_entries': progress_entries
        }
        serialized_project_stats.append(serialized_stat)
    
    # Serialize other data
    serialized_labor_stats = list(labor_stats)
    serialized_delay_categories = list(delay_categories)
    serialized_weather_stats = list(weather_stats)
    serialized_equipment_stats = list(equipment_stats)
    
    context = {
        'project_stats': project_stats,
        'delay_categories': delay_categories,
        'weather_stats': weather_stats,
        'labor_stats': labor_stats,
        'material_stats': material_stats,
        'equipment_stats': equipment_stats,
        'monthly_progress': monthly_progress,
        'overall_summary': overall_summary,
        'projects': projects,
        'start_date': start_date,
        'end_date': end_date,
        'selected_project': selected_project,
        'report_type': report_type,
        # JSON serialized data for JavaScript
        'project_stats_json': json.dumps(serialized_project_stats, cls=DjangoJSONEncoder),
        'labor_stats_json': json.dumps(serialized_labor_stats, cls=DjangoJSONEncoder),
        'delay_categories_json': json.dumps(serialized_delay_categories, cls=DjangoJSONEncoder),
        'weather_stats_json': json.dumps(serialized_weather_stats, cls=DjangoJSONEncoder),
        'equipment_stats_json': json.dumps(serialized_equipment_stats, cls=DjangoJSONEncoder),
        'overall_summary_json': json.dumps(overall_summary, cls=DjangoJSONEncoder),
    }
    return render(request, 'site_diary/reports.html', context)


@require_site_manager_role
def project_detail(request, project_id):
    """Comprehensive Project Detail View for Site Managers"""
    project = get_object_or_404(Project, id=project_id)
    
    # Verify user has access to this project
    if not request.user.is_staff:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user)
        )
        if project not in user_projects:
            messages.error(request, 'You do not have access to this project.')
            return redirect('site_diary:dashboard')
    
    # Get user's company name and profile image from SiteManagerProfile
    user_company = "Triple G Design Studio"  # Default company name
    user_profile_image = None
    try:
        if hasattr(request.user, 'sitemanagerprofile'):
            profile = request.user.sitemanagerprofile
            if profile.company_department:
                user_company = profile.company_department
            user_profile_image = profile.get_profile_image_url()
    except:
        pass
    
    # Get project entries and related data
    project_entries = DiaryEntry.objects.filter(project=project).order_by('-entry_date')
    labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
    material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
    equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
    delay_entries = DelayEntry.objects.filter(diary_entry__in=project_entries)
    
    # Calculate project metrics from real data
    latest_entry = project_entries.first()
    progress = float(latest_entry.progress_percentage) if latest_entry else 0
    
    # Budget calculations from real data
    total_labor_cost = sum(labor.total_cost for labor in labor_entries)
    total_material_cost = sum(material.total_cost for material in material_entries)
    total_equipment_cost = sum(equipment.total_rental_cost for equipment in equipment_entries)
    total_spent = total_labor_cost + total_material_cost + total_equipment_cost
    total_budget = float(project.budget) if project.budget else 0
    remaining_budget = max(0, float(total_budget) - float(total_spent))
    
    # Recent diary entries for summary
    recent_diary_entries = project_entries[:3]
    
    # Resource statistics from real data
    total_workers = labor_entries.aggregate(total=Sum('workers_count'))['total'] or 0
    equipment_count = equipment_entries.values('equipment_type').distinct().count()
    delay_count = delay_entries.count()
    
    # Determine current phase based on progress
    if progress < 25:
        phase_name = "Planning"
    elif progress < 50:
        phase_name = "Foundation"
    elif progress < 75:
        phase_name = "Structure"
    else:
        phase_name = "Finishing"
    
    # Get project milestones
    milestones = Milestone.objects.filter(is_active=True).order_by('order')[:4]
    project_milestones = []
    for i, milestone in enumerate(milestones):
        milestone.threshold = (i + 1) * 25  # 25%, 50%, 75%, 100%
        project_milestones.append(milestone)
    
    project.milestones = project_milestones
    
    context = {
        'project': project,
        'progress': progress,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'remaining_budget': remaining_budget,
        'labor_count': total_workers,
        'equipment_count': equipment_count,
        'delays_count': delay_count,
        'recent_diary_entries': recent_diary_entries,
        'phase_name': phase_name,
        'user_company': user_company,
        'user_profile_image': user_profile_image,
    }
    return render(request, 'site_diary/project-detail.html', context)

@login_required
@require_site_manager_role
@csrf_protect
def update_project_image(request, project_id):
    """Update project image from architect's gallery or device upload"""
    if request.method == 'POST':
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # Verify user is architect
            if not (hasattr(request.user, 'sitemanagerprofile') and 
                    request.user.sitemanagerprofile.site_role and 
                    request.user.sitemanagerprofile.site_role.name == 'architect'):
                return JsonResponse({'success': False, 'message': 'Access denied'}, status=403)
            
            # Handle gallery image URL
            image_url = request.POST.get('image_url')
            if image_url:
                project.image_url = image_url
                project.save()
                return JsonResponse({'success': True})
            
            # Handle device file upload
            if 'image_file' in request.FILES:
                image_file = request.FILES['image_file']
                project.image = image_file
                project.save()
                return JsonResponse({'success': True, 'image_url': project.image.url})
            
            return JsonResponse({'success': False, 'message': 'No image provided'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@login_required
@require_site_manager_role
def settings(request):
    """Site Manager settings and preferences"""
    from accounts.models import SiteManagerProfile
    from accounts.forms import ProfileUpdateForm
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import logout
    from django.http import HttpResponse
    from django.db import transaction
    import csv
    import json
    
    # Get or create site manager profile
    try:
        site_manager_profile = SiteManagerProfile.objects.select_related('site_role').get(user=request.user)
        print(f"DEBUG: Site manager profile found: {site_manager_profile}")
        print(f"DEBUG: Site role: {site_manager_profile.site_role}")
        print(f"DEBUG: Site role display_name: {site_manager_profile.site_role.display_name if site_manager_profile.site_role else 'None'}")
        print(f"DEBUG: Current profile data - Phone: {site_manager_profile.phone}, Emergency: {site_manager_profile.emergency_contact}")
        print(f"DEBUG: Current profile pic: {site_manager_profile.profile_pic}")
        print(f"DEBUG: Employee ID: {site_manager_profile.employee_id}")
    except SiteManagerProfile.DoesNotExist:
        print(f"DEBUG: Site Manager profile not found for user: {request.user}")
        messages.error(request, 'Site Manager profile not found.')
        return redirect('site_diary:dashboard')
    
    if request.method == 'POST':
        print(f"DEBUG: POST request received")
        print(f"DEBUG: POST data: {request.POST}")
        print(f"DEBUG: FILES data: {request.FILES}")
        
        action = request.POST.get('action')
        print(f"DEBUG: Action: {action}")
        
        if action == 'update_profile':
            # Handle profile update
            user = request.user
            user.first_name = request.POST.get('firstName', '')
            user.last_name = request.POST.get('lastName', '')
            user.email = request.POST.get('email', '')
            
            # Update site manager profile fields
            site_manager_profile.phone = request.POST.get('phone', '')
            site_manager_profile.emergency_contact = request.POST.get('emergency_contact', '')
            
            # Handle profile picture upload
            if 'profile_pic' in request.FILES:
                profile_pic = request.FILES['profile_pic']
                print(f"DEBUG: Profile picture uploaded: {profile_pic.name}, Size: {profile_pic.size}")
                
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
                file_type = profile_pic.content_type.lower()
                
                if file_type not in allowed_types:
                    messages.error(request, 'Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.')
                    return redirect('site_diary:settings')
                
                # Validate file size (max 5MB)
                max_size = 5 * 1024 * 1024  # 5MB
                if profile_pic.size > max_size:
                    messages.error(request, 'File size too large. Please upload an image smaller than 5MB.')
                    return redirect('site_diary:settings')
                
                site_manager_profile.profile_pic = profile_pic
                print(f"DEBUG: Profile picture assigned to site_manager_profile")
            
            try:
                with transaction.atomic():
                    # Save user data
                    print(f"DEBUG: Saving user data - First: {user.first_name}, Last: {user.last_name}, Email: {user.email}")
                    user.save()
                    
                    # Save site manager profile data
                    print(f"DEBUG: Saving profile data - Phone: {site_manager_profile.phone}, Emergency: {site_manager_profile.emergency_contact}")
                    site_manager_profile.save()
                    
                    # Verify data was saved by reloading from database
                    user.refresh_from_db()
                    site_manager_profile.refresh_from_db()
                    
                    print(f"DEBUG: Verification - User saved: First={user.first_name}, Last={user.last_name}, Email={user.email}")
                    print(f"DEBUG: Verification - Profile saved: Phone={site_manager_profile.phone}, Emergency={site_manager_profile.emergency_contact}")
                    print(f"DEBUG: Verification - Profile pic: {site_manager_profile.profile_pic}")
                    
                    messages.success(request, 'Profile updated successfully!')
            except Exception as e:
                print(f"DEBUG: Error saving profile: {str(e)}")
                import traceback
                print(f"DEBUG: Full traceback: {traceback.format_exc()}")
                messages.error(request, f'Error updating profile: {str(e)}')
        
        elif action == 'change_password':
            # Handle password change
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                messages.success(request, 'Password changed successfully!')
            else:
                for error in password_form.errors.values():
                    messages.error(request, error[0])
        
        elif action == 'upload_gallery':
            # Handle gallery upload (Architects only)
            if site_manager_profile.site_role and site_manager_profile.site_role.name == 'architect':
                files = request.FILES.getlist('gallery_images')
                if files:
                    from accounts.models import ArchitectGallery
                    for file in files:
                        ArchitectGallery.objects.create(architect=site_manager_profile, image=file)
                    messages.success(request, f'{len(files)} image(s) uploaded successfully!')
                else:
                    messages.error(request, 'No images selected.')
            else:
                messages.error(request, 'Access denied. Only architects can upload to gallery.')
        
        return redirect('site_diary:settings')
    
    # Debug: Show current data being passed to template
    print(f"DEBUG: Template context - User: {request.user}")
    print(f"DEBUG: Template context - Profile: {site_manager_profile}")
    print(f"DEBUG: Template context - site_role: {site_manager_profile.site_role}")
    print(f"DEBUG: Template context - site_role.name: {site_manager_profile.site_role.name if site_manager_profile.site_role else 'None'}")
    print(f"DEBUG: Template context - User first_name: {request.user.first_name}")
    print(f"DEBUG: Template context - User last_name: {request.user.last_name}")
    print(f"DEBUG: Template context - User email: {request.user.email}")
    print(f"DEBUG: Template context - Profile phone: {site_manager_profile.phone}")
    print(f"DEBUG: Template context - Profile emergency_contact: {site_manager_profile.emergency_contact}")
    
    # Get gallery images for architects
    gallery_images = []
    if site_manager_profile.site_role and site_manager_profile.site_role.name == 'architect':
        from accounts.models import ArchitectGallery
        gallery_images = ArchitectGallery.objects.filter(architect=site_manager_profile)
    
    context = {
        'user': request.user,
        'site_manager_profile': site_manager_profile,
        'gallery_images': gallery_images,
    }
    return render(request, 'site_diary/settings.html', context)

@login_required
@require_site_manager_role
def site_manager_logout(request):
    """Site Manager logout view"""
    from django.contrib.auth import logout
    
    if request.method == 'POST':
        # Clear browser data if requested
        clear_browser_data = request.POST.get('clear_browser_data') == 'on'
        
        # Log out the user
        logout(request)
        
        # Add success message
        messages.success(request, 'You have been successfully logged out from the Site Manager panel.')
        
        # Redirect to site manager login
        return redirect('accounts:sitemanager_login')
    
    # If GET request, redirect to settings
    return redirect('site_diary:settings')

@login_required
@require_admin_role
def adminclientproject(request):
    """Admin view for client projects with approval functionality"""
    
    # Handle project approval/rejection
    if request.method == 'POST':
        action = request.POST.get('action')
        project_id = request.POST.get('project_id')
        
        if action and project_id:
            try:
                project = Project.objects.get(id=project_id)
                
                if action == 'approve':
                    project.status = 'planning'
                    project.approved_by = request.user
                    project.approved_at = timezone.now()
                    project.save()
                    messages.success(request, f'Project "{project.name}" approved successfully.')
                    
                elif action == 'reject':
                    rejection_reason = request.POST.get('rejection_reason', '')
                    project.status = 'rejected'
                    project.rejection_reason = rejection_reason
                    project.save()
                    messages.success(request, f'Project "{project.name}" rejected.')
                    
            except Project.DoesNotExist:
                messages.error(request, 'Project not found.')
        
        return redirect('site_diary:adminclientproject')
    
    search_form = ProjectSearchForm(request.GET)
    projects = Project.objects.all().select_related('project_manager', 'architect')
    
    if search_form.is_valid():
        if search_form.cleaned_data['name']:
            projects = projects.filter(name__icontains=search_form.cleaned_data['name'])
        if search_form.cleaned_data['client_name']:
            projects = projects.filter(client_name__icontains=search_form.cleaned_data['client_name'])
        if search_form.cleaned_data['status']:
            projects = projects.filter(status=search_form.cleaned_data['status'])
    
    # Separate pending projects for easy access
    pending_projects = projects.filter(status='pending_approval').order_by('-created_at')
    approved_count = projects.filter(status__in=['planning', 'active', 'on_hold', 'completed']).count()
    rejected_count = projects.filter(status='rejected').count()
    all_projects = projects.order_by('-created_at')
    
    paginator = Paginator(all_projects, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'pending_projects': pending_projects,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'search_form': search_form,
    }
    return render(request, 'admin/adminclientproject.html', context)

@login_required
@require_admin_role
def admindiary(request):
    """Admin view for diary entries with approval functionality"""
    
    # Handle diary entry approval
    if request.method == 'POST':
        action = request.POST.get('action')
        entry_id = request.POST.get('entry_id')
        
        if action and entry_id:
            try:
                entry = DiaryEntry.objects.get(id=entry_id)
                
                if action == 'approve':
                    entry.approved = True
                    entry.reviewed_by = request.user
                    entry.approval_date = timezone.now()
                    entry.save()
                    messages.success(request, f'Diary entry for {entry.project.name} approved.')
                    
            except DiaryEntry.DoesNotExist:
                messages.error(request, 'Diary entry not found.')
        
        return redirect('site_diary:admindiary')
    
    search_form = DiaryEntrySearchForm(request.GET)
    entries = DiaryEntry.objects.all().select_related(
        'project', 'created_by', 'reviewed_by'
    ).order_by('-entry_date')
    
    if search_form.is_valid():
        if search_form.cleaned_data['project']:
            entries = entries.filter(project=search_form.cleaned_data['project'])
        if search_form.cleaned_data['start_date']:
            entries = entries.filter(entry_date__gte=search_form.cleaned_data['start_date'])
        if search_form.cleaned_data['end_date']:
            entries = entries.filter(entry_date__lte=search_form.cleaned_data['end_date'])
    
    # Statistics
    total_entries = entries.count()
    pending_entries = entries.filter(approved=False).count()
    approved_entries = entries.filter(approved=True).count()
    draft_entries = entries.filter(draft=True).count()
    
    # Pagination
    paginator = Paginator(entries, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_entries': total_entries,
        'pending_entries': pending_entries,
        'approved_entries': approved_entries,
        'draft_entries': draft_entries,
    }
    return render(request, 'admin/admindiary.html', context)

@login_required
@require_admin_role
def admindiaryreviewer(request):
    """Project History - Track all project activities and diary entries"""
    print("=== PROJECT HISTORY VIEW CALLED ===")
    
    # Get all diary entries (not just pending) with filtering
    all_entries = DiaryEntry.objects.filter(
        draft=False
    ).select_related('project', 'created_by', 'milestone').order_by('-entry_date')
    
    # Apply filters from GET parameters
    architect = request.GET.get('architect')
    project = request.GET.get('project')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if architect:
        all_entries = all_entries.filter(created_by__username=architect)
    if project:
        all_entries = all_entries.filter(project__name__icontains=project)
    if status:
        if status == 'complete':
            all_entries = all_entries.filter(status='complete')
        elif status == 'needs_revision':
            all_entries = all_entries.filter(status='needs_revision')
    if date_from:
        all_entries = all_entries.filter(entry_date__gte=date_from)
    if date_to:
        all_entries = all_entries.filter(entry_date__lte=date_to)
    if search:
        all_entries = all_entries.filter(
            Q(project__name__icontains=search) |
            Q(created_by__username__icontains=search) |
            Q(project__location__icontains=search)
        )
    
    # Calculate statistics for project history
    total_count = DiaryEntry.objects.filter(draft=False).count()
    recent_count = DiaryEntry.objects.filter(draft=False, created_at__gte=timezone.now() - timedelta(days=30)).count()
    total_entries_count = DiaryEntry.objects.filter(draft=False).count()
    active_projects_count = Project.objects.filter(status__in=['active', 'ongoing']).count()
    
    # Pagination
    paginator = Paginator(all_entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique architects and projects for filter dropdowns
    architects = User.objects.filter(
        diaryentry__isnull=False
    ).distinct().order_by('first_name', 'last_name', 'username')
    
    projects = Project.objects.filter(
        diary_entries__isnull=False
    ).distinct().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'pending_count': recent_count,
        'approved_count': total_entries_count,
        'revision_count': active_projects_count,
        'total_count': Project.objects.count(),
        'architects': architects,
        'projects': projects,
    }
    
    # Debug prints
    print(f"DEBUG: Total entries in database: {total_count}")
    print(f"DEBUG: Total draft entries: {DiaryEntry.objects.filter(draft=True).count()}")
    print(f"DEBUG: Total non-draft entries: {DiaryEntry.objects.filter(draft=False).count()}")
    print(f"DEBUG: All entries count: {DiaryEntry.objects.count()}")
    print(f"DEBUG: Entries after filtering: {all_entries.count()}")
    print(f"DEBUG: Page object count: {len(page_obj)}")
    if page_obj:
        print(f"DEBUG: First entry: {page_obj[0].project.name if page_obj else 'None'}")
    else:
        print("DEBUG: No entries found - page_obj is empty")
        print(f"DEBUG: Sample DiaryEntry exists: {DiaryEntry.objects.exists()}")
        if DiaryEntry.objects.exists():
            sample = DiaryEntry.objects.first()
            print(f"DEBUG: Sample entry - Project: {sample.project.name}, Draft: {sample.draft}, Date: {sample.entry_date}")
    
    return render(request, 'admin/admindiaryreviewer.html', context)

@login_required
@require_admin_role
def diary_entry_detail(request, entry_id):
    """Get diary entry details for modal view"""
    try:
        entry = DiaryEntry.objects.select_related(
            'project', 'created_by', 'milestone', 'reviewed_by'
        ).prefetch_related(
            'labor_entries', 'material_entries', 'equipment_entries', 
            'delay_entries', 'visitor_entries', 'photos'
        ).get(id=entry_id, draft=False)
        
        # Calculate budget information
        project_entries = DiaryEntry.objects.filter(project=entry.project)
        labor_entries = LaborEntry.objects.filter(diary_entry__in=project_entries)
        material_entries = MaterialEntry.objects.filter(diary_entry__in=project_entries)
        equipment_entries = EquipmentEntry.objects.filter(diary_entry__in=project_entries)
        
        total_spent = (
            sum(labor.total_cost for labor in labor_entries) +
            sum(material.total_cost for material in material_entries) +
            sum(equipment.total_rental_cost for equipment in equipment_entries)
        )
        
        # Get subcontractor entries
        subcontractor_entries = SubcontractorEntry.objects.filter(diary_entry=entry)
        
        data = {
            'id': entry.id,
            'project_name': entry.project.name,
            'entry_date': entry.entry_date.strftime('%Y-%m-%d'),
            'created_by': entry.created_by.get_full_name() or entry.created_by.username,
            'work_description': entry.work_description,
            'progress_percentage': float(entry.progress_percentage),
            'milestone': entry.milestone.name if entry.milestone else 'N/A',
            'weather_condition': entry.get_weather_condition_display(),
            'temperature_high': entry.temperature_high,
            'temperature_low': entry.temperature_low,
            'humidity': entry.humidity,
            'wind_speed': float(entry.wind_speed) if entry.wind_speed else None,
            'quality_issues': entry.quality_issues,
            'safety_incidents': entry.safety_incidents,
            'general_notes': entry.general_notes,
            'status': entry.get_status_display(),
            'draft': entry.draft,
            'photos_taken': entry.photos_taken,
            'reviewed_by': entry.reviewed_by.get_full_name() if entry.reviewed_by else 'N/A',
            'reviewed_date': entry.reviewed_date.strftime('%Y-%m-%d %H:%M') if entry.reviewed_date else 'N/A',
            'labor_count': entry.labor_entries.count(),
            'material_count': entry.material_entries.count(),
            'equipment_count': entry.equipment_entries.count(),
            'delay_count': entry.delay_entries.count(),
            'visitor_count': entry.visitor_entries.count(),
            'subcontractor_count': subcontractor_entries.count(),
            'photo_count': entry.photos.count(),
            'project_budget': float(entry.project.budget) if entry.project.budget else 0,
            'total_spent': float(total_spent),
            'remaining_budget': float(entry.project.budget) - float(total_spent) if entry.project.budget else -float(total_spent),
            
            # Detailed entry data
            'labor_entries': [{
                'trade_description': labor.trade_description,
                'labor_type': labor.get_labor_type_display() if hasattr(labor, 'get_labor_type_display') else labor.labor_type,
                'workers_count': labor.workers_count,
                'hours_worked': float(labor.hours_worked),
                'overtime_hours': float(labor.overtime_hours),
                'hourly_rate': float(labor.hourly_rate) if labor.hourly_rate else 0,
            } for labor in entry.labor_entries.all()],
            
            'material_entries': [{
                'material_name': material.material_name,
                'quantity_delivered': float(material.quantity_delivered),
                'quantity_used': float(material.quantity_used),
                'unit': material.get_unit_display() if hasattr(material, 'get_unit_display') else material.unit,
                'unit_cost': float(material.unit_cost) if material.unit_cost else 0,
                'supplier': material.supplier,
            } for material in entry.material_entries.all()],
            
            'equipment_entries': [{
                'equipment_name': equipment.equipment_name,
                'equipment_type': equipment.equipment_type,
                'operator_name': equipment.operator_name,
                'hours_operated': float(equipment.hours_operated),
                'status': equipment.get_status_display() if hasattr(equipment, 'get_status_display') else equipment.status,
                'rental_cost_per_hour': float(equipment.rental_cost_per_hour) if equipment.rental_cost_per_hour else 0,
            } for equipment in entry.equipment_entries.all()],
            
            'delay_entries': [{
                'category': delay.get_category_display() if hasattr(delay, 'get_category_display') else delay.category,
                'description': delay.description,
                'duration_hours': float(delay.duration_hours),
                'impact_level': delay.get_impact_level_display() if hasattr(delay, 'get_impact_level_display') else delay.impact_level,
                'mitigation_actions': delay.mitigation_actions,
            } for delay in entry.delay_entries.all()],
            
            'visitor_entries': [{
                'visitor_name': visitor.visitor_name,
                'company': visitor.company,
                'visitor_type': visitor.get_visitor_type_display() if hasattr(visitor, 'get_visitor_type_display') else visitor.visitor_type,
                'purpose_of_visit': visitor.purpose_of_visit,
                'arrival_time': visitor.arrival_time.strftime('%H:%M') if visitor.arrival_time else 'N/A',
            } for visitor in entry.visitor_entries.all()],
            
            'subcontractor_entries': [{
                'company_name': sub.company_name,
                'work_description': sub.work_description,
                'daily_cost': float(sub.daily_cost),
            } for sub in subcontractor_entries],
        }
        
        return JsonResponse(data)
        
    except DiaryEntry.DoesNotExist:
        return JsonResponse({'error': 'Entry not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_admin_role
def update_entry_status(request, entry_id):
    """Update diary entry status"""
    if request.method == 'POST':
        try:
            entry = DiaryEntry.objects.get(id=entry_id, draft=False)
            action = request.POST.get('action')
            
            if action == 'reviewed':
                entry.status = 'complete'
                entry.reviewed_by = request.user
                entry.reviewed_date = timezone.now()
                entry.save()
                return JsonResponse({'success': True, 'message': 'Entry marked as reviewed'})
            elif action == 'needs_revision':
                entry.status = 'needs_revision'
                entry.reviewed_by = request.user
                entry.reviewed_date = timezone.now()
                entry.save()
                return JsonResponse({'success': True, 'message': 'Entry marked as needs revision', 'project_name': entry.project.name})
            else:
                return JsonResponse({'error': 'Invalid action'}, status=400)
                
        except DiaryEntry.DoesNotExist:
            return JsonResponse({'error': 'Entry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@require_admin_role
def send_revision(request):
    """Send entry to site manager for revision"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entry_id = data.get('entry_id')
            project_name = data.get('project_name')
            
            # Here you would implement notification logic
            # For now, just return success
            return JsonResponse({'success': True, 'message': f'Revision sent to site manager for {project_name}'})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
@require_admin_role
def admin_print_layout(request):
    """Admin print layout view"""
    entry_id = request.GET.get('entry_id')
    
    if entry_id:
        # Single entry print
        try:
            entry = DiaryEntry.objects.get(id=entry_id, draft=False)
            project = entry.project
            context = {
                'project': project,
                'diary_entry': entry,
            }
        except DiaryEntry.DoesNotExist:
            context = {'error': 'Entry not found'}
    else:
        # Multiple entries or filtered print - use sample data for now
        context = {
            'project': {'name': 'Sample Project', 'client_name': 'Sample Client', 'location': 'Sample Location'},
            'diary_entry': None,
        }
    
    return render(request, 'admin/printlayout.html', context)



# This function was replaced by the comprehensive adminreports function above

@require_site_manager_role
def generate_project_report(request, project_id):
    """Generate project report - API endpoint"""
    if request.method == 'POST':
        try:
            project = get_object_or_404(Project, id=project_id)
            
            # Verify user has access
            if not request.user.is_staff:
                user_projects = Project.objects.filter(
                    Q(project_manager=request.user) | Q(architect=request.user)
                )
                if project not in user_projects:
                    return JsonResponse({'error': 'Access denied'}, status=403)
            
            # Mock report generation - replace with actual report logic
            report_data = {
                'project_name': project.name,
                'generated_at': timezone.now().isoformat(),
                'status': 'success',
                'download_url': f'/reports/project_{project_id}_{timezone.now().strftime("%Y%m%d")}.pdf'
            }
            
            return JsonResponse(report_data)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@require_site_manager_role
@require_http_methods(["GET"])
def api_project_location(request, project_id):
    """API endpoint to get project location"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        return JsonResponse({
            'location': escape(project.location or ''),
            'project_name': escape(project.name)
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Project location API error: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)

@require_site_manager_role
@require_http_methods(["GET"])
def api_project_data(request, project_id):
    """API endpoint to get comprehensive project data for reports"""
    try:
        project_id = int(project_id)
        project = get_object_or_404(Project, id=project_id)
        
        # Verify user has access to this project
        if not request.user.is_staff:
            user_projects = Project.objects.filter(
                Q(project_manager=request.user) | Q(architect=request.user)
            )
            if project not in user_projects:
                return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Get project entries for date range calculation
        project_entries = DiaryEntry.objects.filter(project=project).order_by('entry_date')
        
        # Calculate date range from actual entries
        start_date = None
        end_date = None
        if project_entries.exists():
            start_date = project_entries.first().entry_date.strftime('%Y-%m-%d')
            end_date = project_entries.last().entry_date.strftime('%Y-%m-%d')
        else:
            # Fallback to project dates
            start_date = project.start_date.strftime('%Y-%m-%d') if project.start_date else ''
            end_date = project.expected_end_date.strftime('%Y-%m-%d') if project.expected_end_date else ''
        
        # Get latest weather condition from entries
        latest_entry = project_entries.filter(weather_condition__isnull=False).exclude(weather_condition='').last()
        weather_condition = latest_entry.weather_condition if latest_entry else 'sunny'
        
        # Get contractor info (assuming it's stored in project or can be derived)
        contractor = project.client_name or 'Default Contractor'
        
        return JsonResponse({
            'location': escape(project.location or ''),
            'weather_condition': weather_condition,
            'contractor': escape(contractor),
            'start_date': start_date,
            'end_date': end_date,
            'project_name': escape(project.name)
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid project ID'}, status=400)
    except Exception as e:
        logger.error(f"Project data API error: {str(e)}")
        return JsonResponse({'error': 'Server error'}, status=500)

@login_required
@require_site_manager_role
def debug_entries(request):
    """Debug view to check diary entries and related data"""
    entries = DiaryEntry.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    debug_info = []
    
    for entry in entries:
        materials = MaterialEntry.objects.filter(diary_entry=entry)
        equipment = EquipmentEntry.objects.filter(diary_entry=entry)
        labor = LaborEntry.objects.filter(diary_entry=entry)
        
        debug_info.append({
            'entry': entry,
            'materials': materials,
            'equipment': equipment,
            'labor': labor,
        })
    
    return JsonResponse({
        'entries': [{
            'id': info['entry'].id,
            'project': info['entry'].project.name,
            'date': info['entry'].entry_date.strftime('%Y-%m-%d'),
            'materials_count': info['materials'].count(),
            'equipment_count': info['equipment'].count(),
            'labor_count': info['labor'].count(),
            'materials': [{'name': m.material_name, 'quantity': str(m.quantity_delivered), 'cost': str(m.total_cost)} for m in info['materials']],
            'equipment': [{'name': e.equipment_type, 'hours': str(e.hours_operated), 'cost': str(e.total_rental_cost)} for e in info['equipment']],
            'labor': [{'type': l.labor_type, 'workers': l.workers_count, 'hours': str(l.hours_worked), 'cost': str(l.total_cost)} for l in info['labor']],
        } for info in debug_info]
    })

@login_required
@require_site_manager_role
@csrf_protect
def delete_draft(request, draft_id):
    """Delete a specific draft via AJAX"""
    if request.method == 'POST':
        try:
            draft = DiaryEntry.objects.get(id=draft_id, created_by=request.user, draft=True)
            draft.delete()
            logger.info(f"Draft {draft_id} deleted by user {request.user.id}")
            return JsonResponse({'success': True, 'message': 'Draft deleted successfully'})
        except DiaryEntry.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Draft not found or access denied'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting draft {draft_id}: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error deleting draft'}, status=500)
    return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

@login_required
@require_site_manager_role
@csrf_protect
def sitedraft(request):
    """Site Manager drafts view with real database data"""
    # Handle draft deletion via form submission (fallback)
    if request.method == 'POST' and request.POST.get('action') == 'delete_draft':
        draft_id = request.POST.get('draft_id')
        try:
            draft_id = int(draft_id)
            draft = DiaryEntry.objects.get(id=draft_id, created_by=request.user, draft=True)
            draft.delete()
            messages.success(request, 'Draft deleted successfully!')
            logger.info(f"Draft {draft_id} deleted by user {request.user.id}")
        except (ValueError, TypeError, DiaryEntry.DoesNotExist):
            messages.error(request, 'Draft not found or access denied.')
        return redirect('site_diary:sitedraft')
    
    # Get user's draft diary entries
    if request.user.is_staff:
        drafts = DiaryEntry.objects.filter(draft=True)
    else:
        user_projects = Project.objects.filter(
            Q(project_manager=request.user) | Q(architect=request.user),
            status__in=['planning', 'active', 'on_hold', 'completed']
        )
        drafts = DiaryEntry.objects.filter(
            project__in=user_projects,
            draft=True
        )
    
    # Order by most recent
    drafts = drafts.select_related('project', 'created_by').order_by('-created_at')
    
    # Statistics
    total_drafts = drafts.count()
    recent_drafts = drafts.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    submitted_entries = DiaryEntry.objects.filter(
        created_by=request.user,
        draft=False
    ).count()
    
    # Pagination
    paginator = Paginator(drafts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'drafts': page_obj,
        'page_obj': page_obj,
        'stats': {
            'total_drafts': total_drafts,
            'recent_drafts': recent_drafts,
            'submitted_entries': submitted_entries,
        },
        'user': request.user,
    }
    return render(request, 'site_diary/sitedraft.html', context)