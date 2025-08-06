#!/usr/bin/env python3
"""
Debug script to test the group techniques fix.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
import json

def debug_group_techniques():
    """Debug the group techniques loading after the fix."""
    print("Debugging group techniques loading after fix...")
    
    # Initialize data loader
    loader = DataLoader()
    
    try:
        # Load MITRE ATT&CK data
        print("Loading MITRE ATT&CK data...")
        data = loader.load_data_source("mitre_attack")
        
        # Find APT29 (G0016)
        apt29 = None
        for group in data.get("groups", []):
            if group.get("id") == "G0016":
                apt29 = group
                break
        
        if not apt29:
            print("APT29 (G0016) not found!")
            return
        
        print(f"\nAPT29 Group: {apt29.get('name', 'Unknown')}")
        techniques = apt29.get("techniques", [])
        print(f"Number of techniques: {len(techniques)}")
        
        # Check for S-prefixed IDs (should be none now)
        s_techniques = [t for t in techniques if t.startswith("S")]
        t_techniques = [t for t in techniques if t.startswith("T")]
        
        print(f"T-prefixed techniques: {len(t_techniques)}")
        print(f"S-prefixed techniques (should be 0): {len(s_techniques)}")
        
        if s_techniques:
            print("ERROR: Still found S-prefixed techniques:")
            for s_tech in s_techniques[:5]:
                print(f"  {s_tech}")
        else:
            print("SUCCESS: No S-prefixed techniques found!")
        
        # Show first few T-techniques
        print(f"\nFirst 5 T-techniques:")
        for i, tech_id in enumerate(t_techniques[:5]):
            # Look up technique details
            tech_info = None
            for tech in data.get("techniques", []):
                if tech.get("id") == tech_id:
                    tech_info = tech
                    break
            
            if tech_info:
                print(f"  {tech_id}: {tech_info.get('name', 'Unknown')}")
            else:
                print(f"  {tech_id}: (Name not found)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_group_techniques()