/**
 * Smart Form Controls Component
 * 
 * Provides intelligent form population with dropdowns for threat groups,
 * tactics, and autocomplete for techniques. Includes form validation,
 * user feedback, and Bootstrap styling with responsive design.
 */
class SmartFormControls {
    constructor() {
        this.groupsData = [];
        this.tacticsData = [];
        this.techniquesCache = new Map();
        this.initialized = false;
        this.isLoading = false;
        this.hasError = false;
        this.errorMessage = '';
        
        // Configuration
        this.autocompleteMinLength = 2;
        this.autocompleteDelay = 300;
        this.maxSuggestions = 10;
        
        // Debounce timers
        this.debounceTimers = new Map();
        
        // Event listeners storage for cleanup
        this.eventListeners = new Map();
    }

    /**
     * Initialize smart form controls by loading data and setting up controls
     */
    async initialize() {
        if (this.initialized || this.isLoading) return;
        
        try {
            this.isLoading = true;
            this.hasError = false;
            
            console.log('Initializing smart form controls...');
            
            // Load data in parallel for better performance
            await Promise.all([
                this.loadGroups(),
                this.loadTactics()
            ]);
            
            // Setup form controls after data is loaded
            this.setupFormControls();
            
            this.initialized = true;
            this.isLoading = false;
            
            console.log('Smart form controls initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize smart form controls:', error);
            this.isLoading = false;
            this.hasError = true;
            this.errorMessage = error.message || 'Failed to initialize form controls';
            
            // Show error feedback to user
            this.showErrorFeedback('Failed to load form data. Some features may not work properly.');
        }
    }

    /**
     * Load threat groups data from API
     */
    async loadGroups() {
        try {
            console.log('Loading threat groups data...');
            const response = await api.getGroups();
            this.groupsData = Array.isArray(response) ? response : [];
            console.log(`Loaded ${this.groupsData.length} threat groups`);
        } catch (error) {
            console.error('Failed to load groups:', error);
            this.groupsData = [];
            throw new Error(`Failed to load threat groups: ${error.message}`);
        }
    }

    /**
     * Load tactics data from API
     */
    async loadTactics() {
        try {
            console.log('Loading tactics data...');
            const response = await api.getTactics();
            this.tacticsData = Array.isArray(response) ? response : [];
            console.log(`Loaded ${this.tacticsData.length} tactics`);
        } catch (error) {
            console.error('Failed to load tactics:', error);
            this.tacticsData = [];
            throw new Error(`Failed to load tactics: ${error.message}`);
        }
    }

    /**
     * Setup all form controls on the page
     */
    setupFormControls() {
        // Setup group dropdowns
        this.setupGroupDropdowns();
        
        // Setup tactic dropdowns
        this.setupTacticDropdowns();
        
        // Setup technique autocomplete
        this.setupTechniqueAutocomplete();
        
        // Setup form validation
        this.setupFormValidation();
        
        console.log('Form controls setup completed');
    }

    /**
     * Setup threat group dropdown controls
     */
    setupGroupDropdowns() {
        const groupSelects = document.querySelectorAll('.group-select, [data-smart-control="group"]');
        console.log(`Setting up ${groupSelects.length} group dropdowns`);
        
        groupSelects.forEach(select => {
            this.populateGroupSelect(select);
            this.addSearchFunctionality(select, this.groupsData);
        });
    }

    /**
     * Setup tactic dropdown controls
     */
    setupTacticDropdowns() {
        const tacticSelects = document.querySelectorAll('.tactic-select, [data-smart-control="tactic"]');
        console.log(`Setting up ${tacticSelects.length} tactic dropdowns`);
        
        tacticSelects.forEach(select => {
            this.populateTacticSelect(select);
        });
    }

    /**
     * Setup technique autocomplete controls
     */
    setupTechniqueAutocomplete() {
        const techniqueInputs = document.querySelectorAll('.technique-autocomplete, [data-smart-control="technique"]');
        console.log(`Setting up ${techniqueInputs.length} technique autocomplete inputs`);
        
        techniqueInputs.forEach(input => {
            this.setupAutocomplete(input);
        });
    }

