/**
 * Tools Section Component
 * 
 * Dynamically generates forms for all 8 MCP tools with separation between
 * basic analysis tools and advanced threat modeling tools. Includes intelligent
 * form generation based on tool schemas, parameter processing, and validation.
 */
class ToolsSection {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.tools = [];
        this.isLoading = false;
        this.hasError = false;
        this.errorMessage = '';
        
        // Tool categories for proper separation
        this.basicToolNames = [
            'search_attack',
            'get_technique', 
            'list_tactics',
            'get_group_techniques',
            'get_technique_mitigations'
        ];
        
        this.advancedToolNames = [
            'build_attack_path',
            'analyze_coverage_gaps', 
            'detect_technique_relationships'
        ];
        
        if (!this.container) {
            throw new Error(`Container element with ID '${containerId}' not found`);
        }
    }
    
    /**
     * Render the tools section with all forms
     */
    async render() {
        try {
            this.isLoading = true;
            this.hasError = false;
            this.renderLoadingState();
            
            // Fetch tools information
            this.tools = await api.getTools();
            
            this.isLoading = false;
            this.renderToolsSection();
            this.setupEventListeners();
            
        } catch (error) {
            console.error('Failed to render tools section:', error);
            this.isLoading = false;
            this.hasError = true;
            this.errorMessage = error.message || 'Failed to load tools';
            this.renderError();
        }
    }
    
    /**
     * Render loading state
     */
    renderLoadingState() {
        this.container.innerHTML = `
            <div class="tools-section-loading">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <div class="loading-skeleton" style="height: 1.5rem; width: 180px;"></div>
                            </div>
                            <div class="card-body">
                                <div class="loading-skeleton mb-3" style="height: 4rem;"></div>
                                <div class="loading-skeleton mb-3" style="height: 4rem;"></div>
                                <div class="loading-skeleton" style="height: 4rem;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card">
                            <div class="card-header">
                                <div class="loading-skeleton" style="height: 1.5rem; width: 220px;"></div>
                            </div>
                            <div class="card-body">
                                <div class="loading-skeleton mb-3" style="height: 4rem;"></div>
                                <div class="loading-skeleton mb-3" style="height: 4rem;"></div>
                                <div class="loading-skeleton" style="height: 4rem;"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render error state
     */
    renderError() {
        this.container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <div class="d-flex align-items-center mb-2">
                    <i class="bi bi-exclamation-triangle-fill me-2"></i>
                    <strong>Failed to Load Tools</strong>
                </div>
                <p class="mb-3">${this.errorMessage}</p>
                <button type="button" class="btn btn-outline-danger" id="retry-tools">
                    <i class="bi bi-arrow-clockwise me-1"></i>
                    Retry
                </button>
            </div>
        `;
        
        // Setup retry button
        document.getElementById('retry-tools').addEventListener('click', () => {
            this.render();
        });
    }
    
    /**
     * Render the complete tools section
     */
    renderToolsSection() {
        const basicTools = this.tools.filter(tool => this.basicToolNames.includes(tool.name));
        const advancedTools = this.tools.filter(tool => this.advancedToolNames.includes(tool.name));
        
        this.container.innerHTML = `
            <div class="tools-section">
                <div class="row">
                    <!-- Basic Analysis Tools -->
                    <div class="col-lg-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header bg-primary text-white">
                                <h5 class="card-title mb-0">
                                    <i class="bi bi-search me-2"></i>
                                    Basic Analysis Tools
                                </h5>
                                <small class="opacity-75">Fundamental threat intelligence queries</small>
                            </div>
                            <div class="card-body">
                                ${this.renderToolsGroup(basicTools)}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Advanced Threat Modeling Tools -->
                    <div class="col-lg-6 mb-4">
                        <div class="card h-100">
                            <div class="card-header bg-success text-white">
                                <h5 class="card-title mb-0">
                                    <i class="bi bi-diagram-3 me-2"></i>
                                    Advanced Threat Modeling
                                </h5>
                                <small class="opacity-75">Complex analysis and relationship discovery</small>
                            </div>
                            <div class="card-body">
                                ${this.renderToolsGroup(advancedTools)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render a group of tools
     */
    renderToolsGroup(tools) {
        if (!tools || tools.length === 0) {
            return '<p class="text-muted">No tools available</p>';
        }
        
        return tools.map(tool => this.renderToolForm(tool)).join('');
    }
    
    /**
     * Render a single tool form
     */
    renderToolForm(tool) {
        const toolId = `tool-${tool.name}`;
        const isAdvanced = this.advancedToolNames.includes(tool.name);
        
        return `
            <div class="tool-form-container mb-4 pb-4 border-bottom">
                <div class="tool-header mb-3">
                    <h6 class="tool-title">
                        ${this.getToolIcon(tool.name)} ${this.formatToolName(tool.name)}
                        ${isAdvanced ? '<span class="badge bg-warning text-dark ms-2">Advanced</span>' : ''}
                    </h6>
                    <p class="tool-description text-muted small mb-2">
                        ${tool.description || 'No description available'}
                    </p>
                </div>
                
                <form class="tool-form" data-tool="${tool.name}" id="${toolId}">
                    ${this.generateFormFields(tool)}
                    <div class="form-actions mt-3">
                        <button type="submit" class="btn btn-primary btn-sm">
                            <i class="bi bi-play-fill me-1"></i>
                            Execute
                        </button>
                        <button type="reset" class="btn btn-outline-secondary btn-sm ms-2">
                            <i class="bi bi-arrow-clockwise me-1"></i>
                            Reset
                        </button>
                    </div>
                </form>
            </div>
        `;
    }
    
    /**
     * Generate form fields based on tool schema
     */
    generateFormFields(tool) {
        if (!tool.inputSchema || !tool.inputSchema.properties) {
            return '<p class="text-muted small">No parameters required</p>';
        }
        
        const properties = tool.inputSchema.properties;
        const required = tool.inputSchema.required || [];
        
        return Object.entries(properties).map(([key, prop]) => {
            const isRequired = required.includes(key);
            const fieldId = `${tool.name}-${key}`;
            
            return `
                <div class="mb-3">
                    <label for="${fieldId}" class="form-label">
                        ${this.formatFieldLabel(key)}
                        ${isRequired ? '<span class="text-danger">*</span>' : ''}
                    </label>
                    ${this.generateInputField(fieldId, key, prop, tool.name)}
                    ${prop.description ? `<div class="form-text">${prop.description}</div>` : ''}
                </div>
            `;
        }).join('');
    }
    
    /**
     * Generate appropriate input field based on property type
     */
    generateInputField(fieldId, key, prop, toolName) {
        const baseClasses = 'form-control';
        const smartControl = this.getSmartControlType(key);
        const classes = smartControl ? `${baseClasses} ${smartControl}` : baseClasses;
        
        // Check if field is required based on the tool schema
        const tool = this.tools.find(t => t.name === toolName);
        const isRequired = tool?.inputSchema?.required?.includes(key) || false;
        const requiredAttr = isRequired ? 'required' : '';
        
        if (prop.type === 'array') {
            return `
                <textarea 
                    class="${classes}" 
                    id="${fieldId}" 
                    name="${key}" 
                    rows="3" 
                    placeholder="Enter values separated by commas or new lines"
                    data-type="array"
                    ${requiredAttr}
                ></textarea>
            `;
        } else if (prop.enum && prop.enum.length > 0) {
            const options = prop.enum.map(value => 
                `<option value="${value}">${value}</option>`
            ).join('');
            return `
                <select class="form-select ${smartControl || ''}" id="${fieldId}" name="${key}" ${requiredAttr}>
                    <option value="">Select an option...</option>
                    ${options}
                </select>
            `;
        } else if (smartControl === 'technique-autocomplete') {
            // Technique fields should be input elements for autocomplete, not selects
            return `
                <input 
                    type="text" 
                    class="${classes}" 
                    id="${fieldId}" 
                    name="${key}" 
                    placeholder="${prop.description || 'Start typing technique name or ID...'}"
                    data-smart-control="technique"
                    ${requiredAttr}
                >
            `;
        } else if (smartControl) {
            return `
                <select class="form-select ${smartControl}" id="${fieldId}" name="${key}" data-smart-control="${smartControl.replace('-select', '')}" ${requiredAttr}>
                    <option value="">Select...</option>
                </select>
            `;
        } else if (prop.type === 'boolean') {
            return `
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="${fieldId}" name="${key}" ${requiredAttr}>
                    <label class="form-check-label" for="${fieldId}">
                        Enable
                    </label>
                </div>
            `;
        } else if (prop.type === 'number' || prop.type === 'integer') {
            return `
                <input 
                    type="number" 
                    class="${classes}" 
                    id="${fieldId}" 
                    name="${key}" 
                    placeholder="${prop.description || 'Enter a number'}"
                    ${prop.minimum ? `min="${prop.minimum}"` : ''}
                    ${prop.maximum ? `max="${prop.maximum}"` : ''}
                    ${requiredAttr}
                >
            `;
        } else {
            return `
                <input 
                    type="text" 
                    class="${classes}" 
                    id="${fieldId}" 
                    name="${key}" 
                    placeholder="${prop.description || 'Enter value'}"
                    ${requiredAttr}
                >
            `;
        }
    }
    
    /**
     * Get smart control type for field names
     */
    getSmartControlType(fieldName) {
        const lowerField = fieldName.toLowerCase();
        
        if (lowerField.includes('group')) {
            return 'group-select';
        } else if (lowerField.includes('tactic')) {
            return 'tactic-select';
        } else if (lowerField.includes('technique')) {
            return 'technique-autocomplete';
        }
        
        return null;
    }
    
    /**
     * Get appropriate icon for tool
     */
    getToolIcon(toolName) {
        const icons = {
            'search_attack': '<i class="bi bi-search"></i>',
            'get_technique': '<i class="bi bi-bullseye"></i>',
            'list_tactics': '<i class="bi bi-list-ul"></i>',
            'get_group_techniques': '<i class="bi bi-people-fill"></i>',
            'get_technique_mitigations': '<i class="bi bi-shield-check"></i>',
            'build_attack_path': '<i class="bi bi-diagram-2"></i>',
            'analyze_coverage_gaps': '<i class="bi bi-graph-up-arrow"></i>',
            'detect_technique_relationships': '<i class="bi bi-bezier2"></i>'
        };
        
        return icons[toolName] || '<i class="bi bi-gear"></i>';
    }
    
    /**
     * Format tool name for display
     */
    formatToolName(toolName) {
        return toolName
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    /**
     * Format field label for display
     */
    formatFieldLabel(key) {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }
    
    /**
     * Setup event listeners for form interactions
     */
    setupEventListeners() {
        const forms = this.container.querySelectorAll('.tool-form');
        
        forms.forEach(form => {
            // Form submission
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
            
            // Form reset
            form.addEventListener('reset', this.handleFormReset.bind(this));
            
            // Real-time validation
            const inputs = form.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('blur', () => this.validateField(input));
                input.addEventListener('input', () => {
                    if (input.classList.contains('is-invalid')) {
                        this.validateField(input);
                    }
                });
            });
        });
    }
    
    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const toolName = form.dataset.tool;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalBtnContent = submitBtn.innerHTML;
        
        try {
            // Validate form
            if (!this.validateForm(form)) {
                return;
            }
            
            // Show loading state
            this.setFormLoading(form, true);
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Executing...';
            submitBtn.disabled = true;
            
            // Collect and process parameters
            const parameters = this.collectFormParameters(form);
            
            // Call tool via API
            const result = await api.callTool(toolName, parameters);
            
            // Display result
            if (window.resultsSection) {
                window.resultsSection.displayResult(result, toolName);
            } else {
                console.log('Tool result:', result);
            }
            
            // Show success feedback
            this.showToast('Success', `${this.formatToolName(toolName)} executed successfully`, 'success');
            
        } catch (error) {
            console.error(`Tool execution failed:`, error);
            
            // Display error
            if (window.resultsSection) {
                window.resultsSection.displayError(`${this.formatToolName(toolName)}: ${error.message}`);
            }
            
            this.showToast('Error', `Failed to execute ${this.formatToolName(toolName)}: ${error.message}`, 'danger');
            
        } finally {
            // Reset loading state
            this.setFormLoading(form, false);
            submitBtn.innerHTML = originalBtnContent;
            submitBtn.disabled = false;
        }
    }
    
    /**
     * Handle form reset
     */
    handleFormReset(event) {
        const form = event.target;
        
        setTimeout(() => {
            // Clear validation states
            const fields = form.querySelectorAll('.form-control, .form-select');
            fields.forEach(field => {
                field.classList.remove('is-valid', 'is-invalid');
            });
            
            // Remove validation feedback
            const feedbacks = form.querySelectorAll('.invalid-feedback, .valid-feedback');
            feedbacks.forEach(feedback => feedback.remove());
            
            form.classList.remove('was-validated');
        }, 10);
    }
    
    /**
     * Collect and process form parameters
     */
    collectFormParameters(form) {
        const parameters = {};
        
        // Get all form fields 
        const allFields = form.querySelectorAll('input, select, textarea');
        
        allFields.forEach(field => {
            const key = field.name;
            
            if (!key) {
                return; // Skip fields without names
            }
            
            if (field.type === 'checkbox') {
                // Always include checkbox values (true/false)
                parameters[key] = field.checked;
            } else {
                // Get field value and trim whitespace
                let value = field.value;
                
                if (value !== null && value !== undefined && value.trim() !== '') {
                    const dataType = field.dataset?.type;
                    
                    if (dataType === 'array') {
                        // Handle array fields (comma or newline separated)
                        parameters[key] = value.split(/[,\n]/)
                            .map(v => v.trim())
                            .filter(v => v.length > 0);
                    } else if (field.type === 'number') {
                        parameters[key] = parseFloat(value);
                    } else {
                        parameters[key] = value.trim();
                    }
                }
            }
        });
        
        return parameters;
    }
    
    /**
     * Validate form before submission
     */
    validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        form.classList.add('was-validated');
        return isValid;
    }
    
    /**
     * Validate individual field
     */
    validateField(field) {
        const isRequired = field.hasAttribute('required') || 
                          field.labels?.[0]?.textContent?.includes('*');
        const value = field.type === 'checkbox' ? field.checked : field.value.trim();
        
        let isValid = true;
        let errorMessage = '';
        
        // Required field validation
        if (isRequired && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }
        
        // Type-specific validation
        if (value && field.dataset?.type === 'array') {
            const arrayValues = value.split(/[,\n]/).map(v => v.trim()).filter(v => v);
            if (arrayValues.length === 0) {
                isValid = false;
                errorMessage = 'Please provide at least one value';
            }
        }
        
        if (value && field.type === 'number') {
            const numValue = parseFloat(value);
            if (isNaN(numValue)) {
                isValid = false;
                errorMessage = 'Please enter a valid number';
            } else if (field.min && numValue < parseFloat(field.min)) {
                isValid = false;
                errorMessage = `Value must be at least ${field.min}`;
            } else if (field.max && numValue > parseFloat(field.max)) {
                isValid = false;
                errorMessage = `Value must be at most ${field.max}`;
            }
        }
        
        // Update field validation state
        this.updateFieldValidation(field, isValid, errorMessage);
        
        return isValid;
    }
    
    /**
     * Update field validation visual state
     */
    updateFieldValidation(field, isValid, errorMessage) {
        // Remove existing validation classes
        field.classList.remove('is-valid', 'is-invalid');
        
        // Add appropriate class
        if (field.value.trim() || field.type === 'checkbox') {
            field.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }
        
        // Update feedback message
        this.updateValidationFeedback(field, errorMessage, isValid);
    }
    
    /**
     * Update validation feedback message
     */
    updateValidationFeedback(field, message, isValid) {
        // Remove existing feedback
        const existingFeedback = field.parentElement.querySelector('.invalid-feedback, .valid-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        if (!isValid && message) {
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = message;
            field.parentElement.appendChild(feedback);
        }
    }
    
    /**
     * Set form loading state
     */
    setFormLoading(form, isLoading) {
        const fields = form.querySelectorAll('input, select, textarea, button');
        
        fields.forEach(field => {
            if (isLoading) {
                field.disabled = true;
                if (field.type !== 'submit') {
                    field.style.opacity = '0.6';
                }
            } else {
                field.disabled = false;
                field.style.opacity = '';
            }
        });
        
        if (isLoading) {
            form.classList.add('loading');
        } else {
            form.classList.remove('loading');
        }
    }
    
    /**
     * Show toast notification
     */
    showToast(title, message, type = 'info') {
        // Create toast container if it doesn't exist
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
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
        const bsToast = new bootstrap.Toast(toast, { delay: 4000 });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    /**
     * Get tools data
     */
    getTools() {
        return this.tools;
    }
    
    /**
     * Check if tools section is loading
     */
    isLoadingTools() {
        return this.isLoading;
    }
    
    /**
     * Check if tools section has error
     */
    hasErrorState() {
        return this.hasError;
    }
    
    /**
     * Refresh tools section
     */
    async refresh() {
        await this.render();
    }
    
    /**
     * Destroy and cleanup
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ToolsSection;
} else if (typeof window !== 'undefined') {
    window.ToolsSection = ToolsSection;
}