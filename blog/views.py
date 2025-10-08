from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, F, Count
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import BlogPost, Category, Tag, BlogImage
from .decorators import require_site_manager_role, require_admin_role, allow_public_access
from .seo import SEOManager

# Create your views here.

# ============================================================================
# ADMIN VIEWS
# ============================================================================

@require_admin_role
def blog_management(request):
    """Admin dashboard for blog management - Now includes drafts for review"""
    # Get ALL posts including drafts for admin review
    all_blog_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags', 'gallery_images').order_by('-created_date')
    
    # Get statistics for dashboard
    total_posts = all_blog_posts.count()
    published_posts = all_blog_posts.filter(status='published').count()
    draft_posts = all_blog_posts.filter(status='draft').count()
    archived_posts = all_blog_posts.filter(status='archived').count()
    featured_posts = all_blog_posts.filter(featured=True, status='published').count()
    
    # Get all categories for filter dropdown
    all_categories = Category.objects.all().order_by('name')
    
    # Get all authors for filter
    authors = BlogPost.objects.values_list('author__username', 'author__first_name', 'author__last_name').distinct()
    
    context = {
        'blog_posts': all_blog_posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'archived_posts': archived_posts,
        'featured_posts': featured_posts,
        'all_categories': all_categories,
        'authors': authors,
    }
    
    return render(request, 'admin/blogmanagement.html', context)


@require_site_manager_role
def create_blog_post(request):
    """Create a new blog post"""
    if request.method == 'POST':
        try:
            # Extract form data
            title = request.POST.get('title')
            content = request.POST.get('content')
            excerpt = request.POST.get('excerpt', '')
            category_id = request.POST.get('category')
            tag_names = request.POST.get('tags', '').split(',')
            status = request.POST.get('status', 'draft')
            featured = request.POST.get('featured') == 'on'
            seo_meta_title = request.POST.get('seo_meta_title', '')
            seo_meta_description = request.POST.get('seo_meta_description', '')
            
            # Create blog post
            blog_post = BlogPost.objects.create(
                title=title,
                content=content,
                excerpt=excerpt,
                author=request.user,
                status=status,
                featured=featured,
                seo_meta_title=seo_meta_title,
                seo_meta_description=seo_meta_description,
            )
            
            # Set category if provided
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    blog_post.category = category
                    blog_post.save()
                except Category.DoesNotExist:
                    pass
            
            # Handle tags
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    blog_post.tags.add(tag)
            
            # Handle featured image
            if 'featured_image' in request.FILES:
                blog_post.featured_image = request.FILES['featured_image']
                blog_post.save()
            
            # Handle gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for i, image_file in enumerate(gallery_images):
                BlogImage.objects.create(
                    blog_post=blog_post,
                    image=image_file,
                    order=i
                )
            
            # Redirect based on status
            if status == 'draft':
                messages.success(request, f'Draft "{title}" saved successfully!')
                redirect_url = reverse('blog:blog_drafts')
            else:
                messages.success(request, f'Blog post "{title}" submitted for admin approval!')
                redirect_url = reverse('blog:blog_drafts')  # Site managers view their posts in drafts
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Blog post created successfully!',
                    'redirect_url': redirect_url
                })
            
            return redirect(redirect_url)
            
        except Exception as e:
            messages.error(request, f'Error creating blog post: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error creating blog post: {str(e)}'
                })
    
    # GET request - show form
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'categories': categories,
        'tags': tags,
    }
    
    return render(request, 'blogcreation/createblog.html', context)


@require_site_manager_role
def edit_blog_post(request, post_id):
    """Edit an existing blog post"""
    blog_post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        try:
            # Update blog post fields
            blog_post.title = request.POST.get('title')
            blog_post.content = request.POST.get('content')
            blog_post.excerpt = request.POST.get('excerpt', '')
            blog_post.status = request.POST.get('status', 'draft')
            blog_post.featured = request.POST.get('featured') == 'on'
            blog_post.seo_meta_title = request.POST.get('seo_meta_title', '')
            blog_post.seo_meta_description = request.POST.get('seo_meta_description', '')
            
            # Update category
            category_id = request.POST.get('category')
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    blog_post.category = category
                except Category.DoesNotExist:
                    blog_post.category = None
            else:
                blog_post.category = None
            
            # Update featured image
            if 'featured_image' in request.FILES:
                blog_post.featured_image = request.FILES['featured_image']
            
            blog_post.save()
            
            # Update tags
            blog_post.tags.clear()
            tag_names = request.POST.get('tags', '').split(',')
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    blog_post.tags.add(tag)
            
            # Handle new gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for i, image_file in enumerate(gallery_images):
                BlogImage.objects.create(
                    blog_post=blog_post,
                    image=image_file,
                    order=blog_post.gallery_images.count() + i
                )
            
            messages.success(request, f'Blog post "{blog_post.title}" updated successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Blog post updated successfully!',
                    'redirect_url': reverse('blog:blog_drafts')
                })
            
            return redirect('blog:blog_drafts')
            
        except Exception as e:
            messages.error(request, f'Error updating blog post: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': f'Error updating blog post: {str(e)}'
                })
    
    # GET request - show form with existing data
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'blog_post': blog_post,
        'categories': categories,
        'tags': tags,
        'selected_tags': list(blog_post.tags.values_list('name', flat=True)),
    }
    
    return render(request, 'blogcreation/createblog.html', context)


