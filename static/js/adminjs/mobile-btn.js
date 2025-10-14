// Mobile Navigation Button Functionality for Admin
document.addEventListener('DOMContentLoaded', function() {
    // Wait for header to be loaded before initializing
    setTimeout(initializeMobileNavigation, 100);
});

function initializeMobileNavigation() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    const dropdowns = document.querySelectorAll('.dropdown');
    
    if (!mobileMenuBtn || !navLinks) {
        return;
    }
    
    // Set active states based on current URL
    const currentPath = window.location.pathname;
    
    // Check for portfolio section
    if (currentPath.includes('/portfolio/') || currentPath.includes('/blog/')) {
        const portfolioDropdown = document.querySelector('[data-section="portfolio"]');
        if (portfolioDropdown) portfolioDropdown.classList.add('active');
    }
    
    // Check for site diary section
    if (currentPath.includes('/site/') || currentPath.includes('/diary/')) {
        const siteDropdown = document.querySelector('[data-section="site"]');
        if (siteDropdown) siteDropdown.classList.add('active');
    }
    
    // Check for admin tools section
    if (currentPath.includes('/admin/users/') || currentPath.includes('/chatbot/') || currentPath.includes('/admin/settings/')) {
        const adminDropdown = document.querySelector('[data-section="admin"]');
        if (adminDropdown) adminDropdown.classList.add('active');
    }
    
    // Mobile menu toggle
    mobileMenuBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleMobileMenu();
    });
    
    // Dropdown functionality for mobile
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        
        if (toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // On mobile, toggle the dropdown
                if (window.innerWidth <= 768) {
                    dropdown.classList.toggle('active');
                } else {
                    // Desktop behavior
                    closeAllDropdowns();
                    dropdown.classList.add('active');
                }
            });
        }
    });
    
    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.navbar')) {
            closeMobileMenu();
            closeAllDropdowns();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
    
    // Close menu when clicking on nav links (except dropdowns)
    const directNavLinks = navLinks.querySelectorAll('li:not(.dropdown) a');
    directNavLinks.forEach(link => {
        link.addEventListener('click', function() {
            closeMobileMenu();
        });
    });
}

function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (navLinks && mobileMenuBtn) {
        navLinks.classList.toggle('active');
        
        // Update button icon
        const icon = mobileMenuBtn.querySelector('i');
        if (navLinks.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    }
}

function closeMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (navLinks && mobileMenuBtn) {
        navLinks.classList.remove('active');
        
        // Reset button icon
        const icon = mobileMenuBtn.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
}

function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        dropdown.classList.remove('active');
    });
}

console.log("mobile-btn.js loaded");