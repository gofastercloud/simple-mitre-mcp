# Design Document

## Overview

This design document outlines the comprehensive enhancement of the web explorer component, addressing both the immediate dependency resolution issue and significant user experience improvements. The solution involves fixing the `aiohttp` import problem, modernizing the web interface with a professional design, adding intelligent data-driven form controls, implementing system information displays, and establishing robust testing to prevent similar issues.

The enhanced web explorer will transform from a basic functional interface into a sophisticated threat intelligence exploration platform that provides intuitive access to all 8 MCP tools with modern UX patterns and comprehensive data insights.

## Architecture

### Current Architecture
```
start_explorer.py → http_proxy.py (fails on aiohttp import) → web_explorer.html (basic forms)
```

### Enhanced Architecture
```
start_explorer.py → http_proxy.py (fixed dependencies + new endpoints) → Enhanced Web Interface
                                                                        ↓
                                                                   Modern UI Components:
                                                                   - System Dashboard
                                                                   - Smart Form Controls  
                                                                   - Responsive Output Areas
                                                                   - Professional Styling
```

### New Component Structure
```
Web Explorer Enhancement
├── Dependency Resolution Layer
│   ├── UV dependency synchronization
│   ├── Import validation
│   └── Startup error handling
├── Backend API Enhancements  
│   ├── System information endpoint
│   ├── Data population endpoints
│   └── Enhanced error responses
├── Frontend UI Modernization
│   ├── Professional design system
│   ├── Responsive layout components
│   ├── Smart form controls
│   └── Enhanced result display
└── Testing Infrastructure
    ├── Startup validation tests
    ├── UI component tests
    └── Integration test coverage
```

## Components and Interfaces

### 1. Dependency Resolution System

#### Root Cause Analysis and Fix
```python
# Diagnostic approach for dependency issues
def diagnose_dependency_issue():
    """
    Systematic approach to identify and resolve dependency problems:
    1. Check UV lock file consistency
    2. Validate pyproject.toml dependencies
    3. Test import paths in current environment
    4. Verify virtual environment activation
    """
    
def fix_dependency_resolution():
    """
    Multi-step resolution process:
    1. uv sync --force to rebuild dependencies
    2. Validate all web explorer imports
    3. Test HTTP proxy server startup
    4. Verify CORS functionality
    """
```

#### Enhanced Error Handling
```python
# start_explorer.py enhancements
def validate_dependencies():
    """Pre-flight dependency validation before server startup."""
    required_modules = ['aiohttp', 'aiohttp_cors', 'asyncio']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError as e:
            missing_modules.append((module, str(e)))
    
    if missing_modules:
        print("❌ Missing dependencies detected:")
        for module, error in missing_modules:
            print(f"  - {module}: {error}")
        print("\n🔧 Run 'uv sync' to install missing dependencies")
        sys.exit(1)
    
    print("✅ All dependencies validated successfully")
```

### 2. Backend API Enhancements

#### System Information Endpoint
```python
# New endpoint in http_proxy.py
async def handle_system_info(self, request: web_request.Request) -> Response:
    """Provide comprehensive system and data information."""
    try:
        # Get data statistics from MCP server
        data_stats = await self._get_data_statistics()
        
        system_info = {
            "server_info": {
                "version": "1.0.0",  # From package metadata
                "mcp_protocol_version": "1.0",
                "startup_time": self.startup_time.isoformat(),
                "data_source": "MITRE ATT&CK Enterprise"
            },
            "data_statistics": data_stats,
            "capabilities": {
                "basic_tools": 5,
                "advanced_tools": 3,
                "total_tools": 8,
                "web_interface": True,
                "api_access": True
            }
        }
        
        return web.json_response(system_info)
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return web.json_response({"error": str(e)}, status=500)

async def _get_data_statistics(self) -> Dict[str, Any]:
    """Extract comprehensive statistics from loaded data."""
    stats = {}
    
    # Get entity counts
    for entity_type in ['techniques', 'tactics', 'groups', 'mitigations']:
        try:
            result, _ = await self.mcp_server.call_tool('search_attack', {'query': '*'})
            # Parse result to count entities by type
            stats[f"{entity_type}_count"] = self._count_entities_by_type(result, entity_type)
        except Exception as e:
            stats[f"{entity_type}_count"] = 0
            logger.warning(f"Could not get count for {entity_type}: {e}")
    
    # Get relationship statistics
    stats["relationships_count"] = await self._count_relationships()
    stats["last_updated"] = await self._get_data_freshness()
    
    return stats
```

