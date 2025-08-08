# Quick Start Guide

Get up and running with the MITRE ATT&CK MCP Server in 5 minutes.

## 🚀 One-Minute Setup

```bash
# 1. Install UV (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and install
git clone https://github.com/gofastercloud/simple-mitre-mcp.git
cd simple-mitre-mcp
uv sync

# 3. Start the web interface
uv run start_explorer.py
```

Open http://localhost:8000 in your browser - you're ready to go! 🎉

## 🎯 Try These First

### 1. Search for Techniques
- Click **"Search Attack"** 
- Try searching for: `process injection`, `persistence`, `lateral movement`
- Click on results to see detailed information with MITRE deep links

### 2. Explore a Threat Group
- Click **"Get Group Techniques"**
- Enter group ID: `G0016` (APT29/Cozy Bear)
- See all techniques used by this advanced persistent threat group

### 3. Investigate a Specific Technique
- Click **"Get Technique"**
- Enter technique ID: `T1055` (Process Injection)
- View comprehensive details including mitigations and detection methods

### 4. Understand Tactics
- Click **"List Tactics"**
- Explore the 14 MITRE ATT&CK tactics from Initial Access to Impact
- Each tactic shows associated techniques

## 🔧 Different Usage Modes

### Web Interface (Beginner-Friendly)
```bash
uv run start_explorer.py
```
- ✅ Visual interface with forms
- ✅ Formatted results with deep links
- ✅ Dark/light theme toggle
- ✅ Perfect for exploration and learning

### HTTP API (Programmatic)
```bash
uv run src/http_proxy.py
```
Then use curl or any HTTP client:
```bash
curl "http://localhost:8000/call_tool" \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "search_attack", "parameters": {"query": "persistence"}}'
```

### AI Assistant Integration
```bash
uv run src/main_stdio.py
```
Perfect for integrating with Claude Desktop or other MCP-compatible AI assistants.

## 🎛️ Essential Tools Overview

| Tool | Purpose | Example Usage |
|------|---------|---------------|
| **search_attack** | Find techniques, tactics, groups by keyword | Search "privilege escalation" |
| **get_technique** | Get detailed technique information | Look up T1055 details |
| **list_tactics** | See all 14 MITRE tactics | Browse the kill chain |
| **get_group_techniques** | See techniques used by threat groups | Analyze APT29 (G0016) |
| **get_technique_mitigations** | Find defenses for techniques | Get T1055 mitigations |
| **build_attack_path** | Construct attack scenarios | Map Initial Access → Impact |
| **analyze_coverage_gaps** | Identify defense gaps | Analyze coverage vs APT groups |
| **detect_technique_relationships** | Explore technique connections | Find T1055 relationships |

## 💡 Pro Tips

### 1. Use Autocomplete
- Technique fields have autocomplete - start typing "process" to find Process Injection
- Group and tactic dropdowns are pre-populated with current MITRE data

### 2. Explore Deep Links
- Click any MITRE ID (T1055, G0016, TA0001) to go directly to official MITRE documentation
- Results include color-coded links for easy identification

### 3. Theme Switching
- Toggle between dark/light themes using the button in the status bar
- Your preference is saved automatically

### 4. Copy and Download Results
- Use the copy button to copy results to clipboard
- Download button saves results as text files with timestamps

### 5. Result History
- Previous results are saved (last 10 queries)
- Use history panel to quickly restore previous searches

## 📊 System Dashboard

Click the **system info cards** at the top to see:
- **Loaded data statistics** (techniques, groups, tactics, mitigations)
- **Server capabilities** (available tools, interfaces)
- **Real-time status** (data freshness, server uptime)

## 🔍 Advanced Search Examples

### Find Specific Techniques
- `T1055` - Exact technique ID
- `process injection` - Name search
- `DLL injection` - Description search

### Threat Group Analysis
- `G0016` - APT29/Cozy Bear
- `G0032` - Lazarus Group  
- `G0007` - APT1/Comment Crew

### Tactic Exploration
- `TA0001` - Initial Access
- `TA0003` - Persistence
- `TA0040` - Impact

## 🚨 Troubleshooting Quick Fixes

### "Port already in use"
```bash
export MCP_HTTP_PORT=8001
uv run start_explorer.py
```

### "Data loading failed"
```bash
# Clear cache and retry
rm -rf ~/.cache/simple-mitre-mcp/
uv run start_explorer.py
```

### "Import errors"
```bash
# Reinstall dependencies
uv sync --reinstall
```

### "Web interface not loading"
```bash
# Check if server is running
curl http://localhost:8000/system_info

# Try different browser or incognito mode
```

## 📚 What's Next?

### Learning More
- **[User Guide](USER_GUIDE.md)** - Complete usage documentation
- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions

### Integration
- **[Claude Desktop Setup](../deployment/CONFIGURATION.md)** - AI assistant integration
- **[API Documentation](../developer/API.md)** - Programmatic usage
- **[Examples](../../examples/)** - Configuration templates

### Development
- **[Developer Guide](../developer/DEVELOPER_GUIDE.md)** - Contributing to the project
- **[Testing](../developer/TESTING.md)** - Running and writing tests

## 💬 Need Help?

1. **Check system info**: Visit http://localhost:8000 and look at the dashboard
2. **Run validation**: `./deployment/validate_web_explorer.sh`
3. **Check logs**: Look for error messages in the terminal output
4. **GitHub Issues**: Report bugs or ask questions
5. **Documentation**: Browse [docs/](../README.md) for detailed guides

Happy exploring! 🔍✨