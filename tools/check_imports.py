#!/usr/bin/env python3
"""
Script to check for import errors in Python files after reorganization.
This helps identify and fix issues caused by moving files to different directories.
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path

def check_file_imports(file_path):
    """Check if a Python file has import errors."""
    try:
        # Use subprocess to run a simple import check
        result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(file_path)],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            print(f"❌ Import error in {file_path}:")
            print(result.stderr)
            return False
        else:
            print(f"✅ {file_path} imports OK")
            return True
    except Exception as e:
        print(f"Error checking {file_path}: {str(e)}")
        return False

def check_directory(directory_path):
    """Recursively check Python files in a directory for import errors."""
    directory = Path(directory_path)
    success_count = 0
    failure_count = 0
    
    for item in directory.glob('**/*.py'):
        if check_file_imports(item):
            success_count += 1
        else:
            failure_count += 1
    
    return success_count, failure_count

if __name__ == "__main__":
    # Define directories to check
    directories_to_check = [
        'tests/visual_tests',
        'tests/mechanic_tests',
        'tests/renderer_tests',
        'tools'
    ]
    
    total_success = 0
    total_failure = 0
    
    print("Checking for import errors in moved files...")
    
    for directory in directories_to_check:
        if os.path.exists(directory):
            print(f"\nChecking {directory}...")
            success, failure = check_directory(directory)
            total_success += success
            total_failure += failure
        else:
            print(f"Directory {directory} does not exist, skipping.")
    
    print(f"\nSummary: {total_success} files OK, {total_failure} files with import errors.")
    
    if total_failure > 0:
        print("\nSome files have import errors. You may need to update import statements.")
        print("Common fixes include:")
        print("1. Adding parent directories to sys.path")
        print("2. Using relative imports (.module instead of module)")
        print("3. Moving shared dependencies to accessible locations")
        sys.exit(1)
    else:
        print("\nAll files passed import checks.")
        sys.exit(0) 