/**
 * Blog Comments System
 * Handles dynamic comment functionality with Django backend integration
 */

document.addEventListener('DOMContentLoaded', function() {
    initCommentSystem();
});

/**
 * Initialize the comment system
 */
function initCommentSystem() {
    initCommentForm();
    initReplyButtons();
    initCommentLikes();
    loadComments();
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
        if (e.target.classList.contains('reply-btn')) {
            e.preventDefault();
            
            // Check if user is authenticated (form exists)
            const commentForm = document.getElementById('blogCommentForm');
            if (!commentForm) {
                return; // Silently ignore if not authenticated
            }
            
            const commentEl = e.target.closest('.comment');
            const commentId = commentEl.dataset.commentId;
            const commenterName = commentEl.querySelector('.commenter-name').textContent;
            
            // Set parent ID for reply
            const parentInput = document.getElementById('parent_id') || createHiddenInput('parent_id');
            parentInput.value = commentId;
            
            // Focus on comment textarea and add @mention
            const commentTextarea = document.getElementById('commentContent');
            if (commentTextarea) {
                commentTextarea.focus();
                commentTextarea.value = `@${commenterName} `;
                
                // Scroll to form
                const commentFormDiv = document.querySelector('.comment-form');
                if (commentFormDiv) {
                    commentFormDiv.scrollIntoView({ behavior: 'smooth' });
                }
                
                // Show visual feedback in textarea placeholder
                commentTextarea.placeholder = `Replying to ${commenterName}... Clear to cancel reply.`;
            }
        }
    });
}

/**
 * Initialize comment like/dislike functionality
 */
function initCommentLikes() {
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('like-btn') || e.target.classList.contains('dislike-btn')) {
            e.preventDefault();
            
            const commentEl = e.target.closest('.comment');
            const commentId = commentEl.dataset.commentId;
            const isLike = e.target.classList.contains('like-btn');
            
            likeComment(commentId, isLike).then(response => {
                if (response.success) {
                    updateLikeButtons(commentEl, response.likes, response.dislikes);
                }
            }).catch(error => {
                console.error('Like error:', error);
            });
        }
    });
}

/**
 * Like or dislike a comment
 */
async function likeComment(commentId, isLike) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    const response = await fetch(`/blog/comment/like/${commentId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
        body: `is_like=${isLike}`
    });
    
    return await response.json();
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
function updateLikeButtons(commentEl, likes, dislikes) {
    const likeBtn = commentEl.querySelector('.like-btn');
    const dislikeBtn = commentEl.querySelector('.dislike-btn');
    
    if (likeBtn) {
        likeBtn.innerHTML = `<i class="fas fa-thumbs-up"></i> ${likes}`;
    }
    
    if (dislikeBtn) {
        dislikeBtn.innerHTML = `<i class="fas fa-thumbs-down"></i> ${dislikes}`;
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
