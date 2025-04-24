#!/usr/bin/env python3
"""
Run script for testing the pygame renderer
"""

import sys
import os

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.ui.pygame_renderer import main

if __name__ == "__main__":
    print("Running Pygame Renderer Test...")
    main()
    print("Renderer test completed.") 