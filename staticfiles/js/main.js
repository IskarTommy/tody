/**
 * TaskFlow - Main JavaScript
 * Global functionality and utilities
 */

// Global TaskFlow object to avoid conflicts
window.TaskFlow = {
    // Configuration
    config: {
        debug: true,
        toastDuration: 3000,
        animationDelay: 100
    },
    
    // Utility functions
    utils: {
        /**
         * Log messages if debug is enabled
         */
        log: function(message, data = null) {
            if (TaskFlow.config.debug) {
                console.log('[TaskFlow]', message, data || '');
            }
        },
        
        /**
         * Get CSRF token for Django requests
         */
        getCSRFToken: function() {
            const token = document.querySelector('[name=csrfmiddlewaretoken]');
            return token ? token.value : '';
        },
        
        /**
         * Format date for display
         */
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        },
        
        /**
         * Debounce function calls
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },
    
    // UI components
    ui: {
        /**
         * Show loading spinner
         */
        showLoading: function(element) {
            element.disabled = true;
            element.classList.add('opacity-50', 'cursor-not-allowed');
        },
        
        /**
         * Hide loading spinner
         */
        hideLoading: function(element) {
            element.disabled = false;
            element.classList.remove('opacity-50', 'cursor-not-allowed');
        },
        
        /**
         * Animate element entrance
         */
        animateIn: function(element, delay = 0) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease-out';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, delay);
        }
    }
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    TaskFlow.utils.log('TaskFlow Main JS loaded');
    
    // Initialize global features
    initializeGlobalFeatures();
});

/**
 * Initialize features that work across all pages
 */
function initializeGlobalFeatures() {
    // Smooth scroll for anchor links
    initializeSmoothScroll();
    
    // Enhanced form interactions
    initializeFormEnhancements();
    
    // Keyboard shortcuts
    initializeKeyboardShortcuts();
}

/**
 * Smooth scrolling for anchor links
 */
function initializeSmoothScroll() {
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

/**
 * Enhanced form interactions
 */
function initializeFormEnhancements() {
    // Auto-focus first input in forms
    const firstInput = document.querySelector('form input:not([type="hidden"]):first-of-type');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Enhanced input focus effects
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('ring-2', 'ring-indigo-500');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('ring-2', 'ring-indigo-500');
        });
    });
}

/**
 * Keyboard shortcuts
 */
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Cmd/Ctrl + K for search
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="search"], input[placeholder*="Search"]');
            if (searchInput) {
                searchInput.focus();
                TaskFlow.utils.log('Search focused via keyboard shortcut');
            }
        }
        
        // Escape to close modals/dropdowns
        if (e.key === 'Escape') {
            const openDropdowns = document.querySelectorAll('.dropdown-open');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('dropdown-open');
            });
        }
    });
}
