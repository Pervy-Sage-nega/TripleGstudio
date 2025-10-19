from django.urls import path
from . import views

app_name = 'site_diary'

urlpatterns = [
    # Main site diary views
    path('diary/', views.diary, name='diary'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('newproject/', views.newproject, name='newproject'),
    path('history/', views.history, name='history'),
    path('reports/', views.reports, name='reports'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.site_manager_logout, name='site_manager_logout'),
    path('sitedraft/', views.sitedraft, name='sitedraft'),
    
    # Project management
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('print/<int:project_id>/', views.print_preview, name='print_preview'),
    path('sample-print/', views.sample_print, name='sample_print'),
    
    # API endpoints
    path('api/generate-report/<int:project_id>/', views.generate_project_report, name='generate_project_report'),
    path('api/filter-projects/', views.api_filter_projects, name='api_filter_projects'),
    
    # Admin views
    path('admin/clientproject/', views.adminclientproject, name='adminclientproject'),
    path('admin/diary/', views.admindiary, name='admindiary'),
    path('admin/diary-reviewer/', views.admindiaryreviewer, name='admindiaryreviewer'),
    path('admin/history/', views.adminhistory, name='adminhistory'),
    path('admin/reports/', views.adminreports, name='adminreports'),
    
    # External app views (keeping for compatibility)
    path('chatbot/', views.chatbot, name='chatbot'),
    path('createblog/', views.createblog, name='createblog'),
    path('drafts/', views.drafts, name='drafts'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('recently-deleted/', views.recently_deleted, name='recently_deleted'),
    path('restore-blog/<int:blog_id>/', views.restore_blog, name='restore_blog'),
    path('permanent-delete/<int:blog_id>/', views.permanent_delete_blog, name='permanent_delete_blog'),
]