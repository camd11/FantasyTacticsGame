#!/usr/bin/env python3
"""
Thracia 776 Recreation - Main Runner
This script runs the Thracia 776 recreation game.
"""

import os
import sys
import importlib.util

def main():
    """
    Main entry point for the game.
    """
    # Check if the thracia776 package exists
    if not os.path.exists('thracia776'):
        print("Error: thracia776 directory not found.")
        print("Make sure you are running this script from the project root directory.")
        return 1
    
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        # Import and run the main function from thracia776.main
        from thracia776.main import main as game_main
        return game_main()
    except ImportError as e:
        print(f"Error importing game modules: {e}")
        print("Make sure all required packages are installed.")
        return 1
    except Exception as e:
        print(f"Error running the game: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())