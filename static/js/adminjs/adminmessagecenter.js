document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    function getCsrfToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] ||
                         document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        return csrfToken;
    }

    // Toggle between timeline and table views
    const timelineViewBtn = document.getElementById('timelineViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const timelineView = document.getElementById('timelineView');
    const tableView = document.getElementById('tableView');
    
    if (timelineViewBtn && tableViewBtn && timelineView && tableView) {
        timelineViewBtn.addEventListener('click', function() {
            timelineViewBtn.classList.add('active');
            tableViewBtn.classList.remove('active');
            timelineView.style.display = 'block';
            tableView.style.display = 'none';
        });
        
        tableViewBtn.addEventListener('click', function() {
            tableViewBtn.classList.add('active');
            timelineViewBtn.classList.remove('active');
            tableView.style.display = 'block';
            timelineView.style.display = 'none';
        });
    }
    
    // Toggle timeline items to expand/collapse
    const timelineHeaders = document.querySelectorAll('.timeline-header');
    timelineHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            if (e.target.closest('.action-btn')) {
                return;
            }
            
            const content = this.nextElementSibling;
            const expandBtn = this.querySelector('.expand i');
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                if (expandBtn) expandBtn.classList.replace('fa-chevron-up', 'fa-chevron-down');
            } else {
                content.classList.add('active');
                if (expandBtn) expandBtn.classList.replace('fa-chevron-down', 'fa-chevron-up');
            }
        });
    });
    
    // Handle expand button clicks separately
    const expandButtons = document.querySelectorAll('.action-btn.expand');
    expandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const header = this.closest('.timeline-header');
            const content = header.nextElementSibling;
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                this.querySelector('i').classList.replace('fa-chevron-up', 'fa-chevron-down');
            } else {
                content.classList.add('active');
                this.querySelector('i').classList.replace('fa-chevron-down', 'fa-chevron-up');
            }
        });
    });
    
    // Handle filter toggle
    const filterToggle = document.querySelector('.filter-toggle');
    const filterOptions = document.querySelector('.filter-options');
    if (filterToggle && filterOptions) {
        filterToggle.addEventListener('click', function() {
            const isHidden = filterOptions.style.display === 'none';
            filterOptions.style.display = isHidden ? 'grid' : 'none';
            
            const toggleText = this.querySelector('span');
            toggleText.textContent = isHidden ? 'Hide Filters' : 'Show Filters';
            
            const toggleIcon = this.querySelector('i');
            toggleIcon.className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
        });
    }
    
    // Status update function
    function updateMessageStatus(messageId, status, button) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            console.error('CSRF token not found');
            alert('Security token not found. Please refresh the page.');
            return;
        }

        fetch('/chat/api/admin/update-message-status/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_id: messageId,
                status: status
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error updating status: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
            alert('Error updating status. Please try again.');
        });
    }
    
    // Delete message function
    function deleteMessage(messageId) {
        const csrfToken = getCsrfToken();
        if (!csrfToken) {
            console.error('CSRF token not found');
            alert('Security token not found. Please refresh the page.');
            return;
        }

        fetch('/chat/api/admin/delete-message/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message_id: messageId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error deleting message: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            console.error('Error deleting message:', error);
            alert('Error deleting message. Please try again.');
        });
    }
    
    // Mark as Read buttons
    document.querySelectorAll('.action-btn.mark-read').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            updateMessageStatus(messageId, 'read', this);
        });
    });
    
    // Mark as Unread buttons
    document.querySelectorAll('.action-btn.mark-unread').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            updateMessageStatus(messageId, 'new', this);
        });
    });
    
    // Mark as Reviewed buttons
    document.querySelectorAll('.action-btn.mark-reviewed').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            updateMessageStatus(messageId, 'reviewed', this);
        });
    });
    
    // Archive buttons
    document.querySelectorAll('.action-btn.archive').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            updateMessageStatus(messageId, 'archived', this);
        });
    });
    
    // Unarchive buttons
    document.querySelectorAll('.action-btn.unarchive').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            updateMessageStatus(messageId, 'read', this);
        });
    });
    
    // Delete buttons
    document.querySelectorAll('.action-btn.delete').forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            const messageId = this.getAttribute('data-message-id');
            if (confirm('Are you sure you want to delete this message? This action cannot be undone.')) {
                deleteMessage(messageId);
            }
        });
    });
    
    // Tab Navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const tabValue = this.getAttribute('data-tab');
            filterMessagesByStatus(tabValue);
        });
    });
    
    function filterMessagesByStatus(status) {
        const timelineItems = document.querySelectorAll('.timeline-item');
        const tableRows = document.querySelectorAll('tbody tr');
        
        timelineItems.forEach(item => {
            if (status === 'all' || item.getAttribute('data-status') === status) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        tableRows.forEach(row => {
            if (status === 'all' || row.getAttribute('data-status') === status) {
                row.style.display = 'table-row';
            } else {
                row.style.display = 'none';
            }
        });
    }
    
    // Search functionality
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            const searchText = this.value.toLowerCase();
            searchMessages(searchText);
        }, 300));
    }
    
    function searchMessages(searchText) {
        if (!searchText) {
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                filterMessagesByStatus(activeTab.getAttribute('data-tab'));
            }
            return;
        }
        
        const timelineItems = document.querySelectorAll('.timeline-item');
        const tableRows = document.querySelectorAll('tbody tr');
        
        timelineItems.forEach(item => {
            let shouldShow = false;
            
            // Check name
            const nameElement = item.querySelector('h3');
            if (nameElement && nameElement.textContent.toLowerCase().includes(searchText)) {
                shouldShow = true;
            }
            
            // Check email and phone in info values
            const infoValues = item.querySelectorAll('.info-value');
            infoValues.forEach(value => {
                if (value.textContent.toLowerCase().includes(searchText)) {
                    shouldShow = true;
                }
            });
            
            item.style.display = shouldShow ? 'block' : 'none';
        });
        
        tableRows.forEach(row => {
            let shouldShow = false;
            const cells = row.querySelectorAll('td');
            
            if (cells.length >= 3) {
                const clientCell = cells[1];
                const phoneCell = cells[2];
                
                // Check name
                const nameElement = clientCell.querySelector('.client-name');
                if (nameElement && nameElement.textContent.toLowerCase().includes(searchText)) {
                    shouldShow = true;
                }
                
                // Check email
                const emailElement = clientCell.querySelector('.client-email');
                if (emailElement && emailElement.textContent.toLowerCase().includes(searchText)) {
                    shouldShow = true;
                }
                
                // Check phone
                if (phoneCell && phoneCell.textContent.toLowerCase().includes(searchText)) {
                    shouldShow = true;
                }
            }
            
            row.style.display = shouldShow ? 'table-row' : 'none';
        });
    }
    
    // Apply filters
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            applyAdvancedFilters();
        });
    }
    
    // Reset filters
    const resetFiltersBtn = document.getElementById('resetFilters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            document.querySelectorAll('.filter-group input').forEach(input => {
                input.value = '';
            });
            
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                filterMessagesByStatus(activeTab.getAttribute('data-tab'));
            }
            
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.value = '';
            }
        });
    }
    
    function applyAdvancedFilters() {
        const nameFilter = document.getElementById('filter-name').value.toLowerCase();
        const emailFilter = document.getElementById('filter-email').value.toLowerCase();
        const phoneFilter = document.getElementById('filter-phone').value.toLowerCase();
        
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach(item => {
            let shouldShow = true;
            
            // Check name filter
            if (nameFilter) {
                const nameElement = item.querySelector('h3');
                if (!nameElement || !nameElement.textContent.toLowerCase().includes(nameFilter)) {
                    shouldShow = false;
                }
            }
            
            // Check email filter
            if (shouldShow && emailFilter) {
                const emailElements = item.querySelectorAll('.info-value');
                let emailFound = false;
                emailElements.forEach(element => {
                    if (element.textContent.toLowerCase().includes('@') && 
                        element.textContent.toLowerCase().includes(emailFilter)) {
                        emailFound = true;
                    }
                });
                if (!emailFound) shouldShow = false;
            }
            
            // Check phone filter
            if (shouldShow && phoneFilter) {
                const phoneElements = item.querySelectorAll('.info-value');
                let phoneFound = false;
                phoneElements.forEach(element => {
                    if (!element.textContent.toLowerCase().includes('@') && 
                        element.textContent.toLowerCase().includes(phoneFilter)) {
                        phoneFound = true;
                    }
                });
                if (!phoneFound) shouldShow = false;
            }
            
            item.style.display = shouldShow ? 'block' : 'none';
        });
        
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            let shouldShow = true;
            const cells = row.querySelectorAll('td');
            
            if (cells.length >= 3) {
                const clientCell = cells[1];
                const phoneCell = cells[2];
                
                // Check filters
                if (nameFilter) {
                    const nameElement = clientCell.querySelector('.client-name');
                    if (!nameElement || !nameElement.textContent.toLowerCase().includes(nameFilter)) {
                        shouldShow = false;
                    }
                }
                
                if (shouldShow && emailFilter) {
                    const emailElement = clientCell.querySelector('.client-email');
                    if (!emailElement || !emailElement.textContent.toLowerCase().includes(emailFilter)) {
                        shouldShow = false;
                    }
                }
                
                if (shouldShow && phoneFilter && !phoneCell.textContent.toLowerCase().includes(phoneFilter)) {
                    shouldShow = false;
                }
            }
            
            row.style.display = shouldShow ? 'table-row' : 'none';
        });
    }
    
    function debounce(func, delay) {
        let timeoutId;
        return function() {
            const context = this;
            const args = arguments;
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => {
                func.apply(context, args);
            }, delay);
        };
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            location.reload();
        });
    }
    
    // Auto-refresh admin page every 30 seconds to show new messages
    if (window.location.pathname.includes('/adminmessagecenter')) {
        setInterval(() => {
            const currentTab = document.querySelector('.tab-btn.active')?.getAttribute('data-tab') || 'all';
            const currentSearch = document.querySelector('.search-input')?.value || '';
            
            // Only refresh if no search is active and on 'all' or 'new' tab
            if (!currentSearch && (currentTab === 'all' || currentTab === 'new')) {
                location.reload();
            }
        }, 30000); // 30 seconds
    }
});