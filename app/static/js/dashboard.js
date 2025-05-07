// Global variables for user selection
let allUsers = [];
let selectedUserIds = [];

// Expose loadDashboardData to window object so base.js can find and call it
window.loadDashboardData = function() {
    console.log('Loading dashboard data');
    
    const periodFilter = document.getElementById('period-filter');
    const chartTypeFilter = document.getElementById('chart-type-filter');
    
    if (!periodFilter || !chartTypeFilter) {
        console.error('Filter elements not found in the DOM');
        return;
    }
    
    const period = periodFilter.value;
    const chartType = chartTypeFilter.value;
    
    console.log(`Fetching data for period: ${period}, chart type: ${chartType}`);
    
    // Fetch duration data
    fetch(`/api/dashboard/duration?period=${period}`)
        .then(response => response.json())
        .then(data => {
            console.log('Duration data received:', data);
            
            // Update stats
            document.getElementById('total-duration').textContent = Math.round(data.total_study_time || 0);
            document.getElementById('today-learning').textContent = Math.round(data.today_study_time || 0);
            document.getElementById('today-learning-2').textContent = Math.round(data.today_study_time || 0);
            document.getElementById('average-duration').textContent = Math.round(data.avg_study_time || 0);
            
            // Render chart if duration type selected
            if (chartType === 'duration') {
                renderDurationChart(data);
            }
        })
        .catch(error => {
            console.error('Error fetching duration data:', error);
        });
    
    // Fetch task data if task chart selected
    if (chartType === 'task') {
        fetch(`/api/dashboard/task?period=${period}`)
            .then(response => response.json())
            .then(data => {
                console.log('Task data received:', data);
                renderTaskChart(data);
            })
            .catch(error => {
                console.error('Error fetching task data:', error);
            });
    }
};

// Function to render duration chart
function renderDurationChart(data) {
    console.log('Rendering duration chart with data:', data);
    const chartCanvas = document.getElementById('study-chart');
    
    if (!chartCanvas) {
        console.error('Chart canvas element not found');
        return;
    }
    
    const ctx = chartCanvas.getContext('2d');
    
    // Clear any existing chart
    if (window.studyChart) {
        window.studyChart.destroy();
    }
    
    // Process data for the chart
    const studyDurationsByDay = data.study_durations_by_day || {};
    const labels = [];
    const values = [];
    
    // Sort dates and extract data
    const sortedDates = Object.keys(studyDurationsByDay).sort();
    for (const date of sortedDates) {
        // Format date for display
        const displayDate = new Date(date).toLocaleDateString(undefined, {
            month: 'short',
            day: 'numeric'
        });
        labels.push(displayDate);
        values.push(studyDurationsByDay[date]);
    }
    
    // If no data, show empty chart
    if (labels.length === 0) {
        labels.push('No data');
        values.push(0);
    }
    
    console.log('Chart data prepared:', {labels, values});
    
    // Create chart
    window.studyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Study Minutes',
                data: values,
                backgroundColor: 'rgba(64, 173, 162, 0.7)',
                borderColor: 'rgba(64, 173, 162, 1)',
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
                        text: 'Minutes'
                    }
                }
            }
        }
    });
    
    console.log('Chart created successfully');
}

// Function to render task chart
function renderTaskChart(data) {
    console.log('Rendering task chart with data:', data);
    const chartCanvas = document.getElementById('study-chart');
    
    if (!chartCanvas) {
        console.error('Chart canvas element not found');
        return;
    }
    
    const ctx = chartCanvas.getContext('2d');
    
    // Clear any existing chart
    if (window.studyChart) {
        window.studyChart.destroy();
    }
    
    const taskSummary = data.task_summary || { open: 0, completed: 0, deleted: 0 };
    
    // Create chart
    window.studyChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Open Tasks', 'Completed Tasks', 'Deleted Tasks'],
            datasets: [{
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
            maintainAspectRatio: false
        }
    });
    
    console.log('Task chart created successfully');
}

// Function to open share modal
function openShareModal() {
    console.log('Opening share modal');
    
    // Reset selections
    selectedUserIds = [];
    document.getElementById('noUsersSelected').style.display = 'block';
    document.getElementById('selectedUsers').innerHTML = '<span id="noUsersSelected" class="text-muted small">No users selected</span>';
    
    // Initialize and show modal
    try {
        const shareModal = new bootstrap.Modal(document.getElementById('shareModal'));
        loadUsers();
        shareModal.show();
    } catch (error) {
        console.error('Error showing modal:', error);
        alert('Error: ' + error.message);
    }
}

