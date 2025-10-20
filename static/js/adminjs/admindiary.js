// Admin Diary Entry Review JS

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the UI
    initUI();
    
    // Add event listeners
    addEventListeners();
    
    // Parse URL parameters to load specific entry
    loadEntryFromURL();
});

// Initialize UI components
function initUI() {
    // Make all inputs readonly for admin review
    const formInputs = document.querySelectorAll('input, textarea, select');
    formInputs.forEach(input => {
        if (!input.closest('.admin-section')) {
            input.setAttribute('readonly', true);
            input.classList.add('readonly');
        }
    });
    
    // Set the current date in the admin notes if it's empty
    const adminNotes = document.getElementById('adminNotes');
    if (adminNotes && !adminNotes.value.trim()) {
        const today = new Date().toLocaleDateString();
        adminNotes.placeholder = `Admin review notes (${today})...`;
    }
}

// Add event listeners
function addEventListeners() {
    // Back Button
    const backButton = document.getElementById('backButton');
    if (backButton) {
        backButton.addEventListener('click', function() {
            window.location.href = 'admindiaryreviewer.html';
        });
    }
    
    // Request Revision buttons (header and footer)
    const requestRevisionBtns = document.querySelectorAll('#requestRevision, #requestRevisionBtn');
    requestRevisionBtns.forEach(btn => {
        btn.addEventListener('click', openRevisionModal);
    });
    
    // Close Revision Modal button
    const closeRevisionModal = document.getElementById('closeRevisionModal');
    if (closeRevisionModal) {
        closeRevisionModal.addEventListener('click', function() {
            document.getElementById('revisionModal').classList.remove('active');
        });
    }
    
    // Cancel Revision button
    const cancelRevision = document.getElementById('cancelRevision');
    if (cancelRevision) {
        cancelRevision.addEventListener('click', function() {
            document.getElementById('revisionModal').classList.remove('active');
        });
    }
    
    // Submit Revision Request button
    const submitRevisionBtn = document.getElementById('submitRevision');
    if (submitRevisionBtn) {
        submitRevisionBtn.addEventListener('click', submitRevisionRequest);
    }
    
    // Approve Entry buttons (header and footer)
    const approveEntryBtns = document.querySelectorAll('#approveEntry, #approveEntryBtn');
    approveEntryBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            openConfirmModal('approve');
        });
    });
    
    // Close Confirm Modal button
    const closeConfirmModal = document.getElementById('closeConfirmModal');
    if (closeConfirmModal) {
        closeConfirmModal.addEventListener('click', function() {
            document.getElementById('confirmModal').classList.remove('active');
        });
    }
    
    // Cancel Confirm button
    const cancelConfirm = document.getElementById('cancelConfirm');
    if (cancelConfirm) {
        cancelConfirm.addEventListener('click', function() {
            document.getElementById('confirmModal').classList.remove('active');
        });
    }
    
    // Confirm Action button
    const confirmAction = document.getElementById('confirmAction');
    if (confirmAction) {
        confirmAction.addEventListener('click', handleConfirmAction);
    }
    
    // File input change handler to update preview
    const supportingDocs = document.getElementById('supportingDocs');
    if (supportingDocs) {
        supportingDocs.addEventListener('change', updateFileList);
    }
    
    // Admin signature file input
    const adminSignature = document.getElementById('adminSignature');
    if (adminSignature) {
        adminSignature.addEventListener('change', previewAdminSignature);
    }
    
    // Add event listeners to section checkboxes
    const sectionCheckboxes = document.querySelectorAll('input[name="sections"]');
    sectionCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateRevisionImpact);
    });
}

// Load entry from URL parameters
function loadEntryFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const entryId = urlParams.get('entry_id');
    
    if (entryId) {
        // Update entry ID in the UI
        const entryIdElements = document.querySelectorAll('.status-value:first-child');
        entryIdElements.forEach(element => {
            if (element.textContent.includes('SDR-')) {
                element.textContent = entryId;
            }
        });
        
        // In a real application, you would load the entry data from the server using the entryId
        console.log(`Loading entry with ID: ${entryId}`);
        
        // For the demo, we'll simulate loading different data based on entry ID
        simulateLoadEntry(entryId);
    }
}

