from django.urls import path
from . import views, api

urlpatterns = [
    path('projectmanagement/', views.projectmanagement, name='projectmanagement'),
    path('projecttable/', views.projecttable, name='projecttable'),
    
    # Project CRUD operations
    path('create/', views.create_project, name='create_project'),
    path('edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),
    path('get-project/<int:project_id>/', views.get_project_data, name='get_project_data'),
    path('save-draft/', views.save_draft, name='save_draft'),
    path('bulk-update-status/', views.bulk_update_status, name='bulk_update_status'),
    path('bulk-delete/', views.bulk_delete_projects, name='bulk_delete_projects'),
    
    # Public views
    path('', views.project_list, name='project_list'),
    path('<int:project_id>/', views.project_detail, name='project_detail'),
    
    # API endpoints
    path('api/projects/', api.project_list_api, name='project_list_api'),
    path('api/projects/<int:project_id>/', api.project_detail_api, name='project_detail_api'),
    path('api/categories/', api.categories_api, name='categories_api'),
]