// Initialize charts when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeProjectDataFetching();
    initializeExportFunctions();
});

function initializeCharts() {
    // Check if data is available
    if (typeof window.reportsData === 'undefined') {
        console.warn('Reports data not available');
        return;
    }

    const data = window.reportsData;

    // Labor Hours Distribution Chart - Stacked Bar Chart
    const laborChart = document.getElementById('laborChart');
    if (laborChart && data.laborStats && data.laborStats.length > 0) {
        const laborEChart = echarts.init(laborChart);
        
        // Process labor data
        const laborTypes = data.laborStats.map(stat => stat.labor_type || 'Unknown');
        const laborHours = data.laborStats.map(stat => stat.total_hours || 0);
        
        const laborOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                axisPointer: { type: 'shadow' },
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            grid: { left: '10%', right: '10%', bottom: '15%', top: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                data: laborTypes,
                axisLabel: { color: '#666', fontSize: 12, rotate: 45 },
                axisLine: { lineStyle: { color: '#ddd' } }
            },
            yAxis: {
                type: 'value',
                name: 'Hours',
                axisLabel: { color: '#666', fontSize: 12 },
                axisLine: { lineStyle: { color: '#ddd' } },
                splitLine: { lineStyle: { color: '#f0f0f0' } }
            },
            series: [{
                name: 'Total Hours',
                type: 'bar',
                data: laborHours.map((hours, index) => ({
                    value: hours,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'][index % 5] },
                            { offset: 1, color: ['#764ba2', '#f5576c', '#00f2fe', '#38f9d7', '#fee140'][index % 5] }
                        ])
                    }
                }))
            }]
        };
        laborEChart.setOption(laborOption);
    }

    // Project Progress Tracking Chart - Timeline Chart
    const progressChart = document.getElementById('progressChart');
    if (progressChart && data.projectStats && data.projectStats.length > 0) {
        const progressEChart = echarts.init(progressChart);
        
        // Collect all progress entries from all projects
        let allDates = [];
        let seriesData = [];
        
        data.projectStats.forEach((stat, index) => {
            if (stat.progress_entries && stat.progress_entries.length > 0) {
                // Add dates to the master list
                stat.progress_entries.forEach(entry => {
                    if (!allDates.includes(entry.date)) {
                        allDates.push(entry.date);
                    }
                });
                
                // Create series for this project
                const projectData = allDates.map(date => {
                    const entry = stat.progress_entries.find(e => e.date === date);
                    return entry ? entry.progress : null;
                });
                
                seriesData.push({
                    name: stat.project.name.substring(0, 15),
                    type: 'line',
                    smooth: true,
                    connectNulls: false,
                    data: projectData,
                    lineStyle: {
                        color: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'][index % 5]
                    },
                    areaStyle: index === 0 ? {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
                            { offset: 1, color: 'rgba(118, 75, 162, 0.1)' }
                        ])
                    } : null
                });
            }
        });
        
        // Sort dates
        allDates.sort();
        
        const progressOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                bottom: 10,
                textStyle: { color: '#666' }
            },
            grid: { left: '10%', right: '10%', bottom: '20%', top: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                data: allDates,
                axisLabel: { color: '#666', fontSize: 12, rotate: 45 },
                axisLine: { lineStyle: { color: '#ddd' } }
            },
            yAxis: {
                type: 'value',
                name: 'Progress %',
                max: 100,
                axisLabel: { color: '#666', fontSize: 12 },
                axisLine: { lineStyle: { color: '#ddd' } },
                splitLine: { lineStyle: { color: '#f0f0f0' } }
            },
            series: seriesData
        };
        progressEChart.setOption(progressOption);
    }

    // Equipment Usage Hours Chart - Pie Chart
    const materialsChart = document.getElementById('materialsChart');
    if (materialsChart && data.equipmentStats && data.equipmentStats.length > 0) {
        const materialsEChart = echarts.init(materialsChart);
        
        // Process equipment data
        const equipmentData = data.equipmentStats.map((stat, index) => ({
            value: stat.total_hours || 0,
            name: stat.equipment_type || 'Unknown',
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                    { offset: 0, color: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'][index % 5] },
                    { offset: 1, color: ['#764ba2', '#f5576c', '#00f2fe', '#38f9d7', '#fee140'][index % 5] }
                ])
            }
        }));
        
        const materialsOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} hours ({d}%)',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                orient: 'horizontal',
                bottom: 10,
                textStyle: { color: '#666' }
            },
            series: [{
                name: 'Equipment Usage',
                type: 'pie',
                radius: ['40%', '70%'],
                center: ['50%', '45%'],
                data: equipmentData,
                label: {
                    show: true,
                    formatter: '{b}\n{d}%',
                    fontSize: 12,
                    color: '#333'
                },
                itemStyle: {
                    borderRadius: 6,
                    shadowBlur: 15,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                },
                emphasis: {
                    scale: true,
                    scaleSize: 8,
                    itemStyle: {
                        shadowBlur: 25,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        materialsEChart.setOption(materialsOption);
    }

    // Delay Analysis Chart - Rose/Nightingale Chart
    const delaysChart = document.getElementById('delaysChart');
    if (delaysChart && data.delayCategories && data.delayCategories.length > 0) {
        const delaysEChart = echarts.init(delaysChart);
        
        // Process delay data
        const delayData = data.delayCategories.map((delay, index) => ({
            value: delay.total_hours || 0,
            name: delay.category || 'Unknown',
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                    { offset: 0, color: ['#667eea', '#f093fb', '#4facfe', '#43e97b', '#fa709a'][index % 5] },
                    { offset: 1, color: ['#764ba2', '#f5576c', '#00f2fe', '#38f9d7', '#fee140'][index % 5] }
                ])
            }
        }));
        
        const delaysOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: {c} hours ({d}%)',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                orient: 'horizontal',
                bottom: 10,
                textStyle: { color: '#666' }
            },
            series: [{
                name: 'Delay Categories',
                type: 'pie',
                radius: [20, 110],
                center: ['50%', '45%'],
                roseType: 'area',
                data: delayData,
                label: {
                    show: true,
                    formatter: '{b}\n{c}h',
                    fontSize: 11,
                    color: '#333'
                },
                itemStyle: {
                    borderRadius: 6,
                    shadowBlur: 15,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                },
                emphasis: {
                    scale: true,
                    scaleSize: 5,
                    itemStyle: {
                        shadowBlur: 25,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        delaysEChart.setOption(delaysOption);
    }

    // Budget Usage Chart - Donut Chart
    const budgetChart = document.getElementById('budgetChart');
    if (budgetChart && data.projectStats && data.projectStats.length > 0) {
        const budgetEChart = echarts.init(budgetChart);
        
        // Calculate budget data from project stats
        let totalBudget = 0;
        let totalSpent = 0;
        
        data.projectStats.forEach(stat => {
            if (stat.project && stat.project.budget) {
                totalBudget += parseFloat(stat.project.budget) || 0;
            }
            totalSpent += (stat.total_labor_cost || 0) + (stat.total_material_cost || 0) + (stat.total_equipment_cost || 0);
        });
        
        const remaining = Math.max(0, totalBudget - totalSpent);
        
        const budgetOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                formatter: '{a} <br/>{b}: ₱{c} ({d}%)',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                orient: 'horizontal',
                bottom: 10,
                textStyle: { color: '#666' }
            },
            series: [{
                name: 'Budget Allocation',
                type: 'pie',
                radius: ['50%', '70%'],
                center: ['50%', '45%'],
                data: [
                    { 
                        value: totalSpent, 
                        name: 'Spent', 
                        itemStyle: { 
                            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                                { offset: 0, color: '#f093fb' },
                                { offset: 1, color: '#f5576c' }
                            ])
                        } 
                    },
                    { 
                        value: remaining, 
                        name: 'Remaining', 
                        itemStyle: { 
                            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                                { offset: 0, color: '#43e97b' },
                                { offset: 1, color: '#38f9d7' }
                            ])
                        } 
                    }
                ],
                label: {
                    show: true,
                    formatter: '{d}%',
                    fontSize: 12,
                    color: '#333'
                },
                itemStyle: {
                    borderRadius: 6,
                    shadowBlur: 15,
                    shadowColor: 'rgba(0, 0, 0, 0.3)'
                },
                emphasis: {
                    scale: true,
                    scaleSize: 8,
                    itemStyle: {
                        shadowBlur: 25,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        };
        budgetEChart.setOption(budgetOption);
    }

    // Safety & Quality Issues Chart - Bar Chart
    const safetyChart = document.getElementById('safetyChart');
    if (safetyChart && data.projectStats && data.projectStats.length > 0) {
        const safetyEChart = echarts.init(safetyChart);
        
        // Process safety and quality data from project stats
        const projectNames = data.projectStats.map(stat => stat.project.name.substring(0, 10) || 'Project');
        const safetyIncidents = data.projectStats.map(stat => stat.safety_incidents || 0);
        const qualityIssues = data.projectStats.map(stat => stat.quality_issues || 0);
        
        const safetyOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                data: ['Safety Incidents', 'Quality Issues'],
                bottom: 10,
                textStyle: { color: '#666' }
            },
            grid: { left: '10%', right: '10%', bottom: '15%', top: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                data: projectNames,
                axisLabel: { color: '#666', fontSize: 12, rotate: 45 },
                axisLine: { lineStyle: { color: '#ddd' } }
            },
            yAxis: {
                type: 'value',
                name: 'Incidents',
                axisLabel: { color: '#666', fontSize: 12 },
                axisLine: { lineStyle: { color: '#ddd' } },
                splitLine: { lineStyle: { color: '#f0f0f0' } }
            },
            series: [
                {
                    name: 'Safety Incidents',
                    type: 'bar',
                    data: safetyIncidents,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#f093fb' },
                            { offset: 1, color: '#f5576c' }
                        ])
                    }
                },
                {
                    name: 'Quality Issues',
                    type: 'bar',
                    data: qualityIssues,
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#667eea' },
                            { offset: 1, color: '#764ba2' }
                        ])
                    }
                }
            ]
        };
        safetyEChart.setOption(safetyOption);
    }

    // Weather Impact Chart - Radar Chart
    const weatherChart = document.getElementById('weatherChart');
    if (weatherChart && data.weatherStats && data.weatherStats.length > 0) {
        const weatherEChart = echarts.init(weatherChart);
        
        // Process weather data
        const weatherConditions = ['sunny', 'cloudy', 'rainy', 'stormy', 'foggy', 'windy'];
        const weatherCounts = weatherConditions.map(condition => {
            const stat = data.weatherStats.find(w => w.weather_condition === condition);
            return stat ? stat.count : 0;
        });
        
        const maxCount = Math.max(...weatherCounts, 10);
        
        const weatherOption = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'item',
                backgroundColor: '#fff',
                borderColor: '#ccc',
                textStyle: { color: '#333' }
            },
            legend: {
                data: ['Weather Conditions'],
                bottom: 10,
                textStyle: { color: '#666' }
            },
            radar: {
                indicator: [
                    { name: 'Sunny', max: maxCount },
                    { name: 'Cloudy', max: maxCount },
                    { name: 'Rainy', max: maxCount },
                    { name: 'Stormy', max: maxCount },
                    { name: 'Foggy', max: maxCount },
                    { name: 'Windy', max: maxCount }
                ],
                radius: '60%',
                axisName: {
                    color: '#666',
                    fontSize: 12
                }
            },
            series: [{
                name: 'Weather Conditions',
                type: 'radar',
                data: [
                    {
                        value: weatherCounts,
                        name: 'Days Count',
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 1, 1, [
                                { offset: 0, color: '#4facfe' },
                                { offset: 1, color: '#00f2fe' }
                            ])
                        },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(79, 172, 254, 0.3)' },
                                { offset: 1, color: 'rgba(0, 242, 254, 0.1)' }
                            ])
                        }
                    }
                ]
            }]
        };
        weatherEChart.setOption(weatherOption);
    }

    // Make charts responsive
    window.addEventListener('resize', () => {
        if (laborChart) echarts.getInstanceByDom(laborChart)?.resize();
        if (progressChart) echarts.getInstanceByDom(progressChart)?.resize();
        if (materialsChart) echarts.getInstanceByDom(materialsChart)?.resize();
        if (delaysChart) echarts.getInstanceByDom(delaysChart)?.resize();
        if (budgetChart) echarts.getInstanceByDom(budgetChart)?.resize();
        if (safetyChart) echarts.getInstanceByDom(safetyChart)?.resize();
        if (weatherChart) echarts.getInstanceByDom(weatherChart)?.resize();
    });
}

