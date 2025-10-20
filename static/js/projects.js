document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Apply custom scrollbar styles
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
  
    let currentScroll = window.pageYOffset;
    let targetScroll = currentScroll;
    let ticking = false;
    
    function smoothPageScroll() {
        const diff = targetScroll - currentScroll;
        if (Math.abs(diff) < 0.5) {
            currentScroll = targetScroll;
            window.scrollTo(0, currentScroll);
            ticking = false;
            return;
        }
        currentScroll += diff * 0.1;
        window.scrollTo(0, currentScroll);
        if (currentScroll !== targetScroll) {
            requestAnimationFrame(smoothPageScroll);
        } else {
            ticking = false;
        }
    }
    
    function handleWheel(e) {
        e.preventDefault();
        targetScroll = Math.max(0, Math.min(document.body.scrollHeight - window.innerHeight, targetScroll + e.deltaY));
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(smoothPageScroll);
        }
    }
    
    window.addEventListener('wheel', handleWheel, { passive: false });
    
    window.addEventListener('keydown', function(e) {
        let scrollAmount = 0;
        switch(e.key) {
            case 'ArrowDown': scrollAmount = 40; break;
            case 'ArrowUp': scrollAmount = -40; break;
            case 'PageDown': scrollAmount = window.innerHeight * 0.9; break;
            case 'PageUp': scrollAmount = -window.innerHeight * 0.9; break;
            case 'Home': targetScroll = 0; break;
            case 'End': targetScroll = document.body.scrollHeight - window.innerHeight; break;
            default: return;
        }
        if (scrollAmount !== 0) {
            e.preventDefault();
            targetScroll = Math.max(0, Math.min(document.body.scrollHeight - window.innerHeight, targetScroll + scrollAmount));
        }
        if (!ticking) {
            ticking = true;
            requestAnimationFrame(smoothPageScroll);
        }
    });

    // Django handles all project data and rendering
    // This file only provides design enhancements and interactivity

    // Initialize featured projects interactivity (if any exist on the page)
    const featuredProjects = document.querySelectorAll('.featured-project');
    const viewProjectBtn = document.querySelector('.view-project-btn');
    
    // Set up featured project click handling for homepage carousel
    if (featuredProjects.length > 0 && viewProjectBtn) {
        // Add click event listeners to featured projects
        featuredProjects.forEach(project => {
            project.addEventListener('click', function() {
                // Remove active class from all projects
                featuredProjects.forEach(p => p.classList.remove('active'));
                
                // Add active class to clicked project
                this.classList.add('active');
                
                // Update view project button with project ID from data attribute
                const projectId = this.getAttribute('data-project-id');
                if (projectId) {
                    viewProjectBtn.setAttribute('data-project-id', projectId);
                    
                    // Add pulse animation to button
                    viewProjectBtn.classList.add('pulse');
                    setTimeout(() => {
                        viewProjectBtn.classList.remove('pulse');
                    }, 1000);
                }
            });
        });
        
        // Add mousemove event listener to track cursor position for glow effect
        viewProjectBtn.addEventListener('mousemove', (e) => {
            // Get position relative to the button
            const rect = viewProjectBtn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Update CSS variables for glow effect position
            viewProjectBtn.style.setProperty('--x', `${x}px`);
            viewProjectBtn.style.setProperty('--y', `${y}px`);
        });
        
        // Add click event to view project button
        viewProjectBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const projectId = this.getAttribute('data-project-id');
            if (projectId) {
                window.location.href = `/portfolio/${projectId}/`;
            }
        });
    }
});
