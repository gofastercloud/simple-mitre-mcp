"""
Tests for the web interface advanced tools integration.

This module tests the web explorer updates for the new
advanced threat modeling tools.
"""

import pytest
import json
import os


class TestWebInterfaceAdvanced:
    """Test web interface integration with advanced tools."""

    def test_web_explorer_html_contains_advanced_section(self):
        """Test that web_explorer.html contains the advanced tools section."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for advanced tools section
        assert '🚀 Advanced Threat Modeling Tools' in html_content, "Advanced tools section header not found"
        assert 'Build Attack Path' in html_content, "Build Attack Path button not found"
        assert 'Analyze Coverage Gaps' in html_content, "Analyze Coverage Gaps button not found"
        assert 'Detect Relationships' in html_content, "Detect Relationships button not found"

        # Check for advanced form elements
        assert 'buildAttackPath' in html_content, "buildAttackPath function not found"
        assert 'analyzeCoverageGaps' in html_content, "analyzeCoverageGaps function not found"
        assert 'detectTechniqueRelationships' in html_content, "detectTechniqueRelationships function not found"

    def test_web_explorer_html_contains_advanced_css(self):
        """Test that web_explorer.html contains CSS for advanced tools."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for advanced tool CSS classes
        assert '.advanced-section' in html_content, "Advanced section CSS class not found"
        assert '.advanced-button' in html_content, "Advanced button CSS not found"
        assert '.form-group' in html_content, "Form group CSS not found"

    def test_web_explorer_html_javascript_functions(self):
        """Test that web_explorer.html contains required JavaScript functions."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for JavaScript functions
        required_functions = [
            'callTool',
            'buildAttackPath',
            'analyzeCoverageGaps',
            'detectTechniqueRelationships'
        ]

        for func_name in required_functions:
            assert f'function {func_name}' in html_content, f"JavaScript function '{func_name}' not found"

    def test_web_explorer_html_form_configurations(self):
        """Test that web_explorer.html contains proper form configurations for each tool."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check for build_attack_path form elements
        assert 'start_tactic' in html_content, "start_tactic input not found"
        assert 'end_tactic' in html_content, "end_tactic input not found"
        assert 'group_id' in html_content, "group_id input not found"
        assert 'platform' in html_content, "platform select not found"

        # Check for analyze_coverage_gaps form elements
        assert 'threat_groups' in html_content, "threat_groups input not found"
        assert 'technique_list' in html_content, "technique_list input not found"
        assert 'exclude_mitigations' in html_content, "exclude_mitigations input not found"

        # Check for detect_technique_relationships form elements
        assert 'technique_id' in html_content, "technique_id input not found"
        assert 'relationship_types' in html_content, "relationship_types select not found"
        assert 'depth' in html_content, "depth select not found"

    def test_http_proxy_contains_advanced_tools(self):
        """Test that http_proxy.py contains the new advanced tools."""
        # Use relative path that works in both local and CI environments
        proxy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'http_proxy.py')
        
        with open(proxy_path, 'r') as f:
            proxy_content = f.read()

        # Check for advanced tool names
        assert 'build_attack_path' in proxy_content, "build_attack_path not found in HTTP proxy"
        assert 'analyze_coverage_gaps' in proxy_content, "analyze_coverage_gaps not found in HTTP proxy"
        assert 'detect_technique_relationships' in proxy_content, "detect_technique_relationships not found in HTTP proxy"

        # Check for array parameter support
        assert '"type": "array"' in proxy_content, "Array parameter support not found in HTTP proxy"
        assert '"items": {"type": "string"}' in proxy_content, "Array items schema not found in HTTP proxy"

    def test_http_proxy_tool_schemas(self):
        """Test that HTTP proxy contains proper schemas for advanced tools."""
        # Use relative path that works in both local and CI environments
        proxy_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'http_proxy.py')
        
        with open(proxy_path, 'r') as f:
            proxy_content = f.read()

        # Check for build_attack_path schema elements
        assert 'start_tactic' in proxy_content, "start_tactic parameter not found in HTTP proxy"
        assert 'end_tactic' in proxy_content, "end_tactic parameter not found in HTTP proxy"
        assert 'group_id' in proxy_content, "group_id parameter not found in HTTP proxy"

        # Check for analyze_coverage_gaps schema elements
        assert 'threat_groups' in proxy_content, "threat_groups parameter not found in HTTP proxy"
        assert 'technique_list' in proxy_content, "technique_list parameter not found in HTTP proxy"
        assert 'exclude_mitigations' in proxy_content, "exclude_mitigations parameter not found in HTTP proxy"

        # Check for detect_technique_relationships schema elements
        assert 'relationship_types' in proxy_content, "relationship_types parameter not found in HTTP proxy"
        assert 'depth' in proxy_content, "depth parameter not found in HTTP proxy"

    @pytest.mark.integration
    def test_start_explorer_script_compatibility(self):
        """Test that start_explorer.py is compatible with new tools."""
        # This test would verify that the start_explorer.py script
        # can successfully start the server with all 6 tools available
        # This is marked as integration test since it requires actual server startup

        # For now, just verify the file exists and is readable
        explorer_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'start_explorer.py')
        assert os.path.exists(explorer_path), "start_explorer.py not found"

        with open(explorer_path, 'r') as f:
            content = f.read()
            # Basic check that it's a Python script
            assert 'python' in content.lower() or 'import' in content, "start_explorer.py doesn't appear to be a Python script"

    def test_web_interface_tool_count_consistency(self):
        """Test that web interface expects the correct number of tools."""
        # This test ensures the web interface is consistent with the 6 tools we now have
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Count tool buttons in the HTML
        basic_tools = [
            'Search',
            'List All Tactics',
            'Get Technique',
            'Get Group Techniques',
            'Get Mitigations'
        ]

        advanced_tools = [
            'Build Attack Path',
            'Analyze Coverage Gaps',
            'Detect Relationships'
        ]

        # Verify all basic tools are present
        for tool in basic_tools:
            assert tool in html_content, f"Basic tool '{tool}' not found in web interface"

        # Verify all advanced tools are present
        for tool in advanced_tools:
            assert tool in html_content, f"Advanced tool '{tool}' not found in web interface"

    def test_web_interface_styling_consistency(self):
        """Test that advanced tools have consistent styling with basic tools."""
        # Use relative path that works in both local and CI environments
        html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web_explorer.html')
        
        with open(html_path, 'r') as f:
            html_content = f.read()

        # Check that advanced tools use the advanced-button class
        assert 'advanced-button' in html_content, "Advanced tools don't use advanced-button styling"

        # Check that advanced tools have proper hover effects
        assert '.advanced-button:hover' in html_content, "Advanced tools don't have hover effects"

        # Check that the advanced section follows the same pattern as other sections
        assert '<h2>🚀 Advanced Threat Modeling Tools</h2>' in html_content, "Advanced section header not properly formatted"
