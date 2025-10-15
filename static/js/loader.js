/**
 * Triple G BuildHub Loading Screen - Real Functional Loader
 * Tracks actual resource loading progress including images, CSS, JS, and fonts
 */
class TripleGLoader {
    constructor() {
        this.progress = 0;
        this.minLoadTime = 1500; // Minimum display time (ms)
        this.maxLoadTime = 10000; // Maximum time before force complete
        this.loaderContainer = null;
        this.progressBar = null;
        this.startTime = null;
        this.initiated = false;
        this.loadingMessage = null;
        
        // Real loading tracking
        this.totalResources = 0;
        this.loadedResources = 0;
        this.resourceTypes = {
            images: { loaded: 0, total: 0 },
            stylesheets: { loaded: 0, total: 0 },
            scripts: { loaded: 0, total: 0 },
            fonts: { loaded: 0, total: 0 }
        };
        
        // Loading states
        this.domReady = false;
        this.resourcesLoaded = false;
        this.fontsLoaded = false;
        
        // Performance tracking
        this.loadingStages = {
            'DOM Ready': false,
            'Images Loaded': false,
            'Stylesheets Loaded': false,
            'Scripts Loaded': false,
            'Fonts Loaded': false
        };
    }

    /**
     * Initialize the real loading screen
     */
    init() {
        if (this.initiated) return;
        
        // Check if loader has already been shown in this session
        if (sessionStorage.getItem('tripleGLoaderShown')) {
            console.log(' TripleG Loader: Skipping - already shown this session');
            return;
        }
        
        this.initiated = true;
        this.startTime = performance.now();

        console.log(' TripleG Loader: Starting real resource tracking...');
        
        this.createLoaderUI();
        this.setupEventListeners();
        this.startResourceTracking();
        
        // Safety timeout in case something hangs
        this.safetyTimeout = setTimeout(() => {
            console.warn(' Loader timeout reached - forcing completion');
            this.completeLoading();
        }, this.maxLoadTime);
    }

    /**
     * Create all loader DOM elements
     */
    createLoaderUI() {
        // Main container
        this.loaderContainer = document.createElement('div');
        this.loaderContainer.className = 'tripleG-loader-container';
        document.body.appendChild(this.loaderContainer);

        // Background
        const gradientBg = document.createElement('div');
        gradientBg.className = 'gradient-background';
        this.loaderContainer.appendChild(gradientBg);

        // Logo container
        const logoContainer = document.createElement('div');
        logoContainer.className = 'tripleG-logo-container';
        
        // Logo image
        const logoImg = document.createElement('img');
        logoImg.className = 'tripleG-logo';
        
        logoImg.src = '/static/images/logostick.png';
        
        logoImg.alt = 'Triple G Logo';
        logoImg.onerror = () => {
            // Try alternative paths if the first one fails
            if (logoImg.src.includes('/static/images/')) {
                logoImg.src = '/static/images/logostick.png';
                logoImg.src = '/static/images/logostick.png';
            } else if (logoImg.src.includes('../css/')) {
                logoImg.src = '/static/images/logostick.png';
            } else {
                // Final fallback
                logoImg.src = '/static/images/logostick.png';
            }
        };
        logoContainer.appendChild(logoImg);
        
        // Logo text
        const logoText = document.createElement('div');
        logoText.className = 'tripleG-logo-text';
        
        const title = document.createElement('h1');
        title.textContent = 'TRIPLE G';
        
        const subtitle = document.createElement('p');
        subtitle.textContent = 'DESIGN STUDIO + CONSTRUCTION';
        
        logoText.appendChild(title);
        logoText.appendChild(subtitle);
        logoContainer.appendChild(logoText);
        this.loaderContainer.appendChild(logoContainer);



        // Progress bar
        const progressContainer = document.createElement('div');
        progressContainer.className = 'tripleG-progress-container';
        
        this.progressBar = document.createElement('div');
        this.progressBar.className = 'tripleG-progress-bar';
        
        progressContainer.appendChild(this.progressBar);
        this.loaderContainer.appendChild(progressContainer);
        
        // Loading message
        this.loadingMessage = document.createElement('div');
        this.loadingMessage.className = 'tripleG-loading-message';
        this.loadingMessage.textContent = 'Loading creative assets...';
        this.loaderContainer.appendChild(this.loadingMessage);
        

        
        // Lock body scroll
        document.body.style.overflow = 'hidden';
    }