    /**
     * Populate a group select element with data
     */
    populateGroupSelect(selectElement) {
        if (!selectElement) return;
        
        // Clear existing options except placeholder
        const placeholder = selectElement.querySelector('option[value=""]');
        selectElement.innerHTML = '';
        
        // Add placeholder
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder?.textContent || 'Select a threat group...';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        selectElement.appendChild(placeholderOption);
        
        // Add group options
        this.groupsData.forEach(group => {
            const option = document.createElement('option');
            option.value = group.id || group.name;
            
            // Create display name with aliases if available
            let displayName = group.name || group.id;
            if (group.aliases && group.aliases.length > 0) {
                displayName += ` (${group.aliases.slice(0, 2).join(', ')})`;
            }
            if (group.id && group.id !== group.name) {
                displayName += ` [${group.id}]`;
            }
            
            option.textContent = displayName;
            option.title = group.description || displayName;
            selectElement.appendChild(option);
        });
        
        // Add Bootstrap styling
        selectElement.classList.add('form-select');
        
        // Wrap in smart control container if not already wrapped
        if (!selectElement.parentElement.classList.contains('smart-form-control')) {
            this.wrapInSmartContainer(selectElement, 'bi-people-fill');
        }
    }

    /**
     * Populate a tactic select element with data
     */
    populateTacticSelect(selectElement) {
        if (!selectElement) return;
        
        // Clear existing options except placeholder
        const placeholder = selectElement.querySelector('option[value=""]');
        selectElement.innerHTML = '';
        
        // Add placeholder
        const placeholderOption = document.createElement('option');
        placeholderOption.value = '';
        placeholderOption.textContent = placeholder?.textContent || 'Select a tactic...';
        placeholderOption.disabled = true;
        placeholderOption.selected = true;
        selectElement.appendChild(placeholderOption);
        
        // Add tactic options
        this.tacticsData.forEach(tactic => {
            const option = document.createElement('option');
            option.value = tactic.id || tactic.name;
            
            // Create display name with proper formatting
            let displayName = tactic.name || tactic.id;
            if (tactic.id && tactic.id !== tactic.name) {
                displayName += ` (${tactic.id})`;
            }
            
            option.textContent = displayName;
            option.title = tactic.description || displayName;
            selectElement.appendChild(option);
        });
        
        // Add Bootstrap styling
        selectElement.classList.add('form-select');
        
        // Wrap in smart control container if not already wrapped
        if (!selectElement.parentElement.classList.contains('smart-form-control')) {
            this.wrapInSmartContainer(selectElement, 'bi-flag-fill');
        }
    }

    /**
     * Setup autocomplete functionality for technique inputs
     */
    setupAutocomplete(inputElement) {
        if (!inputElement) return;
        
        // Add Bootstrap styling
        inputElement.classList.add('form-control');
        
        // Create autocomplete container
        const container = this.createAutocompleteContainer(inputElement);
        
        // Setup event listeners
        this.setupAutocompleteEvents(inputElement, container);
        
        // Wrap in smart control container if not already wrapped
        if (!inputElement.parentElement.classList.contains('smart-form-control')) {
            this.wrapInSmartContainer(inputElement, 'bi-search');
        }
    }

    /**
     * Create autocomplete container and suggestions list
     */
    createAutocompleteContainer(inputElement) {
        // Check if container already exists
        let container = inputElement.parentElement.querySelector('.autocomplete-container');
        if (container) return container;
        
        // Create container
        container = document.createElement('div');
        container.className = 'autocomplete-container';
        
        // Create suggestions list
        const suggestions = document.createElement('div');
        suggestions.className = 'autocomplete-suggestions';
        suggestions.setAttribute('role', 'listbox');
        container.appendChild(suggestions);
        
        // Insert container after input
        inputElement.parentNode.insertBefore(container, inputElement.nextSibling);
        
        return container;
    }

