"""
Unit tests for SystemDashboard component functionality.

This module tests the SystemDashboard JavaScript component logic and structure.
Since the component is primarily JavaScript, these tests focus on the Python
integration aspects and component structure validation.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock


class TestSystemDashboardComponent:
    """Test suite for SystemDashboard JavaScript component."""

    @pytest.fixture
    def components_js_content(self):
        """Read the actual components.js file content."""
        components_path = os.path.join(os.path.dirname(__file__), '..', 'web_interface', 'js', 'components.js')
        if os.path.exists(components_path):
            with open(components_path, 'r') as f:
                return f.read()
        return ""

    @pytest.fixture
    def mock_system_info(self):
        """Mock system information data for testing."""
        return {
            "server_info": {
                "version": "1.0.0",
                "data_source": "MITRE ATT&CK Enterprise",
                "startup_time": "2024-01-15T10:30:00Z"
            },
            "data_statistics": {
                "techniques_count": 185,
                "tactics_count": 14,
                "groups_count": 142,
                "mitigations_count": 42,
                "relationships_count": 1250
            }
        }

    def test_components_js_file_exists(self, components_js_content):
        """Test that the components.js file exists and contains SystemDashboard class."""
        assert components_js_content != "", "components.js file should exist and not be empty"
        assert "class SystemDashboard" in components_js_content, "Should contain SystemDashboard class"
        assert "constructor(containerId)" in components_js_content, "Should have proper constructor"
        assert "async render()" in components_js_content, "Should have render method"

    def test_dashboard_template_structure(self, components_js_content):
        """Test that dashboard templates contain required elements."""
        # Check for required template methods
        assert "getDashboardTemplate()" in components_js_content, "Should have getDashboardTemplate method"
        assert "getLoadingTemplate()" in components_js_content, "Should have getLoadingTemplate method"
        assert "getErrorTemplate()" in components_js_content, "Should have getErrorTemplate method"
        
        # Check for required HTML elements in templates
        assert "dashboard-title" in components_js_content, "Should include dashboard title"
        assert "stats-grid" in components_js_content, "Should include stats grid"
        assert "stat-card" in components_js_content, "Should include stat cards"
        assert "server-info" in components_js_content, "Should include server info section"

    def test_dashboard_stat_elements(self, components_js_content):
        """Test that dashboard includes all required stat elements."""
        # Check for all 6 stat cards
        stat_elements = [
            'techniques-count',
            'tactics-count', 
            'groups-count',
            'mitigations-count',
            'relationships-count'
        ]
        
        for element_id in stat_elements:
            assert element_id in components_js_content, f"Should include {element_id} element"
        
        # Check for server info elements
        server_info_elements = [
            'server-version',
            'data-source',
            'last-updated'
        ]
        
        for element_id in server_info_elements:
            assert element_id in components_js_content, f"Should include {element_id} element"

    def test_dashboard_loading_state(self, components_js_content):
        """Test dashboard loading state functionality."""
        # Check for loading state methods and elements
        assert "renderLoadingState()" in components_js_content, "Should have renderLoadingState method"
        assert "getLoadingTemplate()" in components_js_content, "Should have getLoadingTemplate method"
        assert "loading-skeleton" in components_js_content, "Should include loading skeleton elements"
        assert "getSkeletonStatCard" in components_js_content, "Should have skeleton stat card method"

    def test_dashboard_error_state(self, components_js_content):
        """Test dashboard error state functionality."""
        # Check for error state methods and elements
        assert "renderError()" in components_js_content, "Should have renderError method"
        assert "getErrorTemplate()" in components_js_content, "Should have getErrorTemplate method"
        assert "alert-danger" in components_js_content, "Should include error alert"
        assert "retry-dashboard" in components_js_content, "Should include retry button"
        assert "setupErrorEventListeners()" in components_js_content, "Should have error event listeners"

    def test_dashboard_interaction_methods(self, components_js_content):
        """Test dashboard interaction and event handling methods."""
        # Check for interaction methods
        assert "setupEventListeners()" in components_js_content, "Should have setupEventListeners method"
        assert "handleStatCardHover" in components_js_content, "Should have hover handler"
        assert "handleStatCardLeave" in components_js_content, "Should have leave handler"
        assert "handleStatCardClick" in components_js_content, "Should have click handler"

    def test_dashboard_custom_events(self, components_js_content):
        """Test dashboard custom event emission."""
        # Check for custom event handling
        assert "CustomEvent" in components_js_content, "Should emit custom events"
        assert "statCardClick" in components_js_content, "Should emit statCardClick event"
        assert "dispatchEvent" in components_js_content, "Should dispatch events"

    def test_dashboard_utility_methods(self, components_js_content):
        """Test dashboard utility and lifecycle methods."""
        # Check for utility methods
        assert "async refresh()" in components_js_content, "Should have refresh method"
        assert "getSystemInfo()" in components_js_content, "Should have getSystemInfo method"
        assert "isLoadingData()" in components_js_content, "Should have isLoadingData method"
        assert "hasErrorState()" in components_js_content, "Should have hasErrorState method"
        assert "destroy()" in components_js_content, "Should have destroy method"

    def test_dashboard_animation_methods(self, components_js_content):
        """Test dashboard animation and visual effect methods."""
        # Check for animation methods
        assert "animateStatUpdate" in components_js_content, "Should have stat animation method"
        assert "requestAnimationFrame" in components_js_content, "Should use requestAnimationFrame"
        assert "toLocaleString" in components_js_content, "Should format numbers with locale"

    def test_dashboard_accessibility_features(self, components_js_content):
        """Test dashboard accessibility features."""
        # Check for proper HTML structure
        assert "<h1" in components_js_content, "Should have h1 heading"
        assert "dashboard-title" in components_js_content, "Should have proper title class"
        assert "bi bi-shield-check" in components_js_content, "Should have icon for visual context"
        
        # Check for proper labeling
        assert "stat-label" in components_js_content, "Should have stat labels"
        assert "info-label" in components_js_content, "Should have info labels"

    def test_dashboard_error_handling(self, components_js_content):
        """Test dashboard error handling mechanisms."""
        # Check for error handling
        assert "try {" in components_js_content, "Should have try-catch blocks"
        assert "catch (error)" in components_js_content, "Should catch errors"
        assert "console.error" in components_js_content, "Should log errors"
        assert "this.hasError = true" in components_js_content, "Should track error state"
        assert "this.errorMessage" in components_js_content, "Should store error messages"

    def test_dashboard_data_handling(self, components_js_content):
        """Test dashboard data handling and fallbacks."""
        # Check for data validation and fallbacks
        assert "|| 0" in components_js_content, "Should have fallback values for missing data"
        assert "|| 'Unknown'" in components_js_content, "Should have fallback text for missing info"
        assert "stats.techniques_count || 0" in components_js_content, "Should handle missing technique count"
        assert "serverInfo.version || 'Unknown'" in components_js_content, "Should handle missing version"

    def test_dashboard_api_integration(self, components_js_content):
        """Test dashboard API integration."""
        # Check for API usage
        assert "api.getSystemInfo()" in components_js_content, "Should call API for system info"
        assert "await api.getSystemInfo()" in components_js_content, "Should use async/await"
        assert "this.systemInfo = await" in components_js_content, "Should store API response"

    def test_dashboard_css_classes(self, components_js_content):
        """Test that dashboard uses proper CSS classes."""
        # Check for Bootstrap and custom CSS classes
        css_classes = [
            'dashboard-title',
            'dashboard-subtitle', 
            'stats-grid',
            'stat-card',
            'stat-number',
            'stat-label',
            'server-info',
            'info-item',
            'info-label',
            'info-value',
            'alert-danger',
            'btn',
            'loading-skeleton'
        ]
        
        for css_class in css_classes:
            assert css_class in components_js_content, f"Should include {css_class} CSS class"

    def test_dashboard_bootstrap_integration(self, components_js_content):
        """Test dashboard Bootstrap integration."""
        # Check for Bootstrap icons
        assert "bi bi-shield-check" in components_js_content, "Should use Bootstrap icons"
        assert "bi bi-exclamation-triangle-fill" in components_js_content, "Should use error icon"
        assert "bi bi-arrow-clockwise" in components_js_content, "Should use refresh icon"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])