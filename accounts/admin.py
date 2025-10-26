from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from .models import Profile, AdminProfile, SiteManagerProfile, SuperAdminProfile, OneTimePassword, SitePersonnelRole


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'assigned_architect')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'admin_role', 'approval_status', 'department', 
        'employee_id', 'failed_login_attempts', 'created_at'
    )
    list_filter = ('admin_role', 'approval_status', 'department')
    search_fields = ('user__username', 'user__email', 'employee_id', 'department')
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip', 'failed_login_attempts')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'admin_role', 'department', 'employee_id')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'approved_by', 'approved_at')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact', 'hire_date')
        }),
        ('Security Information', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_admins', 'deny_admins', 'suspend_admins']
    
    def approve_admins(self, request, queryset):
        from django.utils import timezone
        from .utils import send_admin_approval_email
        
        approved_count = 0
        email_sent_count = 0
        
        for admin_profile in queryset:
            # Update approval status
            admin_profile.approval_status = 'approved'
            admin_profile.approved_by = request.user
            admin_profile.approved_at = timezone.now()
            admin_profile.save()
            approved_count += 1
            
            # Send approval email using utility function
            if send_admin_approval_email(admin_profile, request.user):
                email_sent_count += 1
        
        self.message_user(request, f'{approved_count} admin(s) approved successfully. {email_sent_count} notification email(s) sent.')
    approve_admins.short_description = "Approve selected admin accounts"
    
    def deny_admins(self, request, queryset):
        from .utils import send_admin_denial_email
        
        denied_count = 0
        email_sent_count = 0
        
        for admin_profile in queryset:
            admin_profile.approval_status = 'denied'
            admin_profile.save()
            denied_count += 1
            
            # Send denial email using utility function
            if send_admin_denial_email(admin_profile):
                email_sent_count += 1
        
        self.message_user(request, f'{denied_count} admin(s) denied. {email_sent_count} notification email(s) sent.')
    deny_admins.short_description = "Deny selected admin accounts"
    
    def suspend_admins(self, request, queryset):
        from .utils import send_admin_suspension_email
        
        suspended_count = 0
        email_sent_count = 0
        
        for admin_profile in queryset:
            admin_profile.approval_status = 'suspended'
            admin_profile.save()
            suspended_count += 1
            
            # Send suspension email using utility function
            if send_admin_suspension_email(admin_profile):
                email_sent_count += 1
        
        self.message_user(request, f'{suspended_count} admin(s) suspended. {email_sent_count} notification email(s) sent.')
    suspend_admins.short_description = "Suspend selected admin accounts"


@admin.register(SitePersonnelRole)
class SitePersonnelRoleAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name', 'employee_id_prefix', 'is_active', 'order')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'display_name', 'employee_id_prefix', 'description')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )


@admin.register(SiteManagerProfile)
class SiteManagerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'site_role', 'approval_status', 'department', 
        'employee_id', 'failed_login_attempts', 'created_at'
    )
    list_filter = ('approval_status', 'site_role', 'department')
    search_fields = ('user__username', 'user__email', 'employee_id', 'department')
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip', 'failed_login_attempts')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'site_role', 'department', 'employee_id')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'approved_by', 'approved_at')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact', 'hire_date', 'company_department')
        }),
        ('Security Information', {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_sitemanagers', 'deny_sitemanagers', 'suspend_sitemanagers']
    
    def approve_sitemanagers(self, request, queryset):
        from django.utils import timezone
        from .utils import send_admin_approval_email
        
        approved_count = 0
        email_sent_count = 0
        
        for sitemanager_profile in queryset:
            # Update approval status
            sitemanager_profile.approval_status = 'approved'
            sitemanager_profile.approved_by = request.user
            sitemanager_profile.approved_at = timezone.now()
            sitemanager_profile.save()
            approved_count += 1
            
            # Send approval email using utility function
            if send_admin_approval_email(sitemanager_profile, request.user):
                email_sent_count += 1
        
        self.message_user(request, f'{approved_count} site manager(s) approved successfully. {email_sent_count} notification email(s) sent.')
    approve_sitemanagers.short_description = "Approve selected site manager accounts"
    
    def deny_sitemanagers(self, request, queryset):
        from .utils import send_admin_denial_email
        
        denied_count = 0
        email_sent_count = 0
        
        for sitemanager_profile in queryset:
            sitemanager_profile.approval_status = 'denied'
            sitemanager_profile.save()
            denied_count += 1
            
            # Send denial email using utility function
            if send_admin_denial_email(sitemanager_profile):
                email_sent_count += 1
        
        self.message_user(request, f'{denied_count} site manager(s) denied. {email_sent_count} notification email(s) sent.')
    deny_sitemanagers.short_description = "Deny selected site manager accounts"
    
    def suspend_sitemanagers(self, request, queryset):
        from .utils import send_admin_suspension_email
        
        suspended_count = 0
        email_sent_count = 0
        
        for sitemanager_profile in queryset:
            sitemanager_profile.approval_status = 'suspended'
            sitemanager_profile.save()
            suspended_count += 1
            if send_admin_suspension_email(sitemanager_profile):
                email_sent_count += 1
        
        self.message_user(request, f'{suspended_count} site manager(s) suspended. {email_sent_count} notification email(s) sent.')
    suspend_sitemanagers.short_description = "Suspend selected site manager accounts"


@admin.register(SuperAdminProfile)
class SuperAdminProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'phone', 'created_at')
    search_fields = ('user__username', 'user__email', 'title')
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'title')
        }),
        ('Contact Information', {
            'fields': ('phone', 'emergency_contact')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OneTimePassword)
class OneTimePasswordAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at', 'is_expired')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    
    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = 'Expired'


# Extend the default User admin to show admin profiles
class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip', 'failed_login_attempts')
    fields = ('admin_role', 'approval_status', 'department', 'employee_id', 'phone', 'emergency_contact', 'hire_date')


class CustomUserAdmin(BaseUserAdmin):
    inlines = (AdminProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if obj and obj.is_staff:
            return super().get_inline_instances(request, obj)
        return []


# Comment out the custom user admin for now to avoid conflicts
# admin.site.unregister(User)
# admin.site.register(User, CustomUserAdmin)