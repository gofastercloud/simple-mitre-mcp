# User Guide - MITRE ATT&CK MCP Web Explorer

Welcome to the MITRE ATT&CK MCP Web Explorer! This guide will help you get the most out of the interactive web interface for analyzing MITRE ATT&CK threat intelligence.

## Getting Started

### Accessing the Web Interface

1. **Start the server**:
   ```bash
   uv run start_explorer.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

3. **You should see** the Web Explorer dashboard with:
   - System statistics
   - Available tools
   - Interactive analysis interface

### First Look

The interface consists of several key sections:

- **📊 System Dashboard**: Overview of available data and system status
- **🔧 Tools Section**: Interactive forms for all 8 MCP tools
- **📋 Results Section**: Enhanced display area with smart formatting
- **🎨 Theme Toggle**: Switch between light and dark modes

## Dashboard Overview

### System Statistics
The dashboard shows real-time information about your MITRE ATT&CK data:

- **Techniques**: Total number of attack techniques (e.g., 823)
- **Groups**: Number of threat actor groups (e.g., 181)
- **Tactics**: Number of tactical categories (e.g., 14)
- **Mitigations**: Number of defensive mitigations (e.g., 393)
- **Relationships**: Total mapped relationships between entities

### Server Information
- **Version**: Current server version
- **Data Source**: MITRE ATT&CK Enterprise
- **Last Updated**: When data was last refreshed
- **Status**: Connection status to MCP server

## Using the Tools

### Tool Categories

#### Basic Analysis Tools (5 tools)
Perfect for fundamental threat intelligence queries:

1. **Search Attack**: Find techniques, groups, tactics, or mitigations
2. **List Tactics**: View all MITRE ATT&CK tactics
3. **Get Technique**: Detailed information about specific techniques
4. **Get Group Techniques**: Techniques used by threat groups
5. **Get Technique Mitigations**: Defensive measures for techniques

#### Advanced Threat Modeling Tools (3 tools)
For sophisticated threat analysis and planning:

1. **Build Attack Path**: Multi-stage attack path construction
2. **Analyze Coverage Gaps**: Defensive coverage analysis
3. **Detect Technique Relationships**: Complex relationship discovery

### Using Individual Tools

#### 1. Search Attack
**Purpose**: Universal search across all MITRE ATT&CK entities

**How to use**:
1. Enter search terms (e.g., "powershell", "lateral movement")
2. Click "Execute Search"
3. Browse results organized by entity type

**Examples**:
- Search for "persistence" to find related techniques
- Search for "APT29" to find group information
- Search for "endpoint" to find mitigation strategies

#### 2. Get Technique
**Purpose**: Deep dive into specific attack techniques

**How to use**:
1. Enter technique ID (e.g., "T1055", "T1059.001")
2. Or start typing technique name for autocomplete
3. View comprehensive technique details

**What you'll see**:
- Technique description and examples
- Related sub-techniques
- Detection methods
- Mitigation strategies
- Real-world usage examples

#### 3. Get Group Techniques
**Purpose**: Analyze techniques used by specific threat groups

**How to use**:
1. Select threat group from dropdown (e.g., "APT29", "Lazarus Group")
2. View all techniques attributed to that group
3. Analyze group's tactical preferences

**Use cases**:
- Threat modeling for specific adversaries
- Understanding group capabilities
- Planning defensive strategies

#### 4. Build Attack Path
**Purpose**: Construct multi-stage attack scenarios

**How to use**:
1. Select starting tactic (e.g., "Initial Access")
2. Select target tactic (e.g., "Exfiltration")
3. Optionally filter by group or platform
4. Generate possible attack paths

**Advanced options**:
- **Group Filter**: Limit to techniques used by specific groups
- **Platform Filter**: Focus on Windows, Linux, or macOS

#### 5. Analyze Coverage Gaps
**Purpose**: Identify defensive weaknesses

**How to use**:
1. Select threat groups to analyze
2. Optionally specify techniques to focus on
3. List implemented mitigations to exclude
4. Generate coverage gap analysis

**Output includes**:
- Unmitigated techniques
- High-priority defensive gaps
- Recommended mitigation priorities

## Understanding Results

### Enhanced Result Display

Results are presented in an intelligent, user-friendly format:

#### 🗂️ Accordion Interface
- **Collapsible sections** for easy navigation
- **Section badges** showing counts (e.g., "12 techniques")
- **Auto-expand** first section for immediate viewing
- **Mobile-responsive** design

#### 🔗 MITRE Deep Links
All MITRE identifiers automatically link to official documentation:
- **Groups** (G0001-G9999) → MITRE Groups database
- **Techniques** (T1055, T1055.001) → MITRE Techniques
- **Tactics** (TA0001-TA0043) → MITRE Tactics
- **Mitigations** (M1001-M1999) → MITRE Mitigations
- **Software** (S0001-S9999) → MITRE Software

#### 📝 Smart Text Formatting
- **Numbered lists** with proper hierarchy
- **Field labels** with color coding
- **Professional typography** for readability
- **Structured paragraphs** and sections

### Result Actions

#### 📋 Copy to Clipboard
- Click the copy button to copy results to clipboard
- Instant feedback with success notification
- Preserves formatting for documentation

#### 💾 Download Results
- Download results as text file
- Automatic filename with timestamp
- Perfect for reports and sharing

#### 🗑️ Clear Results
- Clear current results to start fresh
- Confirmation to prevent accidental loss

#### 📚 Result History
- **10-item history** of recent results
- **Restore previous results** with one click
- **Error/success indicators** for each item
- **Preview snippets** to identify results

## Smart Form Features

### 🎯 Autocomplete
- **Technique search**: Start typing technique names for suggestions
- **Real-time matching** on ID, name, and description
- **Intelligent ranking** (ID matches first, then name, then description)

### 📝 Smart Dropdowns  
- **Group selection**: Pre-populated with all threat groups and aliases
- **Tactic selection**: All MITRE tactics with descriptions
- **Dynamic options** based on available data

### ✅ Form Validation
- **Real-time validation** as you type
- **Required field indicators** with visual cues
- **Format guidance** for IDs and parameters
- **Clear error messages** with suggested fixes

## Theme and Customization

### 🎨 Dark/Light Mode
- **Dark mode default** for comfortable viewing
- **One-click toggle** in the top navigation
- **Automatic persistence** remembers your preference
- **Smooth transitions** between themes

### 📱 Responsive Design
- **Mobile-friendly** interface
- **Tablet optimization** for field work
- **Touch-friendly** controls and buttons
- **Adaptive layouts** for all screen sizes

## Error Handling and Support

### 🔧 Intelligent Error Messages
When something goes wrong, you'll see:

- **User-friendly explanations** instead of technical jargon
- **Actionable suggestions** for resolving issues
- **Recovery options** with one-click fixes
- **Technical details** available for advanced users

### Common Error Types

#### 🌐 Connection Issues
**What you'll see**: "Unable to connect to the server"
**What to try**:
- Check internet connection
- Verify server is running
- Try refreshing the page
- Wait a moment and try again

#### ⚠️ Validation Errors  
**What you'll see**: "There was a problem with your request"
**What to try**:
- Check all required fields are filled
- Verify input format is correct
- Ensure valid options are selected

#### 📊 Data Issues
**What you'll see**: "The requested technique was not found"
**What to try**:
- Check ID format (e.g., T1055)
- Verify the technique exists in MITRE ATT&CK
- Try searching for the technique first

#### 🔄 Recovery Options
- **Refresh Page**: Restart the interface
- **Try Again**: Retry the same action
- **Technical Details**: View detailed error information

## Tips and Best Practices

### 🎯 Effective Searching
- Use **specific terms** for better results
- Try **multiple variations** of technique names
- Include **context words** like "persistence" or "lateral movement"
- Use **technique IDs** when you know them

### 📊 Analysis Workflows

#### Threat Group Analysis
1. Use **Get Group Techniques** to understand group capabilities
2. Use **Build Attack Path** to model potential attack scenarios
3. Use **Analyze Coverage Gaps** to identify defensive priorities

#### Technique Research
1. Use **Search Attack** to find related techniques
2. Use **Get Technique** for detailed analysis
3. Use **Get Technique Mitigations** to understand defenses
4. Use **Detect Technique Relationships** to explore connections

#### Defense Planning
1. Use **Analyze Coverage Gaps** to identify weaknesses
2. Use **Get Technique Mitigations** to understand options
3. Use **Build Attack Path** to validate defensive strategies

### 🔍 Advanced Tips
- **Use the history feature** to compare different results
- **Download results** for offline analysis and reports
- **Copy specific sections** using text selection
- **Use MITRE deep links** to explore official documentation
- **Leverage autocomplete** to discover related techniques

## Keyboard Shortcuts

- **Ctrl/Cmd + K**: Focus search input
- **Escape**: Cancel current operation
- **Enter**: Submit forms (when focused)
- **Tab**: Navigate between form fields

## Performance Tips

### 🚀 Optimal Usage
- **Use specific search terms** to get faster results
- **Close unused result history** to save memory
- **Refresh periodically** for updated data
- **Use appropriate tools** for your analysis needs

### 📈 Large Dataset Handling
The interface is optimized for large results:
- **Accordion sections** prevent information overload
- **Lazy loading** for better performance
- **Smart truncation** with full data available
- **Efficient memory management**

## Getting Help

### 🔍 Built-in Help
- **Hover tooltips** on form fields and buttons
- **Contextual error messages** with specific guidance
- **Form validation** with real-time feedback
- **Smart suggestions** in error scenarios

### 📞 Support Resources
- **GitHub Issues**: Report bugs and request features
- **Documentation**: Complete technical documentation
- **Community**: User community and discussions

### 🐛 Reporting Issues
When reporting problems, include:
1. **Steps to reproduce** the issue
2. **Browser and version** you're using
3. **Error messages** or unexpected behavior
4. **Expected results** vs. actual results

## What's New

### Recent Enhancements
- **Enhanced error handling** with actionable guidance
- **Improved security** with comprehensive headers
- **Professional result display** with accordion interface
- **MITRE deep links** to official documentation
- **Smart form validation** with real-time feedback
- **Connection monitoring** and status indicators
- **Performance optimizations** for large datasets

### Upcoming Features
- Additional export formats (JSON, CSV)
- Saved search functionality
- Custom dashboards and views
- Advanced filtering options
- Collaborative features

---

**Happy analyzing!** 🎉

The MITRE ATT&CK MCP Web Explorer makes threat intelligence analysis accessible, interactive, and insightful. Whether you're a security analyst, researcher, or student, these tools help you understand and defend against modern cyber threats.