#### Data Population Endpoints
```python
# New endpoints for populating form controls
async def handle_get_groups(self, request: web_request.Request) -> Response:
    """Get all available threat groups for dropdown population."""
    try:
        result, _ = await self.mcp_server.call_tool('search_attack', {'query': 'intrusion-set'})
        groups = self._extract_groups_for_dropdown(result)
        return web.json_response({"groups": groups})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_get_tactics(self, request: web_request.Request) -> Response:
    """Get all available tactics for dropdown population."""
    try:
        result, _ = await self.mcp_server.call_tool('list_tactics', {})
        tactics = self._extract_tactics_for_dropdown(result)
        return web.json_response({"tactics": tactics})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

async def handle_get_techniques(self, request: web_request.Request) -> Response:
    """Get techniques for autocomplete functionality."""
    query = request.query.get('q', '')
    try:
        result, _ = await self.mcp_server.call_tool('search_attack', {'query': query})
        techniques = self._extract_techniques_for_autocomplete(result, query)
        return web.json_response({"techniques": techniques})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
```

### 3. Frontend UI Modernization

#### File Organization Structure
```
web_interface/
├── index.html              # Main HTML file
├── css/
│   ├── styles.css         # Custom styles and theme
│   └── components.css     # Component-specific styles
├── js/
│   ├── app.js            # Main application logic
│   ├── api.js            # API communication layer
│   ├── components.js     # UI component classes
│   └── utils.js          # Utility functions
└── assets/
    ├── icons/            # Custom icons
    └── images/           # Images and logos
```

#### CSS Framework Selection
**Bootstrap 5.3** (CDN-based for easy maintenance):
- **Pros**: Comprehensive component library, excellent documentation, responsive grid system, extensive utility classes
- **Cons**: Larger bundle size, some design opinions
- **Use Case**: Rapid development with professional appearance

**Alternative: Tailwind CSS** (CDN-based):
- **Pros**: Utility-first approach, smaller bundle when optimized, highly customizable
- **Cons**: Steeper learning curve, requires more custom CSS for complex components
- **Use Case**: More control over design, modern utility-first approach

**Recommendation: Bootstrap 5.3** for this project due to:
- Faster development time
- Built-in components (cards, forms, modals, etc.)
- Excellent responsive design out of the box
- Professional appearance with minimal custom CSS

#### Enhanced HTML Structure
```html
<!-- web_interface/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MITRE ATT&CK Intelligence Platform</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link href="css/styles.css" rel="stylesheet">
    <link href="css/components.css" rel="stylesheet">
</head>
<body>
    <div id="app">
        <!-- Navigation -->
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">
                    <i class="bi bi-shield-check me-2"></i>
                    MITRE ATT&CK Intelligence Platform
                </a>
            </div>
        </nav>
        
        <!-- Main Content -->
        <div class="container-fluid py-4">
            <!-- System Dashboard -->
            <div id="system-dashboard"></div>
            
            <!-- Tools Section -->
            <div id="tools-section"></div>
            
            <!-- Results Section -->
            <div id="results-section"></div>
        </div>
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Custom JS -->
    <script src="js/utils.js"></script>
    <script src="js/api.js"></script>
    <script src="js/components.js"></script>
    <script src="js/app.js"></script>
</body>
</html>
```

#### Custom Theme (CSS)
```css
/* web_interface/css/styles.css */
:root {
    /* Custom color palette building on Bootstrap */
    --bs-primary: #0d47a1;
    --bs-primary-rgb: 13, 71, 161;
    --bs-secondary: #37474f;
    --bs-success: #2e7d32;
    --bs-warning: #f57c00;
    --bs-danger: #d32f2f;
    
    /* Custom variables */
    --threat-red: #d32f2f;
    --security-blue: #1976d2;
    --analysis-green: #388e3c;
    --warning-orange: #f57c00;
    
    /* Typography */
    --font-family-sans-serif: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
    font-family: var(--font-family-sans-serif);
    background-color: #f8f9fa;
}

/* Custom navbar styling */
.navbar-brand {
    font-weight: 600;
    font-size: 1.25rem;
}

/* Dashboard enhancements */
.dashboard-card {
    transition: all 0.2s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.dashboard-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

/* Stat cards */
.stat-card {
    background: linear-gradient(135deg, var(--bs-primary) 0%, #1565c0 100%);
    color: white;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.stat-card:hover {
    transform: scale(1.05);
}

.stat-number {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 0.875rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Form enhancements */
.form-control:focus {
    border-color: var(--bs-primary);
    box-shadow: 0 0 0 0.2rem rgba(13, 71, 161, 0.25);
}

/* Output area styling */
.output-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    overflow: hidden;
}

.output-content {
    max-height: 60vh;
    overflow-y: auto;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
    line-height: 1.6;
    background-color: #f8f9fa;
    padding: 1.5rem;
}

/* Custom scrollbar */
.output-content::-webkit-scrollbar {
    width: 8px;
}

.output-content::-webkit-scrollbar-track {
    background: #e9ecef;
}

.output-content::-webkit-scrollbar-thumb {
    background: #6c757d;
    border-radius: 4px;
}

.output-content::-webkit-scrollbar-thumb:hover {
    background: #495057;
}

/* Loading states */
.loading {
    opacity: 0.6;
    pointer-events: none;
}

.spinner-border-sm {
    width: 1rem;
    height: 1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .stat-number {
        font-size: 2rem;
    }
    
    .container-fluid {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
```

