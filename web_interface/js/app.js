// MITRE ATT&CK MCP Explorer JavaScript

// Global state
let isConnected = false;
let currentTool = '';
let systemDashboard = null;

// Demo configurations
const demos = {
    // Basic Tools
    search_powershell: {
        tool: 'search_attack',
        params: { query: 'powershell' },
        title: 'PowerShell Search Results'
    },
    list_tactics: {
        tool: 'list_tactics',
        params: {},
        title: 'MITRE ATT&CK Tactics'
    },
    technique_t1055: {
        tool: 'get_technique',
        params: { technique_id: 'T1055' },
        title: 'T1055 Process Injection Analysis'
    },
    apt29_techniques: {
        tool: 'get_group_techniques',
        params: { group_id: 'G0016' },
        title: 'APT29 (Cozy Bear) Techniques'
    },
    
    // Advanced Analysis
    attack_path: {
        tool: 'build_attack_path',
        params: { 
            start_tactic: 'TA0001', 
            end_tactic: 'TA0040',
            group_id: 'G0016'
        },
        title: 'APT29 Attack Path: Initial Access → Impact'
    },
    coverage_gaps: {
        tool: 'analyze_coverage_gaps',
        params: { 
            threat_groups: ['G0016', 'G0007'],
            exclude_mitigations: ['M1013', 'M1026']
        },
        title: 'Coverage Gap Analysis: APT29 & APT1'
    },
    technique_relationships: {
        tool: 'detect_technique_relationships',
        params: { 
            technique_id: 'T1055',
            depth: 2
        },
        title: 'T1055 Relationship Analysis'
    },
    apt_comparison: {
        tool: 'analyze_coverage_gaps',
        params: { 
            threat_groups: ['G0016', 'G0007', 'G0032']
        },
        title: 'Multi-APT Coverage Analysis'
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', async function() {
    // Initialize system dashboard
    try {
        systemDashboard = new SystemDashboard('system-dashboard');
        await systemDashboard.render();
    } catch (error) {
        console.error('Failed to initialize system dashboard:', error);
    }
    
    // Set up connection monitoring
    checkConnection();
    setInterval(checkConnection, 30000); // Check every 30 seconds
    
    // Listen for dashboard stat card clicks
    const dashboardContainer = document.getElementById('system-dashboard');
    if (dashboardContainer) {
        dashboardContainer.addEventListener('statCardClick', handleStatCardClick);
    }
});

// Connection management
async function checkConnection() {
    try {
        const response = await fetch('/tools');
        if (response.ok) {
            setConnectionStatus(true);
        } else {
            setConnectionStatus(false);
        }
    } catch (error) {
        setConnectionStatus(false);
    }
}

function setConnectionStatus(connected) {
    isConnected = connected;
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    
    if (connected) {
        indicator.classList.remove('disconnected');
        statusText.textContent = 'Connected to MCP Server';
    } else {
        indicator.classList.add('disconnected');
        statusText.textContent = 'Disconnected from MCP Server';
    }
}

// Dashboard stat card click handler
function handleStatCardClick(event) {
    const { statType, systemInfo } = event.detail;
    console.log(`Stat card clicked: ${statType}`, systemInfo);
    
    // Future enhancement: could navigate to specific tool or filter based on stat type
    // For now, just log the interaction
}

// Tab management
function switchTab(tabName, event) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    const targetTab = document.getElementById(tabName + '-tab');
    if (targetTab) {
        targetTab.classList.add('active');
    }
}

// Demo execution
async function runDemo(demoKey) {
    const demo = demos[demoKey];
    if (!demo) return;
    
    if (!isConnected) {
        showError('Not connected to MCP server. Please check the connection.');
        return;
    }
    
    showLoading(demo.title);
    
    try {
        const response = await fetch('/call_tool', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: demo.tool,
                arguments: demo.params
            })
        });
        
        if (response.ok) {
            const result = await response.text();
            showResults(demo.title, result);
        } else {
            const error = await response.text();
            showError(`Tool execution failed: ${error}`);
        }
    } catch (error) {
        showError(`Network error: ${error.message}`);
    }
}

