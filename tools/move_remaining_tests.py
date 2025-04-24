#!/usr/bin/env python3
"""
Script to handle the remaining test files in the root directory
that need special handling to avoid conflicts.
"""

import os
import shutil
from pathlib import Path

# Ensure we're running from the project root
ROOT_DIR = Path(os.getcwd())
if not (ROOT_DIR / "src").exists() or not (ROOT_DIR / "tests").exists():
    print("This script must be run from the project root directory.")
    exit(1)

# Special case: test_rescue_mechanics.py in root conflicts with tests/mechanic_tests/test_rescue_mechanics.py
# We'll rename it to basic_rescue_demo.py and move it to tests/mechanic_tests
source_file = ROOT_DIR / "test_rescue_mechanics.py"
target_dir = ROOT_DIR / "tests" / "mechanic_tests"
new_filename = "basic_rescue_demo.py"
target_file = target_dir / new_filename

if source_file.exists():
    # Make sure target directory exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Check if target already exists
    if target_file.exists():
        print(f"Warning: {target_file} already exists. Skipping.")
    else:
        try:
            shutil.copy(source_file, target_file)
            print(f"Copied {source_file} to {target_file}")
            
            # Remove the original file from root
            os.remove(source_file)
            print(f"Removed {source_file} from root directory")
        except Exception as e:
            print(f"Error moving file: {str(e)}")
else:
    print(f"{source_file} not found.")

print("Cleanup completed.") 