    /**
     * Setup autocomplete event listeners
     */
    setupAutocompleteEvents(inputElement, container) {
        const suggestions = container.querySelector('.autocomplete-suggestions');
        let activeIndex = -1;
        
        // Input event for search
        const inputHandler = (event) => {
            const query = event.target.value.trim();
            
            if (query.length < this.autocompleteMinLength) {
                this.hideSuggestions(suggestions);
                return;
            }
            
            // Debounce the search
            this.debounceSearch(inputElement, query, suggestions);
        };
        
        // Keydown event for navigation
        const keydownHandler = (event) => {
            const suggestionItems = suggestions.querySelectorAll('.autocomplete-suggestion');
            
            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    activeIndex = Math.min(activeIndex + 1, suggestionItems.length - 1);
                    this.updateActiveSelection(suggestionItems, activeIndex);
                    break;
                    
                case 'ArrowUp':
                    event.preventDefault();
                    activeIndex = Math.max(activeIndex - 1, -1);
                    this.updateActiveSelection(suggestionItems, activeIndex);
                    break;
                    
                case 'Enter':
                    event.preventDefault();
                    if (activeIndex >= 0 && suggestionItems[activeIndex]) {
                        this.selectSuggestion(inputElement, suggestionItems[activeIndex], suggestions);
                    }
                    break;
                    
                case 'Escape':
                    this.hideSuggestions(suggestions);
                    activeIndex = -1;
                    break;
            }
        };
        
        // Focus event to show suggestions if input has value
        const focusHandler = (event) => {
            const query = event.target.value.trim();
            if (query.length >= this.autocompleteMinLength) {
                this.debounceSearch(inputElement, query, suggestions);
            }
        };
        
        // Blur event to hide suggestions (with delay for click handling)
        const blurHandler = () => {
            setTimeout(() => {
                this.hideSuggestions(suggestions);
                activeIndex = -1;
            }, 150);
        };
        
        // Add event listeners
        inputElement.addEventListener('input', inputHandler);
        inputElement.addEventListener('keydown', keydownHandler);
        inputElement.addEventListener('focus', focusHandler);
        inputElement.addEventListener('blur', blurHandler);
        
