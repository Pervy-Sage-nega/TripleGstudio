// Project Detail JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeProjectDetail();
});

function initializeProjectDetail() {
    updateCircularProgress();
    initializeBudgetChart();
    setupModalHandlers();
}

// Circular Progress Animation
function updateCircularProgress() {
    const progressCircles = document.querySelectorAll('.progress-circle');
    
    progressCircles.forEach(circle => {
        const progress = parseInt(circle.dataset.progress) || 0;
        const degree = (progress / 100) * 360;
        
        // Animate the progress
        let currentDegree = 0;
        const increment = degree / 50; // 50 steps for smooth animation
        
        const animate = () => {
            if (currentDegree < degree) {
                currentDegree += increment;
                circle.style.background = `conic-gradient(var(--primary-color) ${currentDegree}deg, var(--light-gray) ${currentDegree}deg)`;
                requestAnimationFrame(animate);
            } else {
                circle.style.background = `conic-gradient(var(--primary-color) ${degree}deg, var(--light-gray) ${degree}deg)`;
            }
        };
        
        setTimeout(animate, 500); // Start animation after 500ms
    });
}

// Budget Chart (Simple Canvas Implementation)
function initializeBudgetChart() {
    const canvas = document.getElementById('budgetChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = 80;
    
    // Mock data - in real app, this would come from backend
    const totalBudget = 2500000;
    const totalSpent = 1550000;
    const remaining = totalBudget - totalSpent;
    
    const spentPercentage = (totalSpent / totalBudget) * 360;
    const remainingPercentage = (remaining / totalBudget) * 360;
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw spent portion
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, (-Math.PI / 2) + (spentPercentage * Math.PI / 180));
    ctx.lineWidth = 20;
    ctx.strokeStyle = '#ff9800'; // Warning color for spent
    ctx.stroke();
    
    // Draw remaining portion
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, (-Math.PI / 2) + (spentPercentage * Math.PI / 180), (-Math.PI / 2) + ((spentPercentage + remainingPercentage) * Math.PI / 180));
    ctx.lineWidth = 20;
    ctx.strokeStyle = '#4caf50'; // Success color for remaining
    ctx.stroke();
    
    // Draw center text
    ctx.fillStyle = '#284b63';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Budget', centerX, centerY - 5);
    ctx.font = '12px Arial';
    ctx.fillText('Overview', centerX, centerY + 10);
}

// Modal Handlers
function setupModalHandlers() {
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('timelineModal');
        if (event.target === modal) {
            closeTimelineModal();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeTimelineModal();
        }
    });
}

function openTimelineModal() {
    const modal = document.getElementById('timelineModal');
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
        
        // Animate timeline items
        const timelineItems = modal.querySelectorAll('.timeline-item');
        timelineItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateX(-20px)';
            
            setTimeout(() => {
                item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                item.style.opacity = '1';
                item.style.transform = 'translateX(0)';
            }, index * 100);
        });
    }
}

function closeTimelineModal() {
    const modal = document.getElementById('timelineModal');
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto'; // Restore scrolling
    }
}

// Report Generation
function generateFinancialReport() {
    showNotification('Generating financial report...', 'info');
    
    // Mock report generation
    setTimeout(() => {
        showNotification('Financial report generated successfully!', 'success');
        // In real implementation, this would trigger a download
        mockDownload('financial-report.pdf');
    }, 2000);
}

// Resource Management
function addResourceEntry() {
    showNotification('Resource entry feature will be available after backend integration.', 'warning');
}

// File Operations
function downloadFile(fileName) {
    showNotification(`Downloading ${fileName}...`, 'info');
    mockDownload(fileName);
}

function previewFile(fileName) {
    showNotification(`Opening preview for ${fileName}...`, 'info');
    // In real implementation, this would open a file preview modal
}

// Mock file download
function mockDownload(fileName) {
    // Create a temporary link element for download simulation
    const link = document.createElement('a');
    link.href = '#';
    link.download = fileName;
    link.style.display = 'none';
    
    document.body.appendChild(link);
    
    setTimeout(() => {
        showNotification(`${fileName} downloaded successfully!`, 'success');
        document.body.removeChild(link);
    }, 1000);
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());
    
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
        z-index: 1001;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
        min-width: 300px;
        max-width: 400px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }
    }, 4000);
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

// Add event listeners for file operations
document.addEventListener('click', function(event) {
    if (event.target.closest('.btn-icon[title="Download"]')) {
        const fileItem = event.target.closest('.file-item');
        const fileName = fileItem.querySelector('.file-name').textContent;
        downloadFile(fileName);
    }
    
    if (event.target.closest('.btn-icon[title="Preview"]')) {
        const fileItem = event.target.closest('.file-item');
        const fileName = fileItem.querySelector('.file-name').textContent;
        previewFile(fileName);
    }
});

// Add CSS animations if not already present
if (!document.querySelector('#project-detail-animations')) {
    const style = document.createElement('style');
    style.id = 'project-detail-animations';
    style.textContent = `
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
        
        .detail-card {
            animation: fadeInUp 0.6s ease-out;
        }
        
        .detail-card:nth-child(1) { animation-delay: 0.1s; }
        .detail-card:nth-child(2) { animation-delay: 0.2s; }
        .detail-card:nth-child(3) { animation-delay: 0.3s; }
        .detail-card:nth-child(4) { animation-delay: 0.4s; }
        .detail-card:nth-child(5) { animation-delay: 0.5s; }
        .detail-card:nth-child(6) { animation-delay: 0.6s; }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}