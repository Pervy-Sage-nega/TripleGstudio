from django.urls import path
from . import views
from . import newsletter_views
from . import comment_views

app_name = 'blog'

urlpatterns = [
    # Admin views
    path('admin/management/', views.blog_management, name='blogmanagement'),
    path('admin/recently-deleted/', views.admin_recently_deleted, name='admin_recently_deleted'),
    path('admin/restore/<int:post_id>/', views.admin_restore_blog, name='admin_restore_blog'),
    path('admin/permanent-delete/<int:post_id>/', views.admin_permanent_delete_blog, name='admin_permanent_delete_blog'),
    path('admin/approve/<int:post_id>/', views.approve_blog_post, name='approve_blog_post'),
    path('admin/reject/<int:post_id>/', views.reject_blog_post, name='reject_blog_post'),
    path('admin/change-status/<int:post_id>/', views.change_blog_status, name='change_blog_status'),
    path('admin/toggle-featured/<int:post_id>/', views.admin_toggle_featured, name='admin_toggle_featured'),
    
    # Site manager views
    path('drafts/', views.drafts, name='drafts'),
    path('createblog/', views.createblog, name='createblog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('recently-deleted/', views.recently_deleted, name='recently_deleted'),
    path('restore-blog/<int:blog_id>/', views.restore_blog, name='restore_blog'),
    path('permanent-delete/<int:blog_id>/', views.permanent_delete_blog, name='permanent_delete_blog'),
    path('get-post-data/<int:post_id>/', views.get_blog_post_data, name='get_blog_post_data'),
    
    # Public views
    path('', views.blog_list, name='blog_list'),
    path('post/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('category/<slug:slug>/', views.category_list, name='category_list'),
    path('tag/<slug:slug>/', views.tag_list, name='tag_list'),
    
    # Search
    path('search/', views.search_posts, name='search_posts'),
    path('search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    
    # Newsletter
    path('newsletter/subscribe/', newsletter_views.newsletter_subscribe, name='newsletter_subscribe'),
    path('newsletter/confirm/<uuid:token>/', newsletter_views.newsletter_confirm, name='newsletter_confirm'),
    path('newsletter/unsubscribe/<uuid:token>/', newsletter_views.newsletter_unsubscribe, name='newsletter_unsubscribe'),
    path('newsletter/track/open/<int:campaign_id>/<int:subscriber_id>/', newsletter_views.newsletter_track_open, name='newsletter_track_open'),
    path('newsletter/track/click/<int:campaign_id>/<int:subscriber_id>/', newsletter_views.newsletter_track_click, name='newsletter_track_click'),
    
    # Comments
    path('post/<slug:post_slug>/comments/', comment_views.get_comments, name='get_comments'),
    path('post/<slug:post_slug>/comment/add/', comment_views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/like/', comment_views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', comment_views.delete_comment, name='delete_comment'),
    
    # Admin comment moderation
    path('admin/comments/', comment_views.moderate_comments, name='moderate_comments'),
    path('admin/comment/<int:comment_id>/moderate/', comment_views.moderate_comment_action, name='moderate_comment_action'),
    path('admin/comments/bulk-moderate/', comment_views.bulk_moderate_comments, name='bulk_moderate_comments'),
    
    # Analytics
    path('admin/analytics/', views.blog_analytics, name='blog_analytics'),
    path('admin/analytics/post/<int:post_id>/', views.post_analytics, name='post_analytics'),
    
    # AJAX endpoints
    path('toggle-featured/<int:post_id>/', views.toggle_featured, name='toggle_featured'),
    path('change-status/<int:post_id>/', views.change_status, name='change_status'),
    path('track-event/', views.track_analytics_event, name='track_analytics_event'),
    path('upload-content-image/', views.upload_content_image, name='upload_content_image'),
    # Legacy URLs for backward compatibility
    path('blogmanagement/', views.blog_management, name='blogmanagement'),
    path('bloglist/', views.blog_list, name='bloglist'),
]