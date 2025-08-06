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

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SystemDashboard;
} else if (typeof window !== 'undefined') {
    window.SystemDashboard = SystemDashboard;
}