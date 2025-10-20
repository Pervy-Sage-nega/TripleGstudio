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
from .models import BlogPost, Comment, CommentLike
from .comments import CommentManager
from .decorators import require_admin_role
import json


@csrf_protect
@require_http_methods(["POST"])
def add_comment(request, post_slug):
    """Add a new comment to a blog post"""
    try:
        blog_post = get_object_or_404(BlogPost, slug=post_slug, status='published')
        
        # Get comment data
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            content = data.get('content', '').strip()
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            parent_id = data.get('parent_id')
        else:
            content = request.POST.get('content', '').strip()
            author_name = request.POST.get('author_name', '').strip()
            author_email = request.POST.get('author_email', '').strip()
            parent_id = request.POST.get('parent_id')
        
        # Validation
        if not content:
            raise ValueError("Comment content is required")
        
        # For authenticated users, use their info
        if request.user.is_authenticated:
            if not author_name:
                author_name = request.user.get_full_name() or request.user.username
            if not author_email:
                author_email = request.user.email
        else:
            # For anonymous users, require name and email
            if not author_name:
                raise ValueError("Author name is required")
            if not author_email:
                raise ValueError("Author email is required")
        
        # Get parent comment if specified
        parent_comment = None
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, blog_post=blog_post)
            except Comment.DoesNotExist:
                parent_comment = None
        
        # Create comment using CommentManager
        comment = CommentManager.create_comment(
            blog_post=blog_post,
            content=content,
            author_name=author_name,
            author_email=author_email,
            parent=parent_comment,
            user=request.user if request.user.is_authenticated else None,
            request=request
        )
        
        # Verify comment was actually saved
        try:
            saved_comment = Comment.objects.get(id=comment.id)
        except Comment.DoesNotExist:
            raise Exception("Comment save failed")
        
        # Return JSON response for AJAX requests
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'message': 'Comment posted successfully!' if comment.status == 'approved' else 'Comment submitted for moderation.',
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author_name': comment.author_name,
                    'status': comment.status,
                    'created_at': comment.created_at.strftime('%B %d, %Y at %I:%M %p'),
                    'parent_id': comment.parent.id if comment.parent else None
                }
            })
        else:
            # No success message - just redirect back to post
            return redirect('blog:blog_detail', slug=post_slug)
        
    except Exception as e:
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'message': str(e) if isinstance(e, ValueError) else 'An error occurred while posting your comment. Please try again.'
            })
        else:
            messages.error(request, str(e) if isinstance(e, ValueError) else 'An error occurred while posting your comment.')
            return redirect('blog:blog_detail', slug=post_slug)


@require_http_methods(["POST"])
def like_comment(request, comment_id):
    """Like or dislike a comment"""
    print(f"like_comment called with comment_id: {comment_id}, type: {type(comment_id)}")
    
    # Disable mock response for real functionality
    # if str(comment_id) == '999':
    #     print("Returning mock response for comment 999")
    #     return JsonResponse({'success': True, 'action': 'added', 'likes': 6, 'dislikes': 2})
    
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
        print(f"Error in like_comment: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@csrf_protect
@require_http_methods(["POST", "DELETE"])
def delete_comment(request, comment_id):
    """Delete a comment (only by the author)"""
    try:
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Check if user is the author of the comment
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'message': 'You must be logged in to delete comments.'
            }, status=401)
        
        if comment.author != request.user:
            return JsonResponse({
                'success': False,
                'message': 'You can only delete your own comments.'
            }, status=403)
        
        # Store comment info before deletion
        comment_id = comment.id
        is_reply = comment.parent is not None
        parent_id = comment.parent.id if comment.parent else None
        
        # Delete the comment
        comment.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Comment deleted successfully.',
            'comment_id': comment_id,
            'is_reply': is_reply,
            'parent_id': parent_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting comment: {str(e)}'
        }, status=500)


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
