/**
 * MITRE ATT&CK Intelligence Platform - Main Application Class
 * 
 * This is the main application orchestrator that coordinates all components
 * and handles the overall application lifecycle with proper error handling
 * and inter-component communication.
 */

class App {
    constructor() {
        this.components = {
            systemDashboard: null,
            toolsSection: null,
            resultsSection: null,
            smartFormControls: null,
            themeToggle: null
        };
        
        this.state = {
            initialized: false,
            connected: false,
            currentTool: null,
            errors: []
        };
        
        this.eventBus = new EventTarget();
        this.connectionCheckInterval = null;
        
        // Bind methods to maintain context
        this.initialize = this.initialize.bind(this);
        this.handleGlobalError = this.handleGlobalError.bind(this);
        this.checkConnection = this.checkConnection.bind(this);
    }
    
    /**
     * Initialize the application with proper error handling and recovery
     */
    async initialize() {
        console.log('🚀 Initializing MITRE ATT&CK Intelligence Platform...');
        
        try {
            // Set up global error handlers first
            this.setupGlobalErrorHandling();
            
            // Initialize components in proper dependency order
            await this.initializeComponents();
            
            // Set up inter-component communication
            this.setupInterComponentCommunication();
            
            // Start connection monitoring
            this.startConnectionMonitoring();
            
            // Set up application-level event listeners
            this.setupApplicationEventListeners();
            
            // Mark application as initialized
            this.state.initialized = true;
            
            console.log('✅ Application initialized successfully');
            this.notifyApplicationReady();
            
        } catch (error) {
            console.error('❌ Application initialization failed:', error);
            this.handleInitializationError(error);
        }
    }
    
    /**
     * Initialize all components in proper dependency order
     */
    async initializeComponents() {
        const initSteps = [
            {
                name: 'ThemeToggle',
                init: () => this.initializeThemeToggle()
            },
            {
                name: 'SystemDashboard',
                init: () => this.initializeSystemDashboard()
            },
            {
                name: 'ToolsSection',
                init: () => this.initializeToolsSection()
            },
            {
                name: 'ResultsSection',
                init: () => this.initializeResultsSection()
            },
            {
                name: 'SmartFormControls',
                init: () => this.initializeSmartFormControls(),
                optional: true // Non-critical component
            }
        ];
        
        for (const step of initSteps) {
            console.log(`Initializing ${step.name}...`);
            try {
                await step.init();
                console.log(`✅ ${step.name} initialized successfully`);
            } catch (error) {
                console.error(`❌ ${step.name} initialization failed:`, error);
                
                if (!step.optional) {
                    throw new Error(`Critical component ${step.name} failed to initialize: ${error.message}`);
                } else {
                    console.warn(`Optional component ${step.name} failed, continuing without it`);
                    this.state.errors.push(`${step.name}: ${error.message}`);
                }
            }
        }
    }
    
    /**
     * Initialize theme toggle component
     */
    async initializeThemeToggle() {
        if (typeof ThemeToggle !== 'undefined') {
            this.components.themeToggle = new ThemeToggle();
            // ThemeToggle initializes itself immediately
        } else {
            throw new Error('ThemeToggle class not available');
        }
    }
    
    /**
     * Initialize system dashboard component
     */
    async initializeSystemDashboard() {
        if (typeof SystemDashboard === 'undefined') {
            throw new Error('SystemDashboard class not available');
        }
        
        const dashboardContainer = document.getElementById('system-dashboard');
        if (!dashboardContainer) {
            throw new Error('System dashboard container not found');
        }
        
        this.components.systemDashboard = new SystemDashboard('system-dashboard');
        await this.components.systemDashboard.render();
    }
    
    /**
     * Initialize tools section component
     */
    async initializeToolsSection() {
        if (typeof ToolsSection === 'undefined') {
            throw new Error('ToolsSection class not available');
        }
        
        const toolsContainer = document.getElementById('tools-section');
        if (!toolsContainer) {
            throw new Error('Tools section container not found');
        }
        
        this.components.toolsSection = new ToolsSection('tools-section');
        await this.components.toolsSection.render();
    }
    
