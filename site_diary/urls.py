from django.urls import path
from . import views

app_name = 'site_diary'

urlpatterns = [
    # Main site diary views
    path('diary/', views.diary, name='diary'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('newproject/', views.newproject, name='newproject'),
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('history/', views.history, name='history'),
    path('logs/', views.diary_logs, name='diary_logs'),
    path('revision/<int:entry_id>/', views.revision_diary, name='revision_diary'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.site_manager_logout, name='site_manager_logout'),
    path('sitedraft/', views.sitedraft, name='sitedraft'),
    path('delete-draft/<int:draft_id>/', views.delete_draft, name='delete_draft'),
    path('debug-entries/', views.debug_entries, name='debug_entries'),
    
    # Project management
    path('api/weather/', views.weather_api, name='weather_api'),
    path('print/<int:project_id>/', views.print_preview, name='print_preview'),
    path('sample-print/', views.sample_print, name='sample_print'),
    
    # API endpoints
    path('api/generate-report/<int:project_id>/', views.generate_project_report, name='generate_project_report'),
    path('api/filter-projects/', views.api_filter_projects, name='api_filter_projects'),
    path('api/project-location/<int:project_id>/', views.api_project_location, name='api_project_location'),
    path('api/project-data/<int:project_id>/', views.api_project_data, name='api_project_data'),
    
    # PDF generation
    path('diary-entry-pdf/<int:entry_id>/', views.diary_entry_pdf, name='diary_entry_pdf'),
    
    # Admin views
    path('admin/clientproject/', views.adminclientproject, name='adminclientproject'),
    path('admin/diary/', views.admindiary, name='admindiary'),
    path('admin/diary-reviewer/', views.admindiaryreviewer, name='admindiaryreviewer'),
    path('admin/diary-entry/<int:entry_id>/', views.diary_entry_detail, name='diary_entry_detail'),
    path('admin/update-entry-status/<int:entry_id>/', views.update_entry_status, name='update_entry_status'),
    path('admin/send-revision/', views.send_revision, name='send_revision'),
    path('admin/print-layout/', views.admin_print_layout, name='admin_print_layout'),

    path('admin/reports/', views.adminreports, name='adminreports'),
    
    # External app views (keeping for compatibility)
    path('chatbot/', views.chatbot, name='chatbot'),
]