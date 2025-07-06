/**
 * TaskFlow - Project Management JavaScript
 * Handles project interactions and AJAX operations
 */

// Wait for page to load before running JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('TaskFlow Projects JS loaded');
    
    // Initialize project toggle functionality
    initializeProjectToggle();
});

/**
 * Handle project completion toggle with AJAX
 */
function initializeProjectToggle() {
    // Find all toggle buttons
    const toggleButtons = document.querySelectorAll('.toggle-project-status');
    
    // Add click event to each button
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const projectId = this.getAttribute('data-project-id');
            console.log('Toggling project:', projectId);
            toggleProject(projectId, this);
        });
    });
}

/**
 * Toggle project completion status via AJAX
 * @param {string} projectId - The ID of the project to toggle
 * @param {Element} buttonElement - The button that was clicked
 */
function toggleProject(projectId, buttonElement) {
    console.log('Starting toggle for project:', projectId);
    
    // Show loading state
    buttonElement.disabled = true;
    buttonElement.classList.add('opacity-50', 'cursor-not-allowed');
    
    // Get CSRF token (Django security requirement)
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Make AJAX request to Django backend
    fetch(`/projects/${projectId}/toggle/`, {
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
            updateProjectUI(buttonElement, projectId, data.completed);
            showToast(data.message, 'success');
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        console.error('Error toggling project:', error);
        showToast('Something went wrong!', 'error');
    })
    .finally(() => {
        // Reset button state
        buttonElement.disabled = false;
        buttonElement.classList.remove('opacity-50', 'cursor-not-allowed');
    });
}

/**
 * Update project UI after toggle
 * @param {Element} buttonElement - The button that was clicked
 * @param {string} projectId - The ID of the project
 * @param {boolean} completed - New completion status
 */
function updateProjectUI(buttonElement, projectId, completed) {
    // Update button text
    buttonElement.textContent = completed ? 'Mark as Active' : 'Mark as Completed';
    
    // Update status badge if it exists
    const statusBadge = document.getElementById(`project-status-${projectId}`);
    if (statusBadge) {
        statusBadge.textContent = completed ? 'Completed' : 'Active';
        
        if (completed) {
            statusBadge.classList.remove('bg-blue-100', 'text-blue-800');
            statusBadge.classList.add('bg-green-100', 'text-green-800');
        } else {
            statusBadge.classList.remove('bg-green-100', 'text-green-800');
            statusBadge.classList.add('bg-blue-100', 'text-blue-800');
        }
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
    
    // Remove after delay
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}