    /**
     * Initialize results section component
     */
    async initializeResultsSection() {
        if (typeof ResultsSection === 'undefined') {
            throw new Error('ResultsSection class not available');
        }
        
        const resultsContainer = document.getElementById('results-section');
        if (!resultsContainer) {
            throw new Error('Results section container not found');
        }
        
        this.components.resultsSection = new ResultsSection('results-section');
        // ResultsSection doesn't require async initialization
    }
    
    /**
     * Initialize smart form controls component
     */
    async initializeSmartFormControls() {
        if (typeof SmartFormControls === 'undefined') {
            throw new Error('SmartFormControls class not available');
        }
        
        this.components.smartFormControls = new SmartFormControls();
        await this.components.smartFormControls.initialize();
    }
    
    /**
     * Set up inter-component communication
     */
    setupInterComponentCommunication() {
        // Listen for tool execution requests from ToolsSection
        this.eventBus.addEventListener('toolExecutionRequested', (event) => {
            this.handleToolExecution(event.detail);
        });
        
        // Listen for result display requests
        this.eventBus.addEventListener('displayResult', (event) => {
            if (this.components.resultsSection) {
                this.components.resultsSection.displayResult(event.detail);
            }
        });
        
        // Listen for error notifications
        this.eventBus.addEventListener('componentError', (event) => {
            this.handleComponentError(event.detail);
        });
        
        // Set up cross-component event delegation
        if (this.components.toolsSection && this.components.resultsSection) {
            // Connect tools section to results section
            this.components.toolsSection.setResultsHandler(
                (result) => this.components.resultsSection.displayResult(result)
            );
        }
    }
    
    /**
     * Handle tool execution from any component
     */
    async handleToolExecution(toolData) {
        const { toolName, parameters, title } = toolData;
        
        if (!this.state.connected) {
            this.showError('Not connected to MCP server. Please check the connection.');
            return;
        }
        
        this.state.currentTool = toolName;
        
        try {
            // Show loading state
            if (this.components.resultsSection) {
                this.components.resultsSection.showLoading(title || `Executing ${toolName}`);
            }
            
            // Execute the tool via API
            const api = new API();
            const result = await api.callTool(toolName, parameters);
            
            // Display results
            if (this.components.resultsSection) {
                this.components.resultsSection.displayResult({
                    title: title || `${toolName} Results`,
                    content: result,
                    toolName: toolName,
                    parameters: parameters,
                    success: true
                });
            }
            
        } catch (error) {
            console.error(`Tool execution failed for ${toolName}:`, error);
            
            if (this.components.resultsSection) {
                this.components.resultsSection.displayResult({
                    title: `${toolName} Error`,
                    content: error.message,
                    toolName: toolName,
                    parameters: parameters,
                    success: false,
                    error: error
                });
            }
        } finally {
            this.state.currentTool = null;
        }
    }
    
    /**
     * Start connection monitoring
     */
    startConnectionMonitoring() {
        // Initial connection check
        this.checkConnection();
        
        // Set up periodic connection checking
        this.connectionCheckInterval = setInterval(() => {
            this.checkConnection();
        }, 30000); // Check every 30 seconds
    }
    
    /**
     * Check connection to MCP server
     */
    async checkConnection() {
        try {
            const response = await fetch('/tools');
            const wasConnected = this.state.connected;
            this.state.connected = response.ok;
            
            // Update UI connection status
            this.updateConnectionStatus(this.state.connected);
            
            // Notify of connection changes
            if (wasConnected !== this.state.connected) {
                this.eventBus.dispatchEvent(new CustomEvent('connectionChanged', {
                    detail: { connected: this.state.connected }
                }));
                
                if (this.state.connected && this.components.resultsSection) {
                    this.components.resultsSection.showToast(
                        'Connection Restored', 
                        'Successfully reconnected to MCP server', 
                        'success'
                    );
                }
            }
            
        } catch (error) {
            this.state.connected = false;
            this.updateConnectionStatus(false);
            console.warn('Connection check failed:', error);
        }
    }
    
