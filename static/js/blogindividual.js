/**
 * Blog Individual Page with Sticky Comments
 * Handles functionality for sticky comments section
 */

document.addEventListener('DOMContentLoaded', function() {
    initMobileMenu();
    
    // Initialize the sticky comments functionality
    initStickyComments();
    
    // Initialize TOC toggle
    initTOCToggle();
    
    // Generate TOC from content headings
    generateTOC();
    
    initScrollEvents();
    
    // Initialize image zoom functionality
    initImageZoom();
});

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
 * Initialize sticky comments functionality
 * - Moves comments section to the sidebar
 * - Creates a sticky container for comments
 */
function initStickyComments() {
    // Create sticky comments section if it doesn't exist already
    if (!document.querySelector('.sticky-comments-section')) {
        // Get the original comments section
        const originalComments = document.querySelector('.comments-section');
        
        if (originalComments) {
            // Clone it to preserve event listeners
            const commentsClone = originalComments.cloneNode(true);
            
            // Create sticky container
            const stickyContainer = document.createElement('div');
            stickyContainer.className = 'sticky-comments-section';
            stickyContainer.appendChild(commentsClone);
            
            // Get the blog post layout
            const blogPostLayout = document.querySelector('.blog-post-layout');
            
            if (blogPostLayout) {
                // Append sticky container to blog post layout
                blogPostLayout.appendChild(stickyContainer);
            }
            
            // Create comments count badge for mobile
            createCommentsBadge();
        }
    }
}

/**
 * Create a badge showing comment count for mobile view
 */
function createCommentsBadge() {
    // Get comment count
    const commentCount = document.querySelectorAll('.comment').length;
    
    // Create badge element
    const badge = document.createElement('div');
    badge.className = 'comments-count-badge';
    badge.innerHTML = `<i class="fas fa-comments"></i> ${commentCount} Comments`;
    
    // Add click event to scroll to comments on mobile
    badge.addEventListener('click', function() {
        const commentsSection = document.querySelector('.sticky-comments-section');
        if (commentsSection) {
            commentsSection.scrollIntoView({ behavior: 'smooth' });
        }
    });
    
    // Append to body
    document.body.appendChild(badge);
    
    // Show badge when scrolling past a certain point on mobile
    let badgeVisible = false;
    window.addEventListener('scroll', function() {
        const scrollPosition = window.scrollY;
        const windowWidth = window.innerWidth;
        
        // Only for mobile devices
        if (windowWidth <= 992) {
            // Show badge after scrolling past 1000px
            if (scrollPosition > 1000 && !badgeVisible) {
                badge.classList.add('visible');
                badgeVisible = true;
            } else if (scrollPosition <= 1000 && badgeVisible) {
                badge.classList.remove('visible');
                badgeVisible = false;
            }
        }
    });
}

/**
 * Initialize TOC toggle functionality
 */
function initTOCToggle() {
    const tocToggle = document.getElementById('tocToggle');
    const tocList = document.getElementById('tocList');
    
    if (tocToggle && tocList) {
        tocToggle.addEventListener('click', function() {
            tocList.style.display = tocList.style.display === 'none' ? 'block' : 'none';
            tocToggle.innerHTML = tocList.style.display === 'none' ? 
                '<i class="fas fa-chevron-down"></i>' : 
                '<i class="fas fa-chevron-up"></i>';
        });
    }
    
    // Also make TOC links smooth scroll to sections
    const tocLinks = document.querySelectorAll('.toc-list a');
    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                // Highlight the section briefly
                targetElement.classList.add('highlight');
                setTimeout(() => {
                    targetElement.classList.remove('highlight');
                }, 2000);
            }
        });
    });
}

/**
 * Generate Table of Contents from blog post headings
 */