@require_site_manager_role
def delete_blog_post(request, post_id):
    """Delete a blog post"""
    blog_post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        title = blog_post.title
        blog_post.delete()
        messages.success(request, f'Blog post "{title}" deleted successfully!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Blog post "{title}" deleted successfully!'
            })
        
        return redirect('blog:blog_drafts')
    
    return render(request, 'admin/blog_delete_confirm.html', {'blog_post': blog_post})


@require_site_manager_role
def get_blog_post_data(request, post_id):
    """AJAX endpoint to get blog post data for editing"""
    try:
        blog_post = get_object_or_404(BlogPost, id=post_id)
        
        data = {
            'id': blog_post.id,
            'title': blog_post.title,
            'content': blog_post.content,
            'excerpt': blog_post.excerpt,
            'category_id': blog_post.category.id if blog_post.category else None,
            'tags': list(blog_post.tags.values_list('name', flat=True)),
            'status': blog_post.status,
            'featured': blog_post.featured,
            'seo_meta_title': blog_post.seo_meta_title,
            'seo_meta_description': blog_post.seo_meta_description,
            'featured_image_url': blog_post.featured_image.url if blog_post.featured_image else None,
        }
        
        return JsonResponse({'success': True, 'data': data})
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


@require_site_manager_role
def blog_drafts(request):
    """Site manager's drafts page - shows all their blog posts (drafts and published)"""
    # Get all blog posts by current user
    user_blog_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags').filter(
        author=request.user
    ).order_by('-created_date')
    
    # Get statistics
    total_posts = user_blog_posts.count()
    draft_posts = user_blog_posts.filter(status='draft').count()
    published_posts = user_blog_posts.filter(status='published').count()
    archived_posts = user_blog_posts.filter(status='archived').count()
    
    # Get all categories for filter
    all_categories = Category.objects.all().order_by('name')
    
    context = {
        'blog_posts': user_blog_posts,
        'total_posts': total_posts,
        'draft_posts': draft_posts,
        'published_posts': published_posts,
        'archived_posts': archived_posts,
        'all_categories': all_categories,
    }
    
    return render(request, 'blogcreation/drafts.html', context)


# ============================================================================
# PUBLIC VIEWS
# ============================================================================

@allow_public_access
def blog_list(request):
    """Public blog listing page with filtering and search"""
    # Get query parameters
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')
    tag_slug = request.GET.get('tag', '')
    sort_by = request.GET.get('sort', 'newest')  # newest, oldest, popular, title
    
    # Base queryset - only published posts
    posts = BlogPost.objects.filter(status='published').select_related('author', 'category').prefetch_related('tags')
    
    # Apply search filter
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(seo_meta_title__icontains=search_query)
        )
    
    # Apply category filter
    selected_category = None
    if category_slug:
        try:
            selected_category = Category.objects.get(slug=category_slug)
            posts = posts.filter(category=selected_category)
        except Category.DoesNotExist:
            pass
    
    # Apply tag filter
    selected_tag = None
    if tag_slug:
        try:
            selected_tag = Tag.objects.get(slug=tag_slug)
            posts = posts.filter(tags=selected_tag)
        except Tag.DoesNotExist:
            pass
    
    # Apply sorting
    if sort_by == 'oldest':
        posts = posts.order_by('published_date')
    elif sort_by == 'popular':
        posts = posts.order_by('-view_count', '-published_date')
    elif sort_by == 'title':
        posts = posts.order_by('title')
    else:  # newest (default)
        posts = posts.order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts, 12)  # 12 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get featured posts for sidebar
    featured_posts = BlogPost.objects.filter(
        status='published', 
        featured=True
    ).order_by('-published_date')[:3]
    
    # Get categories with post counts
    categories = Category.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('name')
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:20]
    
    context = {
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
        'sort_by': sort_by,
        'featured_posts': featured_posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'total_posts': paginator.count,
    }
    
    return render(request, 'bloguser/bloglist.html', context)


