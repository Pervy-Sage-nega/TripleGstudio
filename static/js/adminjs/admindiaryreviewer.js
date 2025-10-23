// Admin Diary Reviewer JS

document.addEventListener('DOMContentLoaded', function() {
    console.log('AdminDiaryReviewer JS loaded');
    
    // Initialize UI
    initUI();
    
    // Add event listeners
    addEventListeners();
    
    // Load filters from URL
    loadFiltersFromURL();
});

function loadFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    
    if (params.get('architect')) document.getElementById('filter-architect').value = params.get('architect');
    if (params.get('project')) document.getElementById('filter-project').value = params.get('project');
    if (params.get('status')) document.getElementById('filter-status').value = params.get('status');
    if (params.get('date_from')) document.getElementById('filter-date-from').value = params.get('date_from');
    if (params.get('date_to')) document.getElementById('filter-date-to').value = params.get('date_to');
    if (params.get('search')) document.getElementById('search').value = params.get('search');
}

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
    // Export buttons - attach immediately
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    const printBtn = document.getElementById('printBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    console.log('Export buttons found:', {
        exportPdfBtn: !!exportPdfBtn,
        exportCsvBtn: !!exportCsvBtn,
        printBtn: !!printBtn,
        refreshBtn: !!refreshBtn
    });
    
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('PDF export clicked');
            exportPdf();
        });
    }
    
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('CSV export clicked');
            exportCsv();
        });
    }
    
    if (printBtn) {
        printBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('Print clicked');
            printData();
        });
    }
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    // View toggle buttons
    const historyModeBtn = document.getElementById('historyModeBtn');
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
    
    if (historyModeBtn) {
        historyModeBtn.addEventListener('click', function() {
            toggleHistoryMode();
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
        // Remove any existing listeners to prevent duplicates
        button.removeEventListener('click', handleViewEntry);
        button.addEventListener('click', handleViewEntry);
    });
    
    // Individual export buttons
    const exportBtns = document.querySelectorAll('.action-btn.export');
    exportBtns.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const entryId = this.closest('tr')?.querySelector('.view-entry-btn')?.getAttribute('data-entry-id') ||
                           this.closest('.timeline-item')?.querySelector('.view-entry-btn')?.getAttribute('data-entry-id');
            if (entryId) {
                exportSingleEntry(entryId);
            }
        });
    });
}

function handleViewEntry() {
    const entryId = this.getAttribute('data-entry-id');
    viewEntryDetails(entryId);
}

    
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
        document.getElementById('exportPdfBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('PDF export clicked');
        exportPdf();
    });
    document.getElementById('exportCsvBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('CSV export clicked');
        exportCsv();
    });
    document.getElementById('refreshBtn')?.addEventListener('click', refreshData);
    document.getElementById('printBtn')?.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('Print clicked');
        printData();
    });
    
    // Approval form submissions
    const approvalForms = document.querySelectorAll('form[method="post"]');
    approvalForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const action = this.querySelector('input[name="action"]').value;
            if (action === 'approve') {
                if (!confirm('Are you sure you want to approve this diary entry?')) {
                    e.preventDefault();
                }
            }
        });
    });
    
    // Pagination buttons
    const paginationBtns = document.querySelectorAll('.page-btn');
    paginationBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.classList.contains('disabled') || this.classList.contains('active')) {
                e.preventDefault();
                return;
            }
        });
    });


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

function exportPdf() {
    console.log('exportPdf function called');
    // Get current filters to pass to print layout
    const params = new URLSearchParams(window.location.search);
    const printUrl = '/diary/admin/print-layout/?' + params.toString();
    console.log('Opening URL:', printUrl);
    window.open(printUrl, '_blank');
}

