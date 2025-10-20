// Admin Diary Reviewer JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI
    initUI();
    
    // Add event listeners
    addEventListeners();
});

function initUI() {
    // Initialize date pickers
    const dateInputs = document.querySelectorAll('.flatpickr');
    dateInputs.forEach(input => {
        flatpickr(input, {
            dateFormat: "Y-m-d",
            allowInput: true
        });
    });
    
    // Show filters by default
    document.getElementById('filterOptions').style.display = 'block';
    
    // Expand the first few timeline items by default
    const timelineContents = document.querySelectorAll('.timeline-content');
    if (timelineContents.length > 0) {
        timelineContents[0].classList.add('active');
    }
}

function addEventListeners() {
    // View toggle buttons
    const timelineViewBtn = document.getElementById('timelineViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const expandAllBtn = document.getElementById('expandAllBtn');
    const collapseAllBtn = document.getElementById('collapseAllBtn');
    
    if (timelineViewBtn && tableViewBtn) {
        timelineViewBtn.addEventListener('click', function() {
            setActiveView('timeline');
            this.classList.add('active');
            tableViewBtn.classList.remove('active');
        });
        
        tableViewBtn.addEventListener('click', function() {
            setActiveView('table');
            this.classList.add('active');
            timelineViewBtn.classList.remove('active');
        });
    }
    
    if (expandAllBtn) {
        expandAllBtn.addEventListener('click', function() {
            expandAllTimelineItems();
        });
    }
    
    if (collapseAllBtn) {
        collapseAllBtn.addEventListener('click', function() {
            collapseAllTimelineItems();
        });
    }
    
    // Filter toggle
    const filterToggle = document.getElementById('filterToggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', function() {
            const filterOptions = document.getElementById('filterOptions');
            const isVisible = filterOptions.style.display !== 'none';
            
            filterOptions.style.display = isVisible ? 'none' : 'block';
            
            // Update button text and icon
            const spanElement = this.querySelector('span');
            const iconElement = this.querySelector('i');
            
            if (isVisible) {
                spanElement.textContent = 'Show Filters';
                iconElement.className = 'fas fa-chevron-down';
            } else {
                spanElement.textContent = 'Hide Filters';
                iconElement.className = 'fas fa-chevron-up';
            }
        });
    }
    
    // Reset filters button
    const resetFiltersBtn = document.getElementById('resetFilters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            resetFilters();
        });
    }
    
    // Apply filters button
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            applyFilters();
        });
    }
    
    // Entry view buttons
    const viewEntryBtns = document.querySelectorAll('.view-entry-btn, .action-btn.view');
    viewEntryBtns.forEach(button => {
        button.addEventListener('click', function() {
            const entryId = this.getAttribute('data-entry-id');
            viewEntryDetails(entryId);
        });
    });
    
    // Timeline item expand/collapse
    const timelineHeaders = document.querySelectorAll('.timeline-header');
    timelineHeaders.forEach(header => {
        header.addEventListener('click', function(e) {
            // Ignore click if it's on the view button
            if (e.target.closest('.view-entry-btn') || e.target.closest('.action-btn.view')) {
                return;
            }
            
            const itemId = this.getAttribute('data-id');
            toggleTimelineItem(itemId);
        });
    });
    
    // Expand/collapse icons separate click
    const expandButtons = document.querySelectorAll('.action-btn.expand');
    expandButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent timeline header click event
            const itemId = this.closest('.timeline-header').getAttribute('data-id');
            toggleTimelineItem(itemId);
            
            // Toggle active class for the button itself
            this.classList.toggle('active');
        });
    });
    
    // Export buttons
    document.getElementById('exportPdfBtn')?.addEventListener('click', exportPdf);
    document.getElementById('exportCsvBtn')?.addEventListener('click', exportCsv);
    document.getElementById('refreshBtn')?.addEventListener('click', refreshData);
    document.getElementById('printBtn')?.addEventListener('click', printData);
}