#### System Dashboard Component
```html
<!-- System information dashboard -->
<div class="system-dashboard">
    <div class="dashboard-header">
        <h1 class="dashboard-title">MITRE ATT&CK Intelligence Platform</h1>
        <p class="dashboard-subtitle">Advanced Threat Intelligence Analysis & Exploration</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-icon">🎯</div>
            <div class="stat-content">
                <div class="stat-number" id="techniques-count">-</div>
                <div class="stat-label">Techniques</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">🏴</div>
            <div class="stat-content">
                <div class="stat-number" id="tactics-count">-</div>
                <div class="stat-label">Tactics</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">👥</div>
            <div class="stat-content">
                <div class="stat-number" id="groups-count">-</div>
                <div class="stat-label">Threat Groups</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">🛡️</div>
            <div class="stat-content">
                <div class="stat-number" id="mitigations-count">-</div>
                <div class="stat-label">Mitigations</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">🔗</div>
            <div class="stat-content">
                <div class="stat-number" id="relationships-count">-</div>
                <div class="stat-label">Relationships</div>
            </div>
        </div>
        
        <div class="stat-card">
            <div class="stat-icon">⚡</div>
            <div class="stat-content">
                <div class="stat-number">8</div>
                <div class="stat-label">Analysis Tools</div>
            </div>
        </div>
    </div>
    
    <div class="server-info">
        <div class="info-item">
            <span class="info-label">Server Version:</span>
            <span class="info-value" id="server-version">-</span>
        </div>
        <div class="info-item">
            <span class="info-label">Data Source:</span>
            <span class="info-value" id="data-source">-</span>
        </div>
        <div class="info-item">
            <span class="info-label">Last Updated:</span>
            <span class="info-value" id="last-updated">-</span>
        </div>
    </div>
</div>
```

#### JavaScript Architecture
```javascript
// web_interface/js/components.js - UI Component Classes
class SystemDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.systemInfo = null;
    }
    
    async render() {
        try {
            this.systemInfo = await API.getSystemInfo();
            this.container.innerHTML = this.getTemplate();
            this.updateStats();
        } catch (error) {
            console.error('Failed to render dashboard:', error);
            this.renderError();
        }
    }
    
    getTemplate() {
        return `
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card dashboard-card">
                        <div class="card-body text-center">
                            <h1 class="card-title mb-2">
                                <i class="bi bi-shield-check text-primary me-2"></i>
                                MITRE ATT&CK Intelligence Platform
                            </h1>
                            <p class="card-text text-muted">Advanced Threat Intelligence Analysis & Exploration</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number" id="techniques-count">-</div>
                        <div class="stat-label">Techniques</div>
                    </div>
                </div>
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number" id="tactics-count">-</div>
                        <div class="stat-label">Tactics</div>
                    </div>
                </div>
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number" id="groups-count">-</div>
                        <div class="stat-label">Threat Groups</div>
                    </div>
                </div>
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number" id="mitigations-count">-</div>
                        <div class="stat-label">Mitigations</div>
                    </div>
                </div>
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number" id="relationships-count">-</div>
                        <div class="stat-label">Relationships</div>
                    </div>
                </div>
                <div class="col-md-2 mb-3">
                    <div class="stat-card">
                        <div class="stat-number">8</div>
                        <div class="stat-label">Analysis Tools</div>
                    </div>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <div class="row text-center">
                                <div class="col-md-4">
                                    <strong>Server Version:</strong>
                                    <span id="server-version" class="text-muted">-</span>
                                </div>
                                <div class="col-md-4">
                                    <strong>Data Source:</strong>
                                    <span id="data-source" class="text-muted">-</span>
                                </div>
                                <div class="col-md-4">
                                    <strong>Last Updated:</strong>
                                    <span id="last-updated" class="text-muted">-</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    updateStats() {
        if (!this.systemInfo) return;
        
        const stats = this.systemInfo.data_statistics;
        document.getElementById('techniques-count').textContent = stats.techniques_count || '-';
        document.getElementById('tactics-count').textContent = stats.tactics_count || '-';
        document.getElementById('groups-count').textContent = stats.groups_count || '-';
        document.getElementById('mitigations-count').textContent = stats.mitigations_count || '-';
        document.getElementById('relationships-count').textContent = stats.relationships_count || '-';
        
        const serverInfo = this.systemInfo.server_info;
        document.getElementById('server-version').textContent = serverInfo.version || '-';
        document.getElementById('data-source').textContent = serverInfo.data_source || '-';
        document.getElementById('last-updated').textContent = 
            serverInfo.startup_time ? new Date(serverInfo.startup_time).toLocaleDateString() : '-';
    }
}

