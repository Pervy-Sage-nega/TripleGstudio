/**
 * Blog Comments System
 * Handles dynamic comment functionality with Django backend integration
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Blog individual JS loaded');
    initCommentSystem();
});

/**
 * Initialize the comment system
 */
function initCommentSystem() {
    console.log('Initializing comment system');
    // Initialize reply buttons
    initReplyButtons();
    
    // Initialize comment likes
    initCommentLikes();
    
    // Initialize delete buttons
    initDeleteButtons();
}

/**
 * Initialize comment form submission
 */
function initCommentForm() {
    const commentForm = document.getElementById('blogCommentForm');
    
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const content = formData.get('content') || document.getElementById('commentContent').value;
            const authorName = formData.get('author_name') || 'Anonymous';
            const authorEmail = formData.get('author_email') || '';
            const parentId = formData.get('parent_id') || null;
            
            if (!content.trim()) {
                showMessage('Please enter a comment.', 'error');
                return;
            }
            
            // For authenticated users, name and email are pre-filled
            if (!authorName.trim()) {
                showMessage('Please enter your name.', 'error');
                return;
            }
            
            if (!authorEmail.trim()) {
                showMessage('Please enter your email.', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Posting...';
            submitBtn.disabled = true;
            
            // Submit comment
            submitComment({
                content: content,
                author_name: authorName,
                author_email: authorEmail,
                parent_id: parentId
            }).then(response => {
                if (response.success) {
                    this.reset();
                    
                    // Clear parent_id for next comment
                    const parentInput = document.getElementById('parent_id');
                    if (parentInput) {
                        parentInput.value = '';
                    }
                    
                    // If comment was approved, add it to the list
                    if (response.comment) {
                        addCommentToDOM(response.comment);
                        updateCommentCount();
                    }
                    
                    // Refresh the page to show the new comment
                    window.location.reload();
                } else {
                    showMessage(response.message, 'error');
                }
            }).catch(error => {
                showMessage('An error occurred. Please try again.', 'error');
            }).finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
}

/**
 * Submit comment to server
 */
async function submitComment(commentData) {
    const postSlug = getPostSlug();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const response = await fetch(`/blog/post/${postSlug}/comment/add/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(commentData)
    });
    
    return await response.json();
}

/**
 * Initialize reply buttons
 */
function initReplyButtons() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('reply-btn') || e.target.closest('.reply-btn')) {
            e.preventDefault();
            
            const replyBtn = e.target.classList.contains('reply-btn') ? e.target : e.target.closest('.reply-btn');
            const commentEl = replyBtn.closest('.comment');
            const commentId = commentEl.dataset.commentId;
            const commenterName = commentEl.querySelector('.commenter-name').textContent;
            
            console.log('Reply button clicked for comment:', commentId, 'by:', commenterName);
            
            // Check if user is authenticated
            const commentForm = document.getElementById('blogCommentForm');
            if (!commentForm) {
                // Show login prompt or redirect to login
                alert('Please log in to reply to comments.');
                return;
            }
            
            // Check if reply form already exists for this comment
            let existingReplyForm = commentEl.nextElementSibling;
            if (existingReplyForm && existingReplyForm.classList.contains('reply-form')) {
                // Toggle existing form
                existingReplyForm.style.display = existingReplyForm.style.display === 'none' ? 'block' : 'none';
                return;
            }
            
            // Create inline reply form
            createInlineReplyForm(commentEl, commentId, commenterName);
        }
    });
}

/**
 * Create inline reply form
 */
function createInlineReplyForm(commentEl, parentId, commenterName) {
    // Create reply form HTML
    const replyFormHTML = `
        <div class="reply-form" style="margin-top: 15px; padding: 15px; background: rgba(255, 255, 255, 0.05); border-radius: 8px; border-left: 3px solid #FF7120;">
            <h5 style="color: #FF7120; margin-bottom: 10px;">
                <i class="fas fa-reply"></i> Replying to ${commenterName}
            </h5>
            <form class="inline-reply-form">
                <input type="hidden" name="parent_id" value="${parentId}">
                <div class="form-group" style="margin-bottom: 15px;">
                    <textarea name="content" rows="3" class="form-control reply-textarea" 
                              placeholder="Write your reply..." required 
                              style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); color: #fff; border-radius: 6px; padding: 10px;"></textarea>
                </div>
                <div class="reply-actions" style="display: flex; gap: 10px;">
                    <button type="submit" class="btn btn-primary btn-sm" style="background: #FF7120; border: none; padding: 8px 16px; border-radius: 6px;">
                        <i class="fas fa-paper-plane"></i> Post Reply
                    </button>
                    <button type="button" class="btn btn-secondary btn-sm cancel-reply" style="background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2); padding: 8px 16px; border-radius: 6px; color: #fff;">
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    `;
    
    // Insert reply form after the entire comment (below it)
    commentEl.insertAdjacentHTML('afterend', replyFormHTML);
    
    // Get the newly created form (it's now the next sibling)
    const replyForm = commentEl.nextElementSibling;
    const inlineForm = replyForm.querySelector('.inline-reply-form');
    const cancelBtn = replyForm.querySelector('.cancel-reply');
    const textarea = replyForm.querySelector('.reply-textarea');
    
    // Focus on textarea
    textarea.focus();
    
    // Handle cancel button
    cancelBtn.addEventListener('click', function() {
        replyForm.remove();
    });
    
    // Handle form submission
    inlineForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const content = formData.get('content').trim();
        
        if (!content) {
            alert('Please enter a reply.');
            return;
        }
        
        // Show loading state
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
        submitBtn.disabled = true;
        
        // Submit reply
        submitReply(parentId, content, commenterName).then(response => {
            if (response.success) {
                // Remove reply form
                replyForm.remove();
                
                // Create and display the new nested reply immediately
                if (response.comment) {
                    createNestedReply(commentEl, response.comment);
                } else {
                    // If comment needs moderation, show message and refresh
                    alert('Reply submitted for moderation.');
                    window.location.reload();
                }
            } else {
                alert('Error posting reply: ' + (response.message || 'Please try again.'));
            }
        }).catch(error => {
            console.error('Reply error:', error);
            alert('Network error occurred. Please try again.');
        }).finally(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        });
    });
}

/**
 * Submit reply to server
 */
async function submitReply(parentId, content, commenterName) {
    const postSlug = getPostSlug();
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Get user info from the main comment form if available
    const authorNameField = document.getElementById('authorName');
    const authorEmailField = document.getElementById('authorEmail');
    
    const requestData = {
        content: `@${commenterName} ${content}`,
        parent_id: parentId
    };
    
    // Add author info if available (for non-authenticated users)
    if (authorNameField && authorNameField.value) {
        requestData.author_name = authorNameField.value;
    }
    if (authorEmailField && authorEmailField.value) {
        requestData.author_email = authorEmailField.value;
    }
    
    console.log('Submitting reply with data:', requestData);
    
    const response = await fetch(`/blog/post/${postSlug}/comment/add/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify(requestData)
    });
    
    const result = await response.json();
    console.log('Reply response:', result);
    return result;
}

