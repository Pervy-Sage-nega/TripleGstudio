// Global functions that need to be available immediately
window.testModal = function() {
    console.log('Testing modal...');
    const modal = document.getElementById('blogPreviewModal');
    if (modal) {
        modal.style.display = 'flex';
        console.log('Modal should be visible now');
    } else {
        console.error('Modal not found!');
    }
};

window.viewBlog = function(blogId) {
    console.log('viewBlog called with ID:', blogId);
    
    const blogPreviewModal = document.getElementById('blogPreviewModal');
    const blogPreviewActions = document.getElementById('blogPreviewActions');
    
    if (!blogPreviewModal) {
        console.error('Blog preview modal not found');
        return;
    }
    
    if (!blogPreviewActions) {
        console.error('Blog preview actions not found');
        return;
    }
    
    // Get the blog content
    const selectedBlog = document.getElementById(`blogPreview${blogId}`);
    if (!selectedBlog) {
        console.error('Blog preview content not found for ID:', blogId);
        return;
    }
    
    // Copy blog content to modal
    const blogPreviewContent = document.getElementById('blogPreviewContent');
    if (!blogPreviewContent) {
        console.error('Blog preview content container not found');
        return;
    }
    
    blogPreviewContent.innerHTML = selectedBlog.innerHTML;
    
    // Get current blog status
    let status = 'draft';
    const blogRow = document.querySelector(`tr .status-select[data-id="${blogId}"]`) || 
                   document.querySelector(`.blog-card .status-select[data-id="${blogId}"]`);
    if (blogRow) {
        status = blogRow.value;
    }
    
    // Clear previous action buttons
    blogPreviewActions.innerHTML = '';
    
    // Add action buttons based on status
    if (status === 'draft') {
        const approveButton = document.createElement('button');
        approveButton.className = 'btn btn-success';
        approveButton.innerHTML = '<i class="fas fa-check"></i> Approve & Publish';
        approveButton.addEventListener('click', () => {
            approveBlog(blogId);
            closeBlogPreview();
        });
        
        const rejectButton = document.createElement('button');
        rejectButton.className = 'btn btn-warning';
        rejectButton.innerHTML = '<i class="fas fa-times"></i> Reject with Comment';
        rejectButton.addEventListener('click', () => {
            showRejectionModal(blogId);
        });
        
        blogPreviewActions.appendChild(approveButton);
        blogPreviewActions.appendChild(rejectButton);
    }
    
    // Add close button
 
    
    // Show the modal
    console.log('Showing modal...');
    blogPreviewModal.style.display = 'flex';
};