function initializeProjectDataFetching() {
    // Project data fetching
    const projectSelect = document.getElementById('project');
    if (projectSelect) {
        projectSelect.addEventListener('change', function() {
            const projectId = this.value;
            if (projectId) {
                fetch(`/diary/api/project-data/${projectId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            console.error('Error:', data.error);
                            return;
                        }
                        
                        // Update fields with project data
                        const locationField = document.getElementById('location');
                        const weatherField = document.getElementById('weather');
                        const contractorField = document.getElementById('contractor');
                        const dateFromField = document.getElementById('dateFrom');
                        const dateToField = document.getElementById('dateTo');
                        
                        if (locationField) locationField.value = data.location || '';
                        if (weatherField) weatherField.value = data.weather_condition || '';
                        if (contractorField) contractorField.value = data.contractor || '';
                        if (dateFromField) dateFromField.value = data.start_date || '';
                        if (dateToField) dateToField.value = data.end_date || '';
                    })
                    .catch(error => {
                        console.error('Error fetching project data:', error);
                    });
            } else {
                // Clear fields when no project selected
                const fields = ['location', 'weather', 'contractor', 'dateFrom', 'dateTo'];
                fields.forEach(fieldId => {
                    const field = document.getElementById(fieldId);
                    if (field) field.value = '';
                });
            }
        });
    }
}

function initializeExportFunctions() {
    // Generate report function
    window.generateReport = function(projectId) {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) {
            alert('CSRF token not found');
            return;
        }
        
        fetch(`/diary/api/generate-report/${projectId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken.value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error generating report: ' + data.error);
            } else {
                alert('Report generated successfully!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error generating report');
        });
    };
    
    // Export to PDF function
    window.exportToPDF = function() {
        window.print();
    };
    
    // Export to CSV function
    window.exportToCSV = function() {
        const table = document.querySelector('table');
        if (!table) {
            alert('No data to export');
            return;
        }
        
        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const row = [];
            const cols = rows[i].querySelectorAll('td, th');
            
            for (let j = 0; j < cols.length - 1; j++) { // Skip last column (Actions)
                let data = cols[j].innerText.replace(/,/g, ';');
                row.push('"' + data + '"');
            }
            csv.push(row.join(','));
        }
        
        const csvFile = new Blob([csv.join('\n')], { type: 'text/csv' });
        const downloadLink = document.createElement('a');
        downloadLink.download = 'site_diary_reports.csv';
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = 'none';
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);
    };
    
    // Print report function
    window.printReport = function() {
        const printContent = document.querySelector('.container').innerHTML;
        const originalContent = document.body.innerHTML;
        
        document.body.innerHTML = `
            <html>
                <head>
                    <title>Site Diary Reports</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; }
                        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                        th { background-color: #f5f5f5; }
                        .summary-section { display: flex; gap: 20px; margin: 20px 0; }
                        .summary-card { border: 1px solid #ddd; padding: 15px; flex: 1; }
                        .charts-section { display: none; }
                        .export-options { display: none; }
                        .filter-container { display: none; }
                    </style>
                </head>
                <body>
                    ${printContent}
                </body>
            </html>
        `;
        
        window.print();
        document.body.innerHTML = originalContent;
        location.reload();
    };
}

// Chart download functionality
function downloadChart(chartId, filename) {
    const chartInstance = echarts.getInstanceByDom(document.getElementById(chartId));
    if (chartInstance) {
        const url = chartInstance.getDataURL({
            type: 'png',
            pixelRatio: 2,
            backgroundColor: '#fff'
        });
        const link = document.createElement('a');
        link.download = filename || 'chart.png';
        link.href = url;
        link.click();
    }
}

// Add click handlers for chart download buttons
document.addEventListener('DOMContentLoaded', function() {
    const chartActions = document.querySelectorAll('.chart-action');
    chartActions.forEach(action => {
        if (action.title === 'Download Chart') {
            action.addEventListener('click', function() {
                const chartContainer = this.closest('.chart-container');
                const chartCanvas = chartContainer.querySelector('[id$="Chart"]');
                if (chartCanvas) {
                    const chartName = chartContainer.querySelector('.chart-title').textContent;
                    downloadChart(chartCanvas.id, `${chartName.replace(/\s+/g, '_')}.png`);
                }
            });
        }
    });
});