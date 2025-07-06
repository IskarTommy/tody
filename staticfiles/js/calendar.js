/**
 * Calendar JavaScript functionality
 * Handles calendar interactions, animations, and task management
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Calendar JS loaded');
    
    // Initialize calendar features
    initializeCalendarInteractions();
    initializeCalendarAnimations();
});

/**
 * Initialize calendar interactions
 */
function initializeCalendarInteractions() {
    // Add hover effects to calendar days
    const calendarDays = document.querySelectorAll('.grid.grid-cols-7.gap-1 > div');
    
    calendarDays.forEach(day => {
        // Skip empty days
        if (!day.textContent.trim() || day.textContent.trim() === '0') return;
        
        day.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'transform 0.2s ease-out';
        });
        
        day.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
        
        // Add click handler for days with tasks
        const taskCount = day.querySelector('.bg-indigo-100');
        if (taskCount) {
            day.style.cursor = 'pointer';
            day.addEventListener('click', function() {
                showDayTasks(this);
            });
        }
    });
    
    // Add smooth transitions to navigation buttons
    const navButtons = document.querySelectorAll('a[href*="month="]');
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Add loading animation
            this.style.opacity = '0.7';
            this.style.transform = 'scale(0.95)';
        });
    });
}

/**
 * Initialize calendar animations
 */
function initializeCalendarAnimations() {
    // Animate calendar grid appearance
    const calendarGrid = document.querySelector('.grid.grid-cols-7.gap-1');
    if (calendarGrid) {
        const days = calendarGrid.querySelectorAll('> div');
        
        days.forEach((day, index) => {
            day.style.opacity = '0';
            day.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                day.style.transition = 'all 0.4s ease-out';
                day.style.opacity = '1';
                day.style.transform = 'translateY(0)';
            }, index * 30);
        });
    }
    
    // Animate task cards
    const taskCards = document.querySelectorAll('.space-y-3 > div');
    taskCards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateX(0)';
        }, 800 + (index * 100));
    });
}

/**
 * Show tasks for a specific day (future enhancement)
 */
function showDayTasks(dayElement) {
    // Get the day number
    const dayNumber = dayElement.querySelector('span').textContent.trim();
    
    // Add visual feedback
    dayElement.style.backgroundColor = '#e0e7ff';
    dayElement.style.borderColor = '#6366f1';
    
    setTimeout(() => {
        dayElement.style.backgroundColor = '';
        dayElement.style.borderColor = '';
    }, 300);
    
    // Future: Could open a modal or sidebar with day's tasks
    console.log(`Clicked on day ${dayNumber}`);
}

/**
 * Calendar utility functions
 */
const CalendarUtils = {
    /**
     * Format date for display
     */
    formatDate: function(date) {
        const options = { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        return date.toLocaleDateString('en-US', options);
    },
    
    /**
     * Get current month and year
     */
    getCurrentMonthYear: function() {
        const now = new Date();
        return {
            month: now.getMonth() + 1,
            year: now.getFullYear()
        };
    },
    
    /**
     * Navigate to specific month
     */
    navigateToMonth: function(month, year) {
        const url = new URL(window.location);
        url.searchParams.set('month', month);
        url.searchParams.set('year', year);
        window.location.href = url.toString();
    },
    
    /**
     * Go to today's date
     */
    goToToday: function() {
        const today = this.getCurrentMonthYear();
        this.navigateToMonth(today.month, today.year);
    }
};

/**
 * Task interaction functions
 */
const TaskInteractions = {
    /**
     * Quick toggle task completion (if needed in future)
     */
    toggleTaskCompletion: function(taskId) {
        // Future implementation for quick task toggle from calendar
        console.log(`Toggle task ${taskId}`);
    },
    
    /**
     * Quick edit task (if needed in future)
     */
    quickEditTask: function(taskId) {
        // Future implementation for quick task editing
        console.log(`Quick edit task ${taskId}`);
    }
};

// Export for global access
window.CalendarUtils = CalendarUtils;
window.TaskInteractions = TaskInteractions;
