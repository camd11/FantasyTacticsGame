#!/usr/bin/env python3
"""
Test script to check if we can import the ItemManager class.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

try:
    # Try to import the ItemManager class
    from thracia776.data.item_manager import ItemManager
    print("Successfully imported ItemManager")
except ImportError as e:
    print(f"Error importing ItemManager: {e}")

# Print the contents of the item_manager.py file
try:
    with open('thracia776/data/item_manager.py', 'r') as f:
        print("\nContents of item_manager.py:")
        print(f.read())
except Exception as e:
    print(f"Error reading item_manager.py: {e}")