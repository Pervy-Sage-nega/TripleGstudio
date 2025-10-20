/**
 * Project Detail Page JavaScript
 * Handles lightbox functionality, mobile menu, and video background
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load project details based on URL parameter
    loadProjectDetails();
    
    // Mobile menu functionality
    initMobileMenu();
    
    // Initialize gallery lightbox
    initGalleryLightbox();
    
    // Initialize video background
    initVideoBackground();
    
    // Add hover effects to stat items
    initStatItemsHover();
});

/**
 * Load project details based on URL parameter
 */
function loadProjectDetails() {
    // Get project ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const projectId = urlParams.get('id');
    
    if (!projectId) {
        console.log('No project ID specified, showing default project');
        return; // Default project will be shown
    }
    
    // This would typically involve an API call to get project data
    // For now, we'll just log that we got the ID
    console.log(`Loading project with ID: ${projectId}`);
    
    // In a real application, you would:
    // 1. Fetch the project data from an API or local data
    // 2. Update the DOM with the project details
    // 3. Update the title, meta tags, etc.
    
    // Example of what this might look like:
    /*
    fetch(`/api/projects/${projectId}`)
        .then(response => response.json())
        .then(project => {
            document.querySelector('.project-hero h1').textContent = project.title;
            document.querySelector('.project-location').innerHTML = 
                `<i class="fas fa-map-marker-alt"></i> ${project.location}`;
            // Update other elements...
        })
        .catch(error => {
            console.error('Error loading project details:', error);
        });
    */
}

/**
 * Initialize mobile menu toggle
 */
function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
}

/**
 * Initialize gallery lightbox functionality
 */
function initGalleryLightbox() {
    const galleryItems = document.querySelectorAll('.gallery-item');
    const lightbox = document.getElementById('gallery-lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.querySelector('.lightbox-close');
    const lightboxNext = document.querySelector('.lightbox-next');
    const lightboxPrev = document.querySelector('.lightbox-prev');
    
    if (!galleryItems.length || !lightbox || !lightboxImg) return;
    
    let currentIndex = 0;
    const images = Array.from(galleryItems).map(item => item.querySelector('img').src);
    
    // Open lightbox when clicking on gallery item
    galleryItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            currentIndex = index;
            openLightbox(currentIndex);
        });
    });
    
    // Close lightbox when clicking on close button
    if (lightboxClose) {
        lightboxClose.addEventListener('click', closeLightbox);
    }
    
    // Close lightbox when clicking outside the image
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
    
    // Navigate to next image
    if (lightboxNext) {
        lightboxNext.addEventListener('click', function() {
            navigateLightbox(1);
        });
    }
    
    // Navigate to previous image
    if (lightboxPrev) {
        lightboxPrev.addEventListener('click', function() {
            navigateLightbox(-1);
        });
    }
    
    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (!lightbox.classList.contains('active')) return;
        
        switch (e.key) {
            case 'ArrowRight':
                navigateLightbox(1);
                break;
            case 'ArrowLeft':
                navigateLightbox(-1);
                break;
            case 'Escape':
                closeLightbox();
                break;
        }
    });
    
    // Open lightbox with specified image index
    function openLightbox(index) {
        lightboxImg.src = images[index];
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    }
    
    // Close lightbox
    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    }
    
    // Navigate to next or previous image
    function navigateLightbox(direction) {
        currentIndex += direction;
        
        // Loop back to start/end if needed
        if (currentIndex < 0) {
            currentIndex = images.length - 1;
        } else if (currentIndex >= images.length) {
            currentIndex = 0;
        }
        
        lightboxImg.src = images[currentIndex];
    }
}

/**
 * Initialize video background functionality
 */
function initVideoBackground() {
    const video = document.getElementById('project-hero-video');
    const videoBackground = document.querySelector('.video-background');
    
    if (!video || !videoBackground) return;
    
    // Don't override video source - let Django template handle it
    // The video sources are already set in the HTML template
    
    // Check if browser can play video
    const canPlayVideo = video.canPlayType && (
        video.canPlayType('video/mp4').replace(/no/, '') ||
        video.canPlayType('video/webm').replace(/no/, '')
    );
    
    // Handle video events
    video.addEventListener('loadeddata', function() {
        // Video has loaded, ensure it's visible
        video.style.opacity = '1';
    });
    
    video.addEventListener('error', function() {
        // Error loading video, show fallback
        showFallbackBackground();
    });
    
    // If browser can't play video, show fallback immediately
    if (!canPlayVideo) {
        showFallbackBackground();
    }
    
    /**
     * Show fallback background when video can't be played
     */
    function showFallbackBackground() {
        // Hide video element
        if (video) video.style.display = 'none';
        
        // Add fallback background image
        if (videoBackground) {
            videoBackground.style.backgroundImage = 'url("/static/images/image1.jpg")';
            videoBackground.style.backgroundSize = 'cover';
            videoBackground.style.backgroundPosition = 'center';
        }
    }
}

/**
 * Initialize hover effects for stat items
 */
function initStatItemsHover() {
    const statItems = document.querySelectorAll('.stat-item');
    
    statItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.4)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
} 