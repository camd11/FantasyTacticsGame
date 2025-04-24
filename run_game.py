#!/usr/bin/env python3
"""
Run script for Fantasy Tactics Game with GUI renderer enabled
"""

import sys
import os

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.main import main

if __name__ == "__main__":
    # Set default Python argument to enable GUI
    sys.argv.append('--gui')
    
    print("Starting Fantasy Tactics Game with GUI renderer...")
    main()
    print("Game session ended.") 