function exportCsv() {
    // Simple CSV export of visible table data
    const table = document.querySelector('.entries-table');
    if (!table) return;
    
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            // Skip action column
            if (!col.querySelector('.table-actions')) {
                rowData.push('"' + col.textContent.trim().replace(/"/g, '""') + '"');
            }
        });
        if (rowData.length > 0) {
            csv.push(rowData.join(','));
        }
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'diary_entries.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

function refreshData() {
    window.location.reload();
}

function printData() {
    // Get current filters to pass to print layout
    const params = new URLSearchParams(window.location.search);
    const printUrl = '/diary/admin/print-layout/?' + params.toString();
    window.open(printUrl, '_blank');
}

function applyFilters() {
    // Get filter values
    const architect = document.getElementById('filter-architect').value;
    const project = document.getElementById('filter-project').value;
    const status = document.getElementById('filter-status').value;
    const dateFrom = document.getElementById('filter-date-from').value;
    const dateTo = document.getElementById('filter-date-to').value;
    const searchTerm = document.getElementById('search').value;
    
    // Build query parameters
    const params = new URLSearchParams();
    if (architect) params.append('architect', architect);
    if (project) params.append('project', project);
    if (status) params.append('status', status);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);
    if (searchTerm) params.append('search', searchTerm);
    
    // Reload page with filters
    window.location.href = window.location.pathname + '?' + params.toString();
}

let isLoadingModal = false;

