#!/usr/bin/env python3
"""
Script to fix all string formatting issues in the MCP server.
Converts template strings to f-strings and fixes logging statements.
"""

import re

def fix_string_formatting(file_path):
    """Fix all string formatting issues in the given file."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix error messages and logging statements
    fixes = [
        # Error messages
        (r'text="Technique \'{technique_id}\' not found\. Please verify the technique ID is correct\."', 
         r'text=f"Technique \'{technique_id}\' not found. Please verify the technique ID is correct."'),
        
        (r'text="Group \'{group_id}\' not found\. Please verify the group ID is correct\."', 
         r'text=f"Group \'{group_id}\' not found. Please verify the group ID is correct."'),
        
        (r'text="Error: Group \'{group_id}\' not found\. Please verify the group ID is correct\."', 
         r'text=f"Error: Group \'{group_id}\' not found. Please verify the group ID is correct."'),
        
        (r'text="Error: Technique \'{tech_id}\' not found\. Please verify the technique ID is correct\."', 
         r'text=f"Error: Technique \'{tech_id}\' not found. Please verify the technique ID is correct."'),
        
        (r'text="No techniques found for group \'{group_id}\' \(\{group\.get\(\'name\', \'Unknown\'\)\}\)\."', 
         r'text=f"No techniques found for group \'{group_id}\' ({group.get(\'name\', \'Unknown\')})."'),
        
        (r'text="No mitigations found for technique \'{technique_id}\' \(\{technique\.get\(\'name\', \'Unknown\'\)\}\)\."', 
         r'text=f"No mitigations found for technique \'{technique_id}\' ({technique.get(\'name\', \'Unknown\')})."'),
        
        # Logging statements
        (r'logger\.error\("Error in (\w+): \{e\}"\)', r'logger.error(f"Error in \1: {e}")'),
        (r'logger\.info\("Executing (\w+)"\)', r'logger.info("Executing \1")'),
        (r'logger\.info\("Executing (\w+) with ID: \{(\w+)\}"\)', r'logger.info(f"Executing \1 with ID: {\2}")'),
        (r'logger\.info\("Executing (\w+) with group: \{(\w+)\}"\)', r'logger.info(f"Executing \1 with group: {\2}")'),
        
        # Error return statements
        (r'text="Error retrieving (\w+): \{str\(e\)\}"', r'text=f"Error retrieving \1: {str(e)}"'),
        (r'text="Error (\w+): \{str\(e\)\}"', r'text=f"Error \1: {str(e)}"'),
        
        # Exception handling
        (r'except Exception:', r'except Exception as e:'),
    ]
    
    # Apply all fixes
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content)
    
    # Fix remaining template strings in advanced functions
    # These are more complex patterns that need manual handling
    advanced_fixes = [
        # Coverage gaps analysis
        (r'f"COVERAGE GAP ANALYSIS\\n====================\\n\\nSpecific Techniques: \{.*?\}\\n', 
         r'f"COVERAGE GAP ANALYSIS\\n====================\\n\\nSpecific Techniques: {\', \'.join(technique_list)}\\n'),
        
        # Build attack path
        (r'f"ATTACK PATH CONSTRUCTION\\n========================\\n\\nPath Configuration:\\n  Start Tactic: \{.*?\}\\n', 
         r'f"ATTACK PATH CONSTRUCTION\\n========================\\n\\nPath Configuration:\\n  Start Tactic: {start_tactic}\\n'),
        
        # Technique relationships
        (r'f"TECHNIQUE RELATIONSHIP ANALYSIS\\n==============================\\n\\nPrimary Technique: \{.*?\}\\n', 
         r'f"TECHNIQUE RELATIONSHIP ANALYSIS\\n==============================\\n\\nPrimary Technique: {technique_id} - {technique.get(\'name\', \'Unknown\')}\\n'),
    ]
    
    for pattern, replacement in advanced_fixes:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed string formatting issues in {file_path}")

if __name__ == "__main__":
    fix_string_formatting("src/mcp_server.py")