    /**
     * Update connection status in UI
     */
    updateConnectionStatus(connected) {
        const indicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        
        if (indicator && statusText) {
            if (connected) {
                indicator.classList.remove('disconnected');
                indicator.classList.add('connected');
                statusText.textContent = 'Connected to MCP Server';
            } else {
                indicator.classList.remove('connected');
                indicator.classList.add('disconnected');
                statusText.textContent = 'Disconnected from MCP Server';
            }
        }
    }
    
    /**
     * Set up global error handling
     */
    setupGlobalErrorHandling() {
        window.addEventListener('error', this.handleGlobalError);
        window.addEventListener('unhandledrejection', this.handleGlobalError);
    }
    
    /**
     * Set up application-level event listeners
     */
    setupApplicationEventListeners() {
        // Listen for dashboard stat card clicks
        const dashboardContainer = document.getElementById('system-dashboard');
        if (dashboardContainer) {
            dashboardContainer.addEventListener('statCardClick', (event) => {
                this.handleStatCardClick(event.detail);
            });
        }
        
        // Listen for keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            this.handleKeyboardShortcuts(event);
        });
        
        // Listen for visibility changes to pause/resume connection monitoring
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseConnectionMonitoring();
            } else {
                this.resumeConnectionMonitoring();
            }
        });
    }
    
    /**
     * Handle dashboard stat card clicks
     */
    handleStatCardClick(detail) {
        const { statType, systemInfo } = detail;
        console.log(`Stat card clicked: ${statType}`, systemInfo);
        
        // Future enhancement: navigate to specific tool or filter based on stat type
        this.eventBus.dispatchEvent(new CustomEvent('statCardClicked', { detail }));
    }
    
    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(event) {
        // Ctrl/Cmd + K: Focus search
        if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
            event.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="search"], input[placeholder*="query"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape: Clear current operation
        if (event.key === 'Escape') {
            if (this.state.currentTool) {
                console.log('Canceling current operation');
                // Future enhancement: implement operation cancellation
            }
        }
    }
    
    /**
     * Pause connection monitoring (when tab is hidden)
     */
    pauseConnectionMonitoring() {
        if (this.connectionCheckInterval) {
            clearInterval(this.connectionCheckInterval);
            this.connectionCheckInterval = null;
        }
    }
    
    /**
     * Resume connection monitoring (when tab becomes visible)
     */
    resumeConnectionMonitoring() {
        if (!this.connectionCheckInterval) {
            this.startConnectionMonitoring();
        }
    }
    
    /**
     * Handle global application errors
     */
    handleGlobalError(event) {
        console.error('Global application error:', event);
        
        const errorDetail = {
            message: event.error?.message || event.reason?.message || 'Unknown error',
            stack: event.error?.stack || event.reason?.stack,
            timestamp: new Date().toISOString(),
            type: event.type
        };
        
        this.state.errors.push(errorDetail);
        
        // Don't show overlay for minor issues
        if (errorDetail.message && !errorDetail.message.includes('Failed to initialize')) {
            // Just log and optionally show toast notification
            if (this.components.resultsSection) {
                this.components.resultsSection.showToast(
                    'Application Error',
                    'An unexpected error occurred. Check console for details.',
                    'warning'
                );
            }
            return;
        }
        
        // Show critical error overlay for initialization failures
        this.showCriticalError(errorDetail.message);
    }
    
    /**
     * Handle component-specific errors
     */
    handleComponentError(errorDetail) {
        console.error('Component error:', errorDetail);
        this.state.errors.push({
            ...errorDetail,
            timestamp: new Date().toISOString()
        });
        
        if (this.components.resultsSection) {
            this.components.resultsSection.showToast(
                `${errorDetail.component} Error`,
                errorDetail.message,
                'danger'
            );
        }
    }
    
    /**
     * Handle initialization errors
     */
    handleInitializationError(error) {
        console.error('Initialization error:', error);
        this.showCriticalError(
            `Failed to initialize application: ${error.message}. Please refresh the page.`
        );
    }
    
    /**
     * Show critical application error overlay
     */
    showCriticalError(message) {
        const appContainer = document.getElementById('app') || document.body;
        
        // Create error overlay
        const errorOverlay = document.createElement('div');
        errorOverlay.className = 'error-overlay';
        errorOverlay.innerHTML = `
            <div class="container-fluid py-5">
                <div class="row justify-content-center">
                    <div class="col-md-8 col-lg-6">
                        <div class="alert alert-danger text-center shadow-lg">
                            <i class="bi bi-exclamation-triangle display-1 mb-3 text-danger"></i>
                            <h4 class="alert-heading">Application Error</h4>
                            <p class="mb-4">${message}</p>
                            <div class="d-grid gap-2 d-md-flex justify-content-md-center">
                                <button class="btn btn-outline-danger" onclick="location.reload()">
                                    <i class="bi bi-arrow-clockwise me-2"></i>Reload Application
                                </button>
                                <button class="btn btn-secondary" onclick="this.closest('.error-overlay').style.display='none'">
                                    <i class="bi bi-eye-slash me-2"></i>Dismiss
                                </button>
                            </div>
                            ${this.state.errors.length > 0 ? `
                                <div class="mt-3">
                                    <small class="text-muted">
                                        Recent errors: ${this.state.errors.length}
                                        <a href="#" onclick="console.log('Application errors:', ${JSON.stringify(this.state.errors)}); return false;" 
                                           class="text-muted ms-2">View in Console</a>
                                    </small>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add overlay styles
        errorOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        appContainer.appendChild(errorOverlay);
    }
    
    /**
     * Show non-critical error message
     */
    showError(message) {
        if (this.components.resultsSection) {
            this.components.resultsSection.displayResult({
                title: 'Error',
                content: message,
                success: false,
                timestamp: new Date().toISOString()
            });
        } else {
            console.error('Error:', message);
            alert(`Error: ${message}`);
        }
    }
    
    /**
     * Notify that application is ready
     */
    notifyApplicationReady() {
        // Dispatch application ready event
        this.eventBus.dispatchEvent(new CustomEvent('applicationReady', {
            detail: {
                components: Object.keys(this.components).filter(k => this.components[k] !== null),
                errors: this.state.errors,
                connected: this.state.connected
            }
        }));
        
        // Show success notification if there were non-critical errors during init
        if (this.state.errors.length > 0 && this.components.resultsSection) {
            this.components.resultsSection.showToast(
                'Application Ready',
                `Initialized with ${this.state.errors.length} non-critical warnings`,
                'warning'
            );
        }
    }
    
    /**
     * Get current application state
     */
    getState() {
        return { ...this.state };
    }
    
    /**
     * Get component instance
     */
    getComponent(componentName) {
        return this.components[componentName];
    }
    
    /**
     * Get event bus for inter-component communication
     */
    getEventBus() {
        return this.eventBus;
    }
    
    /**
     * Cleanup application resources
     */
    destroy() {
        // Clear connection monitoring
        if (this.connectionCheckInterval) {
            clearInterval(this.connectionCheckInterval);
        }
        
        // Remove global event listeners
        window.removeEventListener('error', this.handleGlobalError);
        window.removeEventListener('unhandledrejection', this.handleGlobalError);
        
        // Cleanup components
        Object.values(this.components).forEach(component => {
            if (component && typeof component.destroy === 'function') {
                component.destroy();
            }
        });
        
        console.log('Application cleaned up');
    }
}

// Global application instance
let app = null;

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', async function() {
    console.log('DOM loaded, starting application initialization...');
    
    try {
        // Create and initialize the application
        app = new App();
        await app.initialize();
        
        // Make app globally available for debugging and inter-component access
        window.app = app;
        
    } catch (error) {
        console.error('Failed to create application instance:', error);
        
        // Fallback error display if App class fails to instantiate
        const appContainer = document.getElementById('app') || document.body;
        appContainer.innerHTML = `
            <div class="container-fluid py-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="alert alert-danger text-center">
                            <i class="bi bi-exclamation-triangle display-1 mb-3"></i>
                            <h4>Critical Error</h4>
                            <p>Failed to start application: ${error.message}</p>
                            <button class="btn btn-outline-danger" onclick="location.reload()">
                                <i class="bi bi-arrow-clockwise me-2"></i>Reload Page
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { App };
}