function generateTOC() {
    const tocList = document.getElementById('tocList');
    const postContent = document.querySelector('.post-content');
    const tocContainer = document.getElementById('postToc');
    
    if (!tocList || !postContent) return;
    
    // Find all headings in the post content
    const headings = postContent.querySelectorAll('h1, h2, h3, h4, h5, h6');
    
    if (headings.length === 0) {
        // Hide TOC if no headings found
        if (tocContainer) {
            tocContainer.style.display = 'none';
        }
        return;
    }
    
    // Show TOC container
    if (tocContainer) {
        tocContainer.style.display = 'block';
    }
    
    // Clear existing TOC
    tocList.innerHTML = '';
    
    // Generate TOC items
    headings.forEach((heading, index) => {
        // Create unique ID if heading doesn't have one
        if (!heading.id) {
            // Create slug from heading text
            const slug = heading.textContent
                .toLowerCase()
                .trim()
                .replace(/[^\w\s-]/g, '') // Remove special characters
                .replace(/[\s_-]+/g, '-') // Replace spaces and underscores with hyphens
                .replace(/^-+|-+$/g, ''); // Remove leading/trailing hyphens
            
            heading.id = slug || `heading-${index}`;
        }
        
        // Create TOC item
        const tocItem = document.createElement('li');
        const tocLink = document.createElement('a');
        
        tocLink.href = `#${heading.id}`;
        tocLink.textContent = heading.textContent;
        tocLink.className = `toc-${heading.tagName.toLowerCase()}`;
        
        // Add indentation based on heading level
        const level = parseInt(heading.tagName.charAt(1));
        if (level > 2) {
            tocItem.style.paddingLeft = `${(level - 2) * 20}px`;
            tocItem.classList.add(`toc-level-${level}`);
        }
        
        // Add smooth scroll behavior
        tocLink.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.getElementById(heading.id);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Update URL hash
                history.pushState(null, null, `#${heading.id}`);
            }
        });
        
        tocItem.appendChild(tocLink);
        tocList.appendChild(tocItem);
    });
    
    // Add scroll spy functionality
    addScrollSpy(headings);
}

/**
 * Add scroll spy functionality to highlight current section in TOC
 */
function addScrollSpy(headings) {
    if (headings.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            const id = entry.target.id;
            const tocLink = document.querySelector(`#tocList a[href="#${id}"]`);
            
            if (tocLink) {
                if (entry.isIntersecting) {
                    // Remove active class from all TOC links
                    document.querySelectorAll('#tocList a').forEach(link => {
                        link.classList.remove('active');
                    });
                    
                    // Add active class to current TOC link
                    tocLink.classList.add('active');
                }
            }
        });
    }, {
        rootMargin: '-20% 0% -35% 0%'
    });
    
    // Observe all headings
    headings.forEach(heading => {
        observer.observe(heading);
    });
}

// Comment functionality moved to blog-comments.js

// addNewComment function moved to blog-comments.js

// Comment success and count functions moved to blog-comments.js

/**
 * Initialize scroll events
 * - Highlight active TOC item
 * - Show/hide back to top button
 */
function initScrollEvents() {
    window.addEventListener('scroll', function() {
        // Highlight active TOC item
        highlightActiveTOCItem();
    });
}

/**
 * Highlight the active TOC item based on scroll position
 */
function highlightActiveTOCItem() {
    // Get all section elements
    const sections = document.querySelectorAll('section[id]');
    
    // Get current scroll position
    const scrollPosition = window.scrollY + 100; // 100px offset for better UX
    
    // Find the section currently in view
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionBottom = sectionTop + section.offsetHeight;
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
            // Remove active class from all TOC links
            document.querySelectorAll('.toc-list a').forEach(link => {
                link.classList.remove('active');
            });
            
            // Add active class to current section's TOC link
            const currentTOCLink = document.querySelector(`.toc-list a[href="#${section.id}"]`);
            if (currentTOCLink) {
                currentTOCLink.classList.add('active');
            }
        }
    });
}

/**
 * Initialize image zoom functionality
 * - Creates overlay for full-screen zoom
 * - Adds zoom controls
 * - Handles keyboard navigation
 */