// Function to load users
function loadUsers() {
    console.log('Loading users');
    const userList = document.getElementById('userList');
    
    userList.innerHTML = `
        <div class="d-flex align-items-center justify-content-center p-3">
            <div class="spinner-border spinner-border-sm text-secondary me-2" role="status"></div>
            <span>Loading users...</span>
        </div>
    `;
    
    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            console.log('Users loaded:', users);
            allUsers = users;
            
            if (users.length === 0) {
                userList.innerHTML = `<p class="text-center text-muted p-3">No users available</p>`;
                return;
            }
            
            // Render user list
            userList.innerHTML = '';
            
            users.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'form-check mb-2';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'form-check-input';
                checkbox.id = `user-${user.id}`;
                checkbox.value = user.id;
                
                checkbox.addEventListener('change', function() {
                    if (this.checked) {
                        if (!selectedUserIds.includes(user.id)) {
                            selectedUserIds.push(user.id);
                            updateSelectedUsers();
                        }
                    } else {
                        selectedUserIds = selectedUserIds.filter(id => id !== user.id);
                        updateSelectedUsers();
                    }
                });
                
                const label = document.createElement('label');
                label.className = 'form-check-label';
                label.htmlFor = `user-${user.id}`;
                label.textContent = user.username;
                
                userItem.appendChild(checkbox);
                userItem.appendChild(label);
                userList.appendChild(userItem);
            });
            
            // Setup search functionality
            const searchInput = document.getElementById('userSearchInput');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const searchTerm = this.value.toLowerCase();
                    filterUsers(searchTerm);
                });
            }
        })
        .catch(error => {
            console.error('Error loading users:', error);
            userList.innerHTML = `<p class="text-center text-danger p-3">Error loading users</p>`;
        });
}

// Filter users based on search term
function filterUsers(searchTerm) {
    const userCheckboxes = document.querySelectorAll('#userList .form-check');
    
    userCheckboxes.forEach(item => {
        const label = item.querySelector('.form-check-label');
        const username = label.textContent.toLowerCase();
        
        if (username.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Update selected users display
function updateSelectedUsers() {
    const selectedUsersContainer = document.getElementById('selectedUsers');
    const noUsersSelected = document.getElementById('noUsersSelected');
    
    if (selectedUserIds.length === 0) {
        selectedUsersContainer.innerHTML = '<span id="noUsersSelected" class="text-muted small">No users selected</span>';
        return;
    }
    
    selectedUsersContainer.innerHTML = '';
    
    selectedUserIds.forEach(userId => {
        const user = allUsers.find(u => u.id === userId);
        if (!user) return;
        
        const tag = document.createElement('span');
        tag.className = 'badge bg-info text-dark me-2 mb-2';
        tag.style.display = 'inline-flex';
        tag.style.alignItems = 'center';
        tag.style.padding = '5px 10px';
        tag.style.borderRadius = '16px';
        
        tag.innerHTML = `
            ${user.username}
            <button type="button" class="btn-close btn-close-white ms-2" 
                    style="font-size: 0.5rem;" aria-label="Remove"
                    onclick="removeUser(${userId})"></button>
        `;
        
        selectedUsersContainer.appendChild(tag);
    });
}

// Remove user from selection
function removeUser(userId) {
    const checkbox = document.getElementById(`user-${userId}`);
    if (checkbox) checkbox.checked = false;
    
    selectedUserIds = selectedUserIds.filter(id => id !== userId);
    updateSelectedUsers();
}

// Share data with selected users
function shareData() {
    console.log('Share data function called');
    
    if (selectedUserIds.length === 0) {
        alert('Please select at least one user to share with.');
        return;
    }
    
    const dataType = document.querySelector('input[name="dataType"]:checked').value;
    
    console.log('Sharing data:', dataType, 'with users:', selectedUserIds);
    
    // Prepare data to send
    const data = {
        dataType: dataType,
        users: selectedUserIds
    };
    
    // Send share request
    fetch('/api/share', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Share response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Share result:', result);
        
        if (result.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('shareModal'));
            if (modal) modal.hide();
            
            // Show success message
            alert('Data shared successfully! Recipients will see it in their notifications.');
        } else {
            alert('Failed to share data: ' + (result.message || 'Unknown error'));
        }
    })
    .catch(error => {
        console.error('Error sharing data:', error);
        alert('An error occurred while sharing data.');
    });
}

// Set up event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded in dashboard.js');
    
    // Load dashboard data if we're on the dashboard page
    if (typeof window.loadDashboardData === 'function') {
        window.loadDashboardData();
    }
    
    // Set up filter event listeners
    const periodFilter = document.getElementById('period-filter');
    const chartTypeFilter = document.getElementById('chart-type-filter');
    
    if (periodFilter) {
      periodFilter.addEventListener('change', () => {
          console.log('Period filter changed:', periodFilter.value);
          loadDashboardData();
      });
    } 

    if (chartTypeFilter) {
        chartTypeFilter.addEventListener('change', () => {
            console.log('Chart type filter changed:', chartTypeFilter.value);
            loadDashboardData();
        });
    }

  loadDashboardData(); 
});

window.bindDashboardFilters = function () {
  const periodFilter = document.getElementById('period-filter');
  const chartTypeFilter = document.getElementById('chart-type-filter');

  if (periodFilter) {
      periodFilter.addEventListener('change', loadDashboardData);
  }
  if (chartTypeFilter) {
      chartTypeFilter.addEventListener('change', loadDashboardData);
  }

  console.log('Dashboard filter event listeners bound.');
};
