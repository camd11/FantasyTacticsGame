#!/usr/bin/env python3
"""
Run the inventory mechanics test.
This script runs the inventory mechanics test and outputs the results to a log file.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

# Import the test module
from tests.mechanic_tests.inventory.test_inventory_mechanics import run_test

if __name__ == "__main__":
    # Create a timestamp-based log path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs/mechanic_tests/inventory"
    os.makedirs(log_dir, exist_ok=True)
    log_path = f"{log_dir}/inventory_mechanics_{timestamp}.txt"
    
    # Run the test
    print(f"Running inventory mechanics test...")
    success = run_test(log_path)
    
    if success:
        print(f"Test completed successfully!")
        print(f"Log file: {log_path}")
        print(f"HTML log: {log_path.replace('.txt', '.html')}")
        sys.exit(0)
    else:
        print(f"Test failed!")
        sys.exit(1) 