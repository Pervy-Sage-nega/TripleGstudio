// Admin User Management JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI
    initUI();
    
    // Add event listeners
    addEventListeners();
});

function initUI() {
    // Initialize any UI components that need setup on load
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal(modal.id);
            }
        });
    });
}

function addEventListeners() {
    // Filter toggle
    const filterToggle = document.getElementById('filterToggle');
    if (filterToggle) {
        filterToggle.addEventListener('click', toggleFilters);
    }
    
    // Add User Button
    const addUserBtn = document.getElementById('addUserBtn');
    if (addUserBtn) {
        addUserBtn.addEventListener('click', openAddUserModal);
    }
    
    // View Permissions Button
    const viewPermissionsBtn = document.getElementById('viewPermissionsBtn');
    if (viewPermissionsBtn) {
        viewPermissionsBtn.addEventListener('click', openPermissionsModal);
    }
    
    // Close Buttons
    const closeButtons = document.querySelectorAll('.modal-close');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.closest('.modal').id;
            closeModal(modalId);
        });
    });
    
    // Close Permission View Button
    const closePermissionViewBtn = document.getElementById('closePermissionViewBtn');
    if (closePermissionViewBtn) {
        closePermissionViewBtn.addEventListener('click', function() {
            closeModal('permissionsModal');
        });
    }
    
    // Cancel User Form Button
    const cancelUserBtn = document.getElementById('cancelUserBtn');
    if (cancelUserBtn) {
        cancelUserBtn.addEventListener('click', function() {
            closeModal('userModal');
        });
    }
    
    // Save User Button
    const saveUserBtn = document.getElementById('saveUserBtn');
    if (saveUserBtn) {
        saveUserBtn.addEventListener('click', saveUser);
    }
    
    // Generate Password Button
    const generatePasswordBtn = document.getElementById('generatePasswordBtn');
    if (generatePasswordBtn) {
        generatePasswordBtn.addEventListener('click', generateRandomPassword);
    }
    
    // Password Toggle Buttons
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', togglePasswordVisibility);
    });
    
    // Reset Filters Button
    const resetFiltersBtn = document.getElementById('resetFilters');
    if (resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', resetFilters);
    }
    
    // Apply Filters Button
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyFilters);
    }
    
    // Table Row Actions
    setupTableActions();
    
    // Photo Upload and Preview
    setupPhotoUpload();
    
    // Search Input
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    
    // Export Buttons
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', exportPDF);
    }
    
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', exportCSV);
    }
    
    // Cancel Reset Password Button
    const cancelResetPasswordBtn = document.getElementById('cancelResetPasswordBtn');
    if (cancelResetPasswordBtn) {
        cancelResetPasswordBtn.addEventListener('click', function() {
            closeModal('resetPasswordModal');
        });
    }
    
    // Confirm Reset Password Button
    const confirmResetPasswordBtn = document.getElementById('confirmResetPasswordBtn');
    if (confirmResetPasswordBtn) {
        confirmResetPasswordBtn.addEventListener('click', resetPassword);
    }
    
    // Confirmation Modal Cancel Button
    const cancelConfirmationBtn = document.getElementById('cancelConfirmationBtn');
    if (cancelConfirmationBtn) {
        cancelConfirmationBtn.addEventListener('click', function() {
            closeModal('confirmationModal');
        });
    }
    
    // Confirmation Modal Confirm Button
    const confirmActionBtn = document.getElementById('confirmActionBtn');
    if (confirmActionBtn) {
        confirmActionBtn.addEventListener('click', handleConfirmAction);
    }
}

