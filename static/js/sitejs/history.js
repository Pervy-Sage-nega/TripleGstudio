document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const timelineViewBtn = document.getElementById('timelineViewBtn');
    const tableViewBtn = document.getElementById('tableViewBtn');
    const timelineView = document.getElementById('timelineView');
    const tableView = document.getElementById('tableView');
    const filterToggle = document.getElementById('filterToggle');
    const filterOptions = document.getElementById('filterOptions');
    const searchInput = document.querySelector('.search-input');
    const resetFiltersBtn = document.getElementById('resetFilters');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    const viewEntryModal = document.getElementById('viewEntryModal');
    const closeViewModal = document.getElementById('closeViewModal');
    const modalContent = document.getElementById('modalContent');
    const style = document.createElement('style');
style.textContent = `
/* Webkit browsers (Chrome, Safari, newer versions of Opera) */
::-webkit-scrollbar {
width: 5px;
background-color: transparent;
}

::-webkit-scrollbar-track {
background-color: transparent;
border-radius: 5px;
}

::-webkit-scrollbar-thumb {
background-color: rgba(255, 255, 255, 0);
border-radius: 5px;
border: 2px solid transparent;
background-clip: content-box;
transition: background-color 0.3s;
}

::-webkit-scrollbar-thumb:hover {
background-color: rgba(255, 255, 255, 0);
}

/* For Firefox */
* {
scrollbar-width: thin;
scrollbar-color: rgba(255, 255, 255, 0.2) transparent;
}

/* Hide scrollbar when not scrolling (optional) */
body:not(:hover)::-webkit-scrollbar-thumb {
background-color: rgba(255, 255, 255, 0);
}
`;
document.head.appendChild(style);


// ===== SMOOTH SCROLLING CORE IMPLEMENTATION =====
let isScrolling = false;
let lastScrollTime = 0;
const SCROLL_THROTTLE_TIME = 100;

// Unified easing function
function easeInOutCubic(t) {
return t < 0.5 ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
}

function smoothScrollTo(targetPosition, duration = 10000) {
if (isScrolling) return;
isScrolling = true;

const startPosition = window.pageYOffset;
const distance = targetPosition - startPosition;
const startTime = performance.now();

function animate(currentTime) {
const elapsed = currentTime - startTime;
const progress = Math.min(elapsed / duration, 1);
const easedProgress = easeInOutCubic(progress);

window.scrollTo(0, startPosition + distance * easedProgress);

if (progress < 1) {
    requestAnimationFrame(animate);
} else {
    isScrolling = false;
}
}

requestAnimationFrame(animate);
}

// ===== EVENT HANDLERS =====
function handleWheel(e) {
if (Date.now() - lastScrollTime < SCROLL_THROTTLE_TIME) return;
lastScrollTime = Date.now();

if (Math.abs(e.deltaY) < 20) return;

e.preventDefault();

const direction = Math.sign(e.deltaY);
const pageHeight = window.innerHeight;
const targetPosition = Math.max(0, 
Math.min(document.documentElement.scrollHeight - pageHeight,
window.pageYOffset + (direction * pageHeight))
);

smoothScrollTo(targetPosition, 800);
}

function handleKeyboard(e) {
let targetPosition;
const currentPosition = window.pageYOffset;
const pageHeight = window.innerHeight;
const docHeight = document.documentElement.scrollHeight;

switch(e.key) {
case 'ArrowDown':
    targetPosition = currentPosition + pageHeight * 0.25;
    break;
case 'ArrowUp':
    targetPosition = currentPosition - pageHeight * 0.25;
    break;
case 'PageDown':
    targetPosition = currentPosition + pageHeight * 0.9;
    break;
case 'PageUp':
    targetPosition = currentPosition - pageHeight * 0.9;
    break;
case 'Home':
    targetPosition = 0;
    break;
case 'End':
    targetPosition = docHeight - pageHeight;
    break;
default:
    return;
}

e.preventDefault();
targetPosition = Math.max(0, Math.min(docHeight - pageHeight, targetPosition));
smoothScrollTo(targetPosition, 700);
}

// ===== ANCHOR LINK HANDLING =====
function handleAnchorClick(e) {
e.preventDefault();
const targetId = this.hash;
if (!targetId || targetId === '#') return;

const targetElement = document.querySelector(targetId);
if (!targetElement) return;

const navbar = document.querySelector('.navbar');
const navbarHeight = navbar ? navbar.offsetHeight : 0;
const targetPosition = targetElement.getBoundingClientRect().top + 
                 window.pageYOffset - 
                 (navbarHeight + 20); // 20px buffer

smoothScrollTo(targetPosition, 1000);

// Update URL without jumping
history.replaceState(null, null, targetId);
}