        // Store listeners for cleanup
        const listenerId = this.generateListenerId(inputElement);
        this.eventListeners.set(listenerId, {
            element: inputElement,
            listeners: [
                { event: 'input', handler: inputHandler },
                { event: 'keydown', handler: keydownHandler },
                { event: 'focus', handler: focusHandler },
                { event: 'blur', handler: blurHandler }
            ]
        });
    }

    /**
     * Debounce search requests to avoid excessive API calls
     */
    debounceSearch(inputElement, query, suggestions) {
        const timerId = this.generateListenerId(inputElement);
        
        // Clear existing timer
        if (this.debounceTimers.has(timerId)) {
            clearTimeout(this.debounceTimers.get(timerId));
        }
        
        // Set new timer
        const timer = setTimeout(async () => {
            try {
                await this.searchTechniques(query, suggestions, inputElement);
            } catch (error) {
                console.error('Autocomplete search failed:', error);
                this.showSearchError(suggestions);
            }
        }, this.autocompleteDelay);
        
        this.debounceTimers.set(timerId, timer);
    }

    /**
     * Search for techniques and display suggestions
     */
    async searchTechniques(query, suggestions, inputElement) {
        try {
            // Check cache first
            const cacheKey = query.toLowerCase();
            if (this.techniquesCache.has(cacheKey)) {
                const cachedResults = this.techniquesCache.get(cacheKey);
                this.displaySuggestions(cachedResults, suggestions, inputElement);
                return;
            }
            
            // Show loading state
            this.showLoadingState(suggestions);
            
            // Fetch from API
            const techniques = await api.getTechniques(query);
            
            // Cache results
            this.techniquesCache.set(cacheKey, techniques);
            
            // Display suggestions
            this.displaySuggestions(techniques, suggestions, inputElement);
            
        } catch (error) {
            console.error('Failed to search techniques:', error);
            this.showSearchError(suggestions);
        }
    }

    /**
     * Display technique suggestions
     */
    displaySuggestions(techniques, suggestions, inputElement) {
        // Clear existing suggestions
        suggestions.innerHTML = '';
        
        if (!techniques || techniques.length === 0) {
            this.showNoResults(suggestions);
            return;
        }
        
        // Limit results
        const limitedTechniques = techniques.slice(0, this.maxSuggestions);
        
        // Create suggestion items
        limitedTechniques.forEach((technique, index) => {
            const item = this.createSuggestionItem(technique, index);
            item.addEventListener('click', () => {
                this.selectSuggestion(inputElement, item, suggestions);
            });
            suggestions.appendChild(item);
        });
        
        // Show suggestions
        this.showSuggestions(suggestions);
    }

    /**
     * Create a suggestion item element
     */
    createSuggestionItem(technique, index) {
        const item = document.createElement('div');
        item.className = 'autocomplete-suggestion';
        item.setAttribute('role', 'option');
        item.setAttribute('data-index', index);
        item.setAttribute('data-value', technique.id || technique.name);
        
        // Create content with technique ID and name
        const content = document.createElement('div');
        const title = document.createElement('strong');
        title.textContent = technique.name || technique.id;
        content.appendChild(title);
        
        if (technique.id && technique.id !== technique.name) {
            const id = document.createElement('small');
            id.className = 'text-muted ms-2';
            id.textContent = `(${technique.id})`;
            content.appendChild(id);
        }
        
        if (technique.description) {
            const desc = document.createElement('div');
            desc.className = 'small text-muted';
            desc.textContent = technique.description.substring(0, 100) + (technique.description.length > 100 ? '...' : '');
            content.appendChild(desc);
        }
        
        item.appendChild(content);
        return item;
    }

    /**
     * Select a suggestion and update input
     */
    selectSuggestion(inputElement, suggestionItem, suggestions) {
        const value = suggestionItem.getAttribute('data-value');
        const text = suggestionItem.querySelector('strong').textContent;
        
        // Update input value
        inputElement.value = value;
        
        // Trigger change event
        inputElement.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Hide suggestions
        this.hideSuggestions(suggestions);
        
        // Show success feedback
        this.showSelectionFeedback(inputElement, text);
    }

    /**
     * Update active selection in suggestions
     */
    updateActiveSelection(suggestionItems, activeIndex) {
        suggestionItems.forEach((item, index) => {
            if (index === activeIndex) {
                item.classList.add('active');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('active');
            }
        });
    }

    /**
     * Show suggestions list
     */
    showSuggestions(suggestions) {
        suggestions.classList.add('show');
    }

    /**
     * Hide suggestions list
     */
    hideSuggestions(suggestions) {
        suggestions.classList.remove('show');
    }

    /**
     * Show loading state in suggestions
     */
    showLoadingState(suggestions) {
        suggestions.innerHTML = `
            <div class="autocomplete-suggestion">
                <div class="loading-spinner">
                    <div class="spinner-border spinner-border-sm" role="status"></div>
                    <span>Searching techniques...</span>
                </div>
            </div>
        `;
        this.showSuggestions(suggestions);
    }

    /**
     * Show no results message
     */
    showNoResults(suggestions) {
        suggestions.innerHTML = `
            <div class="autocomplete-suggestion">
                <div class="text-muted text-center">
                    <i class="bi bi-search me-2"></i>
                    No techniques found
                </div>
            </div>
        `;
        this.showSuggestions(suggestions);
    }

    /**
     * Show search error message
     */
    showSearchError(suggestions) {
        suggestions.innerHTML = `
            <div class="autocomplete-suggestion">
                <div class="text-danger text-center">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    Search failed. Please try again.
                </div>
            </div>
        `;
        this.showSuggestions(suggestions);
    }

    /**
     * Add search functionality to select elements
     */
    addSearchFunctionality(selectElement, data) {
        // This could be enhanced with a searchable dropdown library
        // For now, we'll add a title attribute for better UX
        selectElement.title = `Search among ${data.length} options`;
    }

    /**
     * Wrap form control in smart container with icon
     */
    wrapInSmartContainer(element, iconClass) {
        const parent = element.parentElement;
        
        // Create smart container
        const container = document.createElement('div');
        container.className = 'smart-form-control';
        
        // Move element into container
        parent.insertBefore(container, element);
        container.appendChild(element);
        
        // Add icon
        const icon = document.createElement('i');
        icon.className = `bi ${iconClass} form-icon`;
        container.appendChild(icon);
    }

    /**
     * Setup form validation for all forms
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!this.validateForm(form)) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => {
                    this.validateField(input);
                });
                
                input.addEventListener('input', () => {
                    if (input.classList.contains('is-invalid')) {
                        this.validateField(input);
                    }
                });
            });
        });
    }

    /**
     * Validate a form
     */
    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Validate a single field
     */
    validateField(field) {
        const isRequired = field.hasAttribute('required') || field.classList.contains('required');
        const value = field.value.trim();
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Type-specific validation
        if (value && field.type) {
            switch (field.type) {
                case 'email':
                    if (!this.isValidEmail(value)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid email address';
                    }
                    break;
                    
                case 'url':
                    if (!this.isValidUrl(value)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid URL';
                    }
                    break;
            }
        }
        
        // Update field state
        this.updateFieldValidation(field, isValid, errorMessage);
        
        return isValid;
    }

    /**
     * Update field validation state
     */
    updateFieldValidation(field, isValid, errorMessage) {
        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        // Add appropriate class
        if (isValid) {
            field.classList.add('is-valid');
        } else {
            field.classList.add('is-invalid');
        }
        
        // Update or create feedback element
        this.updateValidationFeedback(field, errorMessage, isValid);
    }

    /**
     * Update validation feedback message
     */
    updateValidationFeedback(field, message, isValid) {
        const feedbackClass = isValid ? 'valid-feedback' : 'invalid-feedback';
        let feedback = field.parentElement.querySelector(`.${feedbackClass}`);
        
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = feedbackClass;
            field.parentElement.appendChild(feedback);
        }
        
        feedback.textContent = message;
    }

    /**
     * Show error feedback to user
     */
    showErrorFeedback(message) {
        // Create toast notification
        this.showToast('Error', message, 'danger');
    }

    /**
     * Show selection feedback
     */
    showSelectionFeedback(inputElement, selectedText) {
        // Brief visual feedback
        inputElement.classList.add('is-valid');
        setTimeout(() => {
            inputElement.classList.remove('is-valid');
        }, 2000);
    }

    /**
     * Show toast notification
     */
    showToast(title, message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        
        // Create toast
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${title}:</strong> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        container.appendChild(toast);
        
        // Show toast
        const bsToast = new bootstrap.Toast(toast, { delay: 5000 });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    /**
     * Utility methods
     */
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidUrl(url) {
        try {
            new URL(url);
            return true;
        } catch {
            return false;
        }
    }

    generateListenerId(element) {
        return element.id || element.name || `element_${Date.now()}_${Math.random()}`;
    }

    /**
     * Refresh form controls data
     */
    async refresh() {
        this.initialized = false;
        this.techniquesCache.clear();
        await this.initialize();
    }

    /**
     * Get current data statistics
     */
    getDataStats() {
        return {
            groups: this.groupsData.length,
            tactics: this.tacticsData.length,
            techniquesCached: this.techniquesCache.size,
            initialized: this.initialized,
            hasError: this.hasError
        };
    }

    /**
     * Check if smart form controls are ready
     */
    isReady() {
        return this.initialized && !this.isLoading && !this.hasError;
    }

    /**
     * Clean up event listeners and resources
     */
    destroy() {
        // Clear debounce timers
        this.debounceTimers.forEach(timer => clearTimeout(timer));
        this.debounceTimers.clear();
        
        // Remove event listeners
        this.eventListeners.forEach(({ element, listeners }) => {
            listeners.forEach(({ event, handler }) => {
                element.removeEventListener(event, handler);
            });
        });
        this.eventListeners.clear();
        
        // Clear cache
        this.techniquesCache.clear();
        
        // Reset state
        this.initialized = false;
        this.isLoading = false;
        this.hasError = false;
        
        console.log('Smart form controls destroyed');
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SmartFormControls;
} else if (typeof window !== 'undefined') {
    window.SmartFormControls = SmartFormControls;
}