// Set up table actions (edit, deactivate, etc.)
function setupTableActions() {
    // Edit User Action
    const editButtons = document.querySelectorAll('.action-btn.edit');
    editButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            const userEmail = userRow.querySelector('td:nth-child(2)').textContent;
            const userRole = userRow.dataset.role;
            const userStatus = userRow.dataset.status;
            
            // Open edit modal with user data
            openEditUserModal(userName, userEmail, userRole, userStatus);
        });
    });
    
    // Deactivate User Action
    const deactivateButtons = document.querySelectorAll('.action-btn.deactivate');
    deactivateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            
            // Show confirmation modal
            openConfirmationModal(
                'Deactivate User',
                `Are you sure you want to deactivate ${userName}? They will no longer be able to login to the system.`,
                'deactivateUser',
                userName
            );
        });
    });
    
    // Activate User Action
    const activateButtons = document.querySelectorAll('.action-btn.activate');
    activateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            
            // Show confirmation modal
            openConfirmationModal(
                'Activate User',
                `Are you sure you want to activate ${userName}? They will be able to login to the system.`,
                'activateUser',
                userName
            );
        });
    });
    
    // Reset Password Action
    const resetPasswordButtons = document.querySelectorAll('.action-btn.reset-password');
    resetPasswordButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            
            // Open reset password modal
            openResetPasswordModal(userName);
        });
    });
    
    // Approve User Action
    const approveButtons = document.querySelectorAll('.action-btn.approve');
    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            
            // Show confirmation modal
            openConfirmationModal(
                'Approve User',
                `Are you sure you want to approve ${userName}'s account? They will be activated and able to login to the system.`,
                'approveUser',
                userName
            );
        });
    });
    
    // Reject User Action
    const rejectButtons = document.querySelectorAll('.action-btn.reject');
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            
            // Show confirmation modal
            openConfirmationModal(
                'Reject User',
                `Are you sure you want to reject ${userName}'s account? This action cannot be undone.`,
                'rejectUser',
                userName
            );
        });
    });
    
    // View User Details Action
    const viewButtons = document.querySelectorAll('.action-btn.view');
    viewButtons.forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('tr');
            const userName = userRow.querySelector('.user-name div').textContent;
            const userEmail = userRow.querySelector('td:nth-child(2)').textContent;
            const userRole = userRow.dataset.role;
            
            // Open view user modal (reusing edit modal but in read-only mode)
            openViewUserModal(userName, userEmail, userRole);
        });
    });
}

// Toggle filters visibility
function toggleFilters() {
    const filterOptions = document.getElementById('filterOptions');
    const filterToggle = document.getElementById('filterToggle');
    
    if (filterOptions.style.display === 'none') {
        filterOptions.style.display = 'grid';
        filterToggle.querySelector('span').textContent = 'Hide Filters';
        filterToggle.querySelector('i').classList.remove('fa-chevron-down');
        filterToggle.querySelector('i').classList.add('fa-chevron-up');
    } else {
        filterOptions.style.display = 'none';
        filterToggle.querySelector('span').textContent = 'Show Filters';
        filterToggle.querySelector('i').classList.remove('fa-chevron-up');
        filterToggle.querySelector('i').classList.add('fa-chevron-down');
    }
}

// Open Add User Modal
function openAddUserModal() {
    // Reset form
    document.getElementById('userForm').reset();
    
    // Update modal title
    document.getElementById('userModalTitle').textContent = 'Add New User';
    
    // Reset photo preview
    const photoPreview = document.getElementById('photoPreview');
    photoPreview.innerHTML = '<i class="fas fa-user"></i>';
    
    // Open modal
    openModal('userModal');
}

// Open Edit User Modal with pre-filled data
function openEditUserModal(name, email, role, status) {
    // Split name into first and last name
    const nameParts = name.split(' ');
    const firstName = nameParts[0];
    const lastName = nameParts.slice(1).join(' ');
    
    // Fill form with user data
    document.getElementById('firstName').value = firstName;
    document.getElementById('lastName').value = lastName;
    document.getElementById('email').value = email;
    document.getElementById('role').value = role;
    document.getElementById('status').value = status;
    
    // Update password field placeholder
    document.getElementById('password').value = '••••••••';
    document.getElementById('password').placeholder = 'Leave unchanged to keep current password';
    
    // Update modal title
    document.getElementById('userModalTitle').textContent = 'Edit User';
    
    // Set photo preview (for demo purposes, we'll use a placeholder)
    const photoPreview = document.getElementById('photoPreview');
    photoPreview.innerHTML = `<img src="../../css/images/${role.toLowerCase()}-avatar.jpg" alt="${name}">`;
    
    // Open modal
    openModal('userModal');
}

// Open View User Modal (read-only)
function openViewUserModal(name, email, role) {
    // This is just a demo implementation
    // In a real application, you would show a different modal with complete user details
    
    // For this demo, we'll reuse the edit modal but make it read-only
    openEditUserModal(name, email, role, 'Pending');
    
    // Make form fields read-only
    const inputs = document.querySelectorAll('#userForm input, #userForm select');
    inputs.forEach(input => {
        input.setAttribute('disabled', 'disabled');
    });
    
    // Update modal title
    document.getElementById('userModalTitle').textContent = 'User Details';
    
    // Hide save button
    document.getElementById('saveUserBtn').style.display = 'none';
}

// Open Permissions Modal
function openPermissionsModal() {
    openModal('permissionsModal');
}

// Open Reset Password Modal
function openResetPasswordModal(userName) {
    // Set the user name in the modal
    document.getElementById('resetPasswordUserName').textContent = userName;
    
    // Clear password field
    document.getElementById('newPassword').value = '';
    
    // Open modal
    openModal('resetPasswordModal');
}

