// Admin Message Center JavaScript

document.addEventListener('DOMContentLoaded', function() {
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
            // Don't toggle if clicking on an action button
            if (e.target.closest('.action-btn')) {
                return;
            }
            
            const content = this.nextElementSibling;
            
            // Toggle the content
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                this.querySelector('.expand i').classList.replace('fa-chevron-up', 'fa-chevron-down');
            } else {
                content.classList.add('active');
                this.querySelector('.expand i').classList.replace('fa-chevron-down', 'fa-chevron-up');
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
            
            // Toggle the content
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
    
    // Analytics section toggle
    const analyticsToggle = document.getElementById('analyticsToggle');
    const analyticsContent = document.getElementById('analyticsContent');
    if (analyticsToggle && analyticsContent) {
        analyticsToggle.addEventListener('click', function() {
            const isHidden = analyticsContent.style.display === 'none';
            analyticsContent.style.display = isHidden ? 'block' : 'none';
            this.querySelector('i').className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
            
            // Initialize charts when analytics section is opened
            if (isHidden) {
                initCharts();
            }
        });
    }
    
    // Initialize charts when page loads
    function initCharts() {
        // Only initialize if charts don't already exist
        if (window.inquiryTypeChart || window.projectChart || window.dailyVolumeChart) {
            return;
        }
        
        // Inquiry Type Distribution Chart
        const inquiryTypeCtx = document.getElementById('inquiryTypeChart');
        if (inquiryTypeCtx) {
            window.inquiryTypeChart = new Chart(inquiryTypeCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Appointment', 'Milestone', 'General', 'Complaint'],
                    datasets: [{
                        data: [12, 8, 15, 5],
                        backgroundColor: [
                            '#ff9800',
                            '#2196f3',
                            '#4caf50',
                            '#f44336'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        }
        
        // Project Distribution Chart
        const projectCtx = document.getElementById('projectChart');
        if (projectCtx) {
            window.projectChart = new Chart(projectCtx, {
                type: 'bar',
                data: {
                    labels: ['CBD Tower', 'Highway Bridge', 'Residential', 'Waterfront', 'Tech Hub'],
                    datasets: [{
                        label: 'Message Count',
                        data: [15, 8, 12, 6, 4],
                        backgroundColor: '#00273C',
                        borderColor: '#00273C',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
        
        // Daily Volume Chart
        const dailyVolumeCtx = document.getElementById('dailyVolumeChart');
        if (dailyVolumeCtx) {
            window.dailyVolumeChart = new Chart(dailyVolumeCtx, {
                type: 'line',
                data: {
                    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                    datasets: [{
                        label: 'Messages',
                        data: [8, 12, 5, 9, 14, 3, 2],
                        fill: false,
                        borderColor: '#00273C',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            });
        }
    }
    
    // Message Status Management Functions
    
    // Mark as Read
    const markReadButtons = document.querySelectorAll('.action-btn.mark-read');
    markReadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Get the timeline item or table row
            const timelineItem = this.closest('.timeline-item') || this.closest('tr');
            if (!timelineItem) return;
            
            // Update status text
            const statusElement = timelineItem.querySelector('.log-status');
            if (statusElement) {
                statusElement.textContent = 'Read';
                statusElement.className = 'log-status status-read';
            }
            
            // Update data attribute
            timelineItem.setAttribute('data-status', 'read');
            
            // Update counter in status tracker
            updateStatusCounter('new', -1);
            updateStatusCounter('read', 1);
            
            // Replace this button with mark-reviewed button if not already present
            const actionsContainer = this.closest('.timeline-actions') || this.closest('.table-actions');
            if (actionsContainer && !actionsContainer.querySelector('.mark-reviewed')) {
                const markReviewedBtn = document.createElement('button');
                markReviewedBtn.className = 'action-btn mark-reviewed';
                markReviewedBtn.title = 'Mark as Reviewed';
                markReviewedBtn.innerHTML = '<i class="fas fa-clipboard-check"></i>';
                
                // Add event listener to the new button
                markReviewedBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    markAsReviewed(this);
                });
                
                const markUnreadBtn = document.createElement('button');
                markUnreadBtn.className = 'action-btn mark-unread';
                markUnreadBtn.title = 'Mark as Unread';
                markUnreadBtn.innerHTML = '<i class="fas fa-undo"></i>';
                
                // Add event listener to the new button
                markUnreadBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    markAsUnread(this);
                });
                
                // Replace read button with reviewed and unread buttons
                actionsContainer.replaceChild(markReviewedBtn, this);
                actionsContainer.insertBefore(markUnreadBtn, markReviewedBtn);
            }
        });
    });
    
    // Mark as Reviewed
    const markReviewedButtons = document.querySelectorAll('.action-btn.mark-reviewed');
    markReviewedButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            markAsReviewed(this);
        });
    });
    
    function markAsReviewed(button) {
        // Get the timeline item or table row
        const timelineItem = button.closest('.timeline-item') || button.closest('tr');
        if (!timelineItem) return;
        
        // Get current status
        const statusElement = timelineItem.querySelector('.log-status');
        const currentStatus = statusElement ? statusElement.textContent.toLowerCase().trim() : '';
        
        // Update status text
        if (statusElement) {
            statusElement.textContent = 'Reviewed';
            statusElement.className = 'log-status status-reviewed';
        }
        
        // Update data attribute
        timelineItem.setAttribute('data-status', 'reviewed');
        
        // Update counter in status tracker
        if (currentStatus) {
            updateStatusCounter(currentStatus, -1);
        }
        updateStatusCounter('reviewed', 1);
    }
    
    // Mark as Unread
    const markUnreadButtons = document.querySelectorAll('.action-btn.mark-unread');
    markUnreadButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            markAsUnread(this);
        });
    });
    
    function markAsUnread(button) {
        // Get the timeline item or table row
        const timelineItem = button.closest('.timeline-item') || button.closest('tr');
        if (!timelineItem) return;
        
        // Get current status
        const statusElement = timelineItem.querySelector('.log-status');
        const currentStatus = statusElement ? statusElement.textContent.toLowerCase().trim() : '';
        
        // Update status text
        if (statusElement) {
            statusElement.textContent = 'New';
            statusElement.className = 'log-status status-new';
        }
        
        // Update data attribute
        timelineItem.setAttribute('data-status', 'new');
        
        // Update counter in status tracker
        if (currentStatus) {
            updateStatusCounter(currentStatus, -1);
        }
        updateStatusCounter('new', 1);
    }
    
    // Archive message
    const archiveButtons = document.querySelectorAll('.action-btn.archive');
    archiveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Show confirmation modal
            showConfirmationModal(
                'Archive Message',
                'Are you sure you want to archive this message?',
                () => {
                    archiveMessage(this);
                }
            );
        });
    });
    
    function archiveMessage(button) {
        // Get the timeline item or table row
        const timelineItem = button.closest('.timeline-item') || button.closest('tr');
        if (!timelineItem) return;
        
        // Get current status
        const statusElement = timelineItem.querySelector('.log-status');
        const currentStatus = statusElement ? statusElement.textContent.toLowerCase().trim() : '';
        
        // Update status text
        if (statusElement) {
            statusElement.textContent = 'Archived';
            statusElement.className = 'log-status status-archived';
        }
        
        // Update data attribute
        timelineItem.setAttribute('data-status', 'archived');
        
        // Update counter in status tracker
        if (currentStatus) {
            updateStatusCounter(currentStatus, -1);
        }
        updateStatusCounter('archived', 1);
        
        // Update actions (replace with unarchive button)
        const actionsContainer = button.closest('.timeline-actions') || button.closest('.table-actions');
        if (actionsContainer) {
            // Create unarchive button
            const unarchiveBtn = document.createElement('button');
            unarchiveBtn.className = 'action-btn unarchive';
            unarchiveBtn.title = 'Unarchive Message';
            unarchiveBtn.innerHTML = '<i class="fas fa-box-open"></i>';
            
            // Add event listener to the new button
            unarchiveBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                unarchiveMessage(this);
            });
            
            // Remove existing status buttons
            const statusButtons = actionsContainer.querySelectorAll('.mark-read, .mark-unread, .mark-reviewed, .archive');
            statusButtons.forEach(btn => btn.remove());
            
            // Add unarchive button
            actionsContainer.insertBefore(unarchiveBtn, actionsContainer.firstChild);
        }
    }
    
    // Unarchive message
    const unarchiveButtons = document.querySelectorAll('.action-btn.unarchive');
    unarchiveButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            unarchiveMessage(this);
        });
    });
    
    function unarchiveMessage(button) {
        // Get the timeline item or table row
        const timelineItem = button.closest('.timeline-item') || button.closest('tr');
        if (!timelineItem) return;
        
        // Update status to "Read"
        const statusElement = timelineItem.querySelector('.log-status');
        if (statusElement) {
            statusElement.textContent = 'Read';
            statusElement.className = 'log-status status-read';
        }
        
        // Update data attribute
        timelineItem.setAttribute('data-status', 'read');
        
        // Update counter in status tracker
        updateStatusCounter('archived', -1);
        updateStatusCounter('read', 1);
        
        // Update actions
        const actionsContainer = button.closest('.timeline-actions') || button.closest('.table-actions');
        if (actionsContainer) {
            // Create mark buttons
            const markReviewedBtn = document.createElement('button');
            markReviewedBtn.className = 'action-btn mark-reviewed';
            markReviewedBtn.title = 'Mark as Reviewed';
            markReviewedBtn.innerHTML = '<i class="fas fa-clipboard-check"></i>';
            
            const markUnreadBtn = document.createElement('button');
            markUnreadBtn.className = 'action-btn mark-unread';
            markUnreadBtn.title = 'Mark as Unread';
            markUnreadBtn.innerHTML = '<i class="fas fa-undo"></i>';
            
            const archiveBtn = document.createElement('button');
            archiveBtn.className = 'action-btn archive';
            archiveBtn.title = 'Archive Message';
            archiveBtn.innerHTML = '<i class="fas fa-archive"></i>';
            
            // Add event listeners to the new buttons
            markReviewedBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                markAsReviewed(this);
            });
            
            markUnreadBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                markAsUnread(this);
            });
            
            archiveBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                showConfirmationModal(
                    'Archive Message',
                    'Are you sure you want to archive this message?',
                    () => {
                        archiveMessage(this);
                    }
                );
            });
            
            // Replace unarchive button with mark and archive buttons
            button.remove();
            actionsContainer.insertBefore(markReviewedBtn, actionsContainer.firstChild);
            actionsContainer.insertBefore(markUnreadBtn, actionsContainer.firstChild);
            actionsContainer.insertBefore(archiveBtn, actionsContainer.firstChild);
        }
    }
    
    // Delete message
    const deleteButtons = document.querySelectorAll('.action-btn.delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            // Show confirmation modal
            showConfirmationModal(
                'Delete Message',
                'Are you sure you want to delete this message? This action cannot be undone.',
                () => {
                    deleteMessage(this);
                }
            );
        });
    });
    
    function deleteMessage(button) {
        // Get the timeline item or table row
        const timelineItem = button.closest('.timeline-item') || button.closest('tr');
        if (!timelineItem) return;
        
        // Get current status for counter update
        const statusElement = timelineItem.querySelector('.log-status');
        const currentStatus = statusElement ? statusElement.textContent.toLowerCase().trim() : '';
        
        // Update counter in status tracker before removing
        if (currentStatus) {
            updateStatusCounter(currentStatus, -1);
        }
        
        // Remove the item from DOM with animation
        timelineItem.style.opacity = '0';
        timelineItem.style.height = timelineItem.offsetHeight + 'px';
        
        setTimeout(() => {
            timelineItem.style.height = '0';
            timelineItem.style.margin = '0';
            timelineItem.style.padding = '0';
            timelineItem.style.overflow = 'hidden';
            
            setTimeout(() => {
                timelineItem.remove();
            }, 300);
        }, 300);
    }
    
    // View Details (in table view)
    const viewButtons = document.querySelectorAll('.action-btn.view');
    viewButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation();
            
            const messageId = this.getAttribute('data-id');
            if (messageId) {
                // Find the corresponding timeline content
                const timelineContent = document.getElementById('content' + messageId);
                if (timelineContent) {
                    // Clone the content for the modal
                    const modalContent = timelineContent.cloneNode(true);
                    
                    // Show modal with the content
                    const messageModal = document.getElementById('messageModal');
                    const messageModalContent = document.getElementById('messageModalContent');
                    
                    if (messageModal && messageModalContent) {
                        messageModalContent.innerHTML = '';
                        messageModalContent.appendChild(modalContent);
                        modalContent.style.display = 'block';
                        messageModal.classList.add('active');
                    }
                }
            }
        });
    });
    
    // Close modals
    const closeMessageModalBtn = document.getElementById('closeMessageModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const closeConfirmationModalBtn = document.getElementById('closeConfirmationModal');
    const cancelConfirmationBtn = document.getElementById('cancelConfirmationBtn');
    
    if (closeMessageModalBtn) {
        closeMessageModalBtn.addEventListener('click', closeMessageModal);
    }
    
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', closeMessageModal);
    }
    
    if (closeConfirmationModalBtn) {
        closeConfirmationModalBtn.addEventListener('click', closeConfirmationModal);
    }
    
    if (cancelConfirmationBtn) {
        cancelConfirmationBtn.addEventListener('click', closeConfirmationModal);
    }
    
    function closeMessageModal() {
        const messageModal = document.getElementById('messageModal');
        if (messageModal) {
            messageModal.classList.remove('active');
        }
    }
    
    function closeConfirmationModal() {
        const confirmationModal = document.getElementById('confirmationModal');
        if (confirmationModal) {
            confirmationModal.classList.remove('active');
        }
    }
    
    // Show confirmation modal
    function showConfirmationModal(title, message, confirmCallback) {
        const confirmationModal = document.getElementById('confirmationModal');
        const confirmationTitle = document.getElementById('confirmationTitle');
        const confirmationMessage = document.getElementById('confirmationMessage');
        const confirmActionBtn = document.getElementById('confirmActionBtn');
        
        if (confirmationModal && confirmationTitle && confirmationMessage && confirmActionBtn) {
            confirmationTitle.textContent = title;
            confirmationMessage.textContent = message;
            
            // Remove previous event listener
            const newConfirmBtn = confirmActionBtn.cloneNode(true);
            confirmActionBtn.parentNode.replaceChild(newConfirmBtn, confirmActionBtn);
            
            // Add new event listener
            newConfirmBtn.addEventListener('click', function() {
                if (typeof confirmCallback === 'function') {
                    confirmCallback();
                }
                closeConfirmationModal();
            });
            
            confirmationModal.classList.add('active');
        }
    }
    
    // Status Counter Update
    function updateStatusCounter(status, change) {
        const statusCardSelector = {
            'new': '.status-new-icon',
            'read': '.status-read-icon',
            'reviewed': '.status-reviewed-icon',
            'archived': '.status-archived-icon'
        };
        
        const selector = statusCardSelector[status.toLowerCase()];
        if (!selector) return;
        
        const statusCard = document.querySelector(selector);
        if (statusCard) {
            const countElement = statusCard.nextElementSibling.querySelector('h3');
            if (countElement) {
                let currentCount = parseInt(countElement.textContent, 10);
                currentCount += change;
                
                // Ensure count is not negative
                currentCount = Math.max(0, currentCount);
                
                countElement.textContent = currentCount;
                
                // Update notification badge if new messages
                if (status.toLowerCase() === 'new') {
                    const notificationBadge = document.querySelector('.notification-badge');
                    if (notificationBadge) {
                        notificationBadge.textContent = currentCount;
                        
                        // Hide badge if zero
                        if (currentCount === 0) {
                            notificationBadge.style.display = 'none';
                        } else {
                            notificationBadge.style.display = 'inline-block';
                        }
                    }
                }
            }
        }
    }
    
    // Save Admin Notes
    const saveNotesButtons = document.querySelectorAll('.save-notes-btn');
    saveNotesButtons.forEach(button => {
        button.addEventListener('click', function() {
            const notesSection = this.closest('.admin-notes-section');
            const textarea = notesSection.querySelector('.admin-notes-textarea');
            
            if (textarea) {
                // Flash animation to indicate saved
                this.innerHTML = '<i class="fas fa-check"></i> Saved';
                this.classList.add('success');
                
                setTimeout(() => {
                    this.innerHTML = 'Save Notes';
                    this.classList.remove('success');
                }, 2000);
            }
        });
    });
    
    // Tab Navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Make this button active
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // Get the tab value
            const tabValue = this.getAttribute('data-tab');
            
            // Filter items
            filterMessagesByStatus(tabValue);
        });
    });
    
    function filterMessagesByStatus(status) {
        const timelineItems = document.querySelectorAll('.timeline-item');
        const tableRows = document.querySelectorAll('tbody tr');
        
        if (status === 'all') {
            // Show all items
            timelineItems.forEach(item => {
                item.style.display = 'block';
            });
            tableRows.forEach(row => {
                row.style.display = 'table-row';
            });
        } else {
            // Filter by status
            timelineItems.forEach(item => {
                if (item.getAttribute('data-status') === status) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
            tableRows.forEach(row => {
                if (row.getAttribute('data-status') === status) {
                    row.style.display = 'table-row';
                } else {
                    row.style.display = 'none';
                }
            });
        }
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
            // If search is empty, restore current tab filter
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                filterMessagesByStatus(activeTab.getAttribute('data-tab'));
            }
            return;
        }
        
        const timelineItems = document.querySelectorAll('.timeline-item');
        const tableRows = document.querySelectorAll('tbody tr');
        
        // Search in timeline view
        timelineItems.forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchText) ? 'block' : 'none';
        });
        
        // Search in table view
        tableRows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchText) ? 'table-row' : 'none';
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
            // Reset all filter inputs
            document.querySelectorAll('.filter-group select, .filter-group input').forEach(input => {
                if (input.type === 'date') {
                    input.value = '';
                } else {
                    input.selectedIndex = 0;
                }
            });
            
            // Reset to current tab view
            const activeTab = document.querySelector('.tab-btn.active');
            if (activeTab) {
                filterMessagesByStatus(activeTab.getAttribute('data-tab'));
            }
            
            // Clear search
            const searchInput = document.querySelector('.search-input');
            if (searchInput) {
                searchInput.value = '';
            }
        });
    }
    
    function applyAdvancedFilters() {
        const projectFilter = document.getElementById('filter-project').value.toLowerCase();
        const inquiryFilter = document.getElementById('filter-inquiry').value.toLowerCase();
        const statusFilter = document.getElementById('filter-status').value.toLowerCase();
        const priorityFilter = document.getElementById('filter-priority').value.toLowerCase();
        const dateFromFilter = document.getElementById('filter-date-from').value;
        const dateToFilter = document.getElementById('filter-date-to').value;
        
        // Convert date strings to Date objects for comparison
        const dateFrom = dateFromFilter ? new Date(dateFromFilter) : null;
        const dateTo = dateToFilter ? new Date(dateToFilter) : null;
        
        // Apply filters to timeline items
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach(item => {
            let shouldShow = true;
            
            // Status filter
            if (statusFilter && item.getAttribute('data-status') !== statusFilter) {
                shouldShow = false;
            }
            
            // Project filter
            if (shouldShow && projectFilter) {
                const projectElement = item.querySelector('.info-value');
                if (projectElement && !projectElement.textContent.toLowerCase().includes(projectFilter)) {
                    shouldShow = false;
                }
            }
            
            // Inquiry type filter
            if (shouldShow && inquiryFilter) {
                const inquiryElement = item.querySelector('.inquiry-type');
                if (inquiryElement && !inquiryElement.textContent.toLowerCase().includes(inquiryFilter)) {
                    shouldShow = false;
                }
            }
            
            // Priority filter
            if (shouldShow && priorityFilter) {
                const priorityHighIcon = item.querySelector('.priority-high');
                const priorityMediumIcon = item.querySelector('.priority-medium');
                const priorityLowIcon = item.querySelector('.priority-low');
                
                if (
                    (priorityFilter === 'high' && !priorityHighIcon) ||
                    (priorityFilter === 'medium' && !priorityMediumIcon) ||
                    (priorityFilter === 'low' && !priorityLowIcon)
                ) {
                    shouldShow = false;
                }
            }
            
            // Date filters
            if (shouldShow && (dateFrom || dateTo)) {
                const dateElement = item.querySelector('.timeline-date span');
                if (dateElement) {
                    const dateText = dateElement.textContent.split('•')[0].trim();
                    const itemDate = new Date(dateText);
                    
                    if (dateFrom && itemDate < dateFrom) {
                        shouldShow = false;
                    }
                    
                    if (dateTo && itemDate > dateTo) {
                        shouldShow = false;
                    }
                }
            }
            
            item.style.display = shouldShow ? 'block' : 'none';
        });
        
        // Apply filters to table rows (simplified version)
        const tableRows = document.querySelectorAll('tbody tr');
        tableRows.forEach(row => {
            let shouldShow = true;
            
            // Status filter
            if (statusFilter && row.getAttribute('data-status') !== statusFilter) {
                shouldShow = false;
            }
            
            // Basic text content matching for other filters
            const rowText = row.textContent.toLowerCase();
            
            if (shouldShow && projectFilter && !rowText.includes(projectFilter)) {
                shouldShow = false;
            }
            
            if (shouldShow && inquiryFilter && !rowText.includes(inquiryFilter)) {
                shouldShow = false;
            }
            
            if (shouldShow && priorityFilter) {
                const hasPriority = (
                    (priorityFilter === 'high' && row.querySelector('.priority-high')) ||
                    (priorityFilter === 'medium' && row.querySelector('.priority-medium')) ||
                    (priorityFilter === 'low' && row.querySelector('.priority-low'))
                );
                
                if (!hasPriority) {
                    shouldShow = false;
                }
            }
            
            // Date filtering would be similar to timeline items but simplified here
            
            row.style.display = shouldShow ? 'table-row' : 'none';
        });
    }
    
    // Export functions
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function() {
            alert('PDF export functionality would be implemented here.');
            // In a real implementation, you would use a library like jsPDF to generate the PDF
        });
    }
    
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            exportToCSV();
        });
    }
    
    function exportToCSV() {
        const headers = ['Date', 'Client', 'Email', 'Project', 'Inquiry Type', 'Priority', 'Status', 'Message'];
        const rows = [];
        
        // Gather data from timeline items
        document.querySelectorAll('.timeline-item').forEach(item => {
            const dateElement = item.querySelector('.timeline-date span');
            const nameElement = item.querySelector('.timeline-date h3');
            const emailElement = item.querySelector('.info-value:nth-of-type(2)');
            const projectElement = item.querySelector('.info-value:nth-of-type(1)');
            const inquiryElement = item.querySelector('.inquiry-type');
            const statusElement = item.querySelector('.log-status');
            const messageElement = item.querySelector('.message-content');
            
            // Determine priority
            let priority = 'Medium';
            if (item.querySelector('.priority-high')) {
                priority = 'High';
            } else if (item.querySelector('.priority-low')) {
                priority = 'Low';
            }
            
            const row = [
                dateElement ? dateElement.textContent.trim() : '',
                nameElement ? nameElement.textContent.trim() : '',
                emailElement ? emailElement.textContent.trim() : '',
                projectElement ? projectElement.textContent.trim() : '',
                inquiryElement ? inquiryElement.textContent.trim() : '',
                priority,
                statusElement ? statusElement.textContent.trim() : '',
                messageElement ? messageElement.textContent.trim().replace(/\r?\n/g, ' ') : ''
            ];
            
            rows.push(row);
        });
        
        // Convert to CSV
        let csvContent = headers.join(',') + '\n';
        
        rows.forEach(row => {
            // Escape commas and quotes in cell values
            const escapedRow = row.map(cell => {
                // Remove any existing quotes and escape quotes in the cell
                const escapedCell = String(cell).replace(/"/g, '""');
                // Wrap in quotes if the cell contains commas, quotes, or newlines
                return /[,"\n]/.test(escapedCell) ? `"${escapedCell}"` : escapedCell;
            });
            
            csvContent += escapedRow.join(',') + '\n';
        });
        
        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.setAttribute('href', url);
        link.setAttribute('download', 'messages_export.csv');
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    // Utility function for debouncing input events
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
}); 