// Simulate loading an entry based on the ID (for demo purposes)
function simulateLoadEntry(entryId) {
    // This function would be replaced with a real API call in a production environment
    // For now, we'll update the status badge based on the last digit of the entryId
    const lastDigit = entryId.slice(-1);
    const statusValueElement = document.querySelector('.status-value.status-pending');
    
    if (statusValueElement) {
        if (lastDigit === '0') {
            statusValueElement.textContent = 'Needs Revision';
            statusValueElement.className = 'status-value status-revision';
        } else if (lastDigit === '1' || lastDigit === '9') {
            statusValueElement.textContent = 'Approved';
            statusValueElement.className = 'status-value status-approved';
        } else {
            statusValueElement.textContent = 'Pending Review';
            statusValueElement.className = 'status-value status-pending';
        }
    }
}

// Open the revision request modal
function openRevisionModal() {
    // Set current date as default
    const revisionDateInput = document.getElementById('revisionDate');
    if (revisionDateInput) {
        const today = new Date().toISOString().split('T')[0];
        revisionDateInput.value = today;
    }
    
    // Reset form fields
    const revisionForm = document.getElementById('revisionForm');
    if (revisionForm) {
        revisionForm.reset();
    }
    
    // Clear any previous file previews
    const adminSignaturePreview = document.getElementById('adminSignaturePreview');
    if (adminSignaturePreview) {
        adminSignaturePreview.innerHTML = '<i class="fas fa-signature"></i><span>No signature selected</span>';
    }
    
    // Show the modal
    document.getElementById('revisionModal').classList.add('active');
}

// Submit revision request
function submitRevisionRequest(e) {
    e.preventDefault();
    
    // Get form data
    const revisionDate = document.getElementById('revisionDate').value;
    const revisionType = document.getElementById('revisionType').value;
    const revisionImpact = document.getElementById('revisionImpact').value;
    const revisionDescription = document.getElementById('revisionDescription').value;
    const adminName = document.getElementById('adminName').value;
    
    // Validate required fields
    if (!revisionDate || !revisionType || !revisionImpact || !revisionDescription || !adminName) {
        alert('Please fill in all required fields.');
        return;
    }
    
    // Check if at least one section is selected
    const selectedSections = document.querySelectorAll('input[name="sections"]:checked');
    if (selectedSections.length === 0) {
        alert('Please select at least one section requiring revision.');
        return;
    }
    
    // Check if admin signature is uploaded
    const adminSignature = document.getElementById('adminSignature');
    if (adminSignature && !adminSignature.files.length) {
        alert('Please upload your signature.');
        return;
    }
    
    // In a real application, you would submit the form data to the server
    // For the demo, we'll just close the modal and update the status
    document.getElementById('revisionModal').classList.remove('active');
    
    // Show confirmation modal
    openConfirmModal('revision-submitted');
}

// Open confirm modal
function openConfirmModal(action) {
    const confirmTitle = document.getElementById('confirmTitle');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmAction = document.getElementById('confirmAction');
    
    if (action === 'approve') {
        confirmTitle.innerHTML = '<i class="fas fa-check-circle"></i> Approve Entry';
        confirmMessage.textContent = 'Are you sure you want to approve this diary entry? This will mark it as verified and accessible in reports.';
        confirmAction.textContent = 'Approve Entry';
        confirmAction.dataset.action = 'approve';
    } else if (action === 'revision-submitted') {
        confirmTitle.innerHTML = '<i class="fas fa-history"></i> Revision Requested';
        confirmMessage.textContent = 'Your revision request has been submitted successfully. The architect will be notified to make the requested changes.';
        confirmAction.textContent = 'Return to Review List';
        confirmAction.dataset.action = 'return-to-list';
    } else if (action === 'approved') {
        confirmTitle.innerHTML = '<i class="fas fa-check-circle"></i> Entry Approved';
        confirmMessage.textContent = 'This diary entry has been approved successfully. It is now available in reports and analytics.';
        confirmAction.textContent = 'Return to Review List';
        confirmAction.dataset.action = 'return-to-list';
    }
    
    document.getElementById('confirmModal').classList.add('active');
}

