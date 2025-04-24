#!/usr/bin/env python
"""
Visual Tests Verification Script

This script simply runs a single test (movement by default) in headless mode
to confirm that the visual tests system is working correctly.

It will:
1. Run the test in headless mode
2. Check for successful execution
3. Print success or error messages

This is designed to be the simplest possible verification of the system.

Usage:
    python verify_visual_tests.py [--test TEST_NAME] [--with-screenshots]

Options:
    --test TEST_NAME      Test to run for verification (default: movement)
    --with-screenshots    Enable screenshot capture (disabled by default)
"""

import os
import sys
import time
import argparse
import logging
import pygame
from pathlib import Path
from datetime import datetime

# Set up Python path to include the project root
sys.path.insert(0, str(Path(__file__).parent))

# Set SDL to run in dummy mode for headless operation
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Import the test selector (which has all the key functionality)
from test_selector import TestSelector

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Verify visual tests are working")
    parser.add_argument("--test", type=str, default="movement",
                        help="Test to run for verification (default: movement)")
    parser.add_argument("--with-screenshots", action='store_true',
                        help="Enable screenshot capture (disabled by default)")
    return parser.parse_args()

def main():
    """Run the verification."""
    args = parse_args()
    test_name = args.test
    capture_screenshots = args.with_screenshots
    
    print(f"Verifying visual tests by running '{test_name}' test headlessly...")
    print(f"Screenshot capture: {'enabled' if capture_screenshots else 'disabled'}")
    
    # Create the directory for verification logs
    output_dir = Path("logs/verify_tests")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a test selector in headless mode
    test_selector = TestSelector(
        mode="headless", 
        test_duration=3,
        capture_screenshots=capture_screenshots
    )
    
    test_success = False
    
    try:
        # Run the verification test
        test_selector.run_test(test_name)
        
        # If we get here without exceptions, the test was successful
        test_success = True
        
        # Check if screenshots were saved (if requested)
        if capture_screenshots:
            screenshot_dir = Path("logs/test_selector/screenshots")
            screenshots = list(screenshot_dir.glob(f"*_{test_name}_*.png"))
            
            if screenshots:
                print(f"\nGenerated {len(screenshots)} screenshots:")
                for screenshot in screenshots:
                    print(f"  - {screenshot.name}")
            else:
                print("\nWarning: No screenshots were generated even though they were requested.")
                print("This doesn't necessarily mean the test failed, but it's worth investigating.")
        
        if test_success:
            print("\n✅ Verification successful!")
            print("\nVisual tests system is working correctly.")
    
    except Exception as e:
        print(f"\n❌ Verification failed with error: {str(e)}")
    
    finally:
        # Clean up
        test_selector.cleanup()
        
        # Exit with appropriate status code
        sys.exit(0 if test_success else 1)

if __name__ == "__main__":
    main() 