// Admin Reports JavaScript with Dynamic Data
document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts with real data
    initializeCharts();
    
    // Initialize filter functionality
    initializeFilters();
    
    // Initialize export functionality
    initializeExportFunctions();
    
    // Initialize modal functionality
    initializeModals();
});

function initializeCharts() {
    // Get data from Django context (passed via script tags)
    const laborData = window.reportsData?.laborStats || [];
    const delayData = window.reportsData?.delayStats || [];
    const weatherData = window.reportsData?.weatherStats || [];
    const equipmentData = window.reportsData?.equipmentStats || [];
    const budgetData = window.reportsData?.budgetForecast || [];
    
    // Labor Distribution Chart (Chart.js)
    if (document.getElementById('laborChart')) {
        const laborChart = new Chart(document.getElementById('laborChart'), {
            type: 'doughnut',
            data: {
                labels: laborData.map(item => item.labor_type || 'Unknown'),
                datasets: [{
                    data: laborData.map(item => item.total_hours || 0),
                    backgroundColor: [
                        '#3498db', '#e74c3c', '#f39c12', '#27ae60', 
                        '#9b59b6', '#1abc9c', '#34495e', '#e67e22'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                return `${label}: ${value} hours`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Project Progress Chart (Chart.js)
    if (document.getElementById('progressChart')) {
        const progressChart = new Chart(document.getElementById('progressChart'), {
            type: 'bar',
            data: {
                labels: budgetData.map(item => item.project_name || 'Project'),
                datasets: [{
                    label: 'Budget',
                    data: budgetData.map(item => item.budget || 0),
                    backgroundColor: '#3498db',
                    borderColor: '#2980b9',
                    borderWidth: 1
                }, {
                    label: 'Actual Cost',
                    data: budgetData.map(item => item.actual || 0),
                    backgroundColor: '#e74c3c',
                    borderColor: '#c0392b',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₱' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₱' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Material Cost Analysis Chart (Chart.js)
    if (document.getElementById('materialsChart')) {
        const materialsChart = new Chart(document.getElementById('materialsChart'), {
            type: 'line',
            data: {
                labels: equipmentData.map(item => item.equipment_type || 'Equipment'),
                datasets: [{
                    label: 'Hours Operated',
                    data: equipmentData.map(item => item.total_hours || 0),
                    borderColor: '#27ae60',
                    backgroundColor: 'rgba(39, 174, 96, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
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
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Delay Analysis Chart (ECharts)
    if (document.getElementById('delaysChart')) {
        const delaysChart = echarts.init(document.getElementById('delaysChart'));
        const delaysOption = {
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'shadow'
                }
            },
            xAxis: {
                type: 'category',
                data: delayData.map(item => item.category || 'Unknown')
            },
            yAxis: {
                type: 'value',
                name: 'Hours',
                axisLabel: {
                    formatter: '{value} hrs'
                }
            },
            series: [{
                name: 'Delay Hours',
                type: 'bar',
                data: delayData.map(item => item.total_hours || 0),
                itemStyle: {
                    color: '#f39c12'
                }
            }]
        };
        delaysChart.setOption(delaysOption);
        window.addEventListener('resize', () => delaysChart.resize());
    }
    
    // Budget Forecast Chart (Chart.js)
    if (document.getElementById('budgetForecastChart')) {
        const budgetForecastChart = new Chart(document.getElementById('budgetForecastChart'), {
            type: 'line',
            data: {
                labels: budgetData.map(item => item.project_name || 'Project'),
                datasets: [{
                    label: 'Budget',
                    data: budgetData.map(item => item.budget || 0),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: false
                }, {
                    label: 'Actual Spending',
                    data: budgetData.map(item => item.actual || 0),
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    borderWidth: 2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '₱' + value.toLocaleString();
                            }
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ₱' + context.parsed.y.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    // Resource Allocation Chart (Chart.js)
    if (document.getElementById('resourceChart')) {
        const resourceChart = new Chart(document.getElementById('resourceChart'), {
            type: 'radar',
            data: {
                labels: ['Labor', 'Materials', 'Equipment', 'Budget', 'Timeline', 'Quality'],
                datasets: [{
                    label: 'Resource Efficiency',
                    data: [85, 78, 92, 67, 74, 88],
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.2)',
                    borderWidth: 2,
                    pointBackgroundColor: '#9b59b6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20
                        }
                    }
                }
            }
        });
    }
    
    // Weather Impact Chart (ECharts)
    if (document.getElementById('weatherImpactChart')) {
        const weatherImpactChart = echarts.init(document.getElementById('weatherImpactChart'));
        const weatherOption = {
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} days ({d}%)'
            },
            legend: {
                orient: 'vertical',
                left: 'left'
            },
            series: [{
                name: 'Weather Impact',
                type: 'pie',
                radius: '50%',
                data: weatherData.map(item => ({
                    value: item.count || 0,
                    name: item.weather_condition || 'Unknown'
                })),
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        weatherImpactChart.setOption(weatherOption);
        window.addEventListener('resize', () => weatherImpactChart.resize());
    }
}

function initializeFilters() {
    const filterToggle = document.getElementById('toggleFilter');
    const filterContent = document.getElementById('filterContent');
    
    if (filterToggle && filterContent) {
        filterToggle.addEventListener('click', function() {
            const isVisible = filterContent.style.display !== 'none';
            filterContent.style.display = isVisible ? 'none' : 'block';
            
            const toggleText = filterToggle.querySelector('span');
            const toggleIcon = filterToggle.querySelector('i');
            
            if (toggleText) {
                toggleText.textContent = isVisible ? 'Show Filters' : 'Hide Filters';
            }
            if (toggleIcon) {
                toggleIcon.className = isVisible ? 'fas fa-chevron-down' : 'fas fa-chevron-up';
            }
        });
    }
    
    // Generate Report button
    const generateBtn = document.getElementById('generateReportBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            // Get current form and submit it
            const form = document.querySelector('.filter-container form') || document.querySelector('form');
            if (form) {
                form.submit();
            }
        });
    }
    
    // Reset Filters button
    const resetBtn = document.getElementById('resetFiltersBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            // Clear all form inputs
            const form = document.querySelector('.filter-container form') || document.querySelector('form');
            if (form) {
                form.reset();
                // Redirect to clean URL
                window.location.href = window.location.pathname;
            }
        });
    }
}

function initializeExportFunctions() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            window.location.reload();
        });
    }
    
    // Export PDF button
    const exportPdfBtn = document.getElementById('exportPdfBtn');
    if (exportPdfBtn) {
        exportPdfBtn.addEventListener('click', function() {
            exportToPDF();
        });
    }
    
    // Export CSV button
    const exportCsvBtn = document.getElementById('exportCsvBtn');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            exportToCSV();
        });
    }
    
    // Print button
    const printBtn = document.getElementById('printBtn');
    if (printBtn) {
        printBtn.addEventListener('click', function() {
            window.print();
        });
    }
}

function initializeModals() {
    // New Report Modal
    const newReportBtn = document.getElementById('newReportBtn');
    const newReportModal = document.getElementById('newReportModal');
    const closeNewReportModal = document.getElementById('closeNewReportModal');
    const cancelNewReportBtn = document.getElementById('cancelNewReportBtn');
    
    if (newReportBtn && newReportModal) {
        newReportBtn.addEventListener('click', function() {
            newReportModal.style.display = 'block';
        });
    }
    
    if (closeNewReportModal && newReportModal) {
        closeNewReportModal.addEventListener('click', function() {
            newReportModal.style.display = 'none';
        });
    }
    
    if (cancelNewReportBtn && newReportModal) {
        cancelNewReportBtn.addEventListener('click', function() {
            newReportModal.style.display = 'none';
        });
    }
    
    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === newReportModal) {
            newReportModal.style.display = 'none';
        }
    });
    
    // New Report Form
    const newReportForm = document.getElementById('newReportForm');
    if (newReportForm) {
        newReportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generateNewReport();
        });
    }
}

function exportToPDF() {
    // Create a simple PDF export
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.text('Admin Reports & Analytics', 20, 30);
    
    // Add date
    doc.setFontSize(12);
    doc.text('Generated on: ' + new Date().toLocaleDateString(), 20, 45);
    
    // Add summary data
    const summaryCards = document.querySelectorAll('.summary-card');
    let yPosition = 60;
    
    summaryCards.forEach(card => {
        const title = card.querySelector('.summary-title')?.textContent || '';
        const value = card.querySelector('.summary-value')?.textContent || '';
        
        doc.text(`${title}: ${value}`, 20, yPosition);
        yPosition += 15;
    });
    
    // Save the PDF
    doc.save('admin-reports-' + new Date().toISOString().split('T')[0] + '.pdf');
}

function exportToCSV() {
    // Get project data from the table
    const table = document.querySelector('.reports-section table');
    if (!table) return;
    
    let csv = 'Report ID,Project,Date Range,Type,Generated By,Created Date\n';
    
    const rows = table.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 6) {
            const rowData = Array.from(cells).slice(0, 6).map(cell => 
                '"' + cell.textContent.trim().replace(/"/g, '""') + '"'
            ).join(',');
            csv += rowData + '\n';
        }
    });
    
    // Download CSV
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'admin-reports-' + new Date().toISOString().split('T')[0] + '.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

function generateNewReport() {
    const form = document.getElementById('newReportForm');
    const formData = new FormData(form);
    
    // Show loading state
    const generateBtn = document.getElementById('generateNewReportBtn');
    const originalText = generateBtn.textContent;
    generateBtn.textContent = 'Generating...';
    generateBtn.disabled = true;
    
    // Simulate report generation
    setTimeout(() => {
        alert('Report generated successfully!');
        
        // Reset button
        generateBtn.textContent = originalText;
        generateBtn.disabled = false;
        
        // Close modal
        document.getElementById('newReportModal').style.display = 'none';
        
        // Reset form
        form.reset();
    }, 2000);
}

function generateReport(projectId) {
    // Generate report for specific project
    alert(`Generating report for project ID: ${projectId}`);
}

// Chart action handlers
document.addEventListener('click', function(e) {
    if (e.target.closest('.chart-action')) {
        const action = e.target.closest('.chart-action');
        const chartType = action.getAttribute('data-chart');
        
        if (action.title.includes('Download')) {
            downloadChart(chartType);
        } else if (action.title.includes('Expand')) {
            expandChart(chartType);
        }
    }
});

function downloadChart(chartType) {
    const chartElement = document.getElementById(chartType + 'Chart');
    if (chartElement) {
        // Check if it's an ECharts instance
        const echartsInstance = echarts.getInstanceByDom(chartElement);
        if (echartsInstance) {
            const link = document.createElement('a');
            link.download = chartType + '-chart.png';
            link.href = echartsInstance.getDataURL({
                type: 'png',
                pixelRatio: 2,
                backgroundColor: '#fff'
            });
            link.click();
        } else if (chartElement.tagName === 'CANVAS') {
            // Chart.js canvas
            const link = document.createElement('a');
            link.download = chartType + '-chart.png';
            link.href = chartElement.toDataURL();
            link.click();
        }
    }
}

function expandChart(chartType) {
    // Simple expand functionality - could be enhanced with a modal
    const chartContainer = document.getElementById(chartType + 'Chart').closest('.chart-container');
    if (chartContainer) {
        chartContainer.classList.toggle('expanded');
    }
}