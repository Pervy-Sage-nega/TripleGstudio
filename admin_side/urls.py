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
]