document.addEventListener('DOMContentLoaded', function() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    const roleFilter = document.getElementById('roleFilter');
    const statusFilter = document.getElementById('statusFilter');
    const tableBody = document.getElementById('usersTableBody');
    const rows = tableBody.querySelectorAll('tr');

    // Real-time online status tracking
    let onlineStatusInterval;
    
    function startOnlineStatusTracking() {
        updateOnlineStatus();
        onlineStatusInterval = setInterval(updateOnlineStatus, 30000); // Update every 30 seconds
    }
    
    function updateOnlineStatus() {
        fetch('/admin-panel/users/online-status/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateOnlineIndicators(data.online_status);
            }
        })
        .catch(error => {
            console.error('Error updating online status:', error);
        });
    }
    
    function updateOnlineIndicators(onlineStatus) {
        rows.forEach(row => {
            const userAvatar = row.querySelector('.user-avatar');
            const onlineText = row.querySelector('.online-text');
            const onlineIndicator = row.querySelector('.online-indicator');
            
            if (userAvatar) {
                const userId = row.querySelector('.action-btn')?.dataset.userId;
                if (userId && onlineStatus.hasOwnProperty(userId)) {
                    const isOnline = onlineStatus[userId];
                    
                    // Update online indicator
                    if (isOnline) {
                        if (!onlineIndicator) {
                            const indicator = document.createElement('div');
                            indicator.className = 'online-indicator';
                            indicator.title = 'Online';
                            userAvatar.appendChild(indicator);
                        }
                        if (!onlineText) {
                            const text = document.createElement('small');
                            text.className = 'online-text';
                            text.textContent = 'Online';
                            userAvatar.parentNode.querySelector('div:last-child').appendChild(text);
                        }
                    } else {
                        if (onlineIndicator) {
                            onlineIndicator.remove();
                        }
                        if (onlineText) {
                            onlineText.remove();
                        }
                    }
                }
            }
        });
    }
    
    // Start tracking when page loads
    startOnlineStatusTracking();
    
    // Stop tracking when page unloads
    window.addEventListener('beforeunload', function() {
        if (onlineStatusInterval) {
            clearInterval(onlineStatusInterval);
        }
    });

    function filterTable() {
        const searchTerm = searchInput.value.toLowerCase();
        const roleValue = roleFilter.value;
        const statusValue = statusFilter.value;

        rows.forEach(row => {
            if (row.querySelector('td')) { // Skip empty state row
                const name = row.querySelector('.user-name').textContent.toLowerCase();
                const email = row.querySelectorAll('td')[1].textContent.toLowerCase();
                const role = row.dataset.role;
                const status = row.dataset.status;

                const matchesSearch = name.includes(searchTerm) || email.includes(searchTerm);
                const matchesRole = !roleValue || role === roleValue;
                const matchesStatus = !statusValue || status === statusValue;

                if (matchesSearch && matchesRole && matchesStatus) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }

    // Event listeners for filters
    searchInput.addEventListener('input', filterTable);
    roleFilter.addEventListener('change', filterTable);
    statusFilter.addEventListener('change', filterTable);

    // Sorting functionality
    document.querySelectorAll('[data-sort]').forEach(sortBtn => {
        sortBtn.addEventListener('click', function() {
            const sortBy = this.dataset.sort;
            sortTable(sortBy);
        });
    });

    function sortTable(column) {
        const rowsArray = Array.from(rows).filter(row => row.querySelector('td'));
        
        rowsArray.sort((a, b) => {
            let aVal, bVal;
            
            switch(column) {
                case 'name':
                    aVal = a.querySelector('.user-name').textContent;
                    bVal = b.querySelector('.user-name').textContent;
                    break;
                case 'email':
                    aVal = a.querySelectorAll('td')[1].textContent;
                    bVal = b.querySelectorAll('td')[1].textContent;
                    break;
                case 'role':
                    aVal = a.dataset.role;
                    bVal = b.dataset.role;
                    break;
                case 'status':
                    aVal = a.dataset.status;
                    bVal = b.dataset.status;
                    break;
                case 'date':
                    aVal = new Date(a.querySelectorAll('td')[4].textContent);
                    bVal = new Date(b.querySelectorAll('td')[4].textContent);
                    break;
            }
            
            return aVal > bVal ? 1 : -1;
        });

        // Clear table body and re-append sorted rows
        tableBody.innerHTML = '';
        rowsArray.forEach(row => tableBody.appendChild(row));
    }

    // Action button handlers
    document.addEventListener('click', function(e) {
        if (e.target.closest('.action-btn')) {
            const btn = e.target.closest('.action-btn');
            const userId = btn.dataset.userId;
            const action = btn.classList.contains('approve') ? 'approve' :
                          btn.classList.contains('reject') ? 'deny' :
                          btn.classList.contains('activate') ? 'reactivate' :
                          btn.classList.contains('deactivate') ? 'suspend' :
                          btn.classList.contains('unlock') ? 'unlock' :
                          btn.classList.contains('view') ? 'view' : null;

            if (action === 'view') {
                viewUserDetails(userId);
            } else if (action) {
                showConfirmation(userId, action);
            }
        }
    });

    // View user details
    function viewUserDetails(userId) {
        fetch(`/admin-panel/users/${userId}/`)
            .then(response => response.text())
            .then(html => {
                document.getElementById('userDetailContent').innerHTML = html;
                document.getElementById('userDetailModal').classList.add('active');
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error loading user details');
            });
    }

    // Show confirmation modal
    function showConfirmation(userId, action) {
        const actions = {
            'approve': { title: 'Approve Site Manager', message: 'Are you sure you want to approve this site manager?' },
            'deny': { title: 'Deny Application', message: 'Are you sure you want to deny this site manager application?' },
            'suspend': { title: 'Suspend User', message: 'Are you sure you want to suspend this user?' },
            'reactivate': { title: 'Unsuspend User', message: 'Are you sure you want to unsuspend this user?' },
            'unlock': { title: 'Unlock Account', message: 'Are you sure you want to unlock this account?' }
        };

        const actionData = actions[action];
        document.getElementById('confirmTitle').textContent = actionData.title;
        document.getElementById('confirmMessage').textContent = actionData.message;
        
        document.getElementById('confirmationModal').classList.add('active');
        
        document.getElementById('confirmAction').onclick = () => {
            updateUserStatus(userId, action);
        };
    }

    // Update user status
    window.updateUserStatus = function(userId, action) {
        fetch(`/admin-panel/users/${userId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ action: action })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
        
        document.getElementById('confirmationModal').classList.remove('active');
    }

    // Modal close handlers
    document.getElementById('closeUserModal').onclick = () => {
        document.getElementById('userDetailModal').classList.remove('active');
    };

    document.getElementById('closeModalBtn').onclick = () => {
        document.getElementById('userDetailModal').classList.remove('active');
    };

    document.getElementById('closeConfirmModal').onclick = () => {
        document.getElementById('confirmationModal').classList.remove('active');
    };

    document.getElementById('cancelAction').onclick = () => {
        document.getElementById('confirmationModal').classList.remove('active');
    };

    // Close modals when clicking outside
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    // Tab switching for user detail modal
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('tab-btn')) {
            const tabId = e.target.dataset.tab;
            const container = e.target.closest('.tabs-container');
            
            if (container) {
                // Remove active class from all tabs and content
                container.querySelectorAll('.tab-btn').forEach(t => t.classList.remove('active'));
                container.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                // Add active class to clicked tab and corresponding content
                e.target.classList.add('active');
                const targetContent = container.querySelector('#' + tabId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            }
        }
    });

    // Utility function to get CSRF token
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