function setActiveView(view) {
    const timelineView = document.getElementById('timelineView');
    const tableView = document.getElementById('tableView');
    
    if (view === 'timeline') {
        timelineView.style.display = 'block';
        tableView.style.display = 'none';
    } else {
        timelineView.style.display = 'none';
        tableView.style.display = 'block';
    }
}

function toggleTimelineItem(itemId) {
    const content = document.getElementById('content' + itemId);
    const expandButton = document.querySelector(`.timeline-header[data-id="${itemId}"] .action-btn.expand`);
    
    if (content) {
        content.classList.toggle('active');
        
        // Also toggle icon rotation if button exists
        if (expandButton) {
            expandButton.classList.toggle('active');
        }
    }
}

function expandAllTimelineItems() {
    const timelineContents = document.querySelectorAll('.timeline-content');
    const expandButtons = document.querySelectorAll('.action-btn.expand');
    
    timelineContents.forEach(content => {
        content.classList.add('active');
    });
    
    expandButtons.forEach(button => {
        button.classList.add('active');
    });
}

function collapseAllTimelineItems() {
    const timelineContents = document.querySelectorAll('.timeline-content');
    const expandButtons = document.querySelectorAll('.action-btn.expand');
    
    timelineContents.forEach(content => {
        content.classList.remove('active');
    });
    
    expandButtons.forEach(button => {
        button.classList.remove('active');
    });
}

function resetFilters() {
    const filterForm = document.querySelectorAll('#filterOptions select, #filterOptions input');
    filterForm.forEach(element => {
        if (element.type === 'text' || element.type === 'date' || element.tagName.toLowerCase() === 'select') {
            element.value = '';
        }
    });
    
    // Reset the flatpickr instances
    const dateInputs = document.querySelectorAll('.flatpickr');
    dateInputs.forEach(input => {
        if (input._flatpickr) {
            input._flatpickr.clear();
        }
    });
    
    document.getElementById('search').value = '';
}

function applyFilters() {
    // Get filter values
    const architect = document.getElementById('filter-architect').value;
    const project = document.getElementById('filter-project').value;
    const status = document.getElementById('filter-status').value;
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    const searchTerm = document.getElementById('search').value.toLowerCase();
    
    // Display the filter selections as an alert for now
    // This would be replaced with actual filtering logic in a real implementation
    console.log(`Filters Applied:
        Architect: ${architect || 'All'}
        Project: ${project || 'All'}
        Status: ${status || 'All'}
        Date Range: ${dateFrom || 'Any'} to ${dateTo || 'Any'}
        Search Term: ${searchTerm || 'None'}
    `);
    
    // Simulate a server request with a loading indicator
    showLoadingOverlay();
    
    // Simulate network delay
    setTimeout(() => {
        hideLoadingOverlay();
        
        // Show a success message
        showNotification('Filters Applied', 'Diary entries have been filtered according to your criteria.', 'success');
    }, 1000);
}

function viewEntryDetails(entryId) {
    // Navigate to the diary entry view page with the entry ID as a parameter
    // In a real implementation, this would redirect to the detailed view
    window.location.href = `admindiary.html?id=${entryId}`;
}

function exportPdf() {
    showNotification('PDF Export Started', 'Your PDF file is being generated...', 'info');
    
    // Simulate PDF generation delay
    setTimeout(() => {
        showNotification('PDF Export Complete', 'Your PDF has been downloaded.', 'success');
    }, 1500);
}

function exportCsv() {
    showNotification('CSV Export Started', 'Your CSV file is being generated...', 'info');
    
    // Simulate CSV generation delay
    setTimeout(() => {
        showNotification('CSV Export Complete', 'Your CSV has been downloaded.', 'success');
    }, 1000);
}

function refreshData() {
    showLoadingOverlay();
    
    // Simulate refresh delay
    setTimeout(() => {
        hideLoadingOverlay();
        showNotification('Data Refreshed', 'The diary entries have been refreshed with the latest data.', 'success');
    }, 1500);
}