// Custom query management
function updateCustomForm() {
    const toolSelect = document.getElementById('toolSelect');
    const parametersDiv = document.getElementById('customParameters');
    const selectedTool = toolSelect.value;
    
    if (!selectedTool) {
        parametersDiv.innerHTML = '';
        return;
    }
    
    // Tool-specific parameter forms
    const parameterForms = {
        search_attack: `
            <div class="input-group">
                <label for="query">Search Query:</label>
                <input type="text" id="query" placeholder="e.g., powershell, process injection, APT29">
            </div>
        `,
        get_technique: `
            <div class="input-group">
                <label for="technique_id">Technique ID:</label>
                <input type="text" id="technique_id" placeholder="e.g., T1055, T1059">
            </div>
        `,
        get_group_techniques: `
            <div class="input-group">
                <label for="group_id">Group ID:</label>
                <input type="text" id="group_id" placeholder="e.g., G0016, G0007">
            </div>
        `,
        build_attack_path: `
            <div class="input-group">
                <label for="start_tactic">Start Tactic:</label>
                <input type="text" id="start_tactic" placeholder="e.g., TA0001" value="TA0001">
            </div>
            <div class="input-group">
                <label for="end_tactic">End Tactic:</label>
                <input type="text" id="end_tactic" placeholder="e.g., TA0040" value="TA0040">
            </div>
            <div class="input-group">
                <label for="group_id_path">Group ID (optional):</label>
                <input type="text" id="group_id_path" placeholder="e.g., G0016">
            </div>
        `,
        analyze_coverage_gaps: `
            <div class="input-group">
                <label for="threat_groups">Threat Groups (comma-separated):</label>
                <input type="text" id="threat_groups" placeholder="e.g., G0016,G0007,G0032">
            </div>
            <div class="input-group">
                <label for="exclude_mitigations">Exclude Mitigations (optional):</label>
                <input type="text" id="exclude_mitigations" placeholder="e.g., M1013,M1026">
            </div>
        `,
        detect_technique_relationships: `
            <div class="input-group">
                <label for="technique_id_rel">Technique ID:</label>
                <input type="text" id="technique_id_rel" placeholder="e.g., T1055" value="T1055">
            </div>
            <div class="input-group">
                <label for="depth">Analysis Depth:</label>
                <select id="depth">
                    <option value="1">1 - Direct relationships</option>
                    <option value="2" selected>2 - Extended relationships</option>
                    <option value="3">3 - Deep analysis</option>
                </select>
            </div>
        `
    };
    
    parametersDiv.innerHTML = parameterForms[selectedTool] || '';
}

async function runCustomQuery() {
    const toolSelect = document.getElementById('toolSelect');
    const selectedTool = toolSelect.value;
    
    if (!selectedTool) {
        showError('Please select a tool first.');
        return;
    }
    
    if (!isConnected) {
        showError('Not connected to MCP server. Please check the connection.');
        return;
    }
    
    // Collect parameters based on selected tool
    const params = {};
    const parameterDiv = document.getElementById('customParameters');
    const inputs = parameterDiv.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.value.trim()) {
            if (input.id === 'threat_groups' || input.id === 'exclude_mitigations') {
                // Handle comma-separated arrays
                params[input.id] = input.value.split(',').map(s => s.trim()).filter(s => s);
            } else if (input.type === 'number') {
                params[input.id] = parseInt(input.value);
            } else {
                params[input.id] = input.value.trim();
            }
        }
    });
    
    showLoading(`Custom ${selectedTool} Query`);
    
    try {
        const response = await fetch('/call_tool', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: selectedTool,
                arguments: params
            })
        });
        
        if (response.ok) {
            const result = await response.text();
            showResults(`Custom ${selectedTool} Results`, result);
        } else {
            const error = await response.text();
            showError(`Tool execution failed: ${error}`);
        }
    } catch (error) {
        showError(`Network error: ${error.message}`);
    }
}

// Results display
function showLoading(title) {
    const results = document.getElementById('results');
    results.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <span>Executing ${title}...</span>
        </div>
    `;
}

function showResults(title, content) {
    const results = document.getElementById('results');
    const timestamp = new Date().toLocaleTimeString();
    results.innerHTML = `<div class="success">✅ ${title} - ${timestamp}</div>\n\n${content}`;
    results.scrollTop = 0;
}

function showError(message) {
    const results = document.getElementById('results');
    const timestamp = new Date().toLocaleTimeString();
    results.innerHTML = `<div class="error">❌ Error - ${timestamp}\n\n${message}</div>`;
}