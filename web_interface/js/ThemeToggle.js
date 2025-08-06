/**
 * Theme Toggle Component
 * 
 * Provides dark/light mode switching functionality with persistence
 * to localStorage and smooth transitions between themes.
 */
class ThemeToggle {
    constructor() {
        this.currentTheme = localStorage.getItem('theme') || 'dark';
        this.toggleButton = null;
        this.themeIcon = null;
        
        // Initialize theme toggle when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.init();
            });
        } else {
            this.init();
        }
    }

    /**
     * Initialize the theme toggle functionality
     */
    init() {
        this.toggleButton = document.getElementById('theme-toggle');
        this.themeIcon = document.getElementById('theme-icon');
        
        if (!this.toggleButton || !this.themeIcon) {
            console.warn('Theme toggle elements not found');
            return;
        }

        // Set initial theme
        this.setTheme(this.currentTheme, false);
        
        // Add click event listener
        this.toggleButton.addEventListener('click', () => {
            this.toggle();
        });
        
        // Add keyboard accessibility
        this.toggleButton.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.toggle();
            }
        });

        console.log('Theme toggle initialized with theme:', this.currentTheme);
    }

    /**
     * Toggle between light and dark themes
     */
    toggle() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme, true);
    }

    /**
     * Set the theme
     * @param {string} theme - 'light' or 'dark'
     * @param {boolean} animate - Whether to show animation feedback
     */
    setTheme(theme, animate = true) {
        if (theme !== 'light' && theme !== 'dark') {
            console.error('Invalid theme:', theme);
            return;
        }

        this.currentTheme = theme;
        
        // Apply theme to document
        document.documentElement.setAttribute('data-bs-theme', theme);
        
        // Save to localStorage
        localStorage.setItem('theme', theme);
        
        // Update button icon and tooltip
        this.updateToggleButton(theme);
        
        // Show feedback animation
        if (animate) {
            this.showToggleFeedback();
        }

        // Dispatch custom event for other components
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: theme }
        }));

        console.log('Theme changed to:', theme);
    }

    /**
     * Update toggle button appearance
     * @param {string} theme - Current theme
     */
    updateToggleButton(theme) {
        if (!this.themeIcon || !this.toggleButton) return;

        if (theme === 'dark') {
            // In dark mode, show sun icon (to switch to light)
            this.themeIcon.className = 'bi bi-sun-fill';
            this.toggleButton.title = 'Switch to light mode';
        } else {
            // In light mode, show moon icon (to switch to dark)
            this.themeIcon.className = 'bi bi-moon-fill';
            this.toggleButton.title = 'Switch to dark mode';
        }
    }

    /**
     * Show visual feedback when theme is toggled
     */
    showToggleFeedback() {
        if (!this.toggleButton) return;

        // Add animation class
        this.toggleButton.style.transform = 'scale(0.9)';
        this.toggleButton.style.transition = 'transform 0.15s ease';
        
        setTimeout(() => {
            this.toggleButton.style.transform = 'scale(1)';
            setTimeout(() => {
                this.toggleButton.style.transform = '';
                this.toggleButton.style.transition = '';
            }, 150);
        }, 75);

        // Show toast notification
        this.showThemeToast();
    }

    /**
     * Show theme change notification
     */
    showThemeToast() {
        // Create toast notification
        const themeName = this.currentTheme === 'dark' ? 'Dark' : 'Light';
        const icon = this.currentTheme === 'dark' ? 'bi-moon-fill' : 'bi-sun-fill';
        
        // Check if there's a results section to use its toast method
        if (window.resultsSection && typeof window.resultsSection.showToast === 'function') {
            window.resultsSection.showToast(
                `${themeName} Mode`, 
                `Switched to ${themeName.toLowerCase()} mode`, 
                'info'
            );
        } else {
            // Fallback: create simple toast
            this.createSimpleToast(`Switched to ${themeName.toLowerCase()} mode`);
        }
    }

    /**
     * Create simple toast notification (fallback)
     */
    createSimpleToast(message) {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.theme-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'theme-toast-container position-fixed top-0 start-50 translate-middle-x mt-3';
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }

        // Create toast
        const toast = document.createElement('div');
        toast.className = 'alert alert-info alert-dismissible fade show';
        toast.innerHTML = `
            <i class="bi ${this.currentTheme === 'dark' ? 'bi-moon-fill' : 'bi-sun-fill'} me-2"></i>
            ${message}
        `;

        container.appendChild(toast);

        // Auto remove after 2 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 150);
        }, 2000);
    }

    /**
     * Get current theme
     * @returns {string} Current theme ('light' or 'dark')
     */
    getCurrentTheme() {
        return this.currentTheme;
    }

    /**
     * Check if current theme is dark
     * @returns {boolean} True if dark theme is active
     */
    isDarkMode() {
        return this.currentTheme === 'dark';
    }

    /**
     * Set theme programmatically
     * @param {string} theme - Theme to set
     */
    setThemeDirectly(theme) {
        this.setTheme(theme, false);
    }

    /**
     * Add theme change event listener
     * @param {Function} callback - Callback function to execute on theme change
     */
    onThemeChange(callback) {
        document.addEventListener('themeChanged', callback);
    }

    /**
     * Remove theme change event listener
     * @param {Function} callback - Callback function to remove
     */
    offThemeChange(callback) {
        document.removeEventListener('themeChanged', callback);
    }

    /**
     * Apply theme-specific styles to an element
     * @param {HTMLElement} element - Element to style
     * @param {Object} styles - Object with light and dark style objects
     */
    applyThemeStyles(element, styles) {
        if (!element || !styles) return;

        const themeStyles = styles[this.currentTheme];
        if (themeStyles) {
            Object.assign(element.style, themeStyles);
        }
    }

    /**
     * Destroy and cleanup
     */
    destroy() {
        if (this.toggleButton) {
            this.toggleButton.removeEventListener('click', this.toggle);
            this.toggleButton.removeEventListener('keydown', this.handleKeydown);
        }
        
        // Clean up any remaining toast containers
        const toastContainers = document.querySelectorAll('.theme-toast-container');
        toastContainers.forEach(container => {
            if (container.parentNode) {
                container.parentNode.removeChild(container);
            }
        });
    }
}

// Create global instance
const themeToggle = new ThemeToggle();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeToggle;
} else if (typeof window !== 'undefined') {
    window.ThemeToggle = ThemeToggle;
    window.themeToggle = themeToggle;
}