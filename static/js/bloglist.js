/**
 * Triple G BuildHub Blog Listing JavaScript
 * Handles blog filtering, search, pagination and animations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    const searchInput = document.getElementById('blogSearch');
    const searchButton = document.getElementById('searchButton');
    const blogPostsContainer = document.getElementById('blogPostsContainer');
    const filterTags = document.querySelectorAll('.filter-tag');
    const paginationButtons = document.querySelectorAll('.pagination-btn');

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Initialize video background
    initVideoBackground();

    /**
     * Blog Post Data - Now using Django backend data
     * Posts are already filtered and paginated by Django
     */
    const allPosts = Array.from(document.querySelectorAll('.blog-card'));
    // Remove client-side pagination since Django handles it
    let filteredPosts = [...allPosts]; // Current page posts from Django

    // Initialize the page
    initializePage();

    /**
     * Sets up the initial page state and event listeners
     */
    function initializePage() {
        // Filter tags now use Django URLs (no client-side filtering needed)
        // The active state is handled by Django templates
        
        // Search functionality - Django handles the actual search
        // We just need to ensure smooth UX
        if (searchInput && searchButton) {
            // Add loading state for better UX
            searchButton.addEventListener('click', function() {
                if (searchInput.value.trim()) {
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    // Form will submit to Django
                }
            });

            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchButton.click();
                }
            });
        }

        // Pagination is now handled by Django URLs
        // We just add smooth transitions
        const paginationLinks = document.querySelectorAll('.pagination a');
        if (paginationLinks.length > 0) {
            paginationLinks.forEach(link => {
                link.addEventListener('click', function() {
                    // Add loading state
                    this.style.opacity = '0.6';
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                });
            });
        }

        // Initialize animations and design features
        initializeDesignFeatures();

        // Add animation to blog cards on hover
        addCardAnimations();
        
        // Add entrance animations to posts
        animateBlogPosts();
    }

    /**
     * Initialize design features and animations
     */
    function initializeDesignFeatures() {
        // Add smooth scroll behavior to all internal links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Add loading states to category filter links
        const categoryLinks = document.querySelectorAll('.filter-tag');
        categoryLinks.forEach(link => {
            link.addEventListener('click', function() {
                // Add loading state
                const originalText = this.textContent;
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + originalText;
                this.style.pointerEvents = 'none';
            });
        });

        // Initialize newsletter signup if present
        const newsletterForm = document.querySelector('.newsletter-signup form');
        if (newsletterForm) {
            newsletterForm.addEventListener('submit', function(e) {
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Subscribing...';
                    submitBtn.disabled = true;
                }
            });
        }
    }

    /**
     * Add entrance animations to blog posts
     */
    function animateBlogPosts() {
        const posts = document.querySelectorAll('.blog-card');
        
        posts.forEach((post, index) => {
            // Add staggered entrance animation
            post.style.opacity = '0';
            post.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                post.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                post.style.opacity = '1';
                post.style.transform = 'translateY(0)';
            }, index * 100); // Stagger the animations
        });
    }

    /**
     * Add hover animations to blog cards
     */
    function addCardAnimations() {
        const blogCards = document.querySelectorAll('.blog-card');
        
        blogCards.forEach(card => {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-5px)';
                this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.15)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '';
            });
        });
    }

    /**
     * Initialize video background functionality
     */
    function initVideoBackground() {
        const video = document.getElementById('header-bg-video');
        if (video) {
            // Ensure video plays on mobile devices
            video.muted = true;
            video.playsInline = true;
            
            // Handle video loading errors
            video.addEventListener('error', function() {
                console.log('Video failed to load, hiding video background');
                this.style.display = 'none';
            });
            
            // Optimize video playback
            video.addEventListener('loadeddata', function() {
                this.play().catch(e => console.log('Video autoplay failed:', e));
            });
        }
    }

    // Call initialization when page loads
    animateBlogPosts();
});
