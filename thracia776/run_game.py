#!/usr/bin/env python3
"""
Game runner for the Thracia 776 recreation project.
This script runs the main game loop.
"""

import os
import sys

def run_game():
    """
    Run the main game loop.
    """
    # Use relative import for the main module
    from . import main
    return main()

if __name__ == "__main__":
    sys.exit(run_game())