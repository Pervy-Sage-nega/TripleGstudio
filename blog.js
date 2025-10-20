document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle - Enhanced with animation
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');
    
    // Initialize mobile menu
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Initialize image functionality for both static and dynamic content
    initializeImageFeatures();
    
    // Initialize gallery lightbox if gallery exists
    initializeGalleryLightbox();
    
    // Initialize additional features
    initializeAdditionalFeatures();
});

/**
 * Initialize image features for blog posts
 */
function initializeImageFeatures() {
    const postImageContainers = document.querySelectorAll('.post-image-container, .gallery-item');

    if (postImageContainers.length) {
        postImageContainers.forEach(container => {
            // Skip if buttons already exist (e.g., in a dynamic DOM)
            if (container.querySelector('.image-action-buttons')) return;

            // Get the image element
            const img = container.querySelector('img');
            if (!img) return; // Skip if no image

            // Create toggle button
            const toggleBtn = document.createElement('button');
            toggleBtn.className = 'image-toggle-btn';
            toggleBtn.innerHTML = '<i class="fas fa-expand"></i>';
            toggleBtn.title = 'Toggle image size';
            toggleBtn.setAttribute('aria-label', 'Toggle image size');
            
            // Create download button
            const downloadBtn = document.createElement('a');
            downloadBtn.className = 'image-download-btn';
            downloadBtn.innerHTML = '<i class="fas fa-download"></i>';
            downloadBtn.title = 'Download image';
            downloadBtn.setAttribute('aria-label', 'Download image');
            
            // Set download link (disable if invalid)
            const canDownload = img.src && !img.src.startsWith('data:');
            if (canDownload) {
                downloadBtn.href = img.src;
                downloadBtn.download = img.alt || 'image-download';
            } else {
                downloadBtn.style.opacity = '0.5';
                downloadBtn.title = 'Download not available';
                downloadBtn.onclick = (e) => e.preventDefault();
            }
            
            // Create button container
            const btnContainer = document.createElement('div');
            btnContainer.className = 'image-action-buttons';
            btnContainer.appendChild(toggleBtn);
            btnContainer.appendChild(downloadBtn);
            container.appendChild(btnContainer);

            // Store overlay reference to avoid duplicates
            let overlay = null;

            // Toggle functionality
            const toggleImage = () => {
                container.classList.toggle('expanded');
                
                if (container.classList.contains('expanded')) {
                    // Expanded state
                    toggleBtn.innerHTML = '<i class="fas fa-compress"></i>';
                    toggleBtn.title = 'Minimize image';
                    
                    // Store original dimensions
                    container.dataset.originalWidth = container.style.width || 'auto';
                    container.dataset.originalHeight = container.style.height || 'auto';
                    
                    // Expand to full width
                    container.style.width = '100%';
                    container.style.height = 'auto';
                    container.style.maxWidth = 'none';
                    container.style.cursor = 'zoom-out';
                    
                    // Create overlay if it doesn't exist
                    if (!overlay) {
                        overlay = document.createElement('div');
                        overlay.className = 'image-overlay';
                        overlay.addEventListener('click', toggleImage);
                    }
                    
                    // Focus for keyboard navigation
                    container.setAttribute('tabindex', '0');
                    container.focus();
                } else {
                    // Normal state
                    toggleBtn.innerHTML = '<i class="fas fa-expand"></i>';
                    toggleBtn.title = 'Expand image';
                    
                    // Restore original dimensions
                    container.style.width = container.dataset.originalWidth;
                    container.style.height = container.dataset.originalHeight;
                    container.style.maxWidth = '';
                    container.style.cursor = 'zoom-in';
                    
                    // Remove overlay if it exists
                    if (overlay) {
                        overlay.remove();
                        overlay = null;
                    }
                }
            };

            // Attach toggle event
            toggleBtn.addEventListener('click', toggleImage);
            
            // Keyboard support
            container.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleImage();
                } else if (e.key === 'Escape' && container.classList.contains('expanded')) {
                    toggleImage();
                }
            });
            
            // Toggle on image click (excluding buttons)
            img.addEventListener('click', (e) => {
                if (!e.target.closest('.image-action-buttons')) {
                    toggleImage();
                }
            });
            
            // Prevent button clicks from bubbling to the image
            btnContainer.addEventListener('click', (e) => e.stopPropagation());
        });
    }
}

