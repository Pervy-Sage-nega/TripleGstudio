// Site Manager Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

function initializeDashboard() {
    setupFilters();
    setupSearch();
    updateProgressBars();
}

// Filter and Search Functionality
function setupFilters() {
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterProjects);
    }
    
    if (statusFilter) {
        statusFilter.addEventListener('change', filterProjects);
    }
}

function setupSearch() {
    const searchInput = document.getElementById('projectSearch');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchProjects, 300));
    }
}

function filterProjects() {
    const categoryFilter = document.getElementById('categoryFilter');
    const statusFilter = document.getElementById('statusFilter');
    const projectCards = document.querySelectorAll('.project-card');
    
    const selectedCategory = categoryFilter ? categoryFilter.value : '';
    const selectedStatus = statusFilter ? statusFilter.value : '';
    
    projectCards.forEach(card => {
        const cardCategory = card.dataset.category || '';
        const cardStatus = card.dataset.status || '';
        
        const categoryMatch = !selectedCategory || cardCategory === selectedCategory;
        const statusMatch = !selectedStatus || cardStatus === selectedStatus;
        
        if (categoryMatch && statusMatch) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in';
        } else {
            card.style.display = 'none';
        }
    });
    
    updateResultsCount();
}

function searchProjects() {
    const searchInput = document.getElementById('projectSearch');
    const projectCards = document.querySelectorAll('.project-card');
    const searchTerm = searchInput.value.toLowerCase();
    
    projectCards.forEach(card => {
        const projectTitle = card.querySelector('.project-title').textContent.toLowerCase();
        const projectDescription = card.querySelector('.project-description').textContent.toLowerCase();
        
        if (projectTitle.includes(searchTerm) || projectDescription.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.animation = 'fadeIn 0.3s ease-in';
        } else {
            card.style.display = 'none';
        }
    });
    
    updateResultsCount();
}

function updateResultsCount() {
    const visibleCards = document.querySelectorAll('.project-card[style*="display: block"], .project-card:not([style*="display: none"])');
    const totalCards = document.querySelectorAll('.project-card');
    
    // Update results indicator if it exists
    let resultsIndicator = document.querySelector('.results-indicator');
    if (!resultsIndicator) {
        resultsIndicator = document.createElement('div');
        resultsIndicator.className = 'results-indicator';
        const controlsTitle = document.querySelector('.controls-title');
        if (controlsTitle) {
            controlsTitle.appendChild(resultsIndicator);
        }
    }
    
    if (visibleCards.length !== totalCards.length) {
        resultsIndicator.textContent = ` (${visibleCards.length} of ${totalCards.length})`;
        resultsIndicator.style.color = '#757575';
        resultsIndicator.style.fontSize = '14px';
        resultsIndicator.style.fontWeight = 'normal';
    } else {
        resultsIndicator.textContent = '';
    }
}

// Progress Bar Animation
function updateProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        
        setTimeout(() => {
            bar.style.transition = 'width 1s ease-in-out';
            bar.style.width = width;
        }, 100);
    });
}

// Report Generation
function generateReport(projectId) {
    showNotification(`Generating report for project ${projectId}...`, 'info');
    
    // Call the Django API endpoint
    fetch(`/diary/api/generate-report/${projectId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(`Report for ${data.project_name} generated successfully!`, 'success');
            // In a real implementation, you could trigger a download here
            // window.open(data.download_url, '_blank');
        } else {
            showNotification(`Error generating report: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        showNotification(`Error generating report: ${error.message}`, 'error');
    });
}

// Helper function to get CSRF token
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

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        success: '#4caf50',
        error: '#f44336',
        warning: '#ff9800',
        info: '#2196f3'
    };
    return colors[type] || '#2196f3';
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
        transition: background-color 0.3s;
    }
    
    .notification-close:hover {
        background: rgba(255, 255, 255, 0.2);
    }
`;
document.head.appendChild(style);