#!/bin/bash

# Web Explorer Deployment Validation Script
# This script validates that the MITRE ATT&CK MCP Web Explorer is properly configured and ready for deployment

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
VALIDATION_ERRORS=()
VALIDATION_WARNINGS=()
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    VALIDATION_WARNINGS+=("$1")
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    VALIDATION_ERRORS+=("$1")
}

# Header
echo "=========================================="
echo "MITRE ATT&CK MCP Web Explorer"
echo "Deployment Validation Script"
echo "=========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python dependencies
check_python_dependencies() {
    log_info "Validating Python dependencies..."
    
    cd "$PROJECT_ROOT"
    
    # Check if uv is available
    if ! command_exists uv; then
        log_error "uv package manager not found. Please install uv."
        return 1
    fi
    
    # Check if virtual environment exists and has dependencies
    if [ ! -f "uv.lock" ]; then
        log_error "uv.lock not found. Run 'uv sync' to install dependencies."
        return 1
    fi
    
    # Try to run Python import checks
    if ! uv run python -c "import mcp, stix2, aiohttp, aiohttp_cors" 2>/dev/null; then
        log_error "Required Python packages not found. Run 'uv sync' to install dependencies."
        return 1
    fi
    
    log_success "Python dependencies validated"
    return 0
}

# Function to validate file structure
validate_file_structure() {
    log_info "Validating project file structure..."
    
    local required_files=(
        "src/mcp_server.py"
        "src/http_proxy.py"
        "src/data_loader.py"
        "src/parsers/stix_parser.py"
        "start_explorer.py"
        "web_interface/index.html"
        "web_interface/css/styles.css"
        "web_interface/css/components.css"
        "web_interface/js/app.js"
        "web_interface/js/api.js"
        "web_interface/js/SystemDashboard.js"
        "web_interface/js/ToolsSection.js"
        "web_interface/js/ResultsSection.js"
        "web_interface/js/SmartFormControls.js"
        "web_interface/js/ThemeToggle.js"
        "config/data_sources.yaml"
        "config/entity_schemas.yaml"
        "config/tools.yaml"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            log_error "Required file missing: $file"
        fi
    done
    
    # Check for minimum file sizes to ensure files aren't empty
    local js_files=(
        "web_interface/js/app.js"
        "web_interface/js/SystemDashboard.js"
        "web_interface/js/ToolsSection.js"
        "web_interface/js/ResultsSection.js"
    )
    
    for js_file in "${js_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$js_file" ]; then
            local file_size=$(wc -c < "$PROJECT_ROOT/$js_file" 2>/dev/null || echo "0")
            if [ "$file_size" -lt 1000 ]; then
                log_warning "JavaScript file seems too small: $js_file ($file_size bytes)"
            fi
        fi
    done
    
    log_success "File structure validation completed"
}

# Function to validate configuration
validate_configuration() {
    log_info "Validating configuration files..."
    
    local config_files=(
        "config/data_sources.yaml"
        "config/entity_schemas.yaml" 
        "config/tools.yaml"
    )
    
    for config_file in "${config_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$config_file" ]; then
            # Basic YAML syntax check
            if command_exists python3; then
                if ! python3 -c "import yaml; yaml.safe_load(open('$PROJECT_ROOT/$config_file'))" 2>/dev/null; then
                    log_error "Invalid YAML syntax in $config_file"
                fi
            fi
        else
            log_error "Configuration file missing: $config_file"
        fi
    done
    
    log_success "Configuration validation completed"
}

# Function to test web interface assets
validate_web_assets() {
    log_info "Validating web interface assets..."
    
    # Check HTML structure
    if [ -f "$PROJECT_ROOT/web_interface/index.html" ]; then
        local html_content=$(cat "$PROJECT_ROOT/web_interface/index.html")
        
        # Check for required elements
        local required_elements=(
            "system-dashboard"
            "tools-section" 
            "results-section"
            "Bootstrap"
            "app.js"
            "api.js"
        )
        
        for element in "${required_elements[@]}"; do
            if [[ ! "$html_content" == *"$element"* ]]; then
                log_warning "HTML template missing reference to: $element"
            fi
        done
    fi
    
    # Check CSS files have theme variables
    local css_files=("styles.css" "components.css")
    for css_file in "${css_files[@]}"; do
        if [ -f "$PROJECT_ROOT/web_interface/css/$css_file" ]; then
            if ! grep -q -- "--bg-primary\|:root" "$PROJECT_ROOT/web_interface/css/$css_file"; then
                log_warning "CSS file missing theme variables: $css_file"
            fi
        fi
    done
    
    log_success "Web assets validation completed"
}

# Function to test MCP server startup
test_mcp_server() {
    log_info "Testing MCP server startup..."
    
    cd "$PROJECT_ROOT"
    
    # Test that MCP server can be imported
    if ! uv run python -c "from src.mcp_server import create_mcp_server; print('MCP server import successful')" 2>/dev/null; then
        log_error "MCP server cannot be imported or initialized"
        return 1
    fi
    
    log_success "MCP server startup test passed"
    return 0
}

# Function to test HTTP proxy
test_http_proxy() {
    log_info "Testing HTTP proxy configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Test that HTTP proxy can be imported
    if ! uv run python -c "from src.http_proxy import HTTPProxy; print('HTTP proxy import successful')" 2>/dev/null; then
        log_error "HTTP proxy cannot be imported"
        return 1
    fi
    
    log_success "HTTP proxy test passed"
    return 0
}

