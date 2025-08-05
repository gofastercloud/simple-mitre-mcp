#!/usr/bin/env python3
"""
Tests for advanced web interface functionality.

This module tests the web interface components that support advanced threat modeling tools,
including the HTML structure, CSS styling, JavaScript functions, and HTTP proxy integration.
"""

import os
import pytest
from pathlib import Path


class TestWebInterfaceAdvanced:
    """Test advanced web interface functionality."""

    def test_web_explorer_html_contains_advanced_section(self):
        """Test that web_explorer.html contains advanced tools section."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for advanced tools section in the new tabbed interface
        assert "Advanced Analysis" in html_content, "Advanced Analysis tab not found"
        assert (
            "Attack Path Analysis" in html_content
        ), "Attack Path Analysis demo not found"
        assert (
            "Coverage Gap Analysis" in html_content
        ), "Coverage Gap Analysis demo not found"
        assert (
            "Relationship Discovery" in html_content
        ), "Relationship Discovery demo not found"

        # Check for advanced tool demos
        assert "build_attack_path" in html_content, "build_attack_path tool not found"
        assert (
            "analyze_coverage_gaps" in html_content
        ), "analyze_coverage_gaps tool not found"
        assert (
            "detect_technique_relationships" in html_content
        ), "detect_technique_relationships tool not found"

    def test_web_explorer_html_contains_advanced_css(self):
        """Test that web_explorer.html contains CSS for advanced tools."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for modern CSS classes used in the new interface
        assert ".demo-card" in html_content, "Demo card CSS class not found"
        assert ".tab-content" in html_content, "Tab content CSS not found"
        assert (
            ".custom-input-section" in html_content
        ), "Custom input section CSS not found"
        assert ".input-group" in html_content, "Input group CSS not found"

    def test_web_explorer_html_javascript_functions(self):
        """Test that web_explorer.html contains required JavaScript functions."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for JavaScript functions in the new interface
        required_functions = [
            "runDemo",
            "runCustomQuery",
            "switchTab",
            "updateCustomForm",
            "checkConnection",
        ]

        for func_name in required_functions:
            assert (
                f"function {func_name}" in html_content
                or f"{func_name}(" in html_content
            ), f"JavaScript function '{func_name}' not found"

        # Check for demo configurations
        assert (
            "attack_path:" in html_content
        ), "Attack path demo configuration not found"
        assert (
            "coverage_gaps:" in html_content
        ), "Coverage gaps demo configuration not found"
        assert (
            "technique_relationships:" in html_content
        ), "Technique relationships demo configuration not found"

    def test_web_explorer_html_form_configurations(self):
        """Test that web_explorer.html contains proper form configurations for each tool."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for form elements in the custom query tab
        assert "start_tactic" in html_content, "start_tactic input not found"
        assert "end_tactic" in html_content, "end_tactic input not found"
        assert "threat_groups" in html_content, "threat_groups input not found"
        assert "technique_id_rel" in html_content, "technique_id_rel input not found"

        # Check for tool selection dropdown
        assert "toolSelect" in html_content, "Tool selection dropdown not found"
        assert "build_attack_path" in html_content, "build_attack_path option not found"
        assert (
            "analyze_coverage_gaps" in html_content
        ), "analyze_coverage_gaps option not found"
        assert (
            "detect_technique_relationships" in html_content
        ), "detect_technique_relationships option not found"

    def test_http_proxy_contains_advanced_tools(self):
        """Test that http_proxy.py contains advanced tool definitions."""
        # Use relative path that works in both local and CI environments
        proxy_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "http_proxy.py"
        )

        with open(proxy_path, "r") as f:
            proxy_content = f.read()

        # Check for advanced tools in the HTTP proxy
        assert (
            "build_attack_path" in proxy_content
        ), "build_attack_path not found in HTTP proxy"
        assert (
            "analyze_coverage_gaps" in proxy_content
        ), "analyze_coverage_gaps not found in HTTP proxy"
        assert (
            "detect_technique_relationships" in proxy_content
        ), "detect_technique_relationships not found in HTTP proxy"

        # Check for tool descriptions
        assert (
            "multi-stage attack paths" in proxy_content
        ), "Attack path description not found"
        assert "coverage gaps" in proxy_content, "Coverage gaps description not found"
        assert (
            "STIX relationships" in proxy_content
        ), "STIX relationships description not found"

    def test_http_proxy_tool_schemas(self):
        """Test that http_proxy.py contains proper schemas for advanced tools."""
        # Use relative path that works in both local and CI environments
        proxy_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "http_proxy.py"
        )

        with open(proxy_path, "r") as f:
            proxy_content = f.read()

        # Check for required parameters in tool schemas
        assert "start_tactic" in proxy_content, "start_tactic parameter not found"
        assert "end_tactic" in proxy_content, "end_tactic parameter not found"
        assert "threat_groups" in proxy_content, "threat_groups parameter not found"
        assert "technique_id" in proxy_content, "technique_id parameter not found"

        # Check for parameter types
        assert '"type": "array"' in proxy_content, "Array parameter type not found"
        assert (
            '"items": {"type": "string"}' in proxy_content
        ), "Array items type not found"

    def test_start_explorer_script_compatibility(self):
        """Test that start_explorer.py is compatible with the new interface."""
        # Use relative path that works in both local and CI environments
        script_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "start_explorer.py"
        )

        with open(script_path, "r") as f:
            script_content = f.read()

        # Check for async compatibility
        assert (
            "async def" in script_content
        ), "Async functions not found in start_explorer.py"
        assert (
            "create_http_proxy_server" in script_content
        ), "create_http_proxy_server import not found"
        assert "aiohttp" in script_content, "aiohttp dependency check not found"

    def test_web_interface_tool_count_consistency(self):
        """Test that web interface shows consistent tool count."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )
        proxy_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "http_proxy.py"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        with open(proxy_path, "r") as f:
            proxy_content = f.read()

        # Check that web interface mentions 8 tools
        assert (
            "8 Tools Available" in html_content
            or "8 (5 basic + 3 advanced" in html_content
        ), "Tool count not found in web interface"

        # Count tools in HTTP proxy
        tool_count = proxy_content.count('"name":')
        assert (
            tool_count >= 8
        ), f"Expected at least 8 tools in HTTP proxy, found {tool_count}"

    def test_web_interface_styling_consistency(self):
        """Test that web interface has consistent modern styling."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "web_explorer.html"
        )

        with open(html_path, "r") as f:
            html_content = f.read()

        # Check for modern CSS features
        assert "var(--" in html_content, "CSS custom properties not found"
        assert "linear-gradient" in html_content, "Gradient styling not found"
        assert "border-radius" in html_content, "Modern border radius not found"
        assert "box-shadow" in html_content, "Modern shadows not found"

        # Check for responsive design
        assert "@media" in html_content, "Responsive media queries not found"
        assert "grid-template-columns" in html_content, "CSS Grid not found"
        assert "flex" in html_content, "Flexbox not found"

        # Check for modern interaction features
        assert "transition:" in html_content, "CSS transitions not found"
        assert "transform:" in html_content, "CSS transforms not found"
        assert ":hover" in html_content, "Hover effects not found"
