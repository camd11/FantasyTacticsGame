#!/usr/bin/env python3
"""
Script to clean up Python cache files and directories.
This removes __pycache__ directories and .pyc files.
"""

import os
import shutil
from pathlib import Path

def cleanup_cache(directory):
    """
    Recursively remove __pycache__ directories and .pyc files.
    
    Args:
        directory: The directory to clean
    
    Returns:
        tuple: (count of removed dirs, count of removed files)
    """
    dir_count = 0
    file_count = 0
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(directory, topdown=False):
        # Remove __pycache__ directories
        for d in dirs:
            if d == "__pycache__" or d == ".pytest_cache":
                path = os.path.join(root, d)
                print(f"Removing directory: {path}")
                try:
                    shutil.rmtree(path)
                    dir_count += 1
                except Exception as e:
                    print(f"  Error: {e}")
        
        # Remove .pyc files
        for f in files:
            if f.endswith(".pyc") or f.endswith(".pyo"):
                path = os.path.join(root, f)
                print(f"Removing file: {path}")
                try:
                    os.remove(path)
                    file_count += 1
                except Exception as e:
                    print(f"  Error: {e}")
    
    return dir_count, file_count

if __name__ == "__main__":
    root_dir = Path(".")
    
    print("Cleaning up Python cache files and directories...")
    dir_count, file_count = cleanup_cache(root_dir)
    
    print(f"\nCleanup complete: removed {dir_count} cache directories and {file_count} cache files.") 