// Open Confirmation Modal
function openConfirmationModal(title, message, action, data) {
    // Set modal content
    document.getElementById('confirmationTitle').textContent = title;
    document.getElementById('confirmationMessage').textContent = message;
    
    // Store action type and data for later use
    const confirmActionBtn = document.getElementById('confirmActionBtn');
    confirmActionBtn.dataset.action = action;
    confirmActionBtn.dataset.data = data;
    
    // Open modal
    openModal('confirmationModal');
}

// Handle Save User (Add/Edit)
function saveUser() {
    // Get form data
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const role = document.getElementById('role').value;
    const password = document.getElementById('password').value;
    const status = document.getElementById('status').value;
    
    // Validate form
    if (!firstName || !lastName || !email || !role) {
        alert('Please fill out all required fields.');
        return;
    }
    
    // Determine if this is an add or edit
    const modalTitle = document.getElementById('userModalTitle').textContent;
    const isAdd = modalTitle === 'Add New User';
    
    // Simulate API call with a simple success message
    setTimeout(() => {
        showSuccessMessage(isAdd ? 'User added successfully!' : 'User updated successfully!');
        closeModal('userModal');
        
        // In a real application, you would update the UI with the new/updated user
        if (isAdd) {
            // For demo, we can simulate adding a new row to the table
            simulateAddUser(firstName, lastName, email, role, status);
        } else {
            // For demo, we can simulate updating the user in the table
            simulateUpdateUser(firstName, lastName, email, role, status);
        }
    }, 500);
}

// Simulate adding a new user to the table
function simulateAddUser(firstName, lastName, email, role, status) {
    // Get the table body
    const tableBody = document.querySelector('.users-table tbody');
    
    // Create a new row
    const newRow = document.createElement('tr');
    newRow.dataset.role = role;
    newRow.dataset.status = status;
    
    // Set row content
    newRow.innerHTML = `
        <td>
            <div class="user-info">
                <div class="user-avatar">
                    <i class="fas fa-user"></i>
                </div>
                <div class="user-name">
                    <div>${firstName} ${lastName}</div>
                </div>
            </div>
        </td>
        <td>${email}</td>
        <td>
            <span class="role-badge role-${role.toLowerCase()}">${role}</span>
        </td>
        <td>
            <span class="status-badge status-${status.toLowerCase()}">${status}</span>
        </td>
        <td>${getCurrentDate()}</td>
        <td>
            <div class="action-buttons-cell">
                <button class="action-btn edit" title="Edit User">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="action-btn deactivate" title="Deactivate User">
                    <i class="fas fa-user-slash"></i>
                </button>
                <button class="action-btn reset-password" title="Reset Password">
                    <i class="fas fa-key"></i>
                </button>
            </div>
        </td>
    `;
    
    // Add the row to the table
    tableBody.prepend(newRow);
    
    // Update the UI to reflect the new user
    updateUserCountUI(role, 1);
    
    // Re-attach event listeners
    setupTableActions();
}

// Simulate updating a user in the table
function simulateUpdateUser(firstName, lastName, email, role, status) {
    // For a demo, we'll just show that the action would work
    // In a real app, you would find the user row and update it
    console.log('Updating user:', firstName, lastName, 'with role', role, 'and status', status);
}

// Get current date formatted for the table
function getCurrentDate() {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const date = new Date();
    return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
}

// Update user count in status cards
function updateUserCountUI(role, change) {
    let cardSelector;
    
    switch(role) {
        case 'Admin':
            cardSelector = '.status-admin-icon';
            break;
        case 'Architect':
            cardSelector = '.status-architect-icon';
            break;
        case 'Client':
            cardSelector = '.status-client-icon';
            break;
        default:
            return;
    }
    
    const countElement = document.querySelector(`${cardSelector}`).nextElementSibling.querySelector('h3');
    const currentCount = parseInt(countElement.textContent);
    countElement.textContent = (currentCount + change).toString();
}

// Handle Reset Password
function resetPassword() {
    const userName = document.getElementById('resetPasswordUserName').textContent;
    const newPassword = document.getElementById('newPassword').value;
    
    if (!newPassword) {
        alert('Please enter a new password.');
        return;
    }
    
    // Simulate API call
    setTimeout(() => {
        showSuccessMessage(`Password reset successfully for ${userName}!`);
        closeModal('resetPasswordModal');
    }, 500);
}

// Generate Random Password
function generateRandomPassword() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
    let password = '';
    
    // Generate a 10 character password
    for (let i = 0; i < 10; i++) {
        password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    
    // Set the password field
    const passwordField = document.getElementById('newPassword');
    passwordField.value = password;
    
    // Show the password (toggle visibility)
    const eyeIcon = passwordField.nextElementSibling.querySelector('i');
    passwordField.type = 'text';
    eyeIcon.classList.remove('fa-eye');
    eyeIcon.classList.add('fa-eye-slash');
}

