/**
 * Triple G Client Dashboard JavaScript
 * Handles dynamic content loading and animations
 */

class ClientDashboard {
    constructor() {
        this.projectData = null;
        this.animationSpeed = 1000;
        this.init();
    }

    init() {
        console.log('🏗️ Triple G Client Dashboard Loading...');
        this.loadProjectData();
        this.setupEventListeners();
        this.initializeAnimations();
    }

    /**
     * Load mock project data (will be replaced with Django backend)
     */
    loadProjectData() {
        // Mock data - replace with actual API call
        this.projectData = {
            id: 1,
            title: "Harbor Tower",
            code: "PRJ-2024-001",
            description: "Luxury commercial building with 35 floors, featuring premium office spaces and retail outlets.",
            location: "Downtown Business District",
            startDate: "2024-01-15",
            endDate: "2025-12-20",
            currentPhase: "Structural Framework",
            overallProgress: 65,
            budget: {
                total: 2500000,
                used: 1550000,
                remaining: 950000
            },
            phases: [
                { name: "Planning & Design", status: "completed", targetDate: "2024-01-31", progress: 100 },
                { name: "Foundation Work", status: "completed", targetDate: "2024-03-15", progress: 100 },
                { name: "Structural Framework", status: "in-progress", targetDate: "2024-09-30", progress: 65 },
                { name: "Finishing & Handover", status: "pending", targetDate: "2025-12-20", progress: 0 }
            ],
            activities: [
                {
                    date: "2024-12-15",
                    title: "Concrete pouring completed for Level 15",
                    description: "Structural work progressing on schedule",
                    icon: "fas fa-hammer"
                },
                {
                    date: "2024-12-12",
                    title: "Steel framework installation",
                    description: "Level 14-15 framework completed",
                    icon: "fas fa-tools"
                },
                {
                    date: "2024-12-10",
                    title: "Safety inspection passed",
                    description: "All safety protocols verified",
                    icon: "fas fa-shield-alt"
                }
            ],
            weather: {
                temperature: 24,
                condition: "Sunny",
                humidity: 65,
                icon: "fas fa-sun"
            }
        };

        this.populateProjectData();
    }

    /**
     * Populate the dashboard with project data
     */
    populateProjectData() {
        const data = this.projectData;

        // Update project overview (keep existing values from template)
        // document.getElementById('projectTitle').textContent = data.title;
        // document.getElementById('projectCode').textContent = data.code;
        // document.getElementById('projectDescription').textContent = data.description;
        // document.getElementById('projectLocation').textContent = data.location;
        // document.getElementById('currentPhase').textContent = data.currentPhase;

        // Format dates
        const startDate = new Date(data.startDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        const endDate = new Date(data.endDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
        document.getElementById('projectDates').textContent = `${startDate} - ${endDate}`;

        // Update analytics
        document.getElementById('overallProgressPercent').textContent = `${data.overallProgress}%`;
        
        // Calculate days remaining
        const today = new Date();
        const endDateObj = new Date(data.endDate);
        const daysRemaining = Math.ceil((endDateObj - today) / (1000 * 60 * 60 * 24));
        document.getElementById('daysRemaining').textContent = daysRemaining;

        const budgetUsedPercent = Math.round((data.budget.used / data.budget.total) * 100);
        document.getElementById('budgetUsed').textContent = `${budgetUsedPercent}%`;

        const completedPhases = data.phases.filter(phase => phase.status === 'completed').length;
        document.getElementById('phasesCompleted').textContent = `${completedPhases}/${data.phases.length}`;

        // Update budget summary
        document.getElementById('totalBudget').textContent = this.formatCurrency(data.budget.total);
        document.getElementById('usedBudget').textContent = this.formatCurrency(data.budget.used);
        document.getElementById('remainingBudget').textContent = this.formatCurrency(data.budget.remaining);
        document.getElementById('budgetBar').style.width = `${budgetUsedPercent}%`;

        // Update progress circle
        this.updateProgressCircle(data.overallProgress);
    }

    /**
     * Update the circular progress indicator
     */
    updateProgressCircle(percentage) {
        const circle = document.getElementById('overallProgress');
        const degrees = (percentage / 100) * 360;
        
        // Animate the progress circle
        setTimeout(() => {
            circle.style.background = `conic-gradient(#FF7120 0deg ${degrees}deg, rgba(255, 255, 255, 0.2) ${degrees}deg 360deg)`;
            circle.querySelector('.progress-value').textContent = `${percentage}%`;
        }, 500);
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Animate analytics cards on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe analytics cards
        document.querySelectorAll('.analytics-card').forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            card.style.transition = 'all 0.6s ease';
            observer.observe(card);
        });

        // Observe timeline milestones
        document.querySelectorAll('.milestone').forEach((milestone, index) => {
            milestone.style.opacity = '0';
            milestone.style.transform = 'translateY(20px)';
            milestone.style.transition = `all 0.5s ease ${index * 0.1}s`;
            observer.observe(milestone);
        });
    }

    /**
     * Initialize animations
     */
    initializeAnimations() {
        // Animate numbers counting up
        this.animateCounters();
        
        // Animate progress bars
        setTimeout(() => {
            this.animateProgressBars();
        }, 800);
    }

    /**
     * Animate counter numbers
     */
    animateCounters() {
        const counters = [
            { element: document.getElementById('overallProgressPercent'), target: 65, suffix: '%' },
            { element: document.getElementById('daysRemaining'), target: 287, suffix: '' },
            { element: document.getElementById('budgetUsed'), target: 62, suffix: '%' }
        ];

        counters.forEach(counter => {
            this.animateCounter(counter.element, counter.target, counter.suffix);
        });
    }

    /**
     * Animate individual counter
     */
    animateCounter(element, target, suffix) {
        let current = 0;
        const increment = target / 50;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current) + suffix;
        }, 20);
    }

    /**
     * Animate progress bars
     */
    animateProgressBars() {
        const budgetBar = document.getElementById('budgetBar');
        budgetBar.style.transition = 'width 1s ease';
        budgetBar.style.width = '62%';
    }

    /**
     * Format currency values
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-PH', {
            style: 'currency',
            currency: 'PHP',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(amount);
    }

    /**
     * Update weather data (mock function)
     */
    updateWeather() {
        // This would typically fetch real weather data
        const weatherConditions = [
            { temp: 24, condition: 'Sunny', icon: 'fas fa-sun', humidity: 65 },
            { temp: 18, condition: 'Cloudy', icon: 'fas fa-cloud', humidity: 78 },
            { temp: 15, condition: 'Rainy', icon: 'fas fa-cloud-rain', humidity: 85 }
        ];
        
        const randomWeather = weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
        
        document.querySelector('.temperature').textContent = `${randomWeather.temp}°C`;
        document.querySelector('.condition').textContent = randomWeather.condition;
        document.querySelector('.humidity').textContent = `Humidity: ${randomWeather.humidity}%`;
        document.querySelector('.weather-icon i').className = randomWeather.icon;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ClientDashboard();
});

// Add smooth scrolling for internal links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add loading states for buttons
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function() {
        if (!this.classList.contains('loading')) {
            this.classList.add('loading');
            const originalText = this.textContent;
            this.textContent = 'Loading...';
            
            setTimeout(() => {
                this.classList.remove('loading');
                this.textContent = originalText;
            }, 2000);
        }
    });
});