/**
 * Create nested reply element and insert it after parent comment
 */
function createNestedReply(parentCommentEl, commentData) {
    // Create nested reply HTML
    const nestedReplyHTML = `
        <div class="comment nested-comment" data-comment-id="${commentData.id}">
            <div class="comment-avatar">
                <img src="/static/images/default-avatar.png" alt="${commentData.author_name}">
            </div>
            <div class="comment-content">
                <div class="comment-header">
                    <h4 class="commenter-name">${commentData.author_name}</h4>
                    <span class="comment-date">${commentData.created_at}</span>
                    ${commentData.status === 'pending' ? '<span class="status-badge pending-badge">Pending Approval</span>' : ''}
                </div>
                <p>${commentData.content}</p>
                <div class="comment-actions">
                    <button class="reply-btn" data-comment-id="${commentData.id}">Reply</button>
                    <button class="like-btn" data-comment-id="${commentData.id}">
                        <i class="fas fa-thumbs-up"></i> 0
                    </button>
                    <button class="dislike-btn" data-comment-id="${commentData.id}">
                        <i class="fas fa-thumbs-down"></i> 0
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Find where to insert the nested reply
    let insertAfter = parentCommentEl;
    
    // Look for existing nested comments after the parent
    let nextElement = parentCommentEl.nextElementSibling;
    while (nextElement && nextElement.classList.contains('nested-comment')) {
        insertAfter = nextElement;
        nextElement = nextElement.nextElementSibling;
    }
    
    // Insert the new nested reply
    insertAfter.insertAdjacentHTML('afterend', nestedReplyHTML);
    
    // Add animation effect
    const newReply = insertAfter.nextElementSibling;
    newReply.style.opacity = '0';
    newReply.style.transform = 'translateY(-10px)';
    
    // Animate in
    setTimeout(() => {
        newReply.style.transition = 'all 0.3s ease-out';
        newReply.style.opacity = '1';
        newReply.style.transform = 'translateY(0)';
    }, 10);
}

/**
 * Initialize comment like/dislike functionality
 */
function initCommentLikes() {
    console.log('Initializing comment likes');
    
    // Check if like buttons exist
    const likeButtons = document.querySelectorAll('.like-btn, .dislike-btn');
    console.log('Found like/dislike buttons:', likeButtons.length);
    
    document.addEventListener('click', function(e) {
        console.log('Click detected on:', e.target);
        
        if (e.target.classList.contains('like-btn') || e.target.classList.contains('dislike-btn')) {
            console.log('Like/dislike button clicked');
            e.preventDefault();
            
            const commentEl = e.target.closest('.comment');
            if (!commentEl) {
                console.error('Could not find comment element');
                return;
            }
            
            const commentId = commentEl.dataset.commentId;
            const isLike = e.target.classList.contains('like-btn');
            
            console.log('Comment ID:', commentId, 'Is Like:', isLike);
            
            likeComment(commentId, isLike).then(response => {
                console.log('Like response:', response);
                if (response.success) {
                    const voteType = isLike ? 'like' : 'dislike';
                    updateLikeButtons(commentEl, response.likes, response.dislikes, response.action, voteType);
                } else {
                    console.error('Like failed:', response.message);
                    alert('Error: ' + response.message);
                }
            }).catch(error => {
                console.error('Like error:', error);
                alert('Network error occurred');
            });
        }
    });
}

/**
 * Like or dislike a comment
 */
async function likeComment(commentId, isLike) {
    console.log('likeComment called with:', commentId, isLike);
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfToken) {
        console.error('CSRF token not found');
        throw new Error('CSRF token not found');
    }
    
    console.log('CSRF token found:', csrfToken.value);
    
    const url = `/blog/comment/${commentId}/like/`;
    console.log('Making request to:', url);
    
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken.value,
        },
        body: `is_like=${isLike}`
    });
    
    console.log('Response status:', response.status);
    
    if (!response.ok) {
        console.error('Response not OK:', response.status, response.statusText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('Response data:', data);
    return data;
}

/**
 * Load comments from server
 */
async function loadComments() {
    try {
        const postSlug = getPostSlug();
        const response = await fetch(`/blog/post/${postSlug}/comments/`);
        const data = await response.json();
        
        if (data.success) {
            renderComments(data.comments);
            updateCommentCount(data.total_comments);
        }
    } catch (error) {
        console.error('Error loading comments:', error);
    }
}

/**
 * Render comments in the DOM
 */
function renderComments(comments) {
    const commentsList = document.querySelector('.comments-list');
    if (!commentsList) return;
    
    commentsList.innerHTML = '';
    
    comments.forEach(comment => {
        const commentEl = createCommentElement(comment);
        commentsList.appendChild(commentEl);
        
        // Render replies
        if (comment.replies && comment.replies.length > 0) {
            comment.replies.forEach(reply => {
                const replyEl = createCommentElement(reply, true);
                commentsList.appendChild(replyEl);
            });
        }
    });
}

/**
 * Create comment element
 */
function createCommentElement(comment, isReply = false) {
    const commentEl = document.createElement('div');
    commentEl.className = `comment${isReply ? ' nested-comment' : ''}`;
    commentEl.dataset.commentId = comment.id;
    
    commentEl.innerHTML = `
        <div class="comment-avatar">
            <img src="/static/images/default-avatar.png" alt="${comment.author_name}">
        </div>
        <div class="comment-content">
            <div class="comment-header">
                <h4 class="commenter-name">${comment.author_name}</h4>
                <span class="comment-date">${comment.created_at}</span>
            </div>
            <p>${comment.content}</p>
            <div class="comment-actions">
                <button class="reply-btn">Reply</button>
                <button class="like-btn">
                    <i class="fas fa-thumbs-up"></i> ${comment.likes}
                </button>
                <button class="dislike-btn">
                    <i class="fas fa-thumbs-down"></i> ${comment.dislikes}
                </button>
            </div>
        </div>
    `;
    
    return commentEl;
}

/**
 * Add comment to DOM (for newly posted comments)
 */
function addCommentToDOM(comment) {
    const commentsList = document.querySelector('.comments-list');
    if (!commentsList) return;
    
    const commentEl = createCommentElement(comment);
    
    if (comment.parent_id) {
        // It's a reply - add after parent comment
        const parentComment = document.querySelector(`[data-comment-id="${comment.parent_id}"]`);
        if (parentComment) {
            parentComment.insertAdjacentElement('afterend', commentEl);
        }
    } else {
        // It's a top-level comment - add at the beginning
        commentsList.insertBefore(commentEl, commentsList.firstChild);
    }
}

/**
 * Update like/dislike buttons
 */
function updateLikeButtons(commentEl, likes, dislikes, action, voteType) {
    const likeBtn = commentEl.querySelector('.like-btn');
    const dislikeBtn = commentEl.querySelector('.dislike-btn');
    
    if (likeBtn) {
        likeBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> ${likes}`;
    }
    
    if (dislikeBtn) {
        dislikeBtn.innerHTML = `<i class="fas fa-thumbs-down"></i> ${dislikes}`;
    }
    
    // Update active states based on action
    if (action === 'added') {
        if (voteType === 'like') {
            likeBtn.classList.add('active');
            dislikeBtn.classList.remove('active');
        } else {
            dislikeBtn.classList.add('active');
            likeBtn.classList.remove('active');
        }
    } else if (action === 'removed') {
        likeBtn.classList.remove('active');
        dislikeBtn.classList.remove('active');
    } else if (action === 'changed') {
        if (voteType === 'like') {
            likeBtn.classList.add('active');
            dislikeBtn.classList.remove('active');
        } else {
            dislikeBtn.classList.add('active');
            likeBtn.classList.remove('active');
        }
    }
}

