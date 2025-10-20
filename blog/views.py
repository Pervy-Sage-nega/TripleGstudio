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
from .models import BlogPost, Category, Tag, BlogImage, ContentImage

from .decorators import require_site_manager_role, require_admin_role, allow_public_access
from .seo import SEOManager

# Create your views here.

# ============================================================================
# ADMIN VIEWS
# ============================================================================

@require_admin_role
def blog_management(request):
    """Admin dashboard for blog management - Excludes drafts, shows pending/published/archived"""
    # Get posts excluding drafts and deleted posts (admins only see submitted posts)
    all_blog_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags', 'gallery_images').exclude(
        status='draft'
    ).filter(is_deleted=False).order_by('-created_date')
    
    # Get statistics for dashboard (including drafts for stats only)
    all_posts_for_stats = BlogPost.objects.filter(is_deleted=False)
    total_posts = all_posts_for_stats.count()
    published_posts = all_posts_for_stats.filter(status='published').count()
    draft_posts = all_posts_for_stats.filter(status='draft').count()
    pending_posts = all_posts_for_stats.filter(status='pending').count()
    archived_posts = all_posts_for_stats.filter(status='archived').count()
    featured_posts = all_posts_for_stats.filter(featured=True, status='published').count()
    
    # Get all categories for filter dropdown
    all_categories = Category.objects.all().order_by('name')
    
    # Get all authors for filter
    authors = BlogPost.objects.values_list('author__username', 'author__first_name', 'author__last_name').distinct()
    
    context = {
        'blog_posts': all_blog_posts,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'pending_posts': pending_posts,
        'archived_posts': archived_posts,
        'featured_posts': featured_posts,
        'all_categories': all_categories,
        'authors': authors,
    }
    
    return render(request, 'admin/blogmanagement.html', context)


@require_admin_role
def admin_recently_deleted(request):
    """Admin view for recently deleted blog posts"""
    # Get all deleted blog posts
    deleted_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags').filter(
        is_deleted=True
    ).order_by('-deleted_at')
    
    context = {
        'deleted_posts': deleted_posts,
    }
    
    return render(request, 'admin/recently_deleted_blogs.html', context)


@require_admin_role
def admin_restore_blog(request, post_id):
    """Admin restore a soft deleted blog post"""
    try:
        blog_post = BlogPost.objects.get(id=post_id, is_deleted=True)
        blog_post.is_deleted = False
        blog_post.deleted_at = None
        blog_post.save()
        messages.success(request, f'Blog post "{blog_post.title}" restored successfully.')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found or not deleted.')
    
    return redirect('blog:admin_recently_deleted')


@require_admin_role
def admin_permanent_delete_blog(request, post_id):
    """Admin permanently delete a blog post"""
    try:
        blog_post = BlogPost.objects.get(id=post_id, is_deleted=True)
        blog_title = blog_post.title
        blog_post.delete()
        messages.success(request, f'Blog post "{blog_title}" permanently deleted.')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found or not in deleted state.')
    
    return redirect('blog:admin_recently_deleted')


