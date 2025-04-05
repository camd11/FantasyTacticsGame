#!/usr/bin/env python3
"""
Thracia 776 Recreation - Test Runner
This script runs the test suite for the Thracia 776 recreation game.
"""

import os
import sys
import unittest

def main():
    """
    Main entry point for the test runner.
    """
    # Check if the thracia776 package exists
    if not os.path.exists('thracia776'):
        print("Error: thracia776 directory not found.")
        print("Make sure you are running this script from the project root directory.")
        return 1
    
    # Add the current directory to the Python path
    sys.path.insert(0, os.path.abspath('.'))
    
    try:
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = os.path.join('thracia776', 'tests')
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return 0 if result.wasSuccessful() else 1
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())