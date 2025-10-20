document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.getElementById('navLinks');
    
    if(mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }

    // Filter toggle
    const toggleFilter = document.getElementById('toggleFilter');
    if(toggleFilter) {
        toggleFilter.addEventListener('click', function() {
            const filterContent = document.getElementById('filterContent');
            const toggleIcon = this.querySelector('i');
            const toggleText = this.querySelector('span');
            
            if (filterContent.style.display === 'none') {
                filterContent.style.display = 'block';
                toggleIcon.className = 'fas fa-chevron-up';
                toggleText.textContent = 'Hide Filters';
            } else {
                filterContent.style.display = 'none';
                toggleIcon.className = 'fas fa-chevron-down';
                toggleText.textContent = 'Show Filters';
            }
        });
    }

    // Initialize Charts with delay to ensure Chart.js is loaded
    setTimeout(() => {
        if (typeof Chart !== 'undefined') {
            initializeCharts();
            console.log('Charts initialized successfully');
        } else {
            console.error('Chart.js library not loaded');
        }
    }, 500);

    // Add scrollbar styles
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
});

function initializeCharts() {
    console.log('Initializing charts...');
    
    // Labor Hours Distribution Chart
    const laborCtx = document.getElementById('laborChart')?.getContext('2d');
    if (laborCtx) {
        console.log('Creating labor chart');
        new Chart(laborCtx, {
            type: 'bar',
            data: {
                labels: ['Concrete Work', 'Structural Steel', 'Electrical', 'Plumbing', 'Masonry', 'Carpentry', 'Finishing'],
                datasets: [{
                    label: 'Hours',
                    data: [420, 380, 310, 290, 220, 180, 150],
                    backgroundColor: 'rgba(60, 110, 113, 0.7)',
                    borderColor: 'rgba(60, 110, 113, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Hours'
                        }
                    }
                }
            }
        });
    }

    // Project Progress Tracking Chart
    const progressCtx = document.getElementById('progressChart')?.getContext('2d');
    if (progressCtx) {
        new Chart(progressCtx, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Current'],
                datasets: [{
                    label: 'Planned Progress',
                    data: [5, 15, 25, 40, 55, 70, 85],
                    borderColor: 'rgba(40, 75, 99, 1)',
                    backgroundColor: 'rgba(40, 75, 99, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3
                }, {
                    label: 'Actual Progress',
                    data: [5, 13, 22, 38, 52, 68, 78],
                    borderColor: 'rgba(244, 67, 54, 1)',
                    backgroundColor: 'rgba(244, 67, 54, 0.1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Completion Percentage'
                        }
                    }
                }
            }
        });
    }

    // Material Usage Chart
    const materialsCtx = document.getElementById('materialsChart')?.getContext('2d');
    if (materialsCtx) {
        new Chart(materialsCtx, {
            type: 'pie',
            data: {
                labels: ['Concrete', 'Steel', 'Lumber', 'Glass', 'Electrical', 'Plumbing', 'Other'],
                datasets: [{
                    data: [35, 20, 15, 10, 8, 7, 5],
                    backgroundColor: [
                        'rgba(60, 110, 113, 0.8)',
                        'rgba(40, 75, 99, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(156, 39, 176, 0.8)',
                        'rgba(158, 158, 158, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // Delays Analysis Chart
    const delaysCtx = document.getElementById('delaysChart')?.getContext('2d');
    if (delaysCtx) {
        new Chart(delaysCtx, {
            type: 'doughnut',
            data: {
                labels: ['Weather', 'Material Shortage', 'Equipment Failure', 'Labor Shortage', 'Approval Delays', 'Other'],
                datasets: [{
                    data: [32, 18, 15, 12, 10, 13],
                    backgroundColor: [
                        'rgba(33, 150, 243, 0.8)',
                        'rgba(255, 152, 0, 0.8)',
                        'rgba(244, 67, 54, 0.8)',
                        'rgba(156, 39, 176, 0.8)',
                        'rgba(76, 175, 80, 0.8)',
                        'rgba(158, 158, 158, 0.8)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }
}