function printData() {
    showNotification('Preparing Print View', 'The print dialog will open shortly...', 'info');
    
    // Simulate print preparation delay
    setTimeout(() => {
        window.print();
    }, 800);
}

function showLoadingOverlay() {
    // Check if the overlay already exists
    let overlay = document.getElementById('loading-overlay');
    
    if (!overlay) {
        // Create the overlay
        overlay = document.createElement('div');
        overlay.id = 'loading-overlay';
        overlay.style.position = 'fixed';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.width = '100%';
        overlay.style.height = '100%';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.display = 'flex';
        overlay.style.justifyContent = 'center';
        overlay.style.alignItems = 'center';
        overlay.style.zIndex = '9999';
        
        // Create loading spinner
        const spinner = document.createElement('div');
        spinner.style.border = '5px solid #f3f3f3';
        spinner.style.borderTop = '5px solid #00273C';
        spinner.style.borderRadius = '50%';
        spinner.style.width = '50px';
        spinner.style.height = '50px';
        spinner.style.animation = 'spin 2s linear infinite';
        
        // Add animation style
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(style);
        
        overlay.appendChild(spinner);
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

function showNotification(title, message, type = 'info') {
    // Check if the notification container exists
    let container = document.getElementById('notification-container');
    
    if (!container) {
        // Create the container
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.maxWidth = '400px';
        container.style.zIndex = '10000';
        document.body.appendChild(container);
    }
    
    // Create the notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.backgroundColor = 'white';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    notification.style.marginBottom = '10px';
    notification.style.padding = '15px';
    notification.style.display = 'flex';
    notification.style.alignItems = 'flex-start';
    notification.style.gap = '10px';
    notification.style.transform = 'translateX(120%)';
    notification.style.transition = 'transform 0.3s ease';
    notification.style.opacity = '0';
    
    // Set border color based on notification type
    let iconClass, iconColor, borderColor;
    switch(type) {
        case 'success':
            iconClass = 'fas fa-check-circle';
            iconColor = '#4CAF50';
            borderColor = '#4CAF50';
            break;
        case 'error':
            iconClass = 'fas fa-times-circle';
            iconColor = '#F44336';
            borderColor = '#F44336';
            break;
        case 'warning':
            iconClass = 'fas fa-exclamation-triangle';
            iconColor = '#FF9800';
            borderColor = '#FF9800';
            break;
        case 'info':
        default:
            iconClass = 'fas fa-info-circle';
            iconColor = '#2196F3';
            borderColor = '#2196F3';
            break;
    }
    
    notification.style.borderLeft = `4px solid ${borderColor}`;
    
    // Create icon
    const icon = document.createElement('i');
    icon.className = iconClass;
    icon.style.fontSize = '20px';
    icon.style.color = iconColor;
    
    // Create content
    const content = document.createElement('div');
    content.style.flex = '1';
    
    const titleElement = document.createElement('div');
    titleElement.textContent = title;
    titleElement.style.fontWeight = 'bold';
    titleElement.style.marginBottom = '5px';
    
    const messageElement = document.createElement('div');
    messageElement.textContent = message;
    messageElement.style.fontSize = '14px';
    messageElement.style.color = '#555';
    
    content.appendChild(titleElement);
    content.appendChild(messageElement);
    
    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.innerHTML = '&times;';
    closeBtn.style.background = 'none';
    closeBtn.style.border = 'none';
    closeBtn.style.cursor = 'pointer';
    closeBtn.style.fontSize = '20px';
    closeBtn.style.color = '#555';
    closeBtn.style.padding = '0 5px';
    closeBtn.onclick = function() {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(120%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    };
    
    // Assemble notification
    notification.appendChild(icon);
    notification.appendChild(content);
    notification.appendChild(closeBtn);
    
    // Add to container
    container.appendChild(notification);
    
    // Show with animation
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(120%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
} 