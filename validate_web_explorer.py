#!/usr/bin/env python3
"""
Standalone Web Explorer Validation Script

This script can be run independently to validate the web explorer environment
and dependencies without starting the server. Useful for troubleshooting.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))


def main():
    """Main validation entry point."""
    print("🔍 MITRE ATT&CK MCP Web Explorer - Standalone Validation")
    print("=" * 60)

    try:
        # Import validation functions from start_explorer
        from start_explorer import run_startup_validation

        # Run comprehensive validation
        success = run_startup_validation()

        if success:
            print("\n🎉 SUCCESS: Web Explorer is ready to run!")
            print("   You can now start it with: uv run start_explorer.py")
            sys.exit(0)
        else:
            print("\n❌ VALIDATION FAILED: Please resolve the issues above.")
            sys.exit(1)

    except ImportError as e:
        print(f"❌ Failed to import validation functions: {e}")
        print("   This indicates a critical project structure issue.")
        print("\n🔧 Basic troubleshooting:")
        print("   1. Ensure you're in the project root directory")
        print("   2. Check that start_explorer.py exists")
        print("   3. Run: uv sync")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error during validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
