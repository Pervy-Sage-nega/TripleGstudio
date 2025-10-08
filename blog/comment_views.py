"""
Comment views for the Triple G Blog System
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import BlogPost
from .comments import Comment, CommentManager, CommentLike
from .decorators import require_admin_role
import json


@csrf_protect
@require_http_methods(["POST"])
def add_comment(request, post_slug):
    """Add a new comment to a blog post"""
    try:
        blog_post = get_object_or_404(BlogPost, slug=post_slug, status='published')
        
        # Get form data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST
        
        content = data.get('content', '').strip()
        author_name = data.get('author_name', '').strip()
        author_email = data.get('author_email', '').strip()
        author_website = data.get('author_website', '').strip()
        parent_id = data.get('parent_id')
        
        # Validation
        if not content:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'Comment content is required.'})
            else:
                return redirect('blog:blog_detail', slug=post_slug)
        
        if not author_name:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'Name is required.'})
            else:
                return redirect('blog:blog_detail', slug=post_slug)
        
        if not author_email:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'Email is required.'})
            else:
                return redirect('blog:blog_detail', slug=post_slug)
        
        if len(content) > 1000:
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': 'Comment is too long. Maximum 1000 characters allowed.'})
            else:
                return redirect('blog:blog_detail', slug=post_slug)
        
        # Get parent comment if replying
        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, blog_post=blog_post)
            except Comment.DoesNotExist:
                if request.content_type == 'application/json':
                    return JsonResponse({'success': False, 'message': 'Parent comment not found.'})
                else:
                    return redirect('blog:blog_detail', slug=post_slug)
        
        # Create comment
        comment = CommentManager.create_comment(
            blog_post=blog_post,
            content=content,
            author_name=author_name,
            author_email=author_email,
            author_website=author_website,
            parent=parent,
            user=request.user if request.user.is_authenticated else None,
            request=request
        )
        
        # Handle AJAX vs regular form submission
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author_name': comment.author_name,
                    'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    'status': comment.status,
                    'is_reply': comment.is_reply,
                    'parent_id': comment.parent_id if comment.parent else None,
                } if comment.status == 'approved' else None
            })
        else:
            # Regular form submission - redirect back to blog post
            return redirect('blog:blog_detail', slug=blog_post.slug)
        
    except Exception as e:
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'message': 'An error occurred while posting your comment. Please try again.'
            })
        else:
            return redirect('blog:blog_detail', slug=post_slug)


@require_http_methods(["POST"])
def like_comment(request, comment_id):
    """Like or dislike a comment"""
    try:
        comment = get_object_or_404(Comment, id=comment_id, status='approved')
        is_like = request.POST.get('is_like', 'true').lower() == 'true'
        
        # Check if user already liked/disliked
        user = request.user if request.user.is_authenticated else None
        ip_address = CommentManager.get_client_ip(request) if not user else None
        
        existing_like = CommentLike.objects.filter(
            comment=comment,
            user=user,
            ip_address=ip_address
        ).first()
        
        if existing_like:
            if existing_like.is_like == is_like:
                # Remove like/dislike
                existing_like.delete()
                if is_like:
                    comment.likes = max(0, comment.likes - 1)
                else:
                    comment.dislikes = max(0, comment.dislikes - 1)
                action = 'removed'
            else:
                # Change like to dislike or vice versa
                if existing_like.is_like:
                    comment.likes = max(0, comment.likes - 1)
                    comment.dislikes += 1
                else:
                    comment.dislikes = max(0, comment.dislikes - 1)
                    comment.likes += 1
                
                existing_like.is_like = is_like
                existing_like.save()
                action = 'changed'
        else:
            # Create new like/dislike
            CommentLike.objects.create(
                comment=comment,
                user=user,
                ip_address=ip_address,
                is_like=is_like
            )
            
            if is_like:
                comment.likes += 1
            else:
                comment.dislikes += 1
            
            action = 'added'
        
        comment.save()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'likes': comment.likes,
            'dislikes': comment.dislikes
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred. Please try again.'
        })


@require_admin_role
def moderate_comments(request):
    """Admin view for comment moderation"""
    status_filter = request.GET.get('status', 'pending')
    
    comments = Comment.objects.select_related(
        'blog_post', 'author', 'parent'
    ).filter(status=status_filter).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(comments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get counts for different statuses
    status_counts = {
        'pending': Comment.objects.filter(status='pending').count(),
        'approved': Comment.objects.filter(status='approved').count(),
        'rejected': Comment.objects.filter(status='rejected').count(),
        'spam': Comment.objects.filter(status='spam').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'comments': page_obj.object_list,
        'status_filter': status_filter,
        'status_counts': status_counts,
    }
    
    return render(request, 'admin/comment_moderation.html', context)


@require_admin_role
@require_http_methods(["POST"])
def moderate_comment_action(request, comment_id):
    """Perform moderation action on a comment"""
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        action = request.POST.get('action')
        note = request.POST.get('note', '')
        
        if action == 'approve':
            comment.approve(moderator=request.user)
            message = 'Comment approved successfully.'
        elif action == 'reject':
            comment.reject(moderator=request.user, note=note)
            message = 'Comment rejected successfully.'
        elif action == 'spam':
            comment.mark_as_spam(moderator=request.user)
            message = 'Comment marked as spam.'
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action.'
            })
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_status': comment.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while moderating the comment.'
        })


@require_admin_role
@require_http_methods(["POST"])
def bulk_moderate_comments(request):
    """Bulk moderation actions"""
    try:
        comment_ids = request.POST.getlist('comment_ids')
        action = request.POST.get('action')
        
        if not comment_ids:
            return JsonResponse({
                'success': False,
                'message': 'No comments selected.'
            })
        
        comments = Comment.objects.filter(id__in=comment_ids)
        count = 0
        
        for comment in comments:
            if action == 'approve':
                comment.approve(moderator=request.user)
                count += 1
            elif action == 'reject':
                comment.reject(moderator=request.user)
                count += 1
            elif action == 'spam':
                comment.mark_as_spam(moderator=request.user)
                count += 1
            elif action == 'delete':
                comment.delete()
                count += 1
        
        return JsonResponse({
            'success': True,
            'message': f'{count} comments processed successfully.',
            'count': count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during bulk moderation.'
        })


def get_comments(request, post_slug):
    """Get comments for a blog post (AJAX endpoint)"""
    try:
        blog_post = get_object_or_404(BlogPost, slug=post_slug, status='published')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Get comment tree
        comments = CommentManager.get_comment_tree(blog_post)
        
        # Paginate root comments
        paginator = Paginator(comments, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize comments
        def serialize_comment(comment):
            return {
                'id': comment.id,
                'content': comment.content,
                'author_name': comment.author_name,
                'author_website': comment.author_website,
                'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                'likes': comment.likes,
                'dislikes': comment.dislikes,
                'replies': [serialize_comment(reply) for reply in getattr(comment, 'replies_list', [])],
                'can_reply': True,
            }
        
        serialized_comments = [serialize_comment(comment) for comment in page_obj.object_list]
        
        return JsonResponse({
            'success': True,
            'comments': serialized_comments,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'total_pages': paginator.num_pages,
            'current_page': page,
            'total_comments': Comment.objects.filter(
                blog_post=blog_post, 
                status='approved'
            ).count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error loading comments.'
        })
