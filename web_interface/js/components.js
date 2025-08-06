/**
 * UI Components for MITRE ATT&CK Intelligence Platform
 * 
 * This module contains all the UI component classes for the web interface,
 * including the SystemDashboard, SmartFormControls, ToolsSection, and ResultsSection.
 */

/**
 * System Dashboard Component
 * 
 * Displays comprehensive system information including entity counts,
 * server information, and data statistics with professional styling
 * and responsive design.
 */
class SystemDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.systemInfo = null;
        this.isLoading = false;
        this.hasError = false;
        this.errorMessage = '';
        
        if (!this.container) {
            throw new Error(`Container element with ID '${containerId}' not found`);
        }
    }

    /**
     * Render the dashboard with loading state
     */
    async render() {
        try {
            this.isLoading = true;
            this.hasError = false;
            this.renderLoadingState();
            
            // Fetch system information
            this.systemInfo = await api.getSystemInfo();
            
            this.isLoading = false;
            this.renderDashboard();
            this.updateStats();
            
        } catch (error) {
            console.error('Failed to render dashboard:', error);
            this.isLoading = false;
            this.hasError = true;
            this.errorMessage = error.message || 'Failed to load system information';
            this.renderError();
        }
    }

    /**
     * Render loading state with skeleton cards
     */
    renderLoadingState() {
        this.container.innerHTML = this.getLoadingTemplate();
    }

    /**
     * Render error state with retry option
     */
    renderError() {
        this.container.innerHTML = this.getErrorTemplate();
        this.setupErrorEventListeners();
    }

    /**
     * Render the complete dashboard
     */
    renderDashboard() {
        this.container.innerHTML = this.getDashboardTemplate();
        this.setupEventListeners();
    }

    /**
     * Get the loading template with skeleton cards
     */
    getLoadingTemplate() {
        return `
            <div class="system-dashboard">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">
                        <i class="bi bi-shield-check me-2"></i>
                        MITRE ATT&CK Intelligence Platform
                    </h1>
                    <p class="dashboard-subtitle">Advanced Threat Intelligence Analysis & Exploration</p>
                </div>
                
                <div class="stats-grid">
                    ${this.getSkeletonStatCard('Techniques')}
                    ${this.getSkeletonStatCard('Tactics')}
                    ${this.getSkeletonStatCard('Threat Groups')}
                    ${this.getSkeletonStatCard('Mitigations')}
                    ${this.getSkeletonStatCard('Relationships')}
                    ${this.getSkeletonStatCard('Analysis Tools')}
                </div>
                
                <div class="server-info">
                    <div class="info-item">
                        <span class="info-label">Server Version</span>
                        <div class="loading-skeleton" style="height: 1.5rem; width: 80px;"></div>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Data Source</span>
                        <div class="loading-skeleton" style="height: 1.5rem; width: 120px;"></div>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last Updated</span>
                        <div class="loading-skeleton" style="height: 1.5rem; width: 100px;"></div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Get skeleton stat card for loading state
     */
    getSkeletonStatCard(label) {
        return `
            <div class="stat-card loading">
                <div class="loading-skeleton" style="height: 2.5rem; width: 60px; margin: 0 auto 0.5rem;"></div>
                <div class="stat-label">${label}</div>
            </div>
        `;
    }

    /**
     * Get error template with retry button
     */
    getErrorTemplate() {
        return `
            <div class="system-dashboard">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">
                        <i class="bi bi-shield-check me-2"></i>
                        MITRE ATT&CK Intelligence Platform
                    </h1>
                    <p class="dashboard-subtitle">Advanced Threat Intelligence Analysis & Exploration</p>
                </div>
                
                <div class="alert alert-danger" role="alert">
                    <div class="d-flex align-items-center mb-2">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        <strong>Failed to Load System Information</strong>
                    </div>
                    <p class="mb-3">${this.errorMessage}</p>
                    <button type="button" class="btn btn-outline-danger" id="retry-dashboard">
                        <i class="bi bi-arrow-clockwise me-1"></i>
                        Retry
                    </button>
                </div>
            </div>
        `;
    }

    /**
     * Get the main dashboard template
     */
    getDashboardTemplate() {
        return `
            <div class="system-dashboard">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">
                        <i class="bi bi-shield-check me-2"></i>
                        MITRE ATT&CK Intelligence Platform
                    </h1>
                    <p class="dashboard-subtitle">Advanced Threat Intelligence Analysis & Exploration</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card" data-stat="techniques">
                        <div class="stat-number" id="techniques-count">-</div>
                        <div class="stat-label">Techniques</div>
                    </div>
                    <div class="stat-card" data-stat="tactics">
                        <div class="stat-number" id="tactics-count">-</div>
                        <div class="stat-label">Tactics</div>
                    </div>
                    <div class="stat-card" data-stat="groups">
                        <div class="stat-number" id="groups-count">-</div>
                        <div class="stat-label">Threat Groups</div>
                    </div>
                    <div class="stat-card" data-stat="mitigations">
                        <div class="stat-number" id="mitigations-count">-</div>
                        <div class="stat-label">Mitigations</div>
                    </div>
                    <div class="stat-card" data-stat="relationships">
                        <div class="stat-number" id="relationships-count">-</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                    <div class="stat-card" data-stat="tools">
                        <div class="stat-number">8</div>
                        <div class="stat-label">Analysis Tools</div>
                    </div>
                </div>
                
                <div class="server-info">
                    <div class="info-item">
                        <span class="info-label">Server Version</span>
                        <span class="info-value" id="server-version">-</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Data Source</span>
                        <span class="info-value" id="data-source">-</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Last Updated</span>
                        <span class="info-value" id="last-updated">-</span>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Update statistics with data from system info
     */
    updateStats() {
        if (!this.systemInfo) return;

        try {
            const stats = this.systemInfo.data_statistics || {};
            
            // Update entity counts with animation
            this.animateStatUpdate('techniques-count', stats.techniques_count || 0);
            this.animateStatUpdate('tactics-count', stats.tactics_count || 0);
            this.animateStatUpdate('groups-count', stats.groups_count || 0);
            this.animateStatUpdate('mitigations-count', stats.mitigations_count || 0);
            this.animateStatUpdate('relationships-count', stats.relationships_count || 0);

            // Update server information
            const serverInfo = this.systemInfo.server_info || {};
            document.getElementById('server-version').textContent = serverInfo.version || 'Unknown';
            document.getElementById('data-source').textContent = serverInfo.data_source || 'Unknown';
            
            // Format and display last updated time
            const lastUpdated = serverInfo.startup_time ? 
                new Date(serverInfo.startup_time).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                }) : 'Unknown';
            document.getElementById('last-updated').textContent = lastUpdated;

        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    /**
     * Animate stat number updates with counting effect
     */
    animateStatUpdate(elementId, targetValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        const startValue = 0;
        const duration = 1000; // 1 second
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Use easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentValue = Math.floor(startValue + (targetValue - startValue) * easeOutQuart);
            
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                element.textContent = targetValue.toLocaleString();
            }
        };

        requestAnimationFrame(animate);
    }

    /**
     * Setup event listeners for dashboard interactions
     */
    setupEventListeners() {
        // Add hover effects for stat cards
        const statCards = this.container.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.addEventListener('mouseenter', this.handleStatCardHover.bind(this));
            card.addEventListener('mouseleave', this.handleStatCardLeave.bind(this));
        });

        // Add click handlers for stat cards (future enhancement)
        statCards.forEach(card => {
            card.addEventListener('click', this.handleStatCardClick.bind(this));
        });
    }

    /**
     * Setup event listeners for error state
     */
    setupErrorEventListeners() {
        const retryButton = document.getElementById('retry-dashboard');
        if (retryButton) {
            retryButton.addEventListener('click', () => {
                this.render();
            });
        }
    }

    /**
     * Handle stat card hover effect
     */
    handleStatCardHover(event) {
        const card = event.currentTarget;
        const statType = card.dataset.stat;
        
        // Add visual feedback
        card.style.transform = 'scale(1.05)';
        card.style.boxShadow = 'var(--shadow-lg)';
        
        // Show tooltip with additional information (future enhancement)
        this.showStatTooltip(card, statType);
    }

    /**
     * Handle stat card leave effect
     */
    handleStatCardLeave(event) {
        const card = event.currentTarget;
        
        // Reset visual state
        card.style.transform = '';
        card.style.boxShadow = '';
        
        // Hide tooltip
        this.hideStatTooltip();
    }

    /**
     * Handle stat card click
     */
    handleStatCardClick(event) {
        const card = event.currentTarget;
        const statType = card.dataset.stat;
        
        // Add click animation
        card.style.transform = 'scale(0.95)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);
        
        // Emit custom event for other components to listen to
        this.container.dispatchEvent(new CustomEvent('statCardClick', {
            detail: { statType, systemInfo: this.systemInfo }
        }));
    }

    /**
     * Show tooltip for stat card (placeholder for future enhancement)
     */
    showStatTooltip(card, statType) {
        // Future enhancement: show detailed information about the stat
        // For now, just add a title attribute
        const tooltips = {
            techniques: 'Attack techniques available in the dataset',
            tactics: 'Tactical objectives in the MITRE ATT&CK framework',
            groups: 'Known threat actor groups and campaigns',
            mitigations: 'Security controls and countermeasures',
            relationships: 'Connections between entities in the dataset',
            tools: 'Available analysis and exploration tools'
        };
        
        card.title = tooltips[statType] || '';
    }

    /**
     * Hide tooltip
     */
    hideStatTooltip() {
        // Remove any active tooltips
        const cards = this.container.querySelectorAll('.stat-card');
        cards.forEach(card => {
            card.removeAttribute('title');
        });
    }

    /**
     * Refresh dashboard data
     */
    async refresh() {
        await this.render();
    }

    /**
     * Get current system information
     */
    getSystemInfo() {
        return this.systemInfo;
    }

    /**
     * Check if dashboard is currently loading
     */
    isLoadingData() {
        return this.isLoading;
    }

    /**
     * Check if dashboard has an error
     */
    hasErrorState() {
        return this.hasError;
    }

    /**
     * Get current error message
     */
    getErrorMessage() {
        return this.errorMessage;
    }

    /**
     * Destroy the dashboard and clean up event listeners
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

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

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = { SystemDashboard, SmartFormControls };
} else {
    // Browser environment - attach to window
    window.SystemDashboard = SystemDashboard;
    window.SmartFormControls = SmartFormControls;
}