@require_site_manager_role
def createblog(request):
    """Create blog post - handles both GET (form display) and POST (form submission)"""
    # Handle delete operation
    if request.GET.get('delete'):
        try:
            blog_id = int(request.GET.get('delete'))
            blog_post = BlogPost.objects.get(id=blog_id, author=request.user)
            blog_title = blog_post.title
            blog_post.delete()
            messages.success(request, f'Blog post "{blog_title}" deleted successfully!')
            return redirect('blog:drafts')
        except (BlogPost.DoesNotExist, ValueError):
            messages.error(request, 'Blog post not found or you do not have permission to delete it.')
            return redirect('blog:drafts')
    
    # Handle edit operation
    edit_blog = None
    if request.GET.get('edit'):
        try:
            blog_id = int(request.GET.get('edit'))
            edit_blog = BlogPost.objects.prefetch_related('tags').get(id=blog_id, author=request.user)
        except (BlogPost.DoesNotExist, ValueError):
            messages.error(request, 'Blog post not found or you do not have permission to edit it.')
            return redirect('blog:drafts')
    
    if request.method == 'POST':
        try:
            # Extract form data
            title = request.POST.get('title')
            content = request.POST.get('content')
            # Unescape HTML entities in content
            import html
            content = html.unescape(content) if content else ''
            excerpt = request.POST.get('excerpt', '')
            category_id = request.POST.get('category')
            # Check if this is an edit operation
            edit_id = request.POST.get('edit_id')
            
            tags_raw = request.POST.get('tags', '')
            
            tag_names = tags_raw.split(',')
            status = request.POST.get('status', 'draft')
            featured = request.POST.get('featured') == 'on'
            seo_meta_title = request.POST.get('seo_meta_title', '')
            seo_meta_description = request.POST.get('seo_meta_description', '')
            featured_image_alt = request.POST.get('featured_image_alt', '')
            if edit_id:
                # Update existing blog post
                try:
                    blog_post = BlogPost.objects.get(id=edit_id, author=request.user)
                    blog_post.title = title
                    blog_post.content = content
                    blog_post.excerpt = excerpt
                    blog_post.status = status
                    blog_post.featured = featured
                    blog_post.seo_meta_title = seo_meta_title
                    blog_post.seo_meta_description = seo_meta_description
                    blog_post.featured_image_alt = featured_image_alt
                    blog_post.save()
                except BlogPost.DoesNotExist:
                    messages.error(request, 'Blog post not found or you do not have permission to edit it.')
                    return redirect('blog:drafts')
            else:
                # Create new blog post with proper user isolation
                blog_post = BlogPost.objects.create(
                    title=title,
                    content=content,
                    excerpt=excerpt,
                    author=request.user,  # Critical: Set the author to logged-in user
                    status=status,
                    featured=featured,
                    seo_meta_title=seo_meta_title,
                    seo_meta_description=seo_meta_description,
                    featured_image_alt=featured_image_alt,
                )
            
            # Set category if provided
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    blog_post.category = category
                    blog_post.save()
                except Category.DoesNotExist:
                    pass
            
            # Handle tags - clear existing tags first for edit operations
            if edit_id:
                blog_post.tags.clear()
            
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
            if 'gallery_images' in request.FILES:
                gallery_files = request.FILES.getlist('gallery_images')
                
                for i, gallery_file in enumerate(gallery_files):
                    # Get caption and alt text for new images
                    caption = request.POST.get(f'new_gallery_caption[{i}]', '')
                    alt_text = request.POST.get(f'new_gallery_alt[{i}]', '')
                    
                    BlogImage.objects.create(
                        blog_post=blog_post,
                        image=gallery_file,
                        caption=caption,
                        alt_text=alt_text,
                        order=i
                    )
            
            # Handle content images (images inserted in blog content)
            if 'content_images' in request.FILES:
                content_files = request.FILES.getlist('content_images')
                
                for i, content_file in enumerate(content_files):
                    caption = request.POST.get(f'content_image_caption[{i}]', '')
                    alt_text = request.POST.get(f'content_image_alt[{i}]', '')
                    
                    ContentImage.objects.create(
                        blog_post=blog_post,
                        image=content_file,
                        caption=caption,
                        alt_text=alt_text
                    )
            
            # Handle existing gallery image updates and deletions
            if edit_id:
                # Handle gallery image deletions first
                for key, value in request.POST.items():
                    if key.startswith('delete_gallery_image_') and value == 'true':
                        image_id = key.replace('delete_gallery_image_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.delete()
                        except BlogImage.DoesNotExist:
                            pass
                
                # Update existing gallery images (captions and alt text)
                for key, value in request.POST.items():
                    if key.startswith('gallery_caption_'):
                        image_id = key.replace('gallery_caption_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.caption = value
                            gallery_image.save()
                        except BlogImage.DoesNotExist:
                            pass
                    elif key.startswith('gallery_alt_'):
                        image_id = key.replace('gallery_alt_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.alt_text = value
                            gallery_image.save()
                        except BlogImage.DoesNotExist:
                            pass
            
            # Success message and redirect
            if status == 'draft':
                messages.success(request, 'Blog post saved as draft successfully!')
                return redirect('blog:drafts')  # Redirect to drafts page
            else:
                messages.success(request, 'Blog post created successfully!')
                return redirect('blog:drafts')
                
        except Exception as e:
            messages.error(request, f'Error creating blog post: {str(e)}')
            return redirect('blog:createblog')
    
    # GET request - show the form
    # Get categories and tags for the form
    categories = Category.objects.all().order_by('name')
    tags = Tag.objects.all().order_by('name')
    
    context = {
        'categories': categories,
        'tags': tags,
        'edit_blog': edit_blog,  # Pass the blog post being edited (if any)
    }
    
    return render(request, 'blogcreation/createblog.html', context)


@require_site_manager_role
def edit_blog_post(request, post_id):
    """Edit an existing blog post"""
    blog_post = get_object_or_404(BlogPost, id=post_id)
    
    if request.method == 'POST':
        try:
            # Update blog post fields
            content = request.POST.get('content')
            # Unescape HTML entities in content
            import html
            content = html.unescape(content) if content else ''
            
            blog_post.title = request.POST.get('title')
            blog_post.content = content
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
            
            # Update featured image alt text
            featured_image_alt = request.POST.get('featured_image_alt', '')
            blog_post.featured_image_alt = featured_image_alt
            
            blog_post.save()
            
            # Update tags
            blog_post.tags.clear()
            tag_names = request.POST.get('tags', '').split(',')
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                if tag_name:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    blog_post.tags.add(tag)
            
            # Handle existing gallery image updates and deletions
            for key, value in request.POST.items():
                if key.startswith('gallery_caption_') and not key.endswith('_new'):
                    image_id = key.replace('gallery_caption_', '')
                    try:
                        gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                        gallery_image.caption = value
                        
                        # Update alt text if provided
                        alt_key = f'gallery_alt_{image_id}'
                        if alt_key in request.POST:
                            gallery_image.alt_text = request.POST[alt_key]
                        
                        gallery_image.save()
                    except BlogImage.DoesNotExist:
                        pass
                
                # Handle gallery image deletions
                elif key.startswith('delete_gallery_image_'):
                    if value == 'true':
                        image_id = key.replace('delete_gallery_image_', '')
                        try:
                            gallery_image = BlogImage.objects.get(id=image_id, blog_post=blog_post)
                            gallery_image.delete()
                        except BlogImage.DoesNotExist:
                            pass
            
            # Handle new gallery images
            gallery_images = request.FILES.getlist('gallery_images')
            for i, image_file in enumerate(gallery_images):
                # Get caption and alt text for new images
                caption = request.POST.get(f'gallery_caption_{i}_new', '')
                alt_text = request.POST.get(f'gallery_alt_{i}_new', '')
                
                BlogImage.objects.create(
                    blog_post=blog_post,
                    image=image_file,
                    caption=caption,
                    alt_text=alt_text,
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
        'edit_blog': blog_post,  # Use 'edit_blog' to match template expectations
        'blog_post': blog_post,  # Keep both for compatibility
        'categories': categories,
        'tags': tags,
        'selected_tags': list(blog_post.tags.values_list('name', flat=True)),
    }
    
    return render(request, 'blogcreation/createblog.html', context)


@require_site_manager_role
def delete_blog(request, blog_id):
    """Soft delete a blog post"""
    try:
        # Check if user is admin (can delete any post) or site manager (can only delete their own posts)
        from accounts.utils import get_user_role
        user_role = get_user_role(request.user)
        
        if user_role == 'admin' or request.user.is_superuser:
            blog_post = BlogPost.objects.get(id=blog_id, is_deleted=False)
        else:
            blog_post = BlogPost.objects.get(id=blog_id, author=request.user, is_deleted=False)
            
        blog_post.is_deleted = True
        blog_post.deleted_at = timezone.now()
        blog_post.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Blog post "{blog_post.title}" moved to recently deleted.'
            })
            
        messages.success(request, f'Blog post "{blog_post.title}" moved to recently deleted.')
    except BlogPost.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Blog post not found or already deleted.'
            })
        messages.error(request, 'Blog post not found or already deleted.')
    
    # Redirect based on user role
    from accounts.utils import get_user_role
    user_role = get_user_role(request.user)
    if user_role == 'admin' or request.user.is_superuser:
        return redirect('blog:blogmanagement')
    else:
        return redirect('blog:recently_deleted')

