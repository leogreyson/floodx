#!/usr/bin/env python3
"""
FloodX Launcher Script
Ensures the tool is run from the correct directory with proper imports.
"""

import os
import sys
import asyncio
from pathlib import Path

def main():
    """Launch FloodX from the correct directory."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Change to the script directory to ensure proper imports
    os.chdir(script_dir)
    
    # Add current directory to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Import and run the main module
    try:
        from main import main as floodx_main
        from common.colors import create_colored_banner, success_text, error_text
        
        # Display colored banner
        print(create_colored_banner())
        
        # Run the async main function
        asyncio.run(floodx_main())
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("📁 Please ensure you're running from the correct directory.")
        print(f"   Current directory: {os.getcwd()}")
        print(f"   Expected directory: {script_dir}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n{success_text('🛑 FloodX terminated. Stay safe!')}")
    except Exception as e:
        print(f"{error_text('❌ Fatal error:')} {error_text(str(e))}")
        sys.exit(1)

if __name__ == "__main__":
    main()