window.deleteBlog = function(blogId) {
    if (!confirm('Are you sure you want to delete this blog post? This action cannot be undone.')) {
        return;
    }
    
    const csrftoken = getCookie('csrftoken');
    
    fetch(`/blog/delete/${blogId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Blog post deleted successfully');
            window.location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while deleting the blog post.');
    });
};

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const tableViewBtn = document.getElementById('tableViewBtn');
    const gridViewBtn = document.getElementById('gridViewBtn');
    const tableView = document.getElementById('tableView');
    const gridView = document.getElementById('gridView');
    const expandAllBtn = document.getElementById('expandAllBtn');
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    const filterToggle = document.getElementById('filterToggle');
    const filterOptions = document.getElementById('filterOptions');
    const searchInput = document.querySelector('.search-input');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.getElementById('navLinks');
    
    // Modal Elements
    const blogPreviewModal = document.getElementById('blogPreviewModal');
    const closeBlogPreviewModal = document.getElementById('closeBlogPreviewModal');
    const blogPreviewActions = document.getElementById('blogPreviewActions');
    const rejectionModal = document.getElementById('rejectionModal');
    const closeRejectionModal = document.getElementById('closeRejectionModal');
    const cancelRejection = document.getElementById('cancelRejection');
    const confirmRejection = document.getElementById('confirmRejection');
    const rejectionReason = document.getElementById('rejectionReason');
    const rejectBlogId = document.getElementById('rejectBlogId');
    const notificationModal = document.getElementById('notificationModal');
    const notificationTitle = document.getElementById('notificationTitle');
    const notificationMessage = document.getElementById('notificationMessage');
    const closeNotificationModal = document.getElementById('closeNotificationModal');
    const confirmNotification = document.getElementById('confirmNotification');

    // Initialize view
    let currentView = 'table'; // Default view
    
    // Initialize the page
    init();

    function init() {
        // Set up event listeners
        setupEventListeners();
        
        // Initialize view toggle
        toggleView(currentView);
        
        // Initialize filter toggle
        if (filterOptions) {
            filterOptions.style.display = 'none';
        }
        
        // Update summary counts
        updateSummaryCounts();
        
        // Debug: Check if modal elements exist
        console.log('Modal elements check:');
        console.log('blogPreviewModal:', blogPreviewModal);
        console.log('blogPreviewActions:', blogPreviewActions);
    }

    function setupEventListeners() {
        // View toggle buttons
        if (tableViewBtn && gridViewBtn) {
            tableViewBtn.addEventListener('click', () => toggleView('table'));
            gridViewBtn.addEventListener('click', () => toggleView('grid'));
        }

        // Expand/Collapse buttons
        if (expandAllBtn && collapseAllBtn) {
            expandAllBtn.addEventListener('click', expandAll);
            collapseAllBtn.addEventListener('click', collapseAll);
        }

        // Filter toggle
        if (filterToggle) {
            filterToggle.addEventListener('click', toggleFilters);
        }

        // Mobile menu
        if (mobileMenuBtn && navLinks) {
            mobileMenuBtn.addEventListener('click', toggleMobileMenu);
        }

        // Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', handleSearch);
        }

        // Filter buttons
        if (resetFiltersBtn && applyFiltersBtn) {
            resetFiltersBtn.addEventListener('click', resetFilters);
            applyFiltersBtn.addEventListener('click', applyFilters);
        }

        // Status change dropdowns
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', handleStatusChange);
        });

        // Status filter dropdown
        const statusFilter = document.getElementById('filter-status');
        if (statusFilter) {
            statusFilter.addEventListener('change', applyFilters);
        }
        
        // Modal close buttons
        if (closeBlogPreviewModal) {
            closeBlogPreviewModal.addEventListener('click', closeBlogPreview);
        }
        
        if (closeRejectionModal) {
            closeRejectionModal.addEventListener('click', () => rejectionModal.style.display = 'none');
        }
        
        if (cancelRejection) {
            cancelRejection.addEventListener('click', () => rejectionModal.style.display = 'none');
        }
        
        if (confirmRejection) {
            confirmRejection.addEventListener('click', handleRejection);
        }
        
        if (closeNotificationModal) {
            closeNotificationModal.addEventListener('click', () => notificationModal.style.display = 'none');
        }
        
        if (confirmNotification) {
            confirmNotification.addEventListener('click', () => notificationModal.style.display = 'none');
        }
    }

    function toggleView(view) {
        currentView = view;
        
        if (view === 'table') {
            tableView.style.display = 'block';
            gridView.style.display = 'none';
            tableViewBtn.classList.add('active');
            gridViewBtn.classList.remove('active');
        } else {
            tableView.style.display = 'none';
            gridView.style.display = 'grid';
            gridViewBtn.classList.add('active');
            tableViewBtn.classList.remove('active');
        }
    }

    function toggleFilters() {
        const isVisible = filterOptions.style.display === 'block';
        filterOptions.style.display = isVisible ? 'none' : 'block';
        
        const icon = filterToggle.querySelector('i');
        const text = filterToggle.querySelector('span');
        
        if (isVisible) {
            icon.classList.remove('fa-chevron-up');
            icon.classList.add('fa-chevron-down');
            text.textContent = 'Show Filters';
        } else {
            icon.classList.remove('fa-chevron-down');
            icon.classList.add('fa-chevron-up');
            text.textContent = 'Hide Filters';
        }
    }

    function toggleMobileMenu() {
        navLinks.classList.toggle('active');
        const icon = mobileMenuBtn.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    }

    function expandAll() {
        // For future implementation if needed
        console.log('Expand all functionality');
    }

    function collapseAll() {
        // For future implementation if needed
        console.log('Collapse all functionality');
    }

    function handleSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        
        // Search in table view
        document.querySelectorAll('tbody tr').forEach(row => {
            const blogTitle = row.querySelector('.blog-title').textContent.toLowerCase();
            const category = row.cells[2].textContent.toLowerCase();
            const author = row.cells[3].textContent.toLowerCase();
            const tags = Array.from(row.querySelectorAll('.blog-tag'))
                .map(tag => tag.textContent.toLowerCase())
                .join(' ');
                
            const text = `${blogTitle} ${category} ${author} ${tags}`;
            row.style.display = text.includes(searchTerm) ? '' : 'none';
        });
        
        // Search in grid view
        document.querySelectorAll('.blog-card').forEach(card => {
            const blogTitle = card.querySelector('.blog-card-title').textContent.toLowerCase();
            const category = card.querySelector('.blog-card-info span:nth-child(1)').textContent.toLowerCase();
            const author = card.querySelector('.blog-card-info span:nth-child(2)').textContent.toLowerCase();
            const tags = Array.from(card.querySelectorAll('.blog-tag'))
                .map(tag => tag.textContent.toLowerCase())
                .join(' ');
                
            const text = `${blogTitle} ${category} ${author} ${tags}`;
            card.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    function resetFilters() {
        // Reset all filter inputs
        document.querySelectorAll('#filterOptions select, #filterOptions input').forEach(el => {
            el.value = '';
        });
        
        // Reset search
        if (searchInput) searchInput.value = '';
        
        // Show all blogs
        document.querySelectorAll('tbody tr').forEach(row => {
            row.style.display = '';
        });
        
        document.querySelectorAll('.blog-card').forEach(card => {
            card.style.display = '';
        });
    }

    function applyFilters() {
        const statusFilter = document.getElementById('filter-status')?.value.toLowerCase() || '';
        const categoryFilter = document.getElementById('filter-category')?.value.toLowerCase() || '';
        const authorFilter = document.getElementById('filter-author')?.value.toLowerCase() || '';
        const dateFrom = document.getElementById('filter-date-from')?.value || '';
        const dateTo = document.getElementById('filter-date-to')?.value || '';
        
        // Filter table rows
        document.querySelectorAll('tbody tr').forEach(row => {
            if (row.querySelector('.no-results')) return; // Skip "no results" row
            
            const statusBadge = row.querySelector('.status-badge');
            const status = statusBadge ? statusBadge.textContent.toLowerCase() : '';
            const category = row.cells[2]?.textContent.toLowerCase() || '';
            const author = row.cells[3]?.textContent.toLowerCase() || '';
            const date = row.cells[4]?.textContent || '';
            
            let show = true;
            
            if (statusFilter && !status.includes(statusFilter)) show = false;
            if (categoryFilter && !category.includes(categoryFilter)) show = false;
            if (authorFilter && !author.includes(authorFilter)) show = false;
            
            // Simple date range filtering
            if (dateFrom && date < dateFrom) show = false;
            if (dateTo && date > dateTo) show = false;
            
            row.style.display = show ? '' : 'none';
        });
        
        // Filter grid cards
        document.querySelectorAll('.blog-card').forEach(card => {
            const statusElement = card.querySelector('.blog-card-status');
            const status = statusElement ? statusElement.textContent.toLowerCase() : '';
            const categoryElement = card.querySelector('.blog-card-info span:nth-child(1)');
            const category = categoryElement ? categoryElement.textContent.toLowerCase() : '';
            const authorElement = card.querySelector('.blog-card-info span:nth-child(2)');
            const author = authorElement ? authorElement.textContent.toLowerCase() : '';
            const dateElement = card.querySelector('.blog-card-info span:nth-child(3)');
            const date = dateElement ? dateElement.textContent.replace('Date: ', '') : '';
            
            let show = true;
            
            if (statusFilter && !status.includes(statusFilter)) show = false;
            if (categoryFilter && !category.includes(categoryFilter)) show = false;
            if (authorFilter && !author.includes(authorFilter)) show = false;
            
            // Simple date range filtering
            if (dateFrom && date < dateFrom) show = false;
            if (dateTo && date > dateTo) show = false;
            
            card.style.display = show ? '' : 'none';
        });
    }

    // Handle status change from dropdown
    function handleStatusChange(event) {
        const select = event.target;
        const postId = select.dataset.id;
        const newStatus = select.value;
        const originalStatus = select.querySelector('option[selected]')?.value || 'draft';
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Make AJAX request to change status
        fetch(`/blog/admin/change-status/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI
                const row = select.closest('tr') || select.closest('.blog-card');
                const statusBadge = row.querySelector('.status-badge');
                if (statusBadge) {
                    statusBadge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    statusBadge.className = `status-badge status-${newStatus}`;
                }
                
                // Show notification
                showNotification('Status Updated', `Blog post status changed to ${newStatus}`);
                
                // Update summary counts
                updateSummaryCounts();
            } else {
                alert('Failed to change status: ' + (data.message || 'Unknown error'));
                select.value = originalStatus; // Revert selection
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
            select.value = originalStatus; // Revert selection
        });
    }
    
    // Helper functions for modal actions
    window.approveBlog = function(blogId) {
        if (!confirm('Are you sure you want to approve and publish this blog post?')) {
            return;
        }
        changeStatusTo(blogId, 'published');
    };

    window.showRejectionModal = function(blogId) {
        const rejectionModal = document.getElementById('rejectionModal');
        const rejectBlogId = document.getElementById('rejectBlogId');
        const rejectionReason = document.getElementById('rejectionReason');
        
        if (rejectionModal && rejectBlogId && rejectionReason) {
            rejectBlogId.value = blogId;
            rejectionReason.value = '';
            rejectionModal.style.display = 'flex';
        }
    };

    // Change status helper function
    function changeStatusTo(blogId, newStatus) {
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/blog/admin/change-status/${blogId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert(`Blog post status changed to ${newStatus}`);
                
                // Update UI elements
                const statusSelect = document.querySelector(`[data-id="${blogId}"].status-select`);
                if (statusSelect) {
                    statusSelect.value = newStatus;
                }
                
                const statusBadges = document.querySelectorAll(`tr[data-id="${blogId}"] .status-badge, .blog-card[data-id="${blogId}"] .status-badge`);
                statusBadges.forEach(badge => {
                    badge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    badge.className = `status-badge status-${newStatus}`;
                });
                
                updateSummaryCounts();
            } else {
                alert('Failed to change status: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
    
    function closeBlogPreview() {
        blogPreviewModal.style.display = 'none';
    }

    // Show rejection modal
    function showRejectionModal(blogId) {
        rejectBlogId.value = blogId;
        rejectionReason.value = '';
        rejectionModal.style.display = 'flex';
        closeBlogPreview(); // Close the preview modal
    }

    // Change status helper function
    function changeStatusTo(blogId, newStatus) {
        const csrftoken = getCookie('csrftoken');
        
        fetch(`/blog/admin/change-status/${blogId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Status Updated', `Blog post status changed to ${newStatus}`);
                
                // Update UI elements
                const statusSelect = document.querySelector(`[data-id="${blogId}"].status-select`);
                if (statusSelect) {
                    statusSelect.value = newStatus;
                }
                
                const statusBadges = document.querySelectorAll(`tr[data-id="${blogId}"] .status-badge, .blog-card[data-id="${blogId}"] .status-badge`);
                statusBadges.forEach(badge => {
                    badge.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
                    badge.className = `status-badge status-${newStatus}`;
                });
                
                updateSummaryCounts();
            } else {
                alert('Failed to change status: ' + (data.message || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    }
    
    // Approve blog functionality
    window.approveBlog = function(blogId) {
        if (!confirm('Are you sure you want to approve and publish this blog post?')) {
            return;
        }
        
        changeStatusTo(blogId, 'published');
    };
    
    // Reject blog functionality
    window.rejectBlog = function(blogId) {
        if (!confirm('Are you sure you want to reject this blog post and send it back to draft?')) {
            return;
        }
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Make AJAX request to reject
        fetch(`/blog/admin/reject/${blogId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success notification
                showNotification('Blog Rejected', data.message);
                
                // Reload page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while rejecting the blog post.');
        });
    };
    
    function handleRejection() {
        const blogId = rejectBlogId.value;
        const reason = rejectionReason.value.trim();
        
        if (!reason) {
            alert('Please provide a reason for rejection.');
            return;
        }
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Make AJAX request to reject with comment
        fetch(`/blog/admin/reject/${blogId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: `reason=${encodeURIComponent(reason)}`
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response URL:', response.url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Hide rejection modal
                rejectionModal.style.display = 'none';
                
                // Show success notification
                showNotification('Blog Rejected', 'Blog post has been rejected and sent back to draft with your comments.');
                
                // Update status to draft
                changeStatusTo(blogId, 'draft');
            } else {
                alert('Error: ' + (data.message || 'Failed to reject blog post'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while rejecting the blog post.');
        });
    }
    
    // Delete blog functionality
    window.deleteBlog = function(blogId) {
        if (!confirm('Are you sure you want to delete this blog post? This action cannot be undone.')) {
            return;
        }
        
        // Get CSRF token
        const csrftoken = getCookie('csrftoken');
        
        // Make AJAX request to delete
        fetch(`/blog/delete/${blogId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Show success notification
                showNotification('Blog Deleted', data.message);
                
                // Reload page to reflect changes
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the blog post.');
        });
    };
    
    // Show notification
    function showNotification(title, message) {
        notificationTitle.textContent = title;
        notificationMessage.textContent = message;
        notificationModal.style.display = 'flex';
    }
    
    // Update summary counts
    function updateSummaryCounts() {
        const totalBlogsEl = document.getElementById('totalBlogs');
        const draftBlogsEl = document.getElementById('draftBlogs');
        const publishedBlogsEl = document.getElementById('publishedBlogs');
        const archivedBlogsEl = document.getElementById('archivedBlogs');
        
        // Count blogs by status
        const totalBlogs = document.querySelectorAll('.blog-item').length;
        const draftBlogs = document.querySelectorAll('.status-badge.status-draft').length;
        const publishedBlogs = document.querySelectorAll('.status-badge.status-published').length;
        const archivedBlogs = document.querySelectorAll('.status-badge.status-archived').length;
        
        // Update the display
        if (totalBlogsEl) totalBlogsEl.textContent = totalBlogs;
        if (draftBlogsEl) draftBlogsEl.textContent = draftBlogs;
        if (publishedBlogsEl) publishedBlogsEl.textContent = publishedBlogs;
        if (archivedBlogsEl) archivedBlogsEl.textContent = archivedBlogs;
    }
    
    // Helper function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