function initImageZoom() {
    // Get all post images
    const postImages = document.querySelectorAll('.post-image-container img');
    
    // If no images, exit early
    if (postImages.length === 0) return;
    
    // Create zoom overlay element if it doesn't exist
    let zoomOverlay = document.querySelector('.image-zoom-overlay');
    if (!zoomOverlay) {
        zoomOverlay = document.createElement('div');
        zoomOverlay.className = 'image-zoom-overlay';
        
        // Create zoomed image element
        const zoomedImage = document.createElement('img');
        zoomedImage.className = 'zoomed-image';
        zoomOverlay.appendChild(zoomedImage);
        
        // Create zoom controls
        const zoomControls = document.createElement('div');
        zoomControls.className = 'zoom-controls';
        
        // Previous button
        const prevBtn = document.createElement('button');
        prevBtn.className = 'zoom-btn prev-btn';
        prevBtn.innerHTML = '<i class="fas fa-chevron-left"></i>';
        prevBtn.title = 'Previous image';
        
        // Next button
        const nextBtn = document.createElement('button');
        nextBtn.className = 'zoom-btn next-btn';
        nextBtn.innerHTML = '<i class="fas fa-chevron-right"></i>';
        nextBtn.title = 'Next image';
        
        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'zoom-close';
        closeBtn.innerHTML = '<i class="fas fa-times"></i>';
        closeBtn.title = 'Close';
        
        // Append buttons to controls
        zoomControls.appendChild(prevBtn);
        zoomControls.appendChild(nextBtn);
        zoomOverlay.appendChild(zoomControls);
        zoomOverlay.appendChild(closeBtn);
        
        // Append overlay to body
        document.body.appendChild(zoomOverlay);
    }
    
    // Get references to zoom elements
    const zoomed = zoomOverlay.querySelector('.zoomed-image');
    const prevBtn = zoomOverlay.querySelector('.prev-btn');
    const nextBtn = zoomOverlay.querySelector('.next-btn');
    const closeBtn = zoomOverlay.querySelector('.zoom-close');
    
    // Create array of images for navigation
    const imagesArray = Array.from(postImages);
    let currentImageIndex = 0;
    
    // Add click event to each image
    postImages.forEach((img, index) => {
        const container = img.closest('.post-image-container');
        
        // Set cursor style
        img.style.cursor = 'zoom-in';
        
        // Add click event to image
        img.addEventListener('click', () => {
            openZoom(index);
        });
        
        // Add keyboard support for accessibility
        img.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openZoom(index);
            }
        });
        
        // Make image focusable
        img.setAttribute('tabindex', '0');
    });
    
    // Function to open zoom overlay
    function openZoom(index) {
        currentImageIndex = index;
        
        // Set image source
        zoomed.src = imagesArray[currentImageIndex].src;
        zoomed.alt = imagesArray[currentImageIndex].alt || 'Enlarged image';
        
        // Get caption if it exists
        const imageContainer = imagesArray[currentImageIndex].closest('.post-image-container');
        const caption = imageContainer.querySelector('.image-caption');
        
        // Show overlay
        zoomOverlay.classList.add('active');
        
        // Disable scrolling on body
        document.body.style.overflow = 'hidden';
        
        // Focus on close button for keyboard navigation
        closeBtn.focus();
        
        // Update navigation buttons visibility
        updateNavButtons();
    }
    
    // Function to close zoom overlay
    function closeZoom() {
        // Hide overlay
        zoomOverlay.classList.remove('active');
        
        // Enable scrolling on body
        document.body.style.overflow = '';
        
        // Return focus to the original image
        imagesArray[currentImageIndex].focus();
    }
    
    // Function to navigate to previous/next image
    function navigateZoom(direction) {
        currentImageIndex += direction;
        
        // Handle wrap-around navigation
        if (currentImageIndex < 0) {
            currentImageIndex = imagesArray.length - 1;
        } else if (currentImageIndex >= imagesArray.length) {
            currentImageIndex = 0;
        }
        
        // Update displayed image
        zoomed.src = imagesArray[currentImageIndex].src;
        zoomed.alt = imagesArray[currentImageIndex].alt || 'Enlarged image';
        
        // Update navigation buttons visibility
        updateNavButtons();
    }
    
    // Function to update navigation buttons visibility
    function updateNavButtons() {
        // Only show navigation if there are multiple images
        if (imagesArray.length <= 1) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        } else {
            prevBtn.style.display = 'flex';
            nextBtn.style.display = 'flex';
        }
    }
    
    // Add event listeners for controls
    prevBtn.addEventListener('click', () => navigateZoom(-1));
    nextBtn.addEventListener('click', () => navigateZoom(1));
    closeBtn.addEventListener('click', closeZoom);
    
    // Close when clicking on the overlay (but not the image)
    zoomOverlay.addEventListener('click', (e) => {
        if (e.target === zoomOverlay) {
            closeZoom();
        }
    });
    
    // Add keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!zoomOverlay.classList.contains('active')) return;
        
        switch(e.key) {
            case 'ArrowLeft':
                navigateZoom(-1);
                break;
            case 'ArrowRight':
                navigateZoom(1);
                break;
            case 'Escape':
                closeZoom();
                break;
        }
    });
} 