/**
 * Update comment count
 */
function updateCommentCount(count = null) {
    if (count === null) {
        count = document.querySelectorAll('.comment:not(.nested-comment)').length;
    }
    
    // Update header
    const headerEl = document.querySelector('.comments-section h3');
    if (headerEl) {
        headerEl.textContent = `Comments (${count})`;
    }
    
    // Update badge
    const badge = document.querySelector('.comments-count-badge');
    if (badge) {
        badge.innerHTML = `<i class="fas fa-comments"></i> ${count} Comments`;
    }
}

/**
 * Show message to user
 */
function showMessage(message, type = 'info') {
    const messageEl = document.createElement('div');
    messageEl.className = `comment-message comment-message-${type}`;
    messageEl.innerHTML = `
        <div class="message-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Style the message
    Object.assign(messageEl.style, {
        backgroundColor: type === 'success' ? 'rgba(0, 150, 0, 0.1)' : 
                         type === 'error' ? 'rgba(220, 53, 69, 0.1)' : 
                         'rgba(0, 123, 255, 0.1)',
        color: type === 'success' ? '#00c853' : 
               type === 'error' ? '#dc3545' : 
               '#007bff',
        padding: '10px 15px',
        borderRadius: '5px',
        marginBottom: '15px',
        display: 'flex',
        alignItems: 'center',
        border: `1px solid ${type === 'success' ? '#00c853' : 
                              type === 'error' ? '#dc3545' : 
                              '#007bff'}`,
        opacity: '0',
        transition: 'opacity 0.3s ease'
    });
    
    // Insert before form
    const commentForm = document.querySelector('.comment-form');
    if (commentForm) {
        commentForm.parentElement.insertBefore(messageEl, commentForm);
        
        // Fade in
        setTimeout(() => {
            messageEl.style.opacity = '1';
        }, 10);
        
        // Remove after a few seconds
        setTimeout(() => {
            messageEl.style.opacity = '0';
            setTimeout(() => {
                if (messageEl.parentElement) {
                    messageEl.parentElement.removeChild(messageEl);
                }
            }, 300);
        }, 4000);
    }
}

/**
 * Get post slug from URL
 */
function getPostSlug() {
    const path = window.location.pathname;
    const segments = path.split('/').filter(segment => segment);
    
    // Assuming URL structure: /blog/post/{slug}/
    if (segments.length >= 3 && segments[0] === 'blog' && segments[1] === 'post') {
        return segments[2];
    }
    
    return null;
}

/**
 * Create hidden input field
 */
function createHiddenInput(name) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    
    const form = document.getElementById('blogCommentForm');
    if (form) {
        form.appendChild(input);
    }
    
    return input;
}

/**
 * Initialize delete buttons
 */
function initDeleteButtons() {
    console.log('Initializing delete buttons');
    
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn') || e.target.closest('.delete-btn')) {
            e.preventDefault();
            
            const deleteBtn = e.target.classList.contains('delete-btn') ? e.target : e.target.closest('.delete-btn');
            const commentId = deleteBtn.dataset.commentId;
            const commentEl = deleteBtn.closest('.comment');
            
            console.log('Delete button clicked for comment:', commentId);
            
            // Show confirmation dialog
            if (confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
                deleteComment(commentId, commentEl);
            }
        }
    });
}

/**
 * Delete a comment
 */
async function deleteComment(commentId, commentEl) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    try {
        // Show loading state
        const deleteBtn = commentEl.querySelector('.delete-btn');
        const originalContent = deleteBtn.innerHTML;
        deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        deleteBtn.disabled = true;
        
        const response = await fetch(`/blog/comment/${commentId}/delete/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Remove comment from DOM with animation
            commentEl.style.transition = 'all 0.3s ease-out';
            commentEl.style.opacity = '0';
            commentEl.style.transform = 'translateY(-10px)';
            
            setTimeout(() => {
                commentEl.remove();
            }, 300);
            
            console.log('Comment deleted successfully');
        } else {
            alert('Error deleting comment: ' + result.message);
            // Restore button state
            deleteBtn.innerHTML = originalContent;
            deleteBtn.disabled = false;
        }
        
    } catch (error) {
        console.error('Delete error:', error);
        alert('Network error occurred while deleting comment.');
        
        // Restore button state
        const deleteBtn = commentEl.querySelector('.delete-btn');
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
        deleteBtn.disabled = false;
    }
}