class SmartFormControls {
    constructor() {
        this.groupsData = [];
        this.tacticsData = [];
        this.techniquesData = [];
        this.initialized = false;
    }
    
    async initialize() {
        if (this.initialized) return;
        
        try {
            await Promise.all([
                this.loadGroups(),
                this.loadTactics()
            ]);
            
            this.setupFormControls();
            this.initialized = true;
        } catch (error) {
            console.error('Failed to initialize smart form controls:', error);
        }
    }
    
    async loadGroups() {
        this.groupsData = await API.getGroups();
    }
    
    async loadTactics() {
        this.tacticsData = await API.getTactics();
    }
    
    setupFormControls() {
        this.setupGroupDropdowns();
        this.setupTacticDropdowns();
    }
    
    setupGroupDropdowns() {
        const groupSelects = document.querySelectorAll('.group-select');
        groupSelects.forEach(select => {
            this.populateSelect(select, this.groupsData, 'Select a threat group...');
        });
    }
    
    setupTacticDropdowns() {
        const tacticSelects = document.querySelectorAll('.tactic-select');
        tacticSelects.forEach(select => {
            this.populateSelect(select, this.tacticsData, 'Select a tactic...');
        });
    }
    
    populateSelect(selectElement, data, placeholder) {
        // Clear existing options
        selectElement.innerHTML = `<option value="">${placeholder}</option>`;
        
        // Add data options
        data.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id;
            option.textContent = item.display_name || `${item.name} (${item.id})`;
            selectElement.appendChild(option);
        });
        
        // Add Bootstrap styling
        selectElement.classList.add('form-select');
    }
}