// Handle confirm action button click
function handleConfirmAction() {
    const action = this.dataset.action;
    
    if (action === 'approve') {
        // In a real application, you would send approval to the server
        // For the demo, we'll just show a success confirmation
        document.getElementById('confirmModal').classList.remove('active');
        
        // Update the entry status in the UI
        const statusValueElement = document.querySelector('.status-value');
        if (statusValueElement) {
            statusValueElement.textContent = 'Approved';
            statusValueElement.className = 'status-value status-approved';
        }
        
        // Show the approval confirmation
        setTimeout(() => {
            openConfirmModal('approved');
        }, 500);
    } else if (action === 'return-to-list') {
        // Navigate back to the review list
        window.location.href = 'admindiaryreviewer.html';
    }
}

// Update file list preview when files are selected
function updateFileList() {
    const fileInput = this;
    const fileCount = fileInput.files.length;
    
    if (fileCount > 0) {
        let fileListHtml = `<div class="file-list-preview">`;
        fileListHtml += `<strong>${fileCount} file(s) selected:</strong><ul>`;
        
        for (let i = 0; i < fileCount; i++) {
            const file = fileInput.files[i];
            fileListHtml += `<li>${file.name} (${formatFileSize(file.size)})</li>`;
        }
        
        fileListHtml += `</ul></div>`;
        
        // Add the file list after the input
        const fileListContainer = document.createElement('div');
        fileListContainer.className = 'file-list-container';
        fileListContainer.innerHTML = fileListHtml;
        
        // Remove any existing file list
        const existingFileList = fileInput.parentNode.querySelector('.file-list-container');
        if (existingFileList) {
            existingFileList.remove();
        }
        
        fileInput.parentNode.appendChild(fileListContainer);
    }
}

// Preview admin signature when selected
function previewAdminSignature() {
    const fileInput = this;
    const previewElement = document.getElementById('adminSignaturePreview');
    
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            previewElement.innerHTML = `<img src="${e.target.result}" alt="Admin Signature">`;
        };
        
        reader.readAsDataURL(fileInput.files[0]);
    } else {
        previewElement.innerHTML = '<i class="fas fa-signature"></i><span>No signature selected</span>';
    }
}

// Update revision impact based on selected sections
function updateRevisionImpact() {
    const selectedSections = document.querySelectorAll('input[name="sections"]:checked');
    const impactSelect = document.getElementById('revisionImpact');
    
    if (selectedSections.length >= 5) {
        impactSelect.value = 'major';
    } else if (selectedSections.length >= 2) {
        impactSelect.value = 'moderate';
    } else if (selectedSections.length === 1) {
        impactSelect.value = 'minor';
    }
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes < 1024) {
        return bytes + ' bytes';
    } else if (bytes < 1048576) {
        return (bytes / 1024).toFixed(1) + ' KB';
    } else {
        return (bytes / 1048576).toFixed(1) + ' MB';
    }
}

// Add CSS styles for UI elements
function addCustomStyles() {
    const style = document.createElement('style');
    style.textContent = `
        .file-list-preview {
            margin-top: 10px;
            padding: 10px;
            background-color: #f5f5f5;
            border-radius: 4px;
            font-size: 14px;
        }
        
        .file-list-preview ul {
            margin-top: 5px;
            padding-left: 20px;
        }
        
        .status-value.status-pending {
            color: #2196f3;
            font-weight: bold;
        }
        
        .status-value.status-approved {
            color: #4caf50;
            font-weight: bold;
        }
        
        .status-value.status-revision {
            color: #ff9800;
            font-weight: bold;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.active {
            display: flex;
        }
    `;
    document.head.appendChild(style);
}

// Call the function to add custom styles
addCustomStyles(); 