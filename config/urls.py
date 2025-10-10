"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from site_diary import views as site_diary_views
from core.views import permission_denied_view

# Import sitemaps
from blog.sitemaps import blog_sitemaps
from portfolio.sitemaps import portfolio_sitemaps

# Combine all sitemaps
sitemaps = {
    **blog_sitemaps,
    **portfolio_sitemaps,
}

urlpatterns = [
    # Put accounts URLs BEFORE admin to avoid conflicts
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('portfolio/', include(('portfolio.urls', 'portfolio'), namespace='portfolio')),
    path('diary/', include(('site_diary.urls', 'site'), namespace='site')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),
    path('chat/', include(('chatbot.urls', 'chatbot'), namespace='chatbot')),
    # Admin side URLs
    path('admin-panel/', include(('admin_side.urls', 'admin_side'), namespace='admin_side')),
    # Direct admin URLs for easier access
    path('adminside/clientproject/', site_diary_views.adminclientproject, name='direct_adminclientproject'),
    path('adminside/diary/', site_diary_views.admindiary, name='direct_admindiary'),
    path('adminside/diaryreviewer/', site_diary_views.admindiaryreviewer, name='direct_admindiaryreviewer'),
    path('adminside/history/', site_diary_views.adminhistory, name='direct_adminhistory'),
    path('adminside/reports/', site_diary_views.adminreports, name='direct_adminreports'),
    
    # Sitemap URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler403 = permission_denied_view  # For 403 Forbidden errors (permission denied)