class ToolsSection {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.tools = [];
    }
    
    async render() {
        try {
            this.tools = await API.getTools();
            this.container.innerHTML = this.getTemplate();
            this.setupEventListeners();
        } catch (error) {
            console.error('Failed to render tools section:', error);
        }
    }
    
    getTemplate() {
        const basicTools = this.tools.slice(0, 5);
        const advancedTools = this.tools.slice(5);
        
        return `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-search me-2"></i>Basic Analysis Tools
                            </h5>
                        </div>
                        <div class="card-body">
                            ${basicTools.map(tool => this.getToolForm(tool)).join('')}
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="card-title mb-0">
                                <i class="bi bi-diagram-3 me-2"></i>Advanced Threat Modeling
                            </h5>
                        </div>
                        <div class="card-body">
                            ${advancedTools.map(tool => this.getToolForm(tool)).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    getToolForm(tool) {
        // Generate Bootstrap form for each tool
        return `
            <div class="mb-4">
                <h6>${tool.name}</h6>
                <p class="text-muted small">${tool.description}</p>
                <form class="tool-form" data-tool="${tool.name}">
                    ${this.generateFormFields(tool.inputSchema)}
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-play-fill me-1"></i>Execute
                    </button>
                </form>
            </div>
        `;
    }
    
    generateFormFields(schema) {
        if (!schema.properties) return '';
        
        return Object.entries(schema.properties).map(([key, prop]) => {
            const isRequired = schema.required?.includes(key);
            const fieldClass = this.getFieldClass(key);
            
            return `
                <div class="mb-3">
                    <label class="form-label">${this.formatLabel(key)}${isRequired ? ' *' : ''}</label>
                    ${this.generateInputField(key, prop, fieldClass)}
                    ${prop.description ? `<div class="form-text">${prop.description}</div>` : ''}
                </div>
            `;
        }).join('');
    }
    
    generateInputField(key, prop, fieldClass) {
        if (prop.type === 'array') {
            return `<textarea class="form-control ${fieldClass}" name="${key}" rows="3" placeholder="Enter values separated by commas"></textarea>`;
        } else if (fieldClass.includes('select')) {
            return `<select class="form-select ${fieldClass}" name="${key}"></select>`;
        } else {
            return `<input type="text" class="form-control ${fieldClass}" name="${key}" placeholder="${prop.description || ''}">`;
        }
    }
    
    getFieldClass(fieldName) {
        if (fieldName.includes('group')) return 'group-select';
        if (fieldName.includes('tactic')) return 'tactic-select';
        return '';
    }
    
    formatLabel(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    setupEventListeners() {
        const forms = this.container.querySelectorAll('.tool-form');
        forms.forEach(form => {
            form.addEventListener('submit', this.handleToolSubmit.bind(this));
        });
    }
    
    async handleToolSubmit(event) {
        event.preventDefault();
        const form = event.target;
        const toolName = form.dataset.tool;
        const formData = new FormData(form);
        const parameters = {};
        
        // Convert form data to parameters object
        for (const [key, value] of formData.entries()) {
            if (value.trim()) {
                // Handle array fields
                if (form.querySelector(`[name="${key}"]`).type === 'textarea') {
                    parameters[key] = value.split(',').map(v => v.trim()).filter(v => v);
                } else {
                    parameters[key] = value;
                }
            }
        }
        
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Executing...';
        submitBtn.disabled = true;
        
        try {
            const result = await API.callTool(toolName, parameters);
            ResultsSection.displayResult(result, toolName);
        } catch (error) {
            ResultsSection.displayError(error.message);
        } finally {
            // Restore button state
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    }
}
```

#### API Layer and Results Display
```javascript
// web_interface/js/api.js - API Communication Layer
class API {
    static async getSystemInfo() {
        const response = await fetch('/system_info');
        if (!response.ok) throw new Error('Failed to fetch system info');
        return response.json();
    }
    
    static async getTools() {
        const response = await fetch('/tools');
        if (!response.ok) throw new Error('Failed to fetch tools');
        const data = await response.json();
        return data.tools;
    }
    
    static async getGroups() {
        const response = await fetch('/api/groups');
        if (!response.ok) throw new Error('Failed to fetch groups');
        const data = await response.json();
        return data.groups;
    }
    
    static async getTactics() {
        const response = await fetch('/api/tactics');
        if (!response.ok) throw new Error('Failed to fetch tactics');
        const data = await response.json();
        return data.tactics;
    }
    
    static async callTool(toolName, parameters) {
        const response = await fetch('/call_tool', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tool_name: toolName,
                parameters: parameters
            })
        });
        
        if (!response.ok) {
            const error = await response.text();
            throw new Error(error);
        }
        
        return response.text();
    }
}

// web_interface/js/components.js (continued) - Results Section
class ResultsSection {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.render();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="card output-container">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">
                        <i class="bi bi-terminal me-2"></i>Analysis Results
                    </h5>
                    <div class="btn-group" role="group">
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="ResultsSection.copyResults()">
                            <i class="bi bi-clipboard"></i> Copy
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="ResultsSection.downloadResults()">
                            <i class="bi bi-download"></i> Download
                        </button>
                        <button type="button" class="btn btn-outline-secondary btn-sm" onclick="ResultsSection.clearResults()">
                            <i class="bi bi-trash"></i> Clear
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div class="output-content" id="output">
                        <div class="output-placeholder text-center py-5">
                            <i class="bi bi-search display-1 text-muted mb-3"></i>
                            <p class="text-muted">Execute a query to see results here</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    static displayResult(result, toolName) {
        const outputElement = document.getElementById('output');
        const timestamp = new Date().toLocaleTimeString();
        
        outputElement.innerHTML = `
            <div class="result-header p-3 bg-light border-bottom">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="badge bg-primary">${toolName}</span>
                    <small class="text-muted">${timestamp}</small>
                </div>
            </div>
            <div class="result-content p-3">
                <pre class="mb-0">${this.formatResult(result)}</pre>
            </div>
        `;
        
        // Scroll to results
        outputElement.scrollIntoView({ behavior: 'smooth' });
    }
    
    static displayError(error) {
        const outputElement = document.getElementById('output');
        const timestamp = new Date().toLocaleTimeString();
        
        outputElement.innerHTML = `
            <div class="result-header p-3 bg-danger text-white">
                <div class="d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-exclamation-triangle me-2"></i>Error</span>
                    <small>${timestamp}</small>
                </div>
            </div>
            <div class="result-content p-3">
                <div class="alert alert-danger mb-0">
                    <strong>Error:</strong> ${error}
                </div>
            </div>
        `;
    }
    
    static formatResult(result) {
        try {
            // Try to parse as JSON for pretty formatting
            const parsed = JSON.parse(result);
            return JSON.stringify(parsed, null, 2);
        } catch {
            // Return as-is if not JSON
            return result;
        }
    }
    
    static copyResults() {
        const outputContent = document.querySelector('.result-content pre');
        if (outputContent) {
            navigator.clipboard.writeText(outputContent.textContent);
            // Show toast notification
            this.showToast('Results copied to clipboard!', 'success');
        }
    }
    
    static downloadResults() {
        const outputContent = document.querySelector('.result-content pre');
        if (outputContent) {
            const blob = new Blob([outputContent.textContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `mitre-attack-results-${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
        }
    }
    
    static clearResults() {
        const outputElement = document.getElementById('output');
        outputElement.innerHTML = `
            <div class="output-placeholder text-center py-5">
                <i class="bi bi-search display-1 text-muted mb-3"></i>
                <p class="text-muted">Execute a query to see results here</p>
            </div>
        `;
    }
    
    static showToast(message, type = 'info') {
        // Create Bootstrap toast
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        // Add to toast container (create if doesn't exist)
        let toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // Remove toast element after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }
}

