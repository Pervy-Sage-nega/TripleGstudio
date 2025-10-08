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
    path('sitedraft/', views.sitedraft, name='sitedraft'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    
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
]