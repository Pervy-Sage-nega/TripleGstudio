from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Admin authentication URLs (full system access)
    path('admin-auth/login/', views.admin_login_view, name='admin_login'),
    path('admin-auth/register/', views.admin_register_view, name='admin_register'),
    path('admin-auth/verify-otp/', views.admin_verify_otp, name='admin_verify_otp'),
    path('admin-auth/resend-otp/', views.admin_resend_otp, name='admin_resend_otp'),
    path('admin-auth/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin-auth/forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('admin-auth/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    
    # Site Manager authentication URLs (handles blog creation)
    path('sitemanager/login/', views.sitemanager_login_view, name='sitemanager_login'),
    path('sitemanager/register/', views.sitemanager_register_view, name='sitemanager_register'),
    path('sitemanager/verify-otp/', views.sitemanager_verify_otp, name='sitemanager_verify_otp'),
    path('sitemanager/pending-approval/', views.sitemanager_pending_approval, name='sitemanager_pending_approval'),
    path('sitemanager/logout/', views.sitemanager_logout_view, name='sitemanager_logout'),
    path('sitemanager/forgot-password/', views.sitemanager_forgot_password, name='sitemanager_forgot_password'),
    path('sitemanager/reset-password/', views.sitemanager_reset_password, name='sitemanager_reset_password'),
    
    # Client authentication URLs (public users)
    path('client/login/', views.client_login_view, name='client_login'),
    path('client/register/', views.client_register_view, name='client_register'),
    path('client/verify-otp/', views.client_verify_otp, name='client_verify_otp'),
    path('client/resend-otp/', views.client_resend_otp, name='client_resend_otp'),
    path('client/logout/', views.client_logout_view, name='client_logout'),
    path('client/forgot-password/', views.client_forgot_password, name='client_forgot_password'),
    path('client/reset-password/', views.client_reset_password, name='client_reset_password'),
]