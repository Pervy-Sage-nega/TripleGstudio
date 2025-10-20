// JavaScript for responsive enhancements and interactions
document.addEventListener('DOMContentLoaded', function () {
    // Custom scrollbar styles
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

    // Make progress bars and milestones dynamic
    const projectCards = document.querySelectorAll('.project-card');

    projectCards.forEach(card => {
        // Get progress bar and milestones
        const progressBar = card.querySelector('.progress-bar');
        const milestones = card.querySelectorAll('.milestone');
        
        if (progressBar) {
            const progress = parseFloat(progressBar.style.width);

            // Update milestones based on progress
            milestones.forEach((milestone, index) => {
                const milestonePosition = (index + 1) * 25;
                if (progress >= milestonePosition) {
                    milestone.classList.add('completed');
                } else {
                    milestone.classList.remove('completed');
                }
            });
        }

        // Add click event for buttons
        const detailsBtn = card.querySelector('.btn-primary');
        if (detailsBtn) {
            detailsBtn.addEventListener('click', function () {
                const projectTitle = card.querySelector('.project-title').textContent;
                alert(`Viewing details for project: ${projectTitle}`);
            });
        }


    });

    // ===== ENHANCED FILTER FUNCTIONALITY =====
    
    // Function to apply all active filters
    function applyFilters() {
        const categoryFilter = document.querySelector('.filter-dropdown:nth-child(1)').value;
        const statusFilter = document.querySelector('.filter-dropdown:nth-child(2)').value;
        const searchTerm = document.querySelector('.search-input').value.toLowerCase();
        
        projectCards.forEach(card => {
            // If data attributes don't exist yet, add them temporarily based on class names
            // In production, you should add these attributes directly to your HTML
            if (!card.hasAttribute('data-category')) {
                const classes = card.classList;
                if (classes.contains('commercial')) card.setAttribute('data-category', 'commercial');
                else if (classes.contains('residential')) card.setAttribute('data-category', 'residential');
                else if (classes.contains('industrial')) card.setAttribute('data-category', 'industrial');
                else if (classes.contains('infrastructure')) card.setAttribute('data-category', 'infrastructure');
                else card.setAttribute('data-category', 'other');
            }
            
            if (!card.hasAttribute('data-status')) {
                const statusElement = card.querySelector('.project-status');
                if (statusElement) {
                    const statusText = statusElement.textContent.toLowerCase();
                    card.setAttribute('data-status', statusText);
                } else {
                    // Try to determine status from other elements or classes
                    const classes = card.classList;
                    if (classes.contains('planning')) card.setAttribute('data-status', 'planning');
                    else if (classes.contains('ongoing')) card.setAttribute('data-status', 'ongoing');
                    else if (classes.contains('review')) card.setAttribute('data-status', 'review');
                    else if (classes.contains('completed')) card.setAttribute('data-status', 'completed');
                    else card.setAttribute('data-status', 'other');
                }
            }
            
            const category = card.getAttribute('data-category');
            const status = card.getAttribute('data-status');
            const title = card.querySelector('.project-title').textContent.toLowerCase();
            const description = card.querySelector('.project-description')?.textContent.toLowerCase() || '';
            
            // Check if card matches all active filters
            const matchesCategory = !categoryFilter || category === categoryFilter;
            const matchesStatus = !statusFilter || status === statusFilter;
            const matchesSearch = !searchTerm || 
                                title.includes(searchTerm) || 
                                description.includes(searchTerm);
            
            // Show card only if it matches all active filters
            if (matchesCategory && matchesStatus && matchesSearch) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Update UI to show filter results
        const visibleProjects = document.querySelectorAll('.project-card[style=""]').length;
        console.log(`Showing ${visibleProjects} projects after filtering`);
    }

    // Add event listeners to filter dropdowns
    const filterDropdowns = document.querySelectorAll('.filter-dropdown');
    filterDropdowns.forEach(dropdown => {
        dropdown.addEventListener('change', applyFilters);
    });

    // Update search functionality to work with filters
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }
});