// Toggle Password Visibility
function togglePasswordVisibility() {
    const button = this;
    const input = button.parentElement.querySelector('input');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Handle Search
function handleSearch() {
    const searchTerm = this.value.toLowerCase();
    const rows = document.querySelectorAll('.users-table tbody tr');
    
    rows.forEach(row => {
        const name = row.querySelector('.user-name div').textContent.toLowerCase();
        const email = row.querySelector('td:nth-child(2)').textContent.toLowerCase();
        const role = row.dataset.role.toLowerCase();
        
        if (name.includes(searchTerm) || email.includes(searchTerm) || role.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Reset Filters
function resetFilters() {
    const filterInputs = document.querySelectorAll('#filterOptions select, #filterOptions input');
    filterInputs.forEach(input => {
        input.value = '';
    });
    
    // Show all rows
    const rows = document.querySelectorAll('.users-table tbody tr');
    rows.forEach(row => {
        row.style.display = '';
    });
}

// Apply Filters
function applyFilters() {
    const roleFilter = document.getElementById('filter-role').value;
    const statusFilter = document.getElementById('filter-status').value;
    const dateFromFilter = document.getElementById('filter-date-from').value;
    const dateToFilter = document.getElementById('filter-date-to').value;
    
    const rows = document.querySelectorAll('.users-table tbody tr');
    
    rows.forEach(row => {
        let display = true;
        
        // Role filter
        if (roleFilter && row.dataset.role !== roleFilter) {
            display = false;
        }
        
        // Status filter
        if (statusFilter && row.dataset.status !== statusFilter) {
            display = false;
        }
        
        // Date filter (for demo, we'll just display all rows regardless of date)
        // In a real app, you would parse the date from the table and compare
        
        row.style.display = display ? '' : 'none';
    });
    
    // Hide filters after applying
    toggleFilters();
}

// Handle Confirmation Actions
function handleConfirmAction() {
    const action = this.dataset.action;
    const data = this.dataset.data;
    
    // Close confirmation modal
    closeModal('confirmationModal');
    
    // Handle different actions
    switch(action) {
        case 'deactivateUser':
            deactivateUser(data);
            break;
        case 'activateUser':
            activateUser(data);
            break;
        case 'approveUser':
            approveUser(data);
            break;
        case 'rejectUser':
            rejectUser(data);
            break;
        default:
            console.log('Unknown action:', action);
    }
}

// Deactivate User
function deactivateUser(userName) {
    // In a real app, you would call an API
    // For demo, we'll just show a success message
    showSuccessMessage(`User ${userName} has been deactivated.`);
}

// Activate User
function activateUser(userName) {
    // In a real app, you would call an API
    // For demo, we'll just show a success message
    showSuccessMessage(`User ${userName} has been activated.`);
}

// Approve User
function approveUser(userName) {
    // In a real app, you would call an API
    // For demo, we'll just show a success message
    showSuccessMessage(`User ${userName} has been approved.`);
}

// Reject User
function rejectUser(userName) {
    // In a real app, you would call an API
    // For demo, we'll just show a success message
    showSuccessMessage(`User ${userName} has been rejected.`);
}

// Setup Photo Upload
function setupPhotoUpload() {
    const profilePhotoInput = document.getElementById('profilePhoto');
    const photoPreview = document.getElementById('photoPreview');
    const removePhotoBtn = document.getElementById('removePhoto');
    
    if (profilePhotoInput) {
        profilePhotoInput.addEventListener('change', function() {
            const file = this.files[0];
            
            if (file) {
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    photoPreview.innerHTML = `<img src="${e.target.result}" alt="Profile Photo">`;
                };
                
                reader.readAsDataURL(file);
            }
        });
    }
    
    if (removePhotoBtn) {
        removePhotoBtn.addEventListener('click', function() {
            profilePhotoInput.value = '';
            photoPreview.innerHTML = '<i class="fas fa-user"></i>';
        });
    }
}

// Export to PDF
function exportPDF() {
    // In a real app, you would generate a PDF
    // For demo, we'll just show a success message
    showSuccessMessage('User data exported to PDF.');
}

// Export to CSV
function exportCSV() {
    // In a real app, you would generate a CSV
    // For demo, we'll just show a success message
    showSuccessMessage('User data exported to CSV.');
}

// Show Success Message
function showSuccessMessage(message) {
    // In a real app, you would use a toast/notification component
    // For demo, we'll use a simple alert
    alert(message);
}

// Open Modal
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
    }
}

// Close Modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
    }
} 