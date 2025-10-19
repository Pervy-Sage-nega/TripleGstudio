from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'core'

def user_dashboard_redirect(request):
    """Redirect /user/ to client dashboard for all authenticated users"""
    if request.user.is_authenticated:
        return redirect('core:clientdashboard')
    return redirect('core:usersettings')

urlpatterns = [
    path('', views.home, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('project/', views.project, name='project'),
    path('usersettings/', views.usersettings, name='usersettings'),
    path('clientdashboard/', views.clientdashboard, name='clientdashboard'),
    path('project/<int:project_id>/', views.client_project_detail, name='client_project_detail'),
    path('user/', user_dashboard_redirect, name='user_dashboard'),  # Redirect for backward compatibility
]