/**
 * TaskFlow - Task Management JavaScript
 * Handles task interactions, filtering, and AJAX operations
 */

// Wait for page to load before running JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('TaskFlow Tasks JS loaded');
    
    // Initialize all task functionality
    initializeFilters();
    initializeTaskToggle();
    initializeAnimations();
    initializeCharts();
});

/**
 * Auto-submit filters when user changes dropdowns
 */
function initializeFilters() {
    // Find all filter dropdown elements
    const filterSelects = document.querySelectorAll('select[name="status"], select[name="priority"], select[name="project_id"], select[name="sort"]');

    // Add change event to each dropdown
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            console.log('Filter changed:', this.name, '=', this.value);

            // Build clean URL parameters
            const params = new URLSearchParams();

            // Get all filter values
            const searchValue = document.querySelector('input[name="search"]')?.value?.trim();
            const statusValue = document.querySelector('select[name="status"]')?.value;
            const priorityValue = document.querySelector('select[name="priority"]')?.value;
            const projectValue = document.querySelector('select[name="project_id"]')?.value;
            const sortValue = document.querySelector('select[name="sort"]')?.value;

            // Only add non-empty values
            if (searchValue && searchValue !== '' && searchValue !== 'None') {
                params.append('search', searchValue);
            }
            if (statusValue && statusValue !== '') {
                params.append('status', statusValue);
            }
            if (priorityValue && priorityValue !== '') {
                params.append('priority', priorityValue);
            }
            if (projectValue && projectValue !== '') {
                params.append('project_id', projectValue);
            }
            if (sortValue && sortValue !== '') {
                params.append('sort', sortValue);
            }

            // Navigate to filtered URL
            const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
            window.location.href = newUrl;
        });
    });

    // Search input with debounce (wait for user to stop typing)
    const searchInput = document.querySelector('#topSearchInput');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            console.log('Search input changed:', this.value);

            // Wait 500ms after user stops typing, then submit with preserved filters
            searchTimeout = setTimeout(() => {
                // Build clean URL parameters
                const params = new URLSearchParams();

                // Get all filter values
                const searchValue = this.value?.trim();
                const statusValue = document.querySelector('select[name="status"]')?.value;
                const priorityValue = document.querySelector('select[name="priority"]')?.value;
                const projectValue = document.querySelector('select[name="project_id"]')?.value;
                const sortValue = document.querySelector('select[name="sort"]')?.value;

                // Only add non-empty values
                if (searchValue && searchValue !== '' && searchValue !== 'None') {
                    params.append('search', searchValue);
                }
                if (statusValue && statusValue !== '') {
                    params.append('status', statusValue);
                }
                if (priorityValue && priorityValue !== '') {
                    params.append('priority', priorityValue);
                }
                if (projectValue && projectValue !== '') {
                    params.append('project_id', projectValue);
                }
                if (sortValue && sortValue !== '') {
                    params.append('sort', sortValue);
                }

                // Navigate to filtered URL
                const newUrl = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
                window.location.href = newUrl;
            }, 500);
        });
    }
}

/**
 * Handle task completion toggle with AJAX
 */
function initializeTaskToggle() {
    // Find all toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-task');
    
    // Add click event to each button
    toggleButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.getAttribute('data-task-id');
            console.log('Toggling task:', taskId);
            toggleTask(taskId, this);
        });
    });
}

/**
 * Toggle task completion status via AJAX
 * @param {string} taskId - The ID of the task to toggle
 * @param {Element} buttonElement - The button that was clicked
 */