@allow_public_access
def blog_detail(request, slug):
    """Individual blog post detail page with SEO optimization"""
    # Get the blog post
    blog_post = get_object_or_404(
        BlogPost.objects.select_related('author', 'category').prefetch_related('tags', 'gallery_images'),
        slug=slug,
        status='published'
    )
    
    # Increment view count (use F() to avoid race conditions)
    BlogPost.objects.filter(id=blog_post.id).update(view_count=F('view_count') + 1)
    blog_post.refresh_from_db()
    
    # Generate SEO data
    seo_manager = SEOManager()
    meta_tags = seo_manager.generate_meta_tags(blog_post, request)
    structured_data = seo_manager.generate_structured_data(blog_post, request)
    breadcrumb_data = seo_manager.generate_breadcrumb_data(blog_post, request)
    
    # Get related posts
    related_posts = blog_post.get_related_posts(limit=3)
    
    # Get recent posts for sidebar
    recent_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(id=blog_post.id).order_by('-published_date')[:5]
    
    # Get categories for sidebar
    categories = Category.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('name')
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:10]
    
    # Get comments for this blog post
    from .comments import CommentManager
    comments = CommentManager.get_comment_tree(blog_post)
    
    context = {
        'blog_post': blog_post,
        'related_posts': related_posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'comments': comments,
        'meta_tags': meta_tags,
        'structured_data': structured_data,
        'breadcrumb_data': breadcrumb_data,
    }
    
    return render(request, 'bloguser/blogindividualpage.html', context)


@allow_public_access
def category_list(request, slug):
    """Blog posts filtered by category"""
    category = get_object_or_404(Category, slug=slug)
    
    posts = BlogPost.objects.filter(
        category=category,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    }
    
    return render(request, 'bloguser/category_list.html', context)


