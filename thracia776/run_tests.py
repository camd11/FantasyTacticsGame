#!/usr/bin/env python3
"""
Test runner for the Thracia 776 recreation project.
This script discovers and runs all tests in the tests directory.
"""

import unittest
import os
import sys

def run_tests():
    """
    Discover and run all tests in the tests directory.
    """
    # No need to modify sys.path for relative imports
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())