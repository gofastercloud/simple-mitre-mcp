#!/usr/bin/env python3
"""
Debug script to investigate the tactics loading issue.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader
import json

def debug_tactics():
    """Debug the tactics loading issue."""
    print("Debugging tactics loading...")
    
    # Initialize data loader
    loader = DataLoader()
    
    try:
        # Load MITRE ATT&CK data
        print("Loading MITRE ATT&CK data...")
        data = loader.load_data_source("mitre_attack")
        
        # Check what we got for tactics
        tactics = data.get("tactics", [])
        print(f"\nFound {len(tactics)} tactics")
        
        # Show first 10 tactics to see what's wrong
        print("\nFirst 10 tactics:")
        for i, tactic in enumerate(tactics[:10]):
            tactic_id = tactic.get("id", "N/A")
            tactic_name = tactic.get("name", "N/A")
            print(f"{i+1}. {tactic_id}: {tactic_name}")
        
        # Look for the problematic S-prefixed IDs
        s_tactics = [t for t in tactics if t.get("id", "").startswith("S")]
        if s_tactics:
            print(f"\nFound {len(s_tactics)} tactics with S-prefix (these should be techniques!):")
            for tactic in s_tactics[:5]:  # Show first 5
                print(f"  {tactic.get('id', 'N/A')}: {tactic.get('name', 'N/A')}")
        
        # Check techniques too
        techniques = data.get("techniques", [])
        print(f"\nFound {len(techniques)} techniques")
        
        # Look for T-prefixed techniques (normal)
        t_techniques = [t for t in techniques if t.get("id", "").startswith("T")]
        print(f"T-prefixed techniques: {len(t_techniques)}")
        
        # Look for S-prefixed techniques (should be here, not in tactics)
        s_techniques = [t for t in techniques if t.get("id", "").startswith("S")]
        print(f"S-prefixed techniques: {len(s_techniques)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_tactics()