function toggleTask(taskId, buttonElement) {
    console.log('Starting toggle for task:', taskId);
    
    // Show loading state
    buttonElement.disabled = true;
    buttonElement.classList.add('opacity-50', 'cursor-not-allowed');
    
    // Get CSRF token (Django security requirement)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Make AJAX request to Django backend
    fetch(`/tasks/${taskId}/toggle/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        console.log('Response received:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        
        if (data.success) {
            // Update the UI without page reload
            updateTaskUI(buttonElement, data.completed);
            showToast(data.message, 'success');

            // Refresh charts with new data
            setTimeout(() => {
                const taskStats = getTaskStatsFromTemplate();
                updateCompletionPercentage(taskStats);
                // Note: Charts will need to be recreated for real-time updates
            }, 100);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error toggling task:', error);
        showToast('Something went wrong!', 'error');
    })
    .finally(() => {
        // Remove loading state
        buttonElement.disabled = false;
        buttonElement.classList.remove('opacity-50', 'cursor-not-allowed');
    });
}

/**
 * Update task UI after successful toggle
 * @param {Element} buttonElement - The toggle button
 * @param {boolean} completed - Whether task is now completed
 */
function updateTaskUI(buttonElement, completed) {
    const taskCard = buttonElement.closest('.bg-white\\/80');
    
    // Update button appearance
    if (completed) {
        // Task is now completed - show green checkmark
        buttonElement.classList.remove('border-gray-300');
        buttonElement.classList.add('bg-green-500', 'border-green-500');
        buttonElement.innerHTML = `
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        `;
    } else {
        // Task is now pending - show empty circle
        buttonElement.classList.remove('bg-green-500', 'border-green-500');
        buttonElement.classList.add('border-gray-300');
        buttonElement.innerHTML = '';
    }
    
    // Update task title and description styling
    const taskTitle = taskCard.querySelector('h3');
    const taskDescription = taskCard.querySelector('p');
    
    if (completed) {
        // Add strikethrough for completed tasks
        taskTitle.classList.add('line-through', 'text-gray-500');
        if (taskDescription) taskDescription.classList.add('line-through');
    } else {
        // Remove strikethrough for pending tasks
        taskTitle.classList.remove('line-through', 'text-gray-500');
        if (taskDescription) taskDescription.classList.remove('line-through');
    }
}

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showToast(message, type = 'success') {
    console.log('Showing toast:', message, type);
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 z-50 px-6 py-4 rounded-xl shadow-lg transform translate-x-full transition-transform duration-300 ${
        type === 'success' 
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
    }`;
    toast.textContent = message;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Slide in animation
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Slide out and remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

/**
 * Initialize page animations
 */
function initializeAnimations() {
    // Animate task cards on page load
    const taskCards = document.querySelectorAll('.bg-white\\/80');
    
    taskCards.forEach((card, index) => {
        // Start invisible and moved down
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        // Animate in with staggered timing
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100); // 100ms delay between each card
    });
}

/**
 * Initialize beautiful charts with Chart.js
 */
function initializeCharts() {
    console.log('Initializing charts...');

    // Wait a bit for DOM to be fully ready
    setTimeout(() => {
        // Get task statistics from Django template data
        const taskStats = getTaskStatsFromTemplate();

        // Update completion percentage
        updateCompletionPercentage(taskStats);

        // Create charts
        createCompletionChart(taskStats);
        createPriorityChart(taskStats);
        createWeeklyChart();
    }, 100);
}

/**
 * Calculate task statistics from the page
 */
/**
 * Get task statistics from Django template data (much more reliable)
 */
function getTaskStatsFromTemplate() {
    // Read the actual numbers from the stats cards (Django calculated these)
    const total = parseInt(document.getElementById('totalTasks')?.textContent || '0');
    const completed = parseInt(document.getElementById('completedTasks')?.textContent || '0');
    const pending = parseInt(document.getElementById('pendingTasks')?.textContent || '0');

    // Read priority data from hidden elements (Django calculated these)
    const priorities = {
        high: parseInt(document.getElementById('highPriorityCount')?.textContent || '0'),
        medium: parseInt(document.getElementById('mediumPriorityCount')?.textContent || '0'),
        low: parseInt(document.getElementById('lowPriorityCount')?.textContent || '0')
    };

    console.log('Task stats from template:', { total, completed, pending, priorities });
    return { total, completed, pending, priorities };
}

/**
 * Update completion percentage display
 */
function updateCompletionPercentage(stats) {
    const percentage = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0;
    const percentageElement = document.getElementById('completionPercentage');
    if (percentageElement) {
        percentageElement.textContent = percentage + '%';
    }
}

/**
 * Create beautiful completion donut chart
 */
function createCompletionChart(stats) {
    const ctx = document.getElementById('completionChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending'],
            datasets: [{
                data: [stats.completed, stats.pending],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',   // Green for completed
                    'rgba(249, 115, 22, 0.8)'   // Orange for pending
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(249, 115, 22, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 10
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
                        usePointStyle: true,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                }
            },
            cutout: '60%',
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

/**
 * Create priority distribution bar chart
 */
function createPriorityChart(stats) {
    const ctx = document.getElementById('priorityChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['High', 'Medium', 'Low'],
            datasets: [{
                label: 'Tasks by Priority',
                data: [stats.priorities.high, stats.priorities.medium, stats.priorities.low],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',   // Red for high
                    'rgba(245, 158, 11, 0.8)',  // Yellow for medium
                    'rgba(34, 197, 94, 0.8)'    // Green for low
                ],
                borderColor: [
                    'rgba(239, 68, 68, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(34, 197, 94, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            family: 'Inter'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Inter'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    });
}

/**
 * Create weekly progress line chart
 */
function createWeeklyChart() {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;

    // Get real weekly data from Django
    const weeklyDataElement = document.getElementById('weeklyData');
    const weeklyLabelsElement = document.getElementById('weeklyLabels');

    if (!weeklyDataElement || !weeklyLabelsElement) {
        console.log('Weekly data elements not found');
        return;
    }

    const weeklyDataStr = weeklyDataElement.textContent.trim();
    const weeklyLabelsStr = weeklyLabelsElement.textContent.trim();

    // Parse the data
    const weeklyData = weeklyDataStr ? weeklyDataStr.split(',').map(num => parseInt(num.trim())) : [0, 0, 0, 0, 0, 0, 0];
    const labels = weeklyLabelsStr ? weeklyLabelsStr.split(',').map(label => label.trim()) : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    console.log('Weekly chart data:', { weeklyData, labels });

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tasks Completed',
                data: weeklyData,
                borderColor: 'rgba(34, 197, 94, 1)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(34, 197, 94, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            return context[0].label;
                        },
                        label: function(context) {
                            const value = context.parsed.y;
                            return `${value} task${value !== 1 ? 's' : ''} completed`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            family: 'Inter'
                        },
                        callback: function(value) {
                            return Number.isInteger(value) ? value : '';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        font: {
                            family: 'Inter'
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            },
            interaction: {
                intersect: false,
                mode: 'index'
            }
        }
    });
}

/**
 * Utility function to get CSRF token
 * @returns {string} CSRF token value
 */
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}