/**
 * Initialize gallery lightbox functionality
 */
function initializeGalleryLightbox() {
    // Add lightbox functionality for gallery images
    const galleryImages = document.querySelectorAll('.gallery-item img');
    
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            openLightbox(this.src, this.alt);
        });
    });
}

/**
 * Open lightbox for image viewing
 */
function openLightbox(imageSrc, caption) {
    // Create lightbox if it doesn't exist
    let lightbox = document.getElementById('imageLightbox');
    if (!lightbox) {
        lightbox = document.createElement('div');
        lightbox.id = 'imageLightbox';
        lightbox.className = 'image-lightbox';
        lightbox.innerHTML = `
            <div class="lightbox-content">
                <span class="lightbox-close">&times;</span>
                <img class="lightbox-image" src="" alt="">
                <div class="lightbox-caption"></div>
            </div>
        `;
        document.body.appendChild(lightbox);
        
        // Add close functionality
        lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });
    }
    
    // Set image and caption
    lightbox.querySelector('.lightbox-image').src = imageSrc;
    lightbox.querySelector('.lightbox-image').alt = caption || '';
    lightbox.querySelector('.lightbox-caption').textContent = caption || '';
    
    // Show lightbox
    lightbox.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

/**
 * Close lightbox
 */
function closeLightbox() {
    const lightbox = document.getElementById('imageLightbox');
    if (lightbox) {
        lightbox.style.display = 'none';
        document.body.style.overflow = '';
    }
}