// web_interface/js/app.js - Main Application
class App {
    constructor() {
        this.dashboard = null;
        this.toolsSection = null;
        this.resultsSection = null;
        this.formControls = null;
    }
    
    async initialize() {
        try {
            // Initialize components
            this.dashboard = new SystemDashboard('system-dashboard');
            this.toolsSection = new ToolsSection('tools-section');
            this.resultsSection = new ResultsSection('results-section');
            this.formControls = new SmartFormControls();
            
            // Render components
            await this.dashboard.render();
            await this.toolsSection.render();
            
            // Initialize smart form controls after tools are rendered
            await this.formControls.initialize();
            
            console.log('✅ MITRE ATT&CK Intelligence Platform initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.showErrorState();
        }
    }
    
    showErrorState() {
        document.getElementById('app').innerHTML = `
            <div class="container-fluid py-5">
                <div class="row justify-content-center">
                    <div class="col-md-6">
                        <div class="alert alert-danger text-center">
                            <i class="bi bi-exclamation-triangle display-1 mb-3"></i>
                            <h4>Application Failed to Load</h4>
                            <p>There was an error initializing the MITRE ATT&CK Intelligence Platform.</p>
                            <button class="btn btn-outline-danger" onclick="location.reload()">
                                <i class="bi bi-arrow-clockwise me-2"></i>Retry
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
}

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.initialize();
});
```

## Data Models and Processing

### System Information Model
```python
@dataclass
class SystemInfo:
    """Comprehensive system information model."""
    server_version: str
    mcp_protocol_version: str
    startup_time: datetime
    data_source: str
    techniques_count: int
    tactics_count: int
    groups_count: int
    mitigations_count: int
    relationships_count: int
    last_updated: datetime
    capabilities: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "server_info": {
                "version": self.server_version,
                "mcp_protocol_version": self.mcp_protocol_version,
                "startup_time": self.startup_time.isoformat(),
                "data_source": self.data_source
            },
            "data_statistics": {
                "techniques_count": self.techniques_count,
                "tactics_count": self.tactics_count,
                "groups_count": self.groups_count,
                "mitigations_count": self.mitigations_count,
                "relationships_count": self.relationships_count,
                "last_updated": self.last_updated.isoformat()
            },
            "capabilities": self.capabilities
        }
```

### Form Data Models
```python
@dataclass
class DropdownOption:
    """Model for dropdown option data."""
    id: str
    name: str
    aliases: List[str] = field(default_factory=list)
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "display_name": f"{self.name} ({self.id})",
            "aliases": self.aliases,
            "description": self.description
        }

@dataclass
class FormDataResponse:
    """Response model for form data endpoints."""
    data_type: str
    options: List[DropdownOption]
    total_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_type": self.data_type,
            "options": [option.to_dict() for option in self.options],
            "total_count": self.total_count
        }
```

## Error Handling

### Comprehensive Error Management
```python
class WebExplorerError(Exception):
    """Base exception for web explorer issues."""
    pass

class DependencyError(WebExplorerError):
    """Raised when required dependencies are missing."""
    pass

class DataLoadError(WebExplorerError):
    """Raised when data loading fails."""
    pass

class UIRenderError(WebExplorerError):
    """Raised when UI rendering fails."""
    pass

# Error handling middleware
async def error_handler_middleware(request, handler):
    """Global error handling for web requests."""
    try:
        return await handler(request)
    except DependencyError as e:
        logger.error(f"Dependency error: {e}")
        return web.json_response({
            "error": "System dependency issue",
            "message": "Please run 'uv sync' to install missing dependencies",
            "details": str(e)
        }, status=503)
    except DataLoadError as e:
        logger.error(f"Data load error: {e}")
        return web.json_response({
            "error": "Data loading failed",
            "message": "Unable to load threat intelligence data",
            "details": str(e)
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return web.json_response({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "details": str(e) if DEBUG else "Contact administrator"
        }, status=500)
```

## Testing Strategy

### Startup Validation Tests
```python
# tests/test_web_explorer_startup.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock

class TestWebExplorerStartup:
    """Test web explorer startup and dependency validation."""
    
    def test_dependency_validation_success(self):
        """Test successful dependency validation."""
        from start_explorer import validate_dependencies
        
        # Should not raise any exceptions
        validate_dependencies()
    
    def test_dependency_validation_missing_aiohttp(self):
        """Test handling of missing aiohttp dependency."""
        with patch('builtins.__import__', side_effect=ImportError("No module named 'aiohttp'")):
            with pytest.raises(SystemExit):
                from start_explorer import validate_dependencies
                validate_dependencies()
    
    @pytest.mark.asyncio
    async def test_http_proxy_server_startup(self):
        """Test HTTP proxy server can start successfully."""
        from http_proxy import create_http_proxy_server
        
        # Mock the MCP server creation
        with patch('http_proxy.create_mcp_server') as mock_mcp:
            mock_mcp.return_value = MagicMock()
            
            # Should be able to create server without errors
            runner, mcp_server = await create_http_proxy_server("localhost", 8001)
            
            assert runner is not None
            assert mcp_server is not None
            
            # Cleanup
            await runner.cleanup()
    
    @pytest.mark.asyncio
    async def test_system_info_endpoint(self):
        """Test system information endpoint functionality."""
        from http_proxy import HTTPProxy
        from aiohttp.test_utils import make_mocked_request
        
        # Create mock MCP server
        mock_mcp_server = MagicMock()
        mock_mcp_server.call_tool.return_value = (["mock result"], None)
        
        proxy = HTTPProxy(mock_mcp_server)
        
        # Test system info endpoint
        request = make_mocked_request('GET', '/system_info')
        response = await proxy.handle_system_info(request)
        
        assert response.status == 200
        # Additional assertions for response content
```

### UI Component Tests
```python
# tests/test_web_interface_components.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestWebInterfaceComponents:
    """Test web interface components and functionality."""
    
    @pytest.fixture
    def driver(self):
        """Setup web driver for UI tests."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        yield driver
        driver.quit()
    
    def test_dashboard_loads(self, driver):
        """Test that dashboard loads with system information."""
        driver.get("http://localhost:8000")
        
        # Wait for dashboard to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "system-dashboard"))
        )
        
        # Check that stat cards are present
        stat_cards = driver.find_elements(By.CLASS_NAME, "stat-card")
        assert len(stat_cards) >= 6  # Should have at least 6 stat cards
    
    def test_smart_form_controls(self, driver):
        """Test that form controls are populated with data."""
        driver.get("http://localhost:8000")
        
        # Wait for form controls to initialize
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "group-select"))
        )
        
        # Check that group dropdown has options
        group_select = driver.find_element(By.CLASS_NAME, "group-select")
        options = group_select.find_elements(By.TAG_NAME, "option")
        assert len(options) > 1  # Should have more than just placeholder
    
    def test_responsive_output_area(self, driver):
        """Test that output area handles large results properly."""
        driver.get("http://localhost:8000")
        
        # Execute a query that returns large results
        # ... test implementation
        
        # Check that output area has scrollbars when needed
        output_content = driver.find_element(By.CLASS_NAME, "output-content")
        assert output_content.is_displayed()
```

### Integration Tests
```python
# tests/test_web_explorer_integration.py
import pytest
import asyncio
import aiohttp
from aiohttp.test_utils import AioHTTPTestCase

class TestWebExplorerIntegration(AioHTTPTestCase):
    """Integration tests for web explorer functionality."""
    
    async def get_application(self):
        """Create test application."""
        from http_proxy import create_http_proxy_server
        runner, mcp_server = await create_http_proxy_server("localhost", 0)
        return runner.app
    
    async def test_full_workflow(self):
        """Test complete workflow from UI to MCP tools."""
        # Test system info endpoint
        async with self.client.request("GET", "/system_info") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "server_info" in data
            assert "data_statistics" in data
        
        # Test tools list endpoint
        async with self.client.request("GET", "/tools") as resp:
            assert resp.status == 200
            data = await resp.json()
            assert "tools" in data
            assert len(data["tools"]) == 8
        
        # Test tool execution
        tool_request = {
            "tool_name": "list_tactics",
            "parameters": {}
        }
        async with self.client.request("POST", "/call_tool", json=tool_request) as resp:
            assert resp.status == 200
            result = await resp.text()
            assert len(result) > 0
```

## Deployment Considerations

### Environment Validation
```bash
#!/bin/bash
# deployment/validate_web_explorer.sh

echo "🔍 Validating Web Explorer Deployment..."

# Check UV installation
if ! command -v uv &> /dev/null; then
    echo "❌ UV package manager not found"
    exit 1
fi

# Sync dependencies
echo "📦 Synchronizing dependencies..."
uv sync

# Validate Python imports
echo "🐍 Validating Python imports..."
python -c "
import sys
try:
    import aiohttp
    import aiohttp_cors
    import asyncio
    print('✅ All web explorer dependencies available')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

# Test server startup
echo "🚀 Testing server startup..."
timeout 10s python -c "
import asyncio
from http_proxy import create_http_proxy_server

async def test_startup():
    try:
        runner, mcp_server = await create_http_proxy_server('localhost', 8001)
        print('✅ HTTP proxy server starts successfully')
        await runner.cleanup()
    except Exception as e:
        print(f'❌ Server startup failed: {e}')
        raise

asyncio.run(test_startup())
"

echo "✅ Web Explorer validation complete"
```

### Performance Monitoring
```python
# monitoring/web_explorer_metrics.py
import time
import psutil
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PerformanceMetrics:
    """Web explorer performance metrics."""
    startup_time: float
    memory_usage_mb: float
    response_times: Dict[str, float]
    active_connections: int
    error_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "startup_time_seconds": self.startup_time,
            "memory_usage_mb": self.memory_usage_mb,
            "response_times_ms": {k: v * 1000 for k, v in self.response_times.items()},
            "active_connections": self.active_connections,
            "error_rate_percent": self.error_rate * 100
        }

class WebExplorerMonitor:
    """Monitor web explorer performance and health."""
    
    def __init__(self):
        self.startup_time = time.time()
        self.request_times = {}
        self.error_count = 0
        self.request_count = 0
    
    def record_request(self, endpoint: str, duration: float, success: bool):
        """Record request metrics."""
        self.request_times[endpoint] = duration
        self.request_count += 1
        if not success:
            self.error_count += 1
    
    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        return PerformanceMetrics(
            startup_time=time.time() - self.startup_time,
            memory_usage_mb=memory_mb,
            response_times=self.request_times.copy(),
            active_connections=len(process.connections()),
            error_rate=self.error_count / max(self.request_count, 1)
        )
```

## Security Considerations

### Input Validation Enhancement
```python
# Enhanced input validation for new endpoints
from pydantic import BaseModel, validator
from typing import Optional, List

class SystemInfoRequest(BaseModel):
    """Validation model for system info requests."""
    include_sensitive: bool = False
    
    @validator('include_sensitive')
    def validate_sensitive_access(cls, v):
        # Only allow sensitive info for authenticated requests
        return False  # For now, never include sensitive info

class FormDataRequest(BaseModel):
    """Validation model for form data requests."""
    data_type: str
    query: Optional[str] = None
    limit: int = 100
    
    @validator('data_type')
    def validate_data_type(cls, v):
        allowed_types = ['groups', 'tactics', 'techniques', 'mitigations']
        if v not in allowed_types:
            raise ValueError(f'Invalid data type. Must be one of: {allowed_types}')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v
```

### Content Security Policy
```python
# Enhanced security headers
def add_security_headers(response):
    """Add comprehensive security headers."""
    response.headers.update({
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data:; "
            "connect-src 'self'"
        ),
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    })
    return response
```

This comprehensive design addresses all requirements while maintaining security, performance, and maintainability standards. The solution provides both immediate dependency resolution and significant long-term value through enhanced user experience and robust testing infrastructure.