// ===== INITIALIZATION =====
function initSmoothScroll() {
// Event Listeners
window.addEventListener('wheel', handleWheel, { passive: false });
window.addEventListener('keydown', handleKeyboard);
window.addEventListener('scrollend', () => isScrolling = false);

// Anchor Links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
anchor.addEventListener('click', handleAnchorClick);
});

// Mobile Menu Integration
const mobileMenu = document.getElementById('navLinks');
if (mobileMenu) {
document.addEventListener('click', (e) => {
    if (mobileMenu.classList.contains('active') && 
        !e.target.closest('.navbar')) {
        mobileMenu.classList.remove('active');
    }
});
}
}

document.addEventListener("DOMContentLoaded", initSmoothScroll);
    
    if(mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Toggle View (Timeline/Table)
    if(timelineViewBtn && tableViewBtn) {
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
    
    // Toggle Filter Options
    if(filterToggle) {
        filterToggle.addEventListener('click', function() {
            const isVisible = filterOptions.style.display === 'block';
            filterOptions.style.display = isVisible ? 'none' : 'block';
            filterToggle.querySelector('span').textContent = isVisible ? 'Show Filters' : 'Hide Filters';
            filterToggle.querySelector('i').classList.toggle('fa-chevron-down');
            filterToggle.querySelector('i').classList.toggle('fa-chevron-up');
        });
    }
    
    // Mobile Menu Toggle
    if(mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
            mobileMenuBtn.querySelector('i').classList.toggle('fa-bars');
            mobileMenuBtn.querySelector('i').classList.toggle('fa-times');
        });
    }
    
    // Expand/Collapse Timeline Items
    const expandButtons = document.querySelectorAll('.expand');
    expandButtons.forEach(button => {
        button.addEventListener('click', function() {
            const header = this.closest('.timeline-header');
            const contentId = header.getAttribute('data-id');
            const content = document.getElementById(`content${contentId}`);
            
            // Toggle the active class on the content
            content.classList.toggle('active');
            
            // Toggle the icon
            this.querySelector('i').classList.toggle('fa-chevron-down');
            this.querySelector('i').classList.toggle('fa-chevron-up');
        });
    });
    
    // Search Functionality
    if(searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            // Search in timeline view
            const timelineItems = document.querySelectorAll('.timeline-item');
            timelineItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                item.style.display = text.includes(searchTerm) ? 'block' : 'none';
            });
            
            // Search in table view
            const tableRows = document.querySelectorAll('tbody tr');
            tableRows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }
    
    // Reset Filters
    if(resetFiltersBtn) {
        resetFiltersBtn.addEventListener('click', function() {
            document.querySelectorAll('#filterOptions select, #filterOptions input').forEach(el => {
                el.value = '';
            });
            
            // Reset search and display all items
            if(searchInput) searchInput.value = '';
            
            document.querySelectorAll('.timeline-item').forEach(item => {
                item.style.display = 'block';
            });
            
            document.querySelectorAll('tbody tr').forEach(row => {
                row.style.display = '';
            });
        });
    }
    
    // Apply Filters
    if(applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const project = document.getElementById('filter-project').value.toLowerCase();
            const dateFrom = document.getElementById('filter-date-from').value;
            const dateTo = document.getElementById('filter-date-to').value;
            const weather = document.getElementById('filter-weather').value.toLowerCase();
            const personnel = document.getElementById('filter-personnel').value.toLowerCase();
            
            // Filter timeline items
            document.querySelectorAll('.timeline-item').forEach(item => {
                let show = true;
                const itemProject = item.querySelector('h3').textContent.toLowerCase();
                const itemDate = item.querySelector('.timeline-date span').textContent;
                const itemWeather = item.querySelector('.weather-detail:nth-child(2) span').textContent.toLowerCase();
                const itemPersonnel = item.querySelector('.info-value:nth-child(4)').textContent.toLowerCase();
                
                if (project && !itemProject.includes(project)) show = false;
                if (weather && !itemWeather.includes(weather)) show = false;
                if (personnel && !itemPersonnel.includes(personnel)) show = false;
                
                // Date filtering would need conversion to Date objects for proper comparison
                
                item.style.display = show ? 'block' : 'none';
            });
            
            // Similar filtering for table rows
            document.querySelectorAll('tbody tr').forEach(row => {
                let show = true;
                const rowProject = row.querySelector('.table-project-name').textContent.toLowerCase();
                const rowWeather = row.querySelector('.table-weather span').textContent.toLowerCase();
                
                if (project && !rowProject.includes(project)) show = false;
                if (weather && !rowWeather.includes(weather)) show = false;
                
                row.style.display = show ? '' : 'none';
            });
        });
    }
    
    // View Details in Modal (from Table View)
    document.querySelectorAll('.table-actions .view').forEach(btn => {
        btn.addEventListener('click', function() {
            const row = this.closest('tr');
            const projectName = row.querySelector('.table-project-name').textContent;
            
            // Find the matching timeline item to display in modal
            const timelineItems = document.querySelectorAll('.timeline-item');
            timelineItems.forEach(item => {
                const itemProjectName = item.querySelector('h3').textContent;
                if (itemProjectName === projectName) {
                    // Clone the content for the modal
                    const contentClone = item.querySelector('.timeline-content').cloneNode(true);
                    contentClone.classList.add('active'); // Ensure it's visible in the modal
                    contentClone.style.maxHeight = 'none'; // Remove max-height restriction
                    
                    // Insert into modal
                    modalContent.innerHTML = '';
                    modalContent.appendChild(contentClone);
                    viewEntryModal.style.display = 'flex';
                }
            });
        });
    });
    
    // Close Modal
    if(closeViewModal) {
        closeViewModal.addEventListener('click', function() {
            viewEntryModal.style.display = 'none';
        });
        
        // Close modal when clicking outside the content
        window.addEventListener('click', function(event) {
            if (event.target === viewEntryModal) {
                viewEntryModal.style.display = 'none';
            }
        });
    }
    
    // Revision Modal Functionality
    const revisionModal = document.getElementById('revisionModal');
    const closeRevisionModal = document.getElementById('closeRevisionModal');
    const cancelRevision = document.getElementById('cancelRevision');
    const revisionForm = document.getElementById('revisionForm');
    const clientSignature = document.getElementById('clientSignature');
    const teamPhoto = document.getElementById('teamPhoto');
    const clientSignaturePreview = document.getElementById('clientSignaturePreview');
    const teamPhotoPreview = document.getElementById('teamPhotoPreview');
    let currentProjectName = '';

    // Open revision modal when clicking 'Add Revision' buttons
    document.querySelectorAll('.revision').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            // Get project name from either timeline or table view
            currentProjectName = this.closest('.timeline-item') 
                ? this.closest('.timeline-item').querySelector('h3').textContent
                : this.closest('tr').querySelector('.table-project-name').textContent;
            
            // Show the modal
            revisionModal.style.display = 'flex';
            
            // Reset form fields
            revisionForm.reset();
            clientSignaturePreview.innerHTML = '<i class="fas fa-signature"></i><span>No image selected</span>';
            teamPhotoPreview.innerHTML = '<i class="fas fa-users"></i><span>No image selected</span>';
        });
    });

    // Close revision modal
    if(closeRevisionModal) {
        closeRevisionModal.addEventListener('click', function() {
            revisionModal.style.display = 'none';
        });
    }

    // Cancel button closes the modal
    if(cancelRevision) {
        cancelRevision.addEventListener('click', function() {
            revisionModal.style.display = 'none';
        });
    }

    // Close revision modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === revisionModal) {
            revisionModal.style.display = 'none';
        }
    });

    // Handle client signature file preview
    if(clientSignature) {
        clientSignature.addEventListener('change', function() {
            handleFilePreview(this, clientSignaturePreview);
        });
    }

    // Handle team photo file preview
    if(teamPhoto) {
        teamPhoto.addEventListener('change', function() {
            handleFilePreview(this, teamPhotoPreview);
        });
    }

    // File preview helper function
    function handleFilePreview(input, previewElement) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            
            reader.onload = function(e) {
                previewElement.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Handle revision form submission
    if(revisionForm) {
        revisionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const revisionDescription = document.getElementById('revisionDescription').value;
            const clientName = document.getElementById('clientName').value;
            
            // In a real application, you would submit this data to your server
            // For demo purposes, show a success message
            alert(`Revision for ${currentProjectName} submitted successfully!\n\nRevision details submitted:\n- Description: ${revisionDescription}\n- Client: ${clientName}\n- Signature and team photo would be uploaded to server`);
            
            // Close the modal
            revisionModal.style.display = 'none';
        });
    }
    
    // Edit Entry
    document.querySelectorAll('.edit').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const projectName = this.closest('.timeline-item') 
                ? this.closest('.timeline-item').querySelector('h3').textContent
                : this.closest('tr').querySelector('.table-project-name').textContent;
                
            // In a real application, you would redirect to the edit page or open an edit modal
            alert(`Editing entry for ${projectName}. This would open the edit form in a real application.`);
        });
    });
    
    // Download PDF
    document.querySelectorAll('.download').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const projectName = this.closest('.timeline-item') 
                ? this.closest('.timeline-item').querySelector('h3').textContent
                : this.closest('tr').querySelector('.table-project-name').textContent;
                
            // In a real application, you would generate and download a PDF
            alert(`Generating PDF for ${projectName}. This would download a PDF in a real application.`);
        });
    });
    
    // Pagination Controls
    const paginationButtons = document.querySelectorAll('.pagination .page-btn');
    paginationButtons.forEach(btn => {
        if (!btn.classList.contains('disabled')) {
            btn.addEventListener('click', function() {
                // Remove active class from all buttons
                paginationButtons.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // In a real application, you would fetch and display the next page of data
                // For this demo, we'll just show a message
                if (!this.classList.contains('active')) {
                    alert('In a real application, this would load page ' + this.textContent);
                }
            });
        }
    });
    
    // Expand all button functionality (could be added to the UI)
    function addExpandAllButton() {
        const headerSection = document.querySelector('.page-header');
        if (!headerSection) return;
        
        const expandAllBtn = document.createElement('button');
        expandAllBtn.className = 'btn btn-text';
        expandAllBtn.innerHTML = '<i class="fas fa-expand-alt"></i> Expand All';
        expandAllBtn.addEventListener('click', function() {
            const allContents = document.querySelectorAll('.timeline-content');
            const isAnyCollapsed = Array.from(allContents).some(content => !content.classList.contains('active'));
            
            allContents.forEach(content => {
                if (isAnyCollapsed) {
                    content.classList.add('active');
                } else {
                    content.classList.remove('active');
                }
            });
            
            const allIcons = document.querySelectorAll('.expand i');
            allIcons.forEach(icon => {
                if (isAnyCollapsed) {
                    icon.classList.remove('fa-chevron-down');
                    icon.classList.add('fa-chevron-up');
                } else {
                    icon.classList.remove('fa-chevron-up');
                    icon.classList.add('fa-chevron-down');
                }
            });
            
            expandAllBtn.innerHTML = isAnyCollapsed ? 
                '<i class="fas fa-compress-alt"></i> Collapse All' : 
                '<i class="fas fa-expand-alt"></i> Expand All';
        });
        
        const viewToggle = document.querySelector('.view-toggle');
        if (viewToggle) {
            viewToggle.parentNode.insertBefore(expandAllBtn, viewToggle);
        } else {
            headerSection.appendChild(expandAllBtn);
        }
    }
    
    // Initialize functionality
    function init() {
        // Default view is timeline
        if (timelineView && tableView) {
            timelineView.style.display = 'block';
            tableView.style.display = 'none';
            
            if (timelineViewBtn && tableViewBtn) {
                timelineViewBtn.classList.add('active');
                tableViewBtn.classList.remove('active');
            }
        }
        
        // Add "Expand All" button if we're on the timeline view
        if (document.querySelector('.timeline-view')) {
            addExpandAllButton();
        }
        
        // Set current date in date filters if empty
        const today = new Date().toISOString().split('T')[0];
        const dateFromInput = document.getElementById('filter-date-from');
        const dateToInput = document.getElementById('filter-date-to');
        
        if (dateFromInput && !dateFromInput.value) {
            // Set default from date to 30 days ago
            const thirtyDaysAgo = new Date();
            thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
            dateFromInput.value = thirtyDaysAgo.toISOString().split('T')[0];
        }
        
        if (dateToInput && !dateToInput.value) {
            dateToInput.value = today;
        }
    }
    
    // Call initialization function
    init();
    
    // Responsive height adjustment for timeline entries
    window.addEventListener('resize', function() {
        if (window.innerWidth < 768) {
            document.querySelectorAll('.timeline-content.active').forEach(content => {
                content.style.maxHeight = 'none';
            });
        } else {
            document.querySelectorAll('.timeline-content.active').forEach(content => {
                content.style.maxHeight = content.scrollHeight + 'px';
            });
        }
    });
    
    // Initialize tooltips (if you're using a tooltip library)
    // This is a placeholder - you would need to implement or use a library
    function initTooltips() {
        const tooltipElements = document.querySelectorAll('[title]');
        // Implementation would depend on your tooltip library or custom implementation
    }
    
    // Call tooltip initialization if needed
    // initTooltips();
});