    /**
     * Set up comprehensive event listeners for real loading tracking
     */
    setupEventListeners() {
        // DOM Content Loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.domReady = true;
            this.loadingStages['DOM Ready'] = true;
            this.updateLoadingMessage('DOM Ready - Scanning resources...');
            console.log(' DOM Ready');
            this.scanAndTrackResources();
        });

        // Window Load (all resources loaded)
        window.addEventListener('load', () => {
            this.resourcesLoaded = true;
            this.updateLoadingMessage('All resources loaded!');
            console.log(' Window Load Event');
            this.checkCompletion();
        });

        // Track font loading
        if (document.fonts) {
            document.fonts.ready.then(() => {
                this.fontsLoaded = true;
                this.loadingStages['Fonts Loaded'] = true;
                this.resourceTypes.fonts.loaded = this.resourceTypes.fonts.total;
                console.log(' Fonts Loaded');
                this.updateProgress();
            });
        } else {
            // Fallback for browsers without font loading API
            setTimeout(() => {
                this.fontsLoaded = true;
                this.loadingStages['Fonts Loaded'] = true;
            }, 1000);
        }
    }



    /**
     * Start real resource tracking
     */
    startResourceTracking() {
        this.updateProgress();
        
        // Update progress every 100ms
        this.progressInterval = setInterval(() => {
            this.updateProgress();
            this.checkCompletion();
        }, 100);
    }

    /**
     * Scan and track all page resources
     */
    scanAndTrackResources() {
        // Track images
        this.trackImages();
        // Track stylesheets
        this.trackStylesheets();
        // Track scripts
        this.trackScripts();
        // Track fonts
        this.trackFonts();
        
        console.log(' Resource Summary:', this.resourceTypes);
    }

    /**
     * Track image loading
     */
    trackImages() {
        const images = document.querySelectorAll('img');
        this.resourceTypes.images.total = images.length;
        
        if (images.length === 0) {
            this.loadingStages['Images Loaded'] = true;
            return;
        }
        
        images.forEach((img, index) => {
            if (img.complete) {
                this.resourceTypes.images.loaded++;
            } else {
                img.addEventListener('load', () => {
                    this.resourceTypes.images.loaded++;
                    console.log(` Image ${index + 1}/${images.length} loaded`);
                    if (this.resourceTypes.images.loaded === this.resourceTypes.images.total) {
                        this.loadingStages['Images Loaded'] = true;
                        console.log(' All Images Loaded');
                    }
                });
                img.addEventListener('error', () => {
                    this.resourceTypes.images.loaded++; // Count errors as "loaded"
                    console.warn(` Image ${index + 1} failed to load`);
                });
            }
        });
        
        if (this.resourceTypes.images.loaded === this.resourceTypes.images.total) {
            this.loadingStages['Images Loaded'] = true;
        }
    }

    /**
     * Track stylesheet loading
     */
    trackStylesheets() {
        const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
        this.resourceTypes.stylesheets.total = stylesheets.length;
        
        if (stylesheets.length === 0) {
            this.loadingStages['Stylesheets Loaded'] = true;
            return;
        }
        
        stylesheets.forEach((link, index) => {
            if (link.sheet) {
                this.resourceTypes.stylesheets.loaded++;
            } else {
                link.addEventListener('load', () => {
                    this.resourceTypes.stylesheets.loaded++;
                    console.log(` Stylesheet ${index + 1}/${stylesheets.length} loaded`);
                    if (this.resourceTypes.stylesheets.loaded === this.resourceTypes.stylesheets.total) {
                        this.loadingStages['Stylesheets Loaded'] = true;
                        console.log(' All Stylesheets Loaded');
                    }
                });
                link.addEventListener('error', () => {
                    this.resourceTypes.stylesheets.loaded++;
                    console.warn(` Stylesheet ${index + 1} failed to load`);
                });
            }
        });
        
        if (this.resourceTypes.stylesheets.loaded === this.resourceTypes.stylesheets.total) {
            this.loadingStages['Stylesheets Loaded'] = true;
        }
    }

    /**
     * Track script loading
     */
    trackScripts() {
        const scripts = document.querySelectorAll('script[src]');
        this.resourceTypes.scripts.total = scripts.length;
        
        if (scripts.length === 0) {
            this.loadingStages['Scripts Loaded'] = true;
            return;
        }
        
        scripts.forEach((script, index) => {
            if (script.readyState === 'loaded' || script.readyState === 'complete') {
                this.resourceTypes.scripts.loaded++;
            } else {
                script.addEventListener('load', () => {
                    this.resourceTypes.scripts.loaded++;
                    console.log(` Script ${index + 1}/${scripts.length} loaded`);
                    if (this.resourceTypes.scripts.loaded === this.resourceTypes.scripts.total) {
                        this.loadingStages['Scripts Loaded'] = true;
                        console.log(' All Scripts Loaded');
                    }
                });
                script.addEventListener('error', () => {
                    this.resourceTypes.scripts.loaded++;
                    console.warn(` Script ${index + 1} failed to load`);
                });
            }
        });
        
        if (this.resourceTypes.scripts.loaded === this.resourceTypes.scripts.total) {
            this.loadingStages['Scripts Loaded'] = true;
        }
    }

    /**
     * Track font loading
     */
    trackFonts() {
        // Count Google Fonts and other web fonts
        const fontLinks = document.querySelectorAll('link[href*="fonts.googleapis.com"], link[href*="fonts.gstatic.com"]');
        this.resourceTypes.fonts.total = Math.max(1, fontLinks.length); // At least 1 for system fonts
        
        if (fontLinks.length === 0) {
            this.resourceTypes.fonts.loaded = 1;
            this.loadingStages['Fonts Loaded'] = true;
        }
    }

    /**
     * Calculate and update real progress based on loaded resources
     */
    updateProgress() {
        // Calculate total progress based on different resource types
        const weights = {
            dom: 0.2,        // 20% for DOM ready
            images: 0.3,     // 30% for images
            stylesheets: 0.2, // 20% for CSS
            scripts: 0.2,    // 20% for JS
            fonts: 0.1       // 10% for fonts
        };
        
        let totalProgress = 0;
        
        // DOM Ready
        if (this.domReady) {
            totalProgress += weights.dom;
        }
        
        // Images
        if (this.resourceTypes.images.total > 0) {
            totalProgress += weights.images * (this.resourceTypes.images.loaded / this.resourceTypes.images.total);
        } else {
            totalProgress += weights.images; // No images to load
        }
        
        // Stylesheets
        if (this.resourceTypes.stylesheets.total > 0) {
            totalProgress += weights.stylesheets * (this.resourceTypes.stylesheets.loaded / this.resourceTypes.stylesheets.total);
        } else {
            totalProgress += weights.stylesheets;
        }
        
        // Scripts
        if (this.resourceTypes.scripts.total > 0) {
            totalProgress += weights.scripts * (this.resourceTypes.scripts.loaded / this.resourceTypes.scripts.total);
        } else {
            totalProgress += weights.scripts;
        }
        
        // Fonts
        if (this.resourceTypes.fonts.total > 0) {
            totalProgress += weights.fonts * (this.resourceTypes.fonts.loaded / this.resourceTypes.fonts.total);
        } else {
            totalProgress += weights.fonts;
        }
        
        this.progress = Math.min(1, Math.max(0, totalProgress));
        this.progressBar.style.width = `${this.progress * 100}%`;
        
        // Update loading message based on current stage
        this.updateLoadingMessageByStage();
        
        // Log progress for debugging
        if (Math.floor(this.progress * 100) % 10 === 0) {
            console.log(` Loading Progress: ${Math.floor(this.progress * 100)}%`);
        }
    }

    /**
     * Update loading message based on current loading stage
     */
    updateLoadingMessageByStage() {
        if (!this.domReady) {
            this.updateLoadingMessage('Preparing page structure...');
        } else if (!this.loadingStages['Stylesheets Loaded']) {
            this.updateLoadingMessage(`Loading styles... (${this.resourceTypes.stylesheets.loaded}/${this.resourceTypes.stylesheets.total})`);
        } else if (!this.loadingStages['Images Loaded']) {
            this.updateLoadingMessage(`Loading images... (${this.resourceTypes.images.loaded}/${this.resourceTypes.images.total})`);
        } else if (!this.loadingStages['Scripts Loaded']) {
            this.updateLoadingMessage(`Loading scripts... (${this.resourceTypes.scripts.loaded}/${this.resourceTypes.scripts.total})`);
        } else if (!this.loadingStages['Fonts Loaded']) {
            this.updateLoadingMessage('Loading fonts...');
        } else {
            this.updateLoadingMessage('Finalizing...');
        }
    }

    /**
     * Update the loading message text
     */
    updateLoadingMessage(text) {
        if (this.loadingMessage) {
            this.loadingMessage.textContent = text;
        }
    }

    /**
     * Check if loading should complete based on real resource loading
     */
    checkCompletion() {
        const elapsed = performance.now() - this.startTime;
        const minTimeReached = elapsed >= this.minLoadTime;
        
        // Check if all critical resources are loaded
        const allStagesComplete = Object.values(this.loadingStages).every(stage => stage === true);
        const resourcesReady = this.resourcesLoaded || allStagesComplete;
        
        // Complete if minimum time reached AND resources are ready
        if (minTimeReached && resourcesReady && this.progress >= 0.95) {
            console.log(' Loading Complete! All resources loaded.');
            this.completeLoading();
        }
        // Emergency completion if taking too long
        else if (elapsed >= this.maxLoadTime) {
            console.warn(' Force completing due to timeout');
            this.completeLoading();
        }
        // Complete if progress is essentially done
        else if (this.progress >= 0.99 && minTimeReached) {
            console.log(' Loading Complete! Progress reached 99%');
            this.completeLoading();
        }
    }

    /**
     * Complete the loading process
     */
    completeLoading() {
        clearInterval(this.progressInterval);
        clearTimeout(this.safetyTimeout);
        
        // Mark loader as shown for this session
        sessionStorage.setItem('tripleGLoaderShown', 'true');
        
        // Quickly fill any remaining progress
        this.progress = 1;
        this.progressBar.style.width = '100%';
        this.updateLoadingMessage('Complete!');
        
        // Hide the loader
        setTimeout(() => {
            this.hideLoader();
        }, 500);
    }

    /**
     * Hide the loader with transition
     */
    hideLoader() {
        if (!this.loaderContainer) return;
        
        this.loaderContainer.classList.add('tripleG-loader-hidden');
        

        
        // Remove from DOM after transition
        setTimeout(() => {
            if (this.loaderContainer && this.loaderContainer.parentNode) {
                this.loaderContainer.parentNode.removeChild(this.loaderContainer);
            }
            document.body.style.overflow = '';
        }, 600);
    }



    /**
     * Force hide the loader in emergency situations
     */
    forceHide() {
        clearInterval(this.progressInterval);
        clearTimeout(this.safetyTimeout);
        this.hideLoader();
    }
}

// Initialize loader
const tripleGLoader = new TripleGLoader();

// Start loader based on document state
if (document.readyState === 'complete') {
    tripleGLoader.init();
} else {
    document.addEventListener('DOMContentLoaded', () => tripleGLoader.init());
    window.addEventListener('load', () => tripleGLoader.init());
}

// Export for debugging
window.tripleGLoader = tripleGLoader;