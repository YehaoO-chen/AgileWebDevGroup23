window.loadAndDisplayData = loadAndDisplayData;

function initDashboardFeatures() {
    console.log("Initializing Dashboard Features...");

    const totalDurationEl = document.getElementById('total-duration');
    const todayLearningEl = document.getElementById('today-learning');
    const averageDurationEl = document.getElementById('average-duration');
    // Assuming 'today-learning-2' was a typo or for a different layout, focusing on the primary ones.
    // If 'today-learning-2' is essential, ensure it's handled.

    const periodFilter = document.getElementById('period-filter');
    const chartTypeFilter = document.getElementById('chart-type-filter'); // Assumes this ID exists
    const chartCanvas = document.getElementById('study-chart');

    let studyChartInstance = null; // To store the chart instance

    function renderDurationChart(data) {
        if (!chartCanvas) {
            console.error('Chart canvas element not found for duration chart');
            return;
        }
        const ctx = chartCanvas.getContext('2d');
        if (studyChartInstance) {
            studyChartInstance.destroy();
        }

        const studyDurationsByDay = data.study_durations_by_day || {};
        const labels = [];
        const values = [];

        // Sort dates and extract data
        const sortedDates = Object.keys(studyDurationsByDay).sort((a, b) => new Date(a) - new Date(b));
        
        sortedDates.forEach(date => {
            const displayDate = new Date(date);
            // Adjust formatting to be more suitable for a line chart axis
            labels.push(displayDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric' }));
            values.push(studyDurationsByDay[date]);
        });
        
        if (labels.length === 0) {
            labels.push('No data for period');
            values.push(0);
        }

        studyChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Study Minutes per Day',
                    data: values,
                    backgroundColor: 'rgba(64, 173, 162, 0.2)',
                    borderColor: 'rgba(64, 173, 162, 1)',
                    borderWidth: 2,
                    tension: 0.1, // Makes the line slightly curved
                    fill: true
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
                            text: 'Minutes'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                }
            }
        });
    }

    function renderTaskSummaryChart(data) {
        if (!chartCanvas) {
            console.error('Chart canvas element not found for task chart');
            return;
        }
        const ctx = chartCanvas.getContext('2d');
        if (studyChartInstance) {
            studyChartInstance.destroy();
        }

        const taskSummary = data.task_summary || { open: 0, completed: 0, deleted: 0 };

        studyChartInstance = new Chart(ctx, {
            type: 'pie', // Or 'doughnut'
            data: {
                labels: ['Open Tasks', 'Completed Tasks', 'Deleted Tasks'],
                datasets: [{
                    label: 'Task Status',
                    data: [taskSummary.open, taskSummary.completed, taskSummary.deleted],
                    backgroundColor: [
                        'rgba(255, 206, 86, 0.7)',  // Yellow for open
                        'rgba(75, 192, 192, 0.7)',  // Green for completed
                        'rgba(255, 99, 132, 0.7)'   // Red for deleted
                    ],
                    borderColor: [
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed !== null) {
                                    label += context.parsed;
                                }
                                return label;
                            }
                        }
                    }
                }
            }
        });
    }

    async function loadAndDisplayData() {
        if (!periodFilter || !chartTypeFilter) {
            console.error("Filter elements not found. Cannot load data.");
            return;
        }
        const period = periodFilter.value;
        const chartType = chartTypeFilter.value;

        console.log(`Fetching data for period: ${period}, chart type: ${chartType}`);

        // DOM elements
        const totalTasksEl = document.getElementById('total-tasks');
        const totalTasksCard = document.getElementById('total-tasks-card');

        try {
            // Duration Data - always fetch
            const durationResponse = await fetch(`/api/dashboard/duration?period=${period}`);
            if (durationResponse.ok) {
                const durationData = await durationResponse.json();
                if (totalDurationEl) totalDurationEl.textContent = Math.round(durationData.total_study_time || 0);
                if (todayLearningEl) todayLearningEl.textContent = Math.round(durationData.today_study_time || 0);
                if (averageDurationEl) averageDurationEl.textContent = Math.round(durationData.avg_study_time || 0);

                if (chartType === 'duration') {
                    renderDurationChart(durationData);
                    // ❌ Hide task card if shown
                    if (totalTasksCard) totalTasksCard.style.display = 'none';
                }
            } else {
                const errData = await durationResponse.json();
                console.error("Error fetching duration data:", errData);
            }

            // Task Data - only if selected
            if (chartType === 'task') {
                const taskResponse = await fetch(`/api/dashboard/task?period=${period}`);
                if (taskResponse.ok) {
                    const taskData = await taskResponse.json();
                    renderTaskSummaryChart(taskData);

                    // ✅ Set total task value
                    const taskSummary = taskData.task_summary || {};
                    const totalTasks = (taskSummary.open || 0) + (taskSummary.completed || 0) + (taskSummary.deleted || 0);
                    if (totalTasksEl) totalTasksEl.textContent = totalTasks;
                    if (totalTasksCard) totalTasksCard.style.display = 'block';
                } else {
                    const errData = await taskResponse.json();
                    console.error("Error fetching task data:", errData);
                    if (totalTasksCard) totalTasksCard.style.display = 'none';

                    if (studyChartInstance) {
                        studyChartInstance.destroy();
                        studyChartInstance = null;
                    }
                    if (chartCanvas) {
                        const ctx = chartCanvas.getContext('2d');
                        ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
                        ctx.fillText('Error loading task data.', chartCanvas.width / 2, chartCanvas.height / 2);
                    }
                }
            }

        } catch (error) {
            console.error('Error in loadAndDisplayData:', error);
            if (totalTasksCard) totalTasksCard.style.display = 'none';
        }
    }


    // Event Listeners for filters
    if (periodFilter) {
        periodFilter.addEventListener('change', loadAndDisplayData);
    }
    if (chartTypeFilter) {
        chartTypeFilter.addEventListener('change', loadAndDisplayData);
    }

    // Initial data load
    loadAndDisplayData();
    // ✅ Force load task summary to show total tasks regardless of chart type
    (async () => {
        const taskResponse = await fetch(`/api/dashboard/task?period=week`);
        if (taskResponse.ok) {
            const taskData = await taskResponse.json();
            const taskSummary = taskData.task_summary || {};
            const totalTasks = (taskSummary.open || 0) + (taskSummary.completed || 0) + (taskSummary.deleted || 0);
            const totalTasksEl = document.getElementById('total-tasks');
            const totalTasksCard = document.getElementById('total-tasks-card');
            if (totalTasksEl) totalTasksEl.textContent = totalTasks;
            if (totalTasksCard) totalTasksCard.style.display = 'block';
        }
    })();

    // Note: Share modal functionality (openShareModal, loadUsers, etc.)
    // is assumed to be handled by the sharemodal.js
    // or its own DOMContentLoaded listener. If not, those would also need to be
    // initialized here or ensured they are globally available.
}