@require_site_manager_role
def recently_deleted(request):
    """Show recently deleted blog posts"""
    # Get deleted blog posts by current user
    deleted_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags').filter(
        author=request.user,
        is_deleted=True
    ).order_by('-deleted_at')
    
    context = {
        'deleted_posts': deleted_posts,
    }
    
    return render(request, 'blogcreation/recently_deleted.html', context)

@require_site_manager_role
def restore_blog(request, blog_id):
    """Restore a soft deleted blog post"""
    try:
        blog_post = BlogPost.objects.get(id=blog_id, author=request.user, is_deleted=True)
        blog_post.is_deleted = False
        blog_post.deleted_at = None
        blog_post.save()
        messages.success(request, f'Blog post "{blog_post.title}" restored successfully.')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found or not deleted.')
    
    return redirect('blog:recently_deleted')

@require_site_manager_role
def permanent_delete_blog(request, blog_id):
    """Permanently delete a blog post"""
    try:
        blog_post = BlogPost.objects.get(id=blog_id, author=request.user, is_deleted=True)
        blog_title = blog_post.title
        blog_post.delete()
        messages.success(request, f'Blog post "{blog_title}" permanently deleted.')
    except BlogPost.DoesNotExist:
        messages.error(request, 'Blog post not found or not in deleted state.')
    
    return redirect('blog:recently_deleted')


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
def drafts(request):
    """Site manager's drafts page - shows only their blog posts with proper user isolation"""
    # Get all blog posts by current user (proper user isolation) - exclude deleted
    user_blog_posts = BlogPost.objects.select_related(
        'author', 'category'
    ).prefetch_related('tags').filter(
        author=request.user,  # Critical: Only show posts by the logged-in user
        is_deleted=False  # Exclude soft deleted posts
    ).order_by('-created_date')
    
    # Get statistics for the current user only
    total_posts = user_blog_posts.count()
    draft_posts = user_blog_posts.filter(status='draft').count()
    published_posts = user_blog_posts.filter(status='published').count()
    archived_posts = user_blog_posts.filter(status='archived').count()
    
    # Get all categories for filter dropdown
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
    paginator = Paginator(posts, 10)  # 10 posts per page
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
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        post_count=Count('blog_posts', filter=Q(blog_posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:20]
    
    context = {
        'tag': tag,
        'page_obj': page_obj,
        'posts': page_obj.object_list,
        'popular_tags': popular_tags,
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


@require_admin_role
@require_http_methods(["POST"])
def admin_toggle_featured(request, post_id):
    """Admin endpoint to toggle blog post featured status"""
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
@require_http_methods(["POST"])
def upload_content_image(request):
    """AJAX endpoint for uploading images within blog content"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No image file provided'})
        
        image_file = request.FILES['image']
        blog_post_id = request.POST.get('blog_post_id')
        alt_text = request.POST.get('alt_text', '')
        caption = request.POST.get('caption', '')
        
        # Get or create blog post
        if blog_post_id:
            try:
                blog_post = BlogPost.objects.get(id=blog_post_id, author=request.user)
            except BlogPost.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Blog post not found'})
        else:
            # Create a temporary blog post for the image
            blog_post = BlogPost.objects.create(
                title='Temporary Post',
                content='',
                author=request.user,
                status='draft'
            )
        
        # Create content image
        content_image = ContentImage.objects.create(
            blog_post=blog_post,
            image=image_file,
            alt_text=alt_text,
            caption=caption
        )
        
        return JsonResponse({
            'success': True,
            'image_url': content_image.image.url,
            'image_id': content_image.id,
            'blog_post_id': blog_post.id,
            'message': 'Image uploaded successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
