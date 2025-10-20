/**
 * Project List Filters JavaScript for Django Backend
 * Handles filter interactions and search functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get filter elements
    const yearFilter = document.getElementById('year-filter');
    const categoryFilter = document.getElementById('category-filter');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    
    // Handle filter changes
    if (yearFilter) {
        yearFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            applyFilters();
        });
    }
    
    // Handle search
    if (searchInput && searchBtn) {
        searchBtn.addEventListener('click', function() {
            applyFilters();
        });
        
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    }
    
    /**
     * Apply filters by redirecting to the filtered URL
     */
    function applyFilters() {
        const params = new URLSearchParams();
        
        // Add year filter
        if (yearFilter && yearFilter.value !== 'all') {
            params.set('year', yearFilter.value);
        }
        
        // Add category filter
        if (categoryFilter && categoryFilter.value !== 'all') {
            params.set('category', categoryFilter.value);
        }
        
        // Add search query
        if (searchInput && searchInput.value.trim()) {
            params.set('search', searchInput.value.trim());
        }
        
        // Build URL and redirect
        const baseUrl = window.location.pathname;
        const queryString = params.toString();
        const newUrl = queryString ? `${baseUrl}?${queryString}` : baseUrl;
        
        window.location.href = newUrl;
    }
    
    // Add hover effects to project cards
    const projectCards = document.querySelectorAll('.project-card');
    projectCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 15px 30px rgba(0, 0, 0, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Add click handler to project cards for better UX
    projectCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't trigger if clicking on the link itself
            if (e.target.tagName !== 'A') {
                const link = this.querySelector('.project-link');
                if (link) {
                    window.location.href = link.href;
                }
            }
        });
    });
});
