document.addEventListener('DOMContentLoaded', function() {
    console.log('Admin Message Center JavaScript loaded');
    
    // Timeline expand/collapse functionality
    const timelineHeaders = document.querySelectorAll('.timeline-header');
    timelineHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            // Ignore click if it's on action buttons (except expand)
            if (e.target.closest('.action-btn') && !e.target.closest('.action-btn.expand')) {
                return;
            }
            
            const itemId = this.getAttribute('data-id');
            toggleTimelineItem(itemId);
        });
    });

    function toggleTimelineItem(itemId) {
        const content = document.getElementById('content' + itemId);
        const expandBtn = document.querySelector(`[data-id="${itemId}"] .action-btn.expand`);
        
        if (content) {
            content.classList.toggle('active');
            if (expandBtn) {
                expandBtn.classList.toggle('active');
            }
        }
    }

    // Filter toggle functionality
    const filterToggle = document.getElementById('filterToggle');
    const filterOptions = document.getElementById('filterOptions');
    
    if (filterToggle && filterOptions) {
        filterToggle.addEventListener('click', function() {
            const isHidden = filterOptions.style.display === 'none';
            const toggleText = filterToggle.querySelector('span');
            const toggleIcon = filterToggle.querySelector('i');
            
            if (isHidden) {
                filterOptions.style.display = 'block';
                toggleText.textContent = 'Hide Filters';
                toggleIcon.className = 'fas fa-chevron-up';
            } else {
                filterOptions.style.display = 'none';
                toggleText.textContent = 'Show Filters';
                toggleIcon.className = 'fas fa-chevron-down';
            }
        });
    }

    // View toggle functionality
    const timelineViewBtn = document.getElementById('timelineViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const timelineView = document.getElementById('timelineView');
    const tableView = document.getElementById('tableView');

    if (timelineViewBtn && tableViewBtn) {
        timelineViewBtn.addEventListener('click', function() {
            timelineView.style.display = 'block';
            tableView.style.display = 'none';
            timelineViewBtn.classList.add('active');
            tableViewBtn.classList.remove('active');
        });

        tableViewBtn.addEventListener('click', function() {
            timelineView.style.display = 'none';
            tableView.style.display = 'block';
            tableViewBtn.classList.add('active');
            timelineViewBtn.classList.remove('active');
        });
    }

    // Search and filter functionality
    const searchInput = document.querySelector('.search-input');
    const filterName = document.getElementById('filter-name');
    const filterEmail = document.getElementById('filter-email');
    const filterPhone = document.getElementById('filter-phone');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const timelineItems = document.querySelectorAll('.timeline-item');

    function filterMessages() {
        const searchTerm = searchInput.value.toLowerCase();
        const nameFilter = filterName.value.toLowerCase();
        const emailFilter = filterEmail.value.toLowerCase();
        const phoneFilter = filterPhone.value.toLowerCase();

        timelineItems.forEach(item => {
            const name = item.querySelector('h3').textContent.toLowerCase();
            const infoItems = item.querySelectorAll('.info-value');
            const email = infoItems[1] ? infoItems[1].textContent.toLowerCase() : '';
            const phone = infoItems[2] ? infoItems[2].textContent.toLowerCase() : '';
            const message = item.querySelector('.timeline-description p').textContent.toLowerCase();

            const matchesSearch = !searchTerm || 
                name.includes(searchTerm) || 
                email.includes(searchTerm) || 
                phone.includes(searchTerm) || 
                message.includes(searchTerm);

            const matchesName = !nameFilter || name.includes(nameFilter);
            const matchesEmail = !emailFilter || email.includes(emailFilter);
            const matchesPhone = !phoneFilter || phone.includes(phoneFilter);

            if (matchesSearch && matchesName && matchesEmail && matchesPhone) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    if (searchInput) {
        searchInput.addEventListener('input', filterMessages);
    }

    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', filterMessages);
    }

    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            searchInput.value = '';
            filterName.value = '';
            filterEmail.value = '';
            filterPhone.value = '';
            timelineItems.forEach(item => {
                item.style.display = 'block';
            });
        });
    }

    // Get CSRF token
    function getCsrfToken() {
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            const cookieValue = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
            if (cookieValue) csrfToken = cookieValue.split('=')[1];
        }
        return csrfToken;
    }

    // Action buttons
    document.querySelectorAll('.action-btn.mark-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            updateMessageStatus(this.getAttribute('data-message-id'), 'read');
        });
    });

    document.querySelectorAll('.action-btn.mark-unread').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            updateMessageStatus(this.getAttribute('data-message-id'), 'new');
        });
    });

    document.querySelectorAll('.action-btn.mark-reviewed').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            updateMessageStatus(this.getAttribute('data-message-id'), 'reviewed');
        });
    });

    document.querySelectorAll('.action-btn.archive').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            updateMessageStatus(this.getAttribute('data-message-id'), 'archived');
        });
    });

    document.querySelectorAll('.action-btn.unarchive').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            updateMessageStatus(this.getAttribute('data-message-id'), 'read');
        });
    });

    document.querySelectorAll('.action-btn.delete').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            if (confirm('Delete this message?')) {
                deleteMessage(this.getAttribute('data-message-id'));
            }
        });
    });

    function updateMessageStatus(messageId, status) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) return alert('Please refresh the page.');

        fetch('/chat/api/admin/update-message-status/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message_id: messageId, status: status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(() => alert('Network error. Please try again.'));
    }

    function deleteMessage(messageId) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) return alert('Please refresh the page.');

        fetch('/chat/api/admin/delete-message/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message_id: messageId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(() => alert('Network error. Please try again.'));
    }
});