@allow_public_access
def tag_list(request, slug):
    """Blog posts filtered by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    
    posts = BlogPost.objects.filter(
        tags=tag,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_date')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
    }
    
    return render(request, 'bloguser/tag_list.html', context)


# ============================================================================
# AJAX ENDPOINTS
# ============================================================================

@require_site_manager_role
def toggle_featured(request, post_id):
    """AJAX endpoint to toggle featured status"""
    if request.method == 'POST':
        try:
            blog_post = get_object_or_404(BlogPost, id=post_id)
            blog_post.featured = not blog_post.featured
            blog_post.save()
            
            return JsonResponse({
                'success': True,
                'featured': blog_post.featured,
                'message': f'Post {"featured" if blog_post.featured else "unfeatured"} successfully!'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@require_site_manager_role
def change_status(request, post_id):
    """AJAX endpoint to change post status"""
    if request.method == 'POST':
        try:
            blog_post = get_object_or_404(BlogPost, id=post_id)
            new_status = request.POST.get('status')
            
            if new_status in ['draft', 'published', 'archived']:
                blog_post.status = new_status
                blog_post.save()
                
                return JsonResponse({
                    'success': True,
                    'status': blog_post.status,
                    'message': f'Post status changed to {new_status}!'
                })
            else:
                return JsonResponse({'success': False, 'message': 'Invalid status'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@require_admin_role
def approve_blog_post(request, post_id):
    """Admin approves a blog post - keeps it as published"""
    if request.method == 'POST':
        try:
            blog_post = get_object_or_404(BlogPost, id=post_id)
            blog_post.status = 'published'
            blog_post.save()
            
            messages.success(request, f'Blog post "{blog_post.title}" approved and published!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Blog post "{blog_post.title}" approved!'
                })
            
            return redirect('blog:blogmanagement')
            
        except Exception as e:
            messages.error(request, f'Error approving blog post: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            
            return redirect('blog:blogmanagement')
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@require_admin_role
def reject_blog_post(request, post_id):
    """Admin rejects a blog post - sends it back to draft"""
    if request.method == 'POST':
        try:
            blog_post = get_object_or_404(BlogPost, id=post_id)
            
            # Get rejection reason from request
            rejection_reason = request.POST.get('reason', '').strip()
            
            # Update blog post with rejection details
            blog_post.status = 'draft'
            blog_post.rejection_reason = rejection_reason
            blog_post.rejected_by = request.user
            blog_post.rejected_at = timezone.now()
            blog_post.save()
            
            messages.warning(request, f'Blog post "{blog_post.title}" rejected and sent back to draft.')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'Blog post "{blog_post.title}" rejected!'
                })
            
            return redirect('blog:blogmanagement')
            
        except Exception as e:
            messages.error(request, f'Error rejecting blog post: {str(e)}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': str(e)
                })
            
            return redirect('blog:blogmanagement')
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ============================================================================
# SEARCH VIEWS
# ============================================================================

def search_posts(request):
    """Enhanced search with filters and suggestions"""
    from .search import BlogSearchEngine
    
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    tags = request.GET.getlist('tags')
    sort = request.GET.get('sort', 'relevance')
    page = int(request.GET.get('page', 1))
    
    if not query:
        return redirect('blog:blog_list')
    
    # Build filters
    filters = {
        'category': category,
        'tags': tags,
        'sort': sort,
    }
    
    # Perform search
    search_engine = BlogSearchEngine()
    results = search_engine.search(query, filters, page)
    
    # Track search analytics
    from .analytics import AnalyticsManager
    AnalyticsManager.track_event('search', request, search_query=query)
    
    context = {
        'search_results': results,
        'query': query,
        'categories': Category.objects.all(),
        'popular_tags': Tag.objects.annotate(
            post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count')[:20],
    }
    
    return render(request, 'bloguser/search_results.html', context)


def search_autocomplete(request):
    """AJAX endpoint for search autocomplete"""
    from .search import BlogSearchEngine
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    search_engine = BlogSearchEngine()
    suggestions = search_engine.get_autocomplete_suggestions(query)
    
    return JsonResponse({'suggestions': suggestions})


# ============================================================================
# ANALYTICS VIEWS
# ============================================================================

@require_admin_role
def blog_analytics(request):
    """Admin analytics dashboard"""
    from .analytics import AnalyticsManager
    
    days = int(request.GET.get('days', 30))
    dashboard_data = AnalyticsManager.get_dashboard_data(days)
    
    context = {
        'analytics_data': dashboard_data,
        'days': days,
    }
    
    return render(request, 'admin/blog_analytics.html', context)


@require_admin_role
def post_analytics(request, post_id):
    """Analytics for a specific blog post"""
    from .analytics import AnalyticsManager
    
    blog_post = get_object_or_404(BlogPost, id=post_id)
    days = int(request.GET.get('days', 30))
    
    post_data = AnalyticsManager.get_post_analytics(blog_post, days)
    
    context = {
        'blog_post': blog_post,
        'analytics_data': post_data,
        'days': days,
    }
    
    return render(request, 'admin/post_analytics.html', context)


def track_analytics_event(request):
    """AJAX endpoint for tracking analytics events"""
    from .analytics import AnalyticsManager
    import json
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            
            event_type = data.get('event_type')
            blog_post_id = data.get('blog_post_id')
            time_on_page = data.get('time_on_page')
            scroll_depth = data.get('scroll_depth')
            social_platform = data.get('social_platform')
            
            kwargs = {}
            
            if blog_post_id:
                try:
                    blog_post = BlogPost.objects.get(id=blog_post_id)
                    kwargs['blog_post'] = blog_post
                except BlogPost.DoesNotExist:
                    pass
            
            if time_on_page:
                kwargs['time_on_page'] = int(time_on_page)
            
            if scroll_depth:
                kwargs['scroll_depth'] = int(scroll_depth)
            
            if social_platform:
                kwargs['social_platform'] = social_platform
            
            AnalyticsManager.track_event(event_type, request, **kwargs)
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@require_admin_role
@require_http_methods(["POST"])
def change_blog_status(request, post_id):
    """Admin endpoint to change blog post status"""
    if request.method == 'POST':
        try:
            blog_post = get_object_or_404(BlogPost, id=post_id)
            new_status = request.POST.get('status')
            
            if new_status in ['draft', 'published', 'archived']:
                blog_post.status = new_status
                
                # Set published date when publishing
                if new_status == 'published' and not blog_post.published_date:
                    from django.utils import timezone
                    blog_post.published_date = timezone.now()
                    
                blog_post.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Blog post status changed to {new_status}',
                    'new_status': new_status
                })
            else:
                return JsonResponse({'success': False, 'message': 'Invalid status'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
