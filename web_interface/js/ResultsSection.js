/**
 * Results Section Component
 * 
 * Professional results display system with responsive output area, syntax highlighting,
 * copy/download functionality, timestamp display, error handling, toast notifications,
 * and intelligent accordion display with MITRE ATT&CK deep links.
 */
class ResultsSection {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentResult = null;
        this.resultHistory = [];
        this.maxHistorySize = 10;
        
        if (!this.container) {
            throw new Error(`Container element with ID '${containerId}' not found`);
        }
        
        // Make instance globally available for tool forms
        window.resultsSection = this;
        
        this.render();
    }
    
    /**
     * Initial render of results section
     */
    render() {
        this.container.innerHTML = `
            <div class="results-section">
                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="card-title mb-0">
                            <i class="bi bi-terminal me-2"></i>
                            Analysis Results
                        </h5>
                        <div class="btn-toolbar" role="toolbar">
                            <div class="btn-group me-2" role="group">
                                <button type="button" class="btn btn-outline-secondary btn-sm" id="copy-result" title="Copy to clipboard">
                                    <i class="bi bi-clipboard"></i>
                                </button>
                                <button type="button" class="btn btn-outline-secondary btn-sm" id="download-result" title="Download as file">
                                    <i class="bi bi-download"></i>
                                </button>
                                <button type="button" class="btn btn-outline-secondary btn-sm" id="clear-result" title="Clear results">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                            <div class="btn-group" role="group">
                                <button type="button" class="btn btn-outline-info btn-sm" id="toggle-history" title="Show history">
                                    <i class="bi bi-clock-history"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div class="card-body p-0">
                        <div class="output-area" id="output-area">
                            ${this.getPlaceholderContent()}
                        </div>
                    </div>
                </div>
                
                <!-- History Panel (Initially Hidden) -->
                <div class="card mt-3" id="history-panel" style="display: none;">
                    <div class="card-header">
                        <h6 class="card-title mb-0">
                            <i class="bi bi-clock-history me-2"></i>
                            Result History
                        </h6>
                    </div>
                    <div class="card-body" id="history-content">
                        <p class="text-muted">No previous results</p>
                    </div>
                </div>
            </div>
        `;
        
        this.setupEventListeners();
    }
    
    /**
     * Get placeholder content for empty state
     */
    getPlaceholderContent() {
        return `
            <div class="output-placeholder d-flex flex-column align-items-center justify-content-center py-5">
                <i class="bi bi-terminal display-1 text-muted mb-3"></i>
                <h6 class="text-muted mb-2">Ready for Analysis</h6>
                <p class="text-muted text-center">
                    Execute any tool above to see results here.<br>
                    Results will be formatted with syntax highlighting and timestamps.
                </p>
            </div>
        `;
    }
    
    /**
     * Setup event listeners for result actions
     */
    setupEventListeners() {
        // Copy button
        document.getElementById('copy-result').addEventListener('click', () => {
            this.copyToClipboard();
        });
        
        // Download button  
        document.getElementById('download-result').addEventListener('click', () => {
            this.downloadResult();
        });
        
        // Clear button
        document.getElementById('clear-result').addEventListener('click', () => {
            this.clearResults();
        });
        
        // History toggle
        document.getElementById('toggle-history').addEventListener('click', () => {
            this.toggleHistory();
        });
    }
    
    /**
     * Display a successful result
     */
    displayResult(result, toolName, timestamp = null) {
        const resultTimestamp = timestamp || new Date();
        
        // Store in history
        this.addToHistory(result, toolName, resultTimestamp);
        
        // Update current result
        this.currentResult = {
            data: result,
            toolName: toolName,
            timestamp: resultTimestamp,
            type: 'success'
        };
        
        // Render result
        const outputArea = document.getElementById('output-area');
        outputArea.innerHTML = this.getResultTemplate(result, toolName, resultTimestamp, 'success');
        
        // Enable action buttons
        this.updateActionButtons(true);
        
        // Scroll to results
        this.scrollToResults();
        
        // Show success toast
        this.showToast('Success', `${toolName} completed successfully`, 'success');
    }
    
    /**
     * Display an error result
     */
    displayError(error, toolName = null, timestamp = null) {
        const resultTimestamp = timestamp || new Date();
        const errorMessage = typeof error === 'string' ? error : error.message || 'Unknown error occurred';
        
        // Store in history
        this.addToHistory(errorMessage, toolName || 'Error', resultTimestamp, 'error');
        
        // Update current result
        this.currentResult = {
            data: errorMessage,
            toolName: toolName || 'Error',
            timestamp: resultTimestamp,
            type: 'error'
        };
        
        // Render error
        const outputArea = document.getElementById('output-area');
        outputArea.innerHTML = this.getErrorTemplate(errorMessage, toolName, resultTimestamp);
        
        // Enable action buttons
        this.updateActionButtons(true);
        
        // Scroll to results
        this.scrollToResults();
        
        // Show error toast
        this.showToast('Error', errorMessage, 'danger');
    }
    
    /**
     * Get result template for successful results
     */
    getResultTemplate(result, toolName, timestamp, type) {
        const formattedTimestamp = this.formatTimestamp(timestamp);
        const statusBadge = type === 'error' ? 'danger' : 'success';
        const statusIcon = type === 'error' ? 'bi-exclamation-triangle' : 'bi-check-circle';
        
        return `
            <div class="result-content">
                <div class="result-header p-3 bg-light border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <span class="badge bg-${statusBadge} me-2">
                                <i class="bi ${statusIcon} me-1"></i>
                                ${toolName}
                            </span>
                            <span class="text-muted small">
                                <i class="bi bi-clock me-1"></i>
                                ${formattedTimestamp}
                            </span>
                        </div>
                        <div class="result-stats text-muted small">
                            ${this.getResultStats(result)}
                        </div>
                    </div>
                </div>
                <div class="result-body">
                    ${type === 'error' ? 
                        `<div class="alert alert-danger m-3"><pre><code>${this.formatResult(result)}</code></pre></div>` : 
                        this.parseAndFormatResult(result, toolName)
                    }
                </div>
            </div>
        `;
    }
    
    /**
     * Parse and format result with collapsible sections and MITRE links
     */
    parseAndFormatResult(result, toolName) {
        try {
            // Split result into sections
            const sections = this.parseResultSections(result);
            
            if (sections.length <= 1) {
                // Simple result - no sections found, display as enhanced single block
                return this.formatSimpleResult(result);
            }
            
            // Multi-section result - create accordion
            return this.createAccordionResult(sections, toolName);
            
        } catch (error) {
            console.error('Error parsing result:', error);
            // Fallback to simple formatting
            return `<div class="alert alert-warning m-3">
                <h6>Result (Parsing Error)</h6>
                <pre class="mt-2"><code>${this.escapeHtml(result)}</code></pre>
            </div>`;
        }
    }

    /**
     * Parse result text into logical sections with enhanced intelligence
     */
    parseResultSections(result) {
        const text = String(result).trim();
        const sections = [];
        
        // Enhanced section patterns with capture groups for better parsing
        const sectionPatterns = [
            // Headers with underlines (GROUP TECHNIQUES, TECHNIQUE DETAILS, etc.)
            {
                pattern: /^([A-Z][A-Z\s&'-]+)$\n^={4,}$/gm,
                type: 'header'
            },
            // Numbered technique/item entries (1. T1055: Process Injection)
            {
                pattern: /^(\d+\.\s+([A-Z]\d+(?:\.\d+)?):?\s*([^:\n]+))(?::(.*))?$/gm,
                type: 'numbered_item'
            },
            // Technique entries without numbers (T1055: Process Injection)
            {
                pattern: /^(([A-Z]\d+(?:\.\d+)?):?\s*([^:\n]+)):?$/gm,
                type: 'technique_item'
            },
            // Field labels - disabled to prevent truncation of inline fields
            // {
            //     pattern: /^(Description|Techniques Used|Aliases|Mitigations|Platforms|Tactics|Groups):/gim,
            //     type: 'field'
            // }
        ];
        
        const sectionBoundaries = [];
        
        // Find all section boundaries with enhanced information
        sectionPatterns.forEach(patternObj => {
            let match;
            const pattern = patternObj.pattern;
            while ((match = pattern.exec(text)) !== null) {
                const boundary = {
                    start: match.index,
                    title: match[1].trim(),
                    titleEnd: match.index + match[0].length,
                    type: patternObj.type,
                    rawMatch: match
                };
                
                // Extract enhanced information based on type
                if (patternObj.type === 'numbered_item' || patternObj.type === 'technique_item') {
                    boundary.mitre_id = match[2]; // T1055
                    boundary.technique_name = match[3] ? match[3].trim() : ''; // Process Injection
                    if (match[4]) {
                        boundary.description = match[4].trim();
                    }
                }
                
                sectionBoundaries.push(boundary);
            }
        });
        
        // Sort boundaries by position
        sectionBoundaries.sort((a, b) => a.start - b.start);
        
        if (sectionBoundaries.length === 0) {
            return [{ 
                title: 'Result', 
                content: text,
                enhancedTitle: this.extractMainTitle(text)
            }];
        }
        
        // Create sections with enhanced titles
        for (let i = 0; i < sectionBoundaries.length; i++) {
            const boundary = sectionBoundaries[i];
            const nextBoundary = sectionBoundaries[i + 1];
            
            const sectionStart = boundary.titleEnd;
            const sectionEnd = nextBoundary ? nextBoundary.start : text.length;
            const content = text.substring(sectionStart, sectionEnd).trim();
            
            if (content || boundary.type === 'header') {
                const section = {
                    title: boundary.title,
                    content: content,
                    type: boundary.type,
                    enhancedTitle: this.createEnhancedTitle(boundary, content)
                };
                
                // Add MITRE identifier info if available
                if (boundary.mitre_id) {
                    section.mitre_id = boundary.mitre_id;
                    section.technique_name = boundary.technique_name;
                }
                
                sections.push(section);
            }
        }
        
        return sections;
    }

    /**
     * Extract main title from text for simple results
     */
    extractMainTitle(text) {
        const lines = text.split('\n');
        
        // Look for header patterns
        for (let i = 0; i < Math.min(lines.length, 5); i++) {
            const line = lines[i].trim();
            
            // Group name pattern
            const groupMatch = line.match(/^Group Name:\s*(.+)$/);
            if (groupMatch) {
                return groupMatch[1];
            }
            
            // Technique name pattern  
            const techMatch = line.match(/^Name:\s*(.+)$/);
            if (techMatch) {
                return techMatch[1];
            }
            
            // ID and name pattern
            const idNameMatch = line.match(/^(ID|Name):\s*([A-Z]\d+(?:\.\d+)?)\s*-?\s*(.*)$/);
            if (idNameMatch) {
                return idNameMatch[3] || idNameMatch[2];
            }
        }
        
        return 'Result';
    }

    /**
     * Create enhanced title for accordion headers
     */
    createEnhancedTitle(boundary, content) {
        if (boundary.type === 'numbered_item' || boundary.type === 'technique_item') {
            // For technique entries: "T1055: Process Injection"
            if (boundary.mitre_id && boundary.technique_name) {
                return `${boundary.mitre_id}: ${boundary.technique_name}`;
            }
        }
        
        if (boundary.type === 'header') {
            // For headers, try to extract meaningful context from content
            const contextInfo = this.extractContextFromContent(content);
            if (contextInfo) {
                return `${boundary.title} - ${contextInfo}`;
            }
        }
        
        // Field handling disabled to prevent truncation
        // if (boundary.type === 'field') {
        //     // For fields, try to extract key information
        //     const summary = this.extractFieldSummary(boundary.title, content);
        //     if (summary) {
        //         return `${boundary.title} (${summary})`;
        //     }
        // }
        
        return boundary.title;
    }

    /**
     * Extract context information from content
     */
    extractContextFromContent(content) {
        const lines = content.split('\n').map(line => line.trim()).filter(line => line);
        
        // Look for group name
        for (const line of lines.slice(0, 5)) {
            const groupMatch = line.match(/^Group Name:\s*(.+)$/);
            if (groupMatch) {
                return groupMatch[1];
            }
            
            const nameMatch = line.match(/^Name:\s*(.+)$/);
            if (nameMatch) {
                return nameMatch[1];
            }
        }
        
        // Look for counts in parentheses
        const countMatch = content.match(/\((\d+)\):/);
        if (countMatch) {
            return `${countMatch[1]} items`;
        }
        
        return null;
    }

    /**
     * Extract summary for field sections
     */
    extractFieldSummary(fieldTitle, content) {
        const lines = content.split('\n').filter(line => line.trim());
        
        if (fieldTitle.toLowerCase().includes('techniques')) {
            const countMatch = content.match(/\((\d+)\)/);
            if (countMatch) {
                return `${countMatch[1]} techniques`;
            }
        }
        
        if (fieldTitle.toLowerCase() === 'platforms' && lines.length > 0) {
            const platforms = lines[0].split(',').map(p => p.trim());
            return platforms.slice(0, 3).join(', ') + (platforms.length > 3 ? '...' : '');
        }
        
        if (fieldTitle.toLowerCase() === 'tactics' && lines.length > 0) {
            const tactics = lines.filter(line => line.includes('TA'));
            return `${tactics.length} tactics`;
        }
        
        return null;
    }

    /**
     * Create accordion-style result display with smart expansion
     */
    createAccordionResult(sections, toolName) {
        const accordionId = `accordion-${Date.now()}`;
        
        // Calculate smart expansion - expand all if total content is small enough
        const expansionConfig = this.calculateSmartExpansion(sections);
        
        const accordionItems = sections.map((section, index) => {
            const itemId = `${accordionId}-item-${index}`;
            const shouldExpand = expansionConfig.expandedItems.includes(index);
            
            // Use enhanced title if available, fallback to original title
            const displayTitle = section.enhancedTitle || section.title;
            
            return `
                <div class="accordion-item" data-section-type="${section.type || 'default'}">
                    <h2 class="accordion-header">
                        <button class="accordion-button ${shouldExpand ? '' : 'collapsed'}" type="button" 
                                data-bs-toggle="collapse" data-bs-target="#${itemId}" 
                                aria-expanded="${shouldExpand}" aria-controls="${itemId}">
                            <div class="accordion-title-content">
                                <div class="accordion-main-title">
                                    <strong>${this.escapeHtml(displayTitle)}</strong>
                                </div>
                                ${this.createAccordionSubtitle(section)}
                            </div>
                            ${this.getSectionBadge(section)}
                        </button>
                    </h2>
                    <div id="${itemId}" class="accordion-collapse collapse ${shouldExpand ? 'show' : ''}" 
                         data-bs-parent="#${accordionId}">
                        <div class="accordion-body">
                            ${this.formatSectionContent(section.content)}
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        return `
            <div class="accordion accordion-smart" id="${accordionId}" data-expansion-mode="${expansionConfig.mode}">
                <div class="accordion-info text-muted small mb-2">
                    ${expansionConfig.info}
                </div>
                ${accordionItems}
            </div>
        `;
    }

    /**
     * Calculate smart expansion logic
     */
    calculateSmartExpansion(sections) {
        const totalContentLength = sections.reduce((sum, section) => sum + section.content.length, 0);
        const averageContentLength = totalContentLength / sections.length;
        const viewportHeight = window.innerHeight || 800;
        const estimatedItemHeight = 120; // Base height per accordion item
        const availableHeight = viewportHeight * 0.6; // Use 60% of viewport
        
        // Calculate how many items can fit expanded
        const maxExpandableItems = Math.floor(availableHeight / (estimatedItemHeight + averageContentLength / 5));
        
        let mode, expandedItems, info;
        
        if (sections.length <= 3 && totalContentLength < 2000) {
            // Small result set - expand all
            mode = 'expand_all';
            expandedItems = sections.map((_, index) => index);
            info = `All ${sections.length} sections expanded (compact result)`;
        } else if (maxExpandableItems >= sections.length) {
            // Content fits - expand all
            mode = 'expand_all';
            expandedItems = sections.map((_, index) => index);
            info = `All ${sections.length} sections expanded (fits in view)`;
        } else if (maxExpandableItems >= 2) {
            // Expand first few sections
            mode = 'expand_first';
            expandedItems = Array.from({length: Math.min(maxExpandableItems, sections.length)}, (_, i) => i);
            info = `First ${expandedItems.length} of ${sections.length} sections expanded`;
        } else {
            // Large content - expand only first
            mode = 'expand_first_only';
            expandedItems = [0];
            info = `First section expanded (${sections.length} sections total)`;
        }
        
        return { mode, expandedItems, info };
    }

    /**
     * Create subtitle for accordion headers
     */
    createAccordionSubtitle(section) {
        if (section.type === 'numbered_item' && section.mitre_id) {
            // Extract tactic information from content
            const tacticMatch = section.content.match(/Tactics?:\s*([^\n]+)/i);
            if (tacticMatch) {
                const tactics = tacticMatch[1].split(',').map(t => t.trim()).slice(0, 2);
                return `<div class="accordion-subtitle text-muted">${tactics.join(', ')}</div>`;
            }
        }
        
        if (section.type === 'header' && section.content) {
            // For headers, show a preview of key information
            const lines = section.content.split('\n').slice(0, 3);
            const preview = lines.find(line => 
                line.includes('Group Name:') || 
                line.includes('Name:') || 
                line.includes('ID:')
            );
            if (preview) {
                const cleanPreview = preview.replace(/^[^:]*:\s*/, '').substring(0, 50);
                if (cleanPreview) {
                    return `<div class="accordion-subtitle text-muted">${this.escapeHtml(cleanPreview)}</div>`;
                }
            }
        }
        
        return '';
    }

    /**
     * Format simple result (no sections)
     */
    formatSimpleResult(result) {
        return `
            <div class="card m-3">
                <div class="card-body">
                    <div class="formatted-content">
                        ${this.formatSectionContent(result)}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Format section content with MITRE links and enhanced formatting
     */
    formatSectionContent(content) {
        let formatted = this.escapeHtml(content);
        
        // Add MITRE deep links
        formatted = this.addMitreDeepLinks(formatted);
        
        // Format lists and structure
        formatted = this.formatTextStructure(formatted);
        
        return formatted;
    }

    /**
     * Add MITRE ATT&CK deep links to identifiers
     */
    addMitreDeepLinks(text) {
        // Group IDs (G0001-G9999)
        text = text.replace(/\b(G\d{4})\b/g, 
            '<a href="https://attack.mitre.org/groups/$1" target="_blank" class="mitre-link mitre-group">$1 <i class="bi bi-box-arrow-up-right"></i></a>');
        
        // Technique IDs (T1001, T1001.001)
        text = text.replace(/\b(T\d{4}(?:\.\d{3})?)\b/g, 
            '<a href="https://attack.mitre.org/techniques/$1" target="_blank" class="mitre-link mitre-technique">$1 <i class="bi bi-box-arrow-up-right"></i></a>');
        
        // Tactic IDs (TA0001-TA0043)  
        text = text.replace(/\b(TA\d{4})\b/g, 
            '<a href="https://attack.mitre.org/tactics/$1" target="_blank" class="mitre-link mitre-tactic">$1 <i class="bi bi-box-arrow-up-right"></i></a>');
        
        // Mitigation IDs (M1001-M1999)
        text = text.replace(/\b(M\d{4})\b/g, 
            '<a href="https://attack.mitre.org/mitigations/$1" target="_blank" class="mitre-link mitre-mitigation">$1 <i class="bi bi-box-arrow-up-right"></i></a>');
        
        // Software IDs (S0001-S9999) 
        text = text.replace(/\b(S\d{4})\b/g, 
            '<a href="https://attack.mitre.org/software/$1" target="_blank" class="mitre-link mitre-software">$1 <i class="bi bi-box-arrow-up-right"></i></a>');
        
        return text;
    }

    /**
     * Format text structure (lists, paragraphs, etc.)
     */
    formatTextStructure(text) {
        // Convert numbered lists to proper HTML lists
        let formatted = text.replace(/^(\d+\.\s+)(.+)$/gm, '<li><strong>$1</strong>$2</li>');
        if (formatted.includes('<li>')) {
            formatted = '<ol class="formatted-list">' + formatted.replace(/^(?!<li>)/gm, '') + '</ol>';
        }
        
        // Convert double newlines to paragraphs
        formatted = formatted.split('\n\n').map(para => {
            para = para.trim();
            if (para && !para.includes('<ol') && !para.includes('<li>')) {
                return `<p>${para.replace(/\n/g, '<br>')}</p>`;
            }
            return para;
        }).join('\n');
        
        // Format field labels (Description:, Platforms:, etc.)
        formatted = formatted.replace(/^([A-Z][a-z\s]+):(.+)$/gm, 
            '<div class="field-group"><span class="field-label">$1:</span><span class="field-value">$2</span></div>');
        
        return formatted;
    }

    /**
     * Get badge for section based on content
     */
    getSectionBadge(section) {
        const content = section.content.toLowerCase();
        let count = 0;
        let type = 'secondary';
        
        // Count techniques
        const techniqueMatches = section.content.match(/\bT\d{4}(?:\.\d{3})?\b/g);
        if (techniqueMatches) {
            count = techniqueMatches.length;
            type = 'primary';
        }
        
        // Count groups
        const groupMatches = section.content.match(/\bG\d{4}\b/g);
        if (groupMatches) {
            count = Math.max(count, groupMatches.length);
            type = 'success';
        }
        
        // Count mitigations
        const mitigationMatches = section.content.match(/\bM\d{4}\b/g);
        if (mitigationMatches) {
            count = Math.max(count, mitigationMatches.length);
            type = 'info';
        }
        
        if (count > 0) {
            return `<span class="badge bg-${type} ms-2">${count}</span>`;
        }
        
        return '';
    }

    /**
     * Get error template
     */
    getErrorTemplate(error, toolName, timestamp) {
        const formattedTimestamp = this.formatTimestamp(timestamp);
        
        return `
            <div class="result-content">
                <div class="result-header p-3 bg-danger text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center">
                            <span class="badge bg-light text-danger me-2">
                                <i class="bi bi-exclamation-triangle me-1"></i>
                                ${toolName || 'Error'}
                            </span>
                            <span class="small opacity-75">
                                <i class="bi bi-clock me-1"></i>
                                ${formattedTimestamp}
                            </span>
                        </div>
                    </div>
                </div>
                <div class="result-body">
                    <div class="alert alert-danger m-3 mb-0">
                        <div class="d-flex align-items-start">
                            <i class="bi bi-exclamation-triangle-fill text-danger me-2 mt-1"></i>
                            <div>
                                <strong>Execution Failed</strong>
                                <div class="mt-2">${this.escapeHtml(error)}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Format result data with syntax highlighting
     */
    formatResult(result) {
        let formatted;
        
        try {
            // Try to parse as JSON for pretty formatting
            let data;
            if (typeof result === 'string') {
                try {
                    data = JSON.parse(result);
                } catch {
                    data = result;
                }
            } else {
                data = result;
            }
            
            if (typeof data === 'object') {
                formatted = JSON.stringify(data, null, 2);
            } else {
                formatted = String(data);
            }
            
            // Apply basic syntax highlighting for JSON
            if (formatted.includes('{') || formatted.includes('[')) {
                formatted = this.applySyntaxHighlighting(formatted);
            }
            
        } catch (e) {
            formatted = String(result);
        }
        
        return formatted;
    }
    
    /**
     * Apply basic syntax highlighting to JSON
     */
    applySyntaxHighlighting(json) {
        return json
            .replace(/(".*?")\s*:/g, '<span class="json-key">$1</span>:') // Keys
            .replace(/:\s*(".*?")/g, ': <span class="json-string">$1</span>') // String values
            .replace(/:\s*(\d+\.?\d*)/g, ': <span class="json-number">$1</span>') // Numbers
            .replace(/:\s*(true|false|null)/g, ': <span class="json-boolean">$1</span>'); // Booleans/null
    }
    
    /**
     * Get statistics about the result
     */
    getResultStats(result) {
        try {
            const text = typeof result === 'string' ? result : JSON.stringify(result);
            const lines = text.split('\n').length;
            const chars = text.length;
            const size = new Blob([text]).size;
            
            return `${lines} lines • ${chars} characters • ${this.formatBytes(size)}`;
        } catch {
            return 'Result statistics unavailable';
        }
    }
    
    /**
     * Format timestamp for display
     */
    formatTimestamp(timestamp) {
        return timestamp.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    /**
     * Format bytes for display
     */
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    /**
     * Escape HTML to prevent XSS
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Copy result to clipboard
     */
    async copyToClipboard() {
        if (!this.currentResult) {
            this.showToast('Info', 'No result to copy', 'info');
            return;
        }
        
        try {
            const textToCopy = typeof this.currentResult.data === 'string' 
                ? this.currentResult.data 
                : JSON.stringify(this.currentResult.data, null, 2);
            
            await navigator.clipboard.writeText(textToCopy);
            this.showToast('Success', 'Result copied to clipboard', 'success');
            
            // Visual feedback on button
            const copyBtn = document.getElementById('copy-result');
            const originalIcon = copyBtn.innerHTML;
            copyBtn.innerHTML = '<i class="bi bi-check"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = originalIcon;
            }, 1000);
            
        } catch (error) {
            console.error('Failed to copy:', error);
            this.showToast('Error', 'Failed to copy to clipboard', 'danger');
        }
    }
    
    /**
     * Download result as file
     */
    downloadResult() {
        if (!this.currentResult) {
            this.showToast('Info', 'No result to download', 'info');
            return;
        }
        
        try {
            const content = typeof this.currentResult.data === 'string' 
                ? this.currentResult.data 
                : JSON.stringify(this.currentResult.data, null, 2);
            
            const blob = new Blob([content], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `${this.currentResult.toolName}_${this.formatTimestamp(this.currentResult.timestamp).replace(/[/:,\s]/g, '-')}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            URL.revokeObjectURL(url);
            
            this.showToast('Success', 'Result downloaded successfully', 'success');
            
        } catch (error) {
            console.error('Failed to download:', error);
            this.showToast('Error', 'Failed to download result', 'danger');
        }
    }
    
    /**
     * Clear all results
     */
    clearResults() {
        this.currentResult = null;
        
        const outputArea = document.getElementById('output-area');
        outputArea.innerHTML = this.getPlaceholderContent();
        
        // Disable action buttons
        this.updateActionButtons(false);
        
        // Hide history panel
        document.getElementById('history-panel').style.display = 'none';
        
        this.showToast('Info', 'Results cleared', 'info');
    }
    
    /**
     * Update action button states
     */
    updateActionButtons(enabled) {
        const buttons = ['copy-result', 'download-result'];
        buttons.forEach(id => {
            const btn = document.getElementById(id);
            btn.disabled = !enabled;
            if (enabled) {
                btn.classList.remove('disabled');
            } else {
                btn.classList.add('disabled');
            }
        });
    }
    
    /**
     * Add result to history
     */
    addToHistory(data, toolName, timestamp, type = 'success') {
        const historyItem = {
            data,
            toolName,
            timestamp,
            type,
            id: Date.now() + Math.random()
        };
        
        this.resultHistory.unshift(historyItem);
        
        // Limit history size
        if (this.resultHistory.length > this.maxHistorySize) {
            this.resultHistory = this.resultHistory.slice(0, this.maxHistorySize);
        }
        
        this.updateHistoryDisplay();
    }
    
    /**
     * Toggle history panel visibility
     */
    toggleHistory() {
        const panel = document.getElementById('history-panel');
        const btn = document.getElementById('toggle-history');
        
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
            btn.title = 'Hide history';
        } else {
            panel.style.display = 'none';
            btn.innerHTML = '<i class="bi bi-clock-history"></i>';
            btn.title = 'Show history';
        }
    }
    
    /**
     * Update history display
     */
    updateHistoryDisplay() {
        const historyContent = document.getElementById('history-content');
        
        if (this.resultHistory.length === 0) {
            historyContent.innerHTML = '<p class="text-muted">No previous results</p>';
            return;
        }
        
        const historyItems = this.resultHistory.map((item, index) => {
            const badge = item.type === 'error' ? 'danger' : 'success';
            const icon = item.type === 'error' ? 'bi-exclamation-triangle' : 'bi-check-circle';
            
            return `
                <div class="history-item border rounded p-2 mb-2 ${item.type === 'error' ? 'border-danger' : ''}" data-id="${item.id}">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="badge bg-${badge}">
                            <i class="bi ${icon} me-1"></i>
                            ${item.toolName}
                        </span>
                        <small class="text-muted">${this.formatTimestamp(item.timestamp)}</small>
                    </div>
                    <div class="history-preview small text-muted" style="max-height: 60px; overflow: hidden;">
                        ${this.getHistoryPreview(item.data)}
                    </div>
                    <div class="mt-1">
                        <button class="btn btn-sm btn-outline-secondary" onclick="resultsSection.restoreFromHistory('${item.id}')">
                            <i class="bi bi-arrow-up-square"></i> Restore
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        historyContent.innerHTML = historyItems;
    }
    
    /**
     * Get preview text for history item
     */
    getHistoryPreview(data) {
        const text = typeof data === 'string' ? data : JSON.stringify(data);
        const preview = text.substring(0, 100);
        return this.escapeHtml(preview) + (text.length > 100 ? '...' : '');
    }
    
    /**
     * Restore result from history
     */
    restoreFromHistory(historyId) {
        const historyItem = this.resultHistory.find(item => item.id == historyId);
        if (!historyItem) return;
        
        if (historyItem.type === 'error') {
            this.displayError(historyItem.data, historyItem.toolName, historyItem.timestamp);
        } else {
            this.displayResult(historyItem.data, historyItem.toolName, historyItem.timestamp);
        }
        
        this.showToast('Info', 'Result restored from history', 'info');
    }
    
    /**
     * Scroll to results area
     */
    scrollToResults() {
        this.container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
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
            container.style.zIndex = '9999';
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
        const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }
    
    /**
     * Get current result
     */
    getCurrentResult() {
        return this.currentResult;
    }
    
    /**
     * Get result history
     */
    getHistory() {
        return this.resultHistory;
    }
    
    /**
     * Clear history
     */
    clearHistory() {
        this.resultHistory = [];
        this.updateHistoryDisplay();
        this.showToast('Info', 'History cleared', 'info');
    }
    
    /**
     * Check if results section has content
     */
    hasResults() {
        return this.currentResult !== null;
    }
    
    /**
     * Destroy and cleanup
     */
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        // Remove global reference
        if (window.resultsSection === this) {
            delete window.resultsSection;
        }
    }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ResultsSection;
} else if (typeof window !== 'undefined') {
    window.ResultsSection = ResultsSection;
}