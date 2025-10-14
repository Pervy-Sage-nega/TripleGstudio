from django.urls import path
from . import views

app_name = 'admin_side'

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('home/', views.admin_home, name='admin_home'),
    path('settings/', views.admin_settings, name='admin_settings'),
    path('settings/update/', views.update_admin_settings, name='update_admin_settings'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('check-session/', views.check_session, name='check_session'),
    
    # User Management URLs
    path('users/', views.admin_user_list, name='admin_user_list'),
    path('users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('users/<int:user_id>/update-status/', views.update_user_status, name='update_user_status'),
    path('generate-employee-id/', views.generate_employee_id, name='generate_employee_id'),
]