function viewEntryDetails(entryId) {
    // Prevent multiple simultaneous calls
    if (isLoadingModal) return;
    isLoadingModal = true;
    
    const modal = document.getElementById('entryModal');
    const modalBody = document.getElementById('modalBody');
    const modalTitle = document.getElementById('modalTitle');
    
    // Show modal with loading state
    modal.style.display = 'block';
    modalTitle.innerHTML = '<i class="fas fa-book-open"></i> Entry Details';
    modalBody.innerHTML = '<div class="admin-diary-loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>';
    document.getElementById('modalFooter').style.display = 'none';
    
    // Fetch entry details
    fetch(`/diary/admin/diary-entry/${entryId}/`)
        .then(response => response.json())
        .then(data => {
            isLoadingModal = false;
            if (data.error) {
                modalBody.innerHTML = `<div class="error">Error: ${data.error}</div>`;
                return;
            }
            
            // Add fallback values for missing data
            data.draft = data.draft || false;
            data.photos_taken = data.photos_taken || false;
            data.subcontractor_count = data.subcontractor_count || 0;
            data.labor_entries = data.labor_entries || [];
            data.material_entries = data.material_entries || [];
            data.equipment_entries = data.equipment_entries || [];
            data.delay_entries = data.delay_entries || [];
            data.visitor_entries = data.visitor_entries || [];
            data.subcontractor_entries = data.subcontractor_entries || [];
            
            modalTitle.innerHTML = `<i class="fas fa-book-open"></i> ${data.project_name} - ${data.entry_date}`;
            modalBody.innerHTML = `
                <div class="entry-details">
                    <div class="section-header">
                        <i class="fas fa-info-circle"></i>
                        Basic Information
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-building"></i> Project:</label>
                        <span>${data.project_name}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-calendar"></i> Date:</label>
                        <span>${data.entry_date}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-user"></i> Created By:</label>
                        <span>${data.created_by}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-flag"></i> Status:</label>
                        <span class="status-badge">${data.status}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-save"></i> Draft:</label>
                        <span>${data.draft ? 'Yes' : 'No'}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-camera"></i> Photos Taken:</label>
                        <span>${data.photos_taken ? 'Yes' : 'No'}</span>
                    </div>
                    
                    <div class="section-header">
                        <i class="fas fa-tasks"></i>
                        Progress & Work Details
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-percentage"></i> Progress:</label>
                        <span>${data.progress_percentage}%</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-milestone"></i> Milestone:</label>
                        <span>${data.milestone}</span>
                    </div>
                    <div class="detail-item full-width">
                        <label><i class="fas fa-tasks"></i> Work Description:</label>
                        <p>${data.work_description || 'No description provided'}</p>
                    </div>
                    
                    <div class="section-header">
                        <i class="fas fa-cloud-sun"></i>
                        Weather Conditions
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-cloud-sun"></i> Weather:</label>
                        <span>${data.weather_condition || 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-thermometer-half"></i> Temperature:</label>
                        <span>${data.temperature_high ? data.temperature_high + '°C' : 'N/A'} / ${data.temperature_low ? data.temperature_low + '°C' : 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-tint"></i> Humidity:</label>
                        <span>${data.humidity ? data.humidity + '%' : 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-wind"></i> Wind Speed:</label>
                        <span>${data.wind_speed ? data.wind_speed + ' km/h' : 'N/A'}</span>
                    </div>
                    
                    ${data.quality_issues || data.safety_incidents || data.general_notes ? '<hr class="section-divider">' : ''}
                    
                    ${data.quality_issues ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-exclamation-triangle"></i> Quality Issues:</label>
                        <p>${data.quality_issues}</p>
                    </div>
                    ` : ''}
                    ${data.safety_incidents ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-shield-alt"></i> Safety Incidents:</label>
                        <p>${data.safety_incidents}</p>
                    </div>
                    ` : ''}
                    ${data.general_notes ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-sticky-note"></i> General Notes:</label>
                        <p>${data.general_notes}</p>
                    </div>
                    ` : ''}
                    
                    <div class="section-header">
                        <i class="fas fa-dollar-sign"></i>
                        Budget Information
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-dollar-sign"></i> Project Budget:</label>
                        <span>₱${data.project_budget.toLocaleString()}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-credit-card"></i> Total Spent:</label>
                        <span>₱${data.total_spent.toLocaleString()}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-piggy-bank"></i> Remaining:</label>
                        <span style="color: ${data.remaining_budget >= 0 ? '#28a745' : '#dc3545'}">₱${data.remaining_budget.toLocaleString()}</span>
                    </div>
                    
                    <div class="section-header">
                        <i class="fas fa-list-alt"></i>
                        Detailed Entry Information
                    </div>
                    ${data.labor_entries && data.labor_entries.length > 0 ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-users"></i> Labor Entries (${data.labor_entries.length}):</label>
                        <div class="entry-list">
                            ${data.labor_entries.map(labor => `
                                <div class="entry-item">
                                    <strong>${labor.trade_description}</strong> - ${labor.workers_count} workers, ${labor.hours_worked}h
                                    <br><small>Type: ${labor.labor_type} | Rate: ₱${labor.hourly_rate || 'N/A'}/hr</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.material_entries && data.material_entries.length > 0 ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-boxes"></i> Material Entries (${data.material_entries.length}):</label>
                        <div class="entry-list">
                            ${data.material_entries.map(material => `
                                <div class="entry-item">
                                    <strong>${material.material_name}</strong> - ${material.quantity_delivered} ${material.unit}
                                    <br><small>Used: ${material.quantity_used} ${material.unit} | Supplier: ${material.supplier || 'N/A'}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.equipment_entries && data.equipment_entries.length > 0 ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-tools"></i> Equipment Entries (${data.equipment_entries.length}):</label>
                        <div class="entry-list">
                            ${data.equipment_entries.map(equipment => `
                                <div class="entry-item">
                                    <strong>${equipment.equipment_name}</strong> (${equipment.equipment_type})
                                    <br><small>Operator: ${equipment.operator_name || 'N/A'} | Hours: ${equipment.hours_operated}h | Status: ${equipment.status}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.delay_entries && data.delay_entries.length > 0 ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-clock"></i> Delay Entries (${data.delay_entries.length}):</label>
                        <div class="entry-list">
                            ${data.delay_entries.map(delay => `
                                <div class="entry-item">
                                    <strong>${delay.category}</strong> - ${delay.duration_hours}h delay
                                    <br><small>Impact: ${delay.impact_level} | ${delay.description}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.visitor_entries && data.visitor_entries.length > 0 ? `
                    <div class="detail-item full-width">
                        <label><i class="fas fa-user-friends"></i> Visitor Entries (${data.visitor_entries.length}):</label>
                        <div class="entry-list">
                            ${data.visitor_entries.map(visitor => `
                                <div class="entry-item">
                                    <strong>${visitor.visitor_name}</strong> (${visitor.company || 'N/A'})
                                    <br><small>Type: ${visitor.visitor_type} | Purpose: ${visitor.purpose_of_visit}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    ${data.subcontractor_entries && data.subcontractor_entries.length > 0 ? `
                    <hr class="section-divider">
                    <div class="detail-item full-width">
                        <label><i class="fas fa-building"></i> Subcontractor Work:</label>
                        <div class="subcontractor-list">
                            ${data.subcontractor_entries.map(sub => `
                                <div class="subcontractor-item">
                                    <strong>${sub.company_name}</strong> - ₱${sub.daily_cost.toLocaleString()}
                                    <br><small>${sub.work_description}</small>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="section-header">
                        <i class="fas fa-user-check"></i>
                        Review Information
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-user-check"></i> Reviewed By:</label>
                        <span>${data.reviewed_by}</span>
                    </div>
                    <div class="detail-item">
                        <label><i class="fas fa-clock"></i> Review Date:</label>
                        <span>${data.reviewed_date}</span>
                    </div>
                </div>
            `;
            
            // Add footer buttons
            const modalFooter = document.getElementById('modalFooter');
            modalFooter.innerHTML = `
                <button class="btn btn-success" onclick="updateEntryStatus(${data.id}, 'reviewed')">
                    <i class="fas fa-check"></i> Mark as Reviewed
                </button>
                <button class="btn btn-warning" onclick="updateEntryStatus(${data.id}, 'needs_revision')">
                    <i class="fas fa-edit"></i> Send for Revision
                </button>
            `;
            modalFooter.style.display = 'flex';
        })
        .catch(error => {
            isLoadingModal = false;
            modalBody.innerHTML = `<div class="error">Error loading entry details: ${error.message}</div>`;
        });
    
    // Close modal functionality
    const closeBtn = modal.querySelector('.close');
    closeBtn.onclick = function() {
        modal.style.display = 'none';
        isLoadingModal = false;
    };
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
            isLoadingModal = false;
        }
    };
}

function updateEntryStatus(entryId, action) {
    const formData = new FormData();
    formData.append('action', action);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        formData.append('csrfmiddlewaretoken', csrfToken.value);
    }
    
    fetch(`/diary/admin/update-entry-status/${entryId}/`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (action === 'needs_revision') {
                // Send to site manager and update timeline
                sendToSiteManager(entryId, data.project_name);
                updateTimelineHeader(entryId, 'revision');
            }
            document.getElementById('entryModal').style.display = 'none';
            window.location.reload();
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        alert('Error updating entry status: ' + error.message);
    });
}

function sendToSiteManager(entryId, projectName) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    const headers = {
        'Content-Type': 'application/json'
    };
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken.value;
    }
    
    fetch('/diary/admin/send-revision/', {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            entry_id: entryId,
            project_name: projectName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Revision Sent', `Entry sent to site manager for revision`, 'warning');
        }
    });
}

function updateTimelineHeader(entryId, status) {
    const timelineItem = document.querySelector(`.timeline-header[data-id="${entryId}"]`);
    if (timelineItem) {
        const statusBadge = timelineItem.querySelector('.status-badge');
        if (statusBadge) {
            statusBadge.className = 'status-badge status-revision-badge';
            statusBadge.textContent = 'Needs Revision';
        }
        timelineItem.closest('.timeline-item').className = 'timeline-item status-revision';
    }
}

function toggleHistoryMode() {
    const historyModeBtn = document.getElementById('historyModeBtn');
    const approvalButtons = document.querySelectorAll('.btn-success, .action-btn.approve');
    const isHistoryMode = historyModeBtn.classList.contains('active');
    
    if (isHistoryMode) {
        // Exit history mode
        historyModeBtn.classList.remove('active');
        approvalButtons.forEach(btn => {
            btn.style.display = 'inline-block';
        });
        document.querySelector('.section-title').innerHTML = '<i class="fas fa-list"></i> Submitted Diary Entries';
    } else {
        // Enter history mode
        historyModeBtn.classList.add('active');
        approvalButtons.forEach(btn => {
            btn.style.display = 'none';
        });
        document.querySelector('.section-title').innerHTML = '<i class="fas fa-history"></i> Diary Entries History (Read-Only)';
    }
}

function navigateToPage(pageNumber) {
    // Get current filter parameters
    const params = new URLSearchParams(window.location.search);
    
    // Update page parameter
    params.set('page', pageNumber);
    
    // Navigate to new page with filters preserved
    window.location.href = window.location.pathname + '?' + params.toString();
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

function exportSingleEntry(entryId) {
    const printUrl = `/diary/admin/print-layout/?entry_id=${entryId}`;
    window.open(printUrl, '_blank');
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