// Additional functionality that was outside of functions
// This code should be inside a function or removed if duplicate
function initializeAdditionalFeatures() {
    // Enhanced Back to Top Button with progress indicator
    const backToTopBtn = document.querySelector('.back-to-top');
    
    if (backToTopBtn) {
        // Create progress circle
        const progressCircle = document.createElement('div');
        progressCircle.className = 'progress-circle';
        backToTopBtn.appendChild(progressCircle);
        
        window.addEventListener('scroll', function() {
            const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
            const scrollPosition = window.pageYOffset;
            const scrollProgress = (scrollPosition / scrollHeight) * 100;
            
            if (scrollPosition > 300) {
                backToTopBtn.classList.add('visible');
                progressCircle.style.background = `conic-gradient(#FF7120 ${scrollProgress}%, transparent ${scrollProgress}% 100%)`;
            } else {
                backToTopBtn.classList.remove('visible');
            }
        });
        
        backToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Enhanced Table of Contents with Intersection Observer
    const tocLinks = document.querySelectorAll('.toc-list a');
    const blogSections = document.querySelectorAll('.post-content h2, .post-content h3');
    
    if (tocLinks.length && blogSections.length) {
        // Add IDs to headings if not present
        blogSections.forEach((section, index) => {
            if (!section.id) {
                section.id = `section-${index}`;
            }
        });
        
        // Smooth scroll with offset for navbar
        tocLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    const navbarHeight = document.querySelector('.navbar').offsetHeight;
                    const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight - 20;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Update URL without page reload
                    history.pushState(null, null, targetId);
                }
            });
        });
        
        // Use IntersectionObserver for better performance
        const observerOptions = {
            root: null,
            rootMargin: '0px 0px -50% 0px',
            threshold: 0.1
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const id = '#' + entry.target.id;
                    
                    tocLinks.forEach(link => {
                        link.parentElement.classList.remove('active');
                        if (link.getAttribute('href') === id) {
                            link.parentElement.classList.add('active');
                            
                            // Scroll TOC item into view if needed
                            const tocItem = link.parentElement;
                            const tocContainer = document.querySelector('.toc-list');
                            const tocRect = tocContainer.getBoundingClientRect();
                            const itemRect = tocItem.getBoundingClientRect();
                            
                            if (itemRect.bottom > tocRect.bottom || itemRect.top < tocRect.top) {
                                tocItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                            }
                        }
                    });
                }
            });
        }, observerOptions);
        
        blogSections.forEach(section => {
            observer.observe(section);
        });
    }
    
    // Enhanced Related Articles Slider with touch support
    const sliderPrev = document.querySelector('.slider-prev');
    const sliderNext = document.querySelector('.slider-next');
    const articlesContainer = document.querySelector('.related-posts-grid');
    
    if (sliderNext && sliderPrev && articlesContainer) {
        // Convert to horizontal slider on mobile
        if (window.innerWidth < 992) {
            articlesContainer.style.overflowX = 'auto';
            articlesContainer.style.scrollSnapType = 'x mandatory';
            articlesContainer.style.gridAutoFlow = 'column';
            articlesContainer.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
            
            document.querySelectorAll('.related-post-card').forEach(card => {
                card.style.scrollSnapAlign = 'start';
            });
        }
        
        const cardWidth = document.querySelector('.related-post-card').offsetWidth + 20;
        const scrollAmount = cardWidth * 2;
        
        sliderNext.addEventListener('click', function() {
            articlesContainer.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        });
        
        sliderPrev.addEventListener('click', function() {
            articlesContainer.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        });
        
        // Touch support for mobile
        let isDown = false;
        let startX;
        let scrollLeft;
        
        articlesContainer.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - articlesContainer.offsetLeft;
            scrollLeft = articlesContainer.scrollLeft;
            articlesContainer.style.cursor = 'grabbing';
            articlesContainer.style.userSelect = 'none';
        });
        
        articlesContainer.addEventListener('mouseleave', () => {
            isDown = false;
            articlesContainer.style.cursor = 'grab';
        });
        
        articlesContainer.addEventListener('mouseup', () => {
            isDown = false;
            articlesContainer.style.cursor = 'grab';
        });
        
        articlesContainer.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - articlesContainer.offsetLeft;
            const walk = (x - startX) * 2;
            articlesContainer.scrollLeft = scrollLeft - walk;
        });
        
        // Touch events
        articlesContainer.addEventListener('touchstart', (e) => {
            isDown = true;
            startX = e.touches[0].pageX - articlesContainer.offsetLeft;
            scrollLeft = articlesContainer.scrollLeft;
        });
        
        articlesContainer.addEventListener('touchend', () => {
            isDown = false;
        });
        
        articlesContainer.addEventListener('touchmove', (e) => {
            if (!isDown) return;
            const x = e.touches[0].pageX - articlesContainer.offsetLeft;
            const walk = (x - startX) * 2;
            articlesContainer.scrollLeft = scrollLeft - walk;
        });
    }
    
    // Enhanced Lightbox with keyboard navigation
    const contentImages = document.querySelectorAll('.post-content img:not(.author-avatar)');
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
        <div class="lightbox-content">
            <img class="lightbox-img" src="" alt="Enlarged view">
            <button class="lightbox-close">&times;</button>
            <button class="lightbox-nav lightbox-prev">&lt;</button>
            <button class="lightbox-nav lightbox-next">&gt;</button>
        </div>
    `;
    document.body.appendChild(lightbox);
    
    if (contentImages.length) {
        let currentImageIndex = 0;
        const imagesArray = Array.from(contentImages);
        
        contentImages.forEach((img, index) => {
            img.style.cursor = 'zoom-in';
            img.setAttribute('tabindex', '0');
            
            img.addEventListener('click', function() {
                openLightbox(index);
            });
            
            img.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    openLightbox(index);
                }
            });
        });
        
        function openLightbox(index) {
            currentImageIndex = index;
            const lightboxImg = lightbox.querySelector('.lightbox-img');
            lightboxImg.src = imagesArray[currentImageIndex].src;
            lightboxImg.alt = imagesArray[currentImageIndex].alt || 'Enlarged view';
            lightbox.classList.add('active');
            document.body.style.overflow = 'hidden';
            
            // Focus for keyboard navigation
            lightbox.querySelector('.lightbox-close').focus();
        }
        
        function closeLightbox() {
            lightbox.classList.remove('active');
            document.body.style.overflow = '';
            imagesArray[currentImageIndex].focus();
        }
        
        function navigateLightbox(direction) {
            currentImageIndex += direction;
            
            if (currentImageIndex < 0) {
                currentImageIndex = imagesArray.length - 1;
            } else if (currentImageIndex >= imagesArray.length) {
                currentImageIndex = 0;
            }
            
            const lightboxImg = lightbox.querySelector('.lightbox-img');
            lightboxImg.src = imagesArray[currentImageIndex].src;
            lightboxImg.alt = imagesArray[currentImageIndex].alt || 'Enlarged view';
        }
        
        lightbox.querySelector('.lightbox-close').addEventListener('click', closeLightbox);
        lightbox.querySelector('.lightbox-prev').addEventListener('click', () => navigateLightbox(-1));
        lightbox.querySelector('.lightbox-next').addEventListener('click', () => navigateLightbox(1));
        
        lightbox.addEventListener('click', function(e) {
            if (e.target === lightbox) {
                closeLightbox();
            }
        });
        
        // Keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (!lightbox.classList.contains('active')) return;
            
            switch(e.key) {
                case 'Escape':
                    closeLightbox();
                    break;
                case 'ArrowLeft':
                    navigateLightbox(-1);
                    break;
                case 'ArrowRight':
                    navigateLightbox(1);
                    break;
            }
        });
    }
    
    // Enhanced Comment Form with AJAX submission
    const commentForm = document.getElementById('blogCommentForm');
    
    if (commentForm) {
        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Validate form
            let isValid = true;
            const nameInput = this.querySelector('#commenterName');
            const emailInput = this.querySelector('#commenterEmail');
            const commentInput = this.querySelector('#commentContent');
            
            // Clear previous errors
            clearErrors();
            
            // Name validation
            if (!nameInput.value.trim()) {
                showError(nameInput, 'Please enter your name');
                isValid = false;
            }
            
            // Email validation
            if (!emailInput.value.trim()) {
                showError(emailInput, 'Please enter your email');
                isValid = false;
            } else if (!isValidEmail(emailInput.value)) {
                showError(emailInput, 'Please enter a valid email address');
                isValid = false;
            }
            
            // Comment validation
            if (!commentInput.value.trim()) {
                showError(commentInput, 'Please enter your comment');
                isValid = false;
            } else if (commentInput.value.trim().length < 10) {
                showError(commentInput, 'Comment must be at least 10 characters');
                isValid = false;
            }
            
            if (!isValid) return;
            
            // Disable submit button during submission
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';
            
            try {
                // Simulate API call (replace with actual fetch in production)
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                // Create success message
                const successMessage = document.createElement('div');
                successMessage.className = 'comment-success';
                successMessage.innerHTML = `
                    <i class="fas fa-check-circle"></i>
                    <div>
                        <h4>Thank you for your comment!</h4>
                        <p>Your comment has been submitted and is awaiting moderation.</p>
                    </div>
                `;
                
                // Replace form with success message
                commentForm.replaceWith(successMessage);
                
                // Scroll to success message
                successMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
            } catch (error) {
                showError(submitBtn, 'An error occurred. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
        
        function showError(element, message) {
            const errorElement = document.createElement('div');
            errorElement.className = 'error-message';
            errorElement.textContent = message;
            
            element.classList.add('error');
            element.parentNode.insertBefore(errorElement, element.nextSibling);
            
            // Focus on first error field
            if (!document.querySelector('.error-message:first-of-type')) {
                element.focus();
            }
        }
        
        function clearErrors() {
            document.querySelectorAll('.error').forEach(el => {
                el.classList.remove('error');
            });
            
            document.querySelectorAll('.error-message').forEach(el => {
                el.remove();
            });
        }
        
        function isValidEmail(email) {
            return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
        }
    }
    
    // Enhanced Share Functionality with Web Share API
    const shareButtons = document.querySelectorAll('.share-btn');
    
    if (shareButtons.length) {
        shareButtons.forEach(btn => {
            btn.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const platform = this.classList.contains('facebook') ? 'facebook' :
                                this.classList.contains('twitter') ? 'twitter' :
                                this.classList.contains('linkedin') ? 'linkedin' :
                                this.classList.contains('email') ? 'email' : null;
                
                // Use Web Share API if available (mobile devices)
                if (navigator.share && platform === null) {
                    try {
                        await navigator.share({
                            title: document.title,
                            text: 'Check out this article from Triple G BuildHub',
                            url: window.location.href
                        });
                        return;
                    } catch (err) {
                        console.log('Share cancelled:', err);
                    }
                }
                
                const url = encodeURIComponent(window.location.href);
                const title = encodeURIComponent(document.title);
                const text = encodeURIComponent('Check out this article from Triple G BuildHub');
                
                let shareUrl;
                
                switch(platform) {
                    case 'facebook':
                        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
                        break;
                    case 'twitter':
                        shareUrl = `https://twitter.com/intent/tweet?url=${url}&text=${title}&via=TripleGBuildHub`;
                        break;
                    case 'linkedin':
                        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${url}`;
                        break;
                    case 'email':
                        shareUrl = `mailto:?subject=${title}&body=${text}%0A%0A${url}`;
                        break;
                    default:
                        // Fallback for other platforms
                        shareUrl = `https://www.addtoany.com/share#url=${url}&title=${title}`;
                }
                
                if (platform === 'email') {
                    window.location.href = shareUrl;
                } else {
                    window.open(shareUrl, '_blank', 'width=600,height=400');
                }
            });
        });
    }
    
    // Dynamic Reading Time Calculation
    const readingTimeElement = document.querySelector('.read-time');
    
    if (readingTimeElement) {
        const calculateReadingTime = () => {
            const articleText = document.querySelector('.post-content').textContent;
            const wordCount = articleText.trim().split(/\s+/).length;
            const imagesCount = document.querySelectorAll('.post-content img').length;
            
            // Calculate reading time (200 words per minute + 12 seconds per image)
            const wordsPerMinute = 200;
            const imageTime = imagesCount * 12 / 60;
            const readingTime = Math.ceil(wordCount / wordsPerMinute + imageTime);
            
            readingTimeElement.innerHTML = `<i class="fas fa-clock"></i> ${readingTime} min read`;
        };
        
        // Calculate initially and on content changes
        calculateReadingTime();
        
        // Optional: Recalculate if content changes (e.g., for SPAs)
        const observer = new MutationObserver(calculateReadingTime);
        observer.observe(document.querySelector('.post-content'), {
            childList: true,
            subtree: true,
            characterData: true
        });
    }
    
    // Lazy Loading for Images
    if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img.lazy');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    if (img.dataset.srcset) img.srcset = img.dataset.srcset;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Dynamic Table of Contents Generation
    const tocContainer = document.getElementById('tocList');
    const contentHeadings = document.querySelectorAll('.post-content h2, .post-content h3');
    
    if (tocContainer && contentHeadings.length) {
        // Clear any existing TOC items
        tocContainer.innerHTML = '';
        
        contentHeadings.forEach((heading, index) => {
            // Add ID to heading if not present
            if (!heading.id) {
                heading.id = `section-${index}`;
            }
            
            const listItem = document.createElement('li');
            listItem.className = heading.tagName === 'H3' ? 'toc-subitem' : '';
            
            const link = document.createElement('a');
            link.href = `#${heading.id}`;
            link.textContent = heading.textContent;
            
            listItem.appendChild(link);
            tocContainer.appendChild(listItem);
        });
        
        // Toggle functionality for mobile
        const tocToggle = document.getElementById('tocToggle');
        if (tocToggle) {
            tocToggle.addEventListener('click', function() {
                tocContainer.classList.toggle('visible');
                this.querySelector('i').classList.toggle('fa-chevron-down');
                this.querySelector('i').classList.toggle('fa-chevron-up');
            });
        }
    }
    
    // Add copy button to code blocks (if any)
    document.querySelectorAll('pre code').forEach(codeBlock => {
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-code';
        copyButton.innerHTML = '<i class="far fa-copy"></i> Copy';
        copyButton.title = 'Copy to clipboard';
        
        const pre = codeBlock.parentElement;
        pre.style.position = 'relative';
        pre.insertBefore(copyButton, codeBlock);
        
        copyButton.addEventListener('click', () => {
            navigator.clipboard.writeText(codeBlock.textContent)
                .then(() => {
                    copyButton.innerHTML = '<i class="fas fa-check"></i> Copied!';
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="far fa-copy"></i> Copy';
                    }, 2000);
                })
                .catch(err => {
                    console.error('Failed to copy: ', err);
                    copyButton.innerHTML = '<i class="fas fa-times"></i> Error';
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="far fa-copy"></i> Copy';
                    }, 2000);
                });
        });
    });
}

// Helper function to debounce events
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

