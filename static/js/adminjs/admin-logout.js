/**
 * Admin Logout Functionality
 * Handles secure logout with session cleanup and confirmation
 */

// Admin logout configuration
window.AdminLogout = window.AdminLogout || {
    // Configuration
    config: {
        confirmMessage: 'Are you sure you want to log out from the admin panel?',
        logoutUrl: '/admin-panel/logout/',
        loginRedirectUrl: '/accounts/admin-auth/login/',
        clearStorage: true,
        preventBackNavigation: true,
        sessionCheckUrl: '/admin-panel/check-session/'
    },

    // Initialize logout functionality
    init: function() {
        this.bindLogoutEvents();
        this.preventBackNavigation();
        this.setupSessionMonitoring();
    },

    // Bind logout events to elements
    bindLogoutEvents: function() {
        const bindEvents = () => {
            // Find all logout elements
            const logoutSelectors = [
                '[data-action="logout"]',
                '.logout-btn',
                '#logout-btn',
                '.admin-logout',
                'a[href*="logout"]'
            ];

            logoutSelectors.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    element.addEventListener('click', (e) => {
                        e.preventDefault();
                        window.AdminLogout.confirmLogout();
                    });
                });
            });

            // Handle keyboard shortcuts (Ctrl+Shift+L)
            document.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.shiftKey && e.key === 'L') {
                    e.preventDefault();
                    window.AdminLogout.confirmLogout();
                }
            });
        };

        // Bind events immediately if DOM is ready, otherwise wait
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', bindEvents);
        } else {
            bindEvents();
        }

        // Also use event delegation for dynamically loaded content
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action="logout"], .logout-btn, #logout-btn, .admin-logout');
            if (target) {
                e.preventDefault();
                window.AdminLogout.confirmLogout();
            }
        });
    },

    // Show logout confirmation
    confirmLogout: function() {
        // Check if we're on the settings page with the enhanced logout section
        const clearBrowserDataToggle = document.getElementById('clearBrowserData');
        
        if (clearBrowserDataToggle) {
            // We're on the settings page - show enhanced confirmation
            this.showEnhancedConfirmation();
        } else {
            // Standard confirmation for other pages
            this.showLogoutModal();
        }
    },

    // Show standard logout modal
    showLogoutModal: function() {
        this.createLogoutModal(
            'Confirm Logout',
            'Are you sure you want to log out from the admin panel?',
            false
        );
    },

    // Show enhanced confirmation dialog for settings page
    showEnhancedConfirmation: function() {
        const clearBrowserData = document.getElementById('clearBrowserData')?.checked || false;
        
        const message = `Are you sure you want to log out from the admin panel?

This will:
• End your current admin session
• Clear all cached admin data
• Prevent access to admin pages until you log in again
• Redirect you to the admin login page
${clearBrowserData ? '• Clear browser data and temporary files' : ''}`;

        this.createLogoutModal('Confirm Logout', message, clearBrowserData);
    },

    // Create logout confirmation modal
    createLogoutModal: function(title, message, clearBrowserData) {
        // Remove existing modal if any
        const existingModal = document.getElementById('logout-modal');
        if (existingModal) {
            existingModal.remove();
        }

        // Create modal HTML
        const modal = document.createElement('div');
        modal.id = 'logout-modal';
        modal.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10000;
                font-family: Arial, sans-serif;
            ">
                <div style="
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    max-width: 400px;
                    width: 90%;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                    text-align: center;
                ">
                    <div style="
                        color: #ff7120;
                        font-size: 48px;
                        margin-bottom: 20px;
                    ">
                        <i class="fas fa-sign-out-alt"></i>
                    </div>
                    <h3 style="
                        margin: 0 0 15px 0;
                        color: #333;
                        font-size: 24px;
                        font-weight: bold;
                    ">${title}</h3>
                    <p style="
                        margin: 0 0 30px 0;
                        color: #666;
                        font-size: 16px;
                        line-height: 1.5;
                        white-space: pre-line;
                    ">${message}</p>
                    <div style="
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                    ">
                        <button id="logout-cancel-btn" style="
                            background: #6c757d;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 5px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: background-color 0.3s;
                        ">
                            <i class="fas fa-times"></i> No, Stay Logged In
                        </button>
                        <button id="logout-confirm-btn" style="
                            background: #dc3545;
                            color: white;
                            border: none;
                            padding: 12px 24px;
                            border-radius: 5px;
                            font-size: 16px;
                            cursor: pointer;
                            transition: background-color 0.3s;
                        ">
                            <i class="fas fa-sign-out-alt"></i> Yes, Logout
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Add modal to page
        document.body.appendChild(modal);

        // Add button hover effects
        const cancelBtn = modal.querySelector('#logout-cancel-btn');
        const confirmBtn = modal.querySelector('#logout-confirm-btn');

        cancelBtn.addEventListener('mouseenter', () => {
            cancelBtn.style.backgroundColor = '#5a6268';
        });
        cancelBtn.addEventListener('mouseleave', () => {
            cancelBtn.style.backgroundColor = '#6c757d';
        });

        confirmBtn.addEventListener('mouseenter', () => {
            confirmBtn.style.backgroundColor = '#c82333';
        });
        confirmBtn.addEventListener('mouseleave', () => {
            confirmBtn.style.backgroundColor = '#dc3545';
        });

        // Handle button clicks
        cancelBtn.addEventListener('click', () => {
            this.closeLogoutModal();
        });

        confirmBtn.addEventListener('click', () => {
            this.closeLogoutModal();
            // Update config based on clear browser data setting
            this.config.clearStorage = clearBrowserData;
            this.performLogout();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeLogoutModal();
            }
        });

        // Handle escape key
        document.addEventListener('keydown', this.handleEscapeKey);
    },

    // Close logout modal
    closeLogoutModal: function() {
        const modal = document.getElementById('logout-modal');
        if (modal) {
            modal.remove();
        }
        document.removeEventListener('keydown', this.handleEscapeKey);
    },

    // Handle escape key press
    handleEscapeKey: function(e) {
        if (e.key === 'Escape') {
            window.AdminLogout.closeLogoutModal();
        }
    },

    // Perform the actual logout
    performLogout: function() {
        // Show loading indicator
        this.showLoadingIndicator();

        // Clear client-side storage
        if (this.config.clearStorage) {
            this.clearClientStorage();
        }

        // Clear browser cache for admin pages
        this.clearPageCache();

        // Add a small delay to ensure cleanup completes
        setTimeout(() => {
            // Redirect to logout URL
            window.location.href = this.config.logoutUrl;
        }, 500);
    },

    // Clear client-side storage
    clearClientStorage: function() {
        try {
            // Always clear session storage
            if (typeof(Storage) !== "undefined" && sessionStorage) {
                sessionStorage.clear();
            }

            // Clear specific localStorage items
            if (typeof(Storage) !== "undefined" && localStorage) {
                const adminKeys = [
                    'admin_session',
                    'admin_preferences',
                    'admin_cache',
                    'admin_temp_data',
                    'admin_authenticated'
                ];
                
                adminKeys.forEach(key => {
                    localStorage.removeItem(key);
                });

                // If enhanced clearing is enabled, clear more data
                if (this.config.clearStorage) {
                    const additionalKeys = [
                        'form_data',
                        'temp_uploads',
                        'draft_content',
                        'user_preferences',
                        'cached_data'
                    ];
                    
                    additionalKeys.forEach(key => {
                        localStorage.removeItem(key);
                    });
                }
            }

            // Clear any cookies related to admin session
            this.clearAdminCookies();

            // Clear browser cache if enhanced clearing is enabled
            if (this.config.clearStorage) {
                this.clearBrowserCache();
            }
        } catch (error) {
            console.warn('Could not clear storage:', error);
        }
    },

    // Clear admin-related cookies
    clearAdminCookies: function() {
        const adminCookies = ['admin_session', 'admin_prefs', 'csrftoken'];
        adminCookies.forEach(cookieName => {
            document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        });
    },

    // Clear browser cache (enhanced clearing)
    clearBrowserCache: function() {
        try {
            // Clear IndexedDB if available
            if ('indexedDB' in window) {
                indexedDB.databases().then(databases => {
                    databases.forEach(db => {
                        if (db.name.includes('admin') || db.name.includes('cache')) {
                            indexedDB.deleteDatabase(db.name);
                        }
                    });
                }).catch(() => {
                    // Ignore errors - not critical
                });
            }

            // Clear Web SQL if available (deprecated but still used by some browsers)
            if ('openDatabase' in window) {
                try {
                    const db = openDatabase('', '', '', '');
                    if (db) {
                        db.transaction(tx => {
                            tx.executeSql('DELETE FROM cache');
                        });
                    }
                } catch (e) {
                    // Ignore - Web SQL might not be available
                }
            }

            // Clear application cache if available (deprecated but still check)
            if ('applicationCache' in window && window.applicationCache) {
                try {
                    window.applicationCache.update();
                } catch (e) {
                    // Ignore errors
                }
            }

            // Clear service worker cache if available
            if ('serviceWorker' in navigator && 'caches' in window) {
                caches.keys().then(cacheNames => {
                    cacheNames.forEach(cacheName => {
                        if (cacheName.includes('admin') || cacheName.includes('static')) {
                            caches.delete(cacheName);
                        }
                    });
                }).catch(() => {
                    // Ignore errors - not critical
                });
            }
        } catch (error) {
            console.warn('Could not clear browser cache:', error);
        }
    },

    // Clear page cache to prevent back navigation
    clearPageCache: function() {
        if (this.config.preventBackNavigation) {
            // Add cache control headers via meta tags
            const metaTags = [
                { name: 'Cache-Control', content: 'no-cache, no-store, must-revalidate' },
                { name: 'Pragma', content: 'no-cache' },
                { name: 'Expires', content: '0' }
            ];

            metaTags.forEach(tag => {
                let meta = document.querySelector(`meta[http-equiv="${tag.name}"]`);
                if (!meta) {
                    meta = document.createElement('meta');
                    meta.setAttribute('http-equiv', tag.name);
                    document.head.appendChild(meta);
                }
                meta.setAttribute('content', tag.content);
            });
        }
    },

    // Prevent back navigation after logout
    preventBackNavigation: function() {
        if (this.config.preventBackNavigation) {
            // Push a dummy state to prevent back navigation
            window.addEventListener('beforeunload', () => {
                history.pushState(null, null, location.href);
            });

            // Handle back button
            window.addEventListener('popstate', () => {
                if (this.isLoggedOut()) {
                    history.pushState(null, null, location.href);
                    window.location.href = this.config.loginRedirectUrl;
                }
            });
        }
    },

    // Check if user is logged out
    isLoggedOut: function() {
        // Check if we're on a login page or if session is cleared
        return window.location.href.includes('login') || 
               !sessionStorage.getItem('admin_authenticated');
    },

    // Show loading indicator during logout
    showLoadingIndicator: function() {
        const clearingData = this.config.clearStorage;
        const message = clearingData ? 
            'Logging out and clearing data...' : 
            'Logging out...';
        
        // Create and show loading overlay
        const overlay = document.createElement('div');
        overlay.id = 'logout-loading';
        overlay.innerHTML = `
            <div style="
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
                color: white;
                font-size: 18px;
                font-family: Arial, sans-serif;
            ">
                <div style="text-align: center; padding: 30px; background: rgba(255, 255, 255, 0.1); border-radius: 10px; backdrop-filter: blur(10px);">
                    <div style="margin-bottom: 20px; font-weight: bold;">${message}</div>
                    <div style="width: 50px; height: 50px; border: 4px solid rgba(255, 255, 255, 0.3); border-top: 4px solid #ff7120; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto;"></div>
                    ${clearingData ? '<div style="margin-top: 15px; font-size: 14px; opacity: 0.8;">Clearing browser data...</div>' : ''}
                </div>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;
        document.body.appendChild(overlay);
    },

    // Setup session monitoring
    setupSessionMonitoring: function() {
        // Monitor for session expiry
        setInterval(() => {
            this.checkSessionStatus();
        }, 300000); // Check every 5 minutes

        // Monitor for tab visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.checkSessionStatus();
            }
        });
    },

    // Check session status
    checkSessionStatus: function() {
        // This would typically make an AJAX call to check session validity
        // For now, we'll just check if we're still on an admin page
        if (window.location.pathname.includes('/admin-side/') || 
            window.location.pathname.includes('/admin/')) {
            
            // AJAX call to verify session
            fetch(this.config.sessionCheckUrl, {
                method: 'GET',
                credentials: 'same-origin',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(response => {
                if (response.status === 401 || response.status === 403) {
                    this.handleSessionExpiry();
                }
            }).catch(() => {
                // Network error - don't force logout
            });
        }
    },

    // Handle session expiry
    handleSessionExpiry: function() {
        alert('Your admin session has expired. You will be redirected to the login page.');
        this.clearClientStorage();
        window.location.href = this.config.loginRedirectUrl;
    },

    // Force logout (can be called externally)
    forceLogout: function(reason = 'Session expired') {
        console.warn('Force logout:', reason);
        this.clearClientStorage();
        window.location.href = this.config.loginRedirectUrl;
    }
};

// Auto-initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => window.AdminLogout.init());
} else {
    window.AdminLogout.init();
}