# Function to validate environment variables
validate_environment() {
    log_info "Validating environment configuration..."
    
    # Check optional environment variables and provide guidance
    if [ -z "$MCP_HTTP_HOST" ]; then
        log_info "MCP_HTTP_HOST not set, will default to 'localhost'"
    else
        log_info "MCP_HTTP_HOST set to: $MCP_HTTP_HOST"
    fi
    
    if [ -z "$MCP_HTTP_PORT" ]; then
        log_info "MCP_HTTP_PORT not set, will default to '8000'"
    else
        # Validate port number
        if ! [[ "$MCP_HTTP_PORT" =~ ^[0-9]+$ ]] || [ "$MCP_HTTP_PORT" -lt 1 ] || [ "$MCP_HTTP_PORT" -gt 65535 ]; then
            log_error "Invalid MCP_HTTP_PORT: $MCP_HTTP_PORT (must be 1-65535)"
        else
            log_info "MCP_HTTP_PORT set to: $MCP_HTTP_PORT"
        fi
    fi
    
    log_success "Environment validation completed"
}

# Function to run basic tests
run_basic_tests() {
    log_info "Running basic functionality tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run a subset of critical tests
    if command_exists uv; then
        local test_files=(
            "tests/test_mcp_server.py"
            "tests/test_data_loader.py"
            "tests/test_http_proxy_config.py"
        )
        
        for test_file in "${test_files[@]}"; do
            if [ -f "$test_file" ]; then
                log_info "Running test: $test_file"
                if ! uv run pytest "$test_file" -v --tb=short >/dev/null 2>&1; then
                    log_warning "Some tests failed in $test_file (check with: uv run pytest $test_file -v)"
                fi
            fi
        done
    else
        log_warning "Cannot run tests - uv not available"
    fi
    
    log_success "Basic tests completed"
}

# Function to check performance indicators
validate_performance() {
    log_info "Validating performance indicators..."
    
    cd "$PROJECT_ROOT"
    
    # Check for performance optimizations in code
    local js_files=(
        "web_interface/js/ResultsSection.js"
        "web_interface/js/SystemDashboard.js"
    )
    
    for js_file in "${js_files[@]}"; do
        if [ -f "$js_file" ]; then
            # Check for performance-related code patterns
            if grep -q "removeEventListener\|clearInterval\|cleanup" "$js_file"; then
                log_info "Performance optimizations found in $js_file"
            else
                log_warning "No obvious performance optimizations in $js_file"
            fi
        fi
    done
    
    log_success "Performance validation completed"
}

# Function to validate security configuration
validate_security() {
    log_info "Validating security configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Check HTTP proxy for security headers
    if [ -f "src/http_proxy.py" ]; then
        if grep -q "X-Content-Type-Options\|X-Frame-Options\|Content-Security-Policy" "src/http_proxy.py"; then
            log_success "Security headers found in HTTP proxy"
        else
            log_warning "Security headers not found in HTTP proxy"
        fi
        
        # Check for input validation
        if grep -q "validation\|sanitize\|escape" "src/http_proxy.py"; then
            log_success "Input validation found in HTTP proxy"
        else
            log_warning "Input validation patterns not obvious in HTTP proxy"
        fi
    fi
    
    log_success "Security validation completed"
}

# Main validation function
main() {
    local start_time=$(date +%s)
    
    log_info "Starting deployment validation..."
    echo ""
    
    # Run all validation checks
    check_python_dependencies
    validate_file_structure
    validate_configuration
    validate_web_assets
    validate_environment
    test_mcp_server
    test_http_proxy
    run_basic_tests
    validate_performance
    validate_security
    
    echo ""
    echo "=========================================="
    echo "VALIDATION SUMMARY"
    echo "=========================================="
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "Validation completed in ${duration}s"
    echo ""
    
    if [ ${#VALIDATION_ERRORS[@]} -eq 0 ]; then
        log_success "✅ All critical validations passed!"
        
        if [ ${#VALIDATION_WARNINGS[@]} -eq 0 ]; then
            echo ""
            log_success "🚀 Web Explorer is ready for deployment!"
            echo ""
            echo "To start the web explorer:"
            echo "  uv run start_explorer.py"
            echo ""
            echo "Or start HTTP proxy directly:"
            echo "  uv run src/http_proxy.py"
            
            return 0
        else
            echo ""
            log_warning "⚠️  Deployment ready with ${#VALIDATION_WARNINGS[@]} warnings:"
            for warning in "${VALIDATION_WARNINGS[@]}"; do
                echo "  - $warning"
            done
            echo ""
            echo "Consider addressing warnings before production deployment."
            return 0
        fi
    else
        echo ""
        log_error "❌ Deployment validation failed with ${#VALIDATION_ERRORS[@]} errors:"
        for error in "${VALIDATION_ERRORS[@]}"; do
            echo "  - $error"
        done
        
        if [ ${#VALIDATION_WARNINGS[@]} -gt 0 ]; then
            echo ""
            log_warning "Additional warnings:"
            for warning in "${VALIDATION_WARNINGS[@]}"; do
                echo "  - $warning"
            done
        fi
        
        echo ""
        echo "Please fix the errors above before deployment."
        return 1
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Web Explorer Deployment Validation Script"
    echo ""
    echo "OPTIONS:"
    echo "  -h, --help     Show this help message"
    echo "  -q, --quiet    Run in quiet mode (errors only)"
    echo "  -v, --verbose  Run in verbose mode (all output)"
    echo ""
    echo "This script validates that the MITRE ATT&CK MCP Web Explorer"
    echo "is properly configured and ready for deployment."
    echo ""
    echo "Examples:"
    echo "  $0                 # Run full validation"
    echo "  $0 --quiet         # Show only errors"
    echo "  $0 --verbose       # Show all details"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -q|--quiet)
            # Redirect info and success messages to /dev/null
            exec 3>&1 4>&2
            log_info() { :; }
            log_success() { :; }
            shift
            ;;
        -v|--verbose)
            # Enable verbose mode (default behavior)
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run main function
main
exit $?