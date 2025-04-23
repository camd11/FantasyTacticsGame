"""
Unit Mechanics Test Runner

This script runs all unit-related mechanic tests including:
- Death mechanics
- Retreat mechanics
- Rescue mechanics
- Promotion mechanics
"""

import os
import sys
import importlib
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.abspath('.'))

def run_test_module(module_name, log_file_prefix=None):
    """Run a test module by importing and calling its run_test function."""
    try:
        # Import the module
        module = importlib.import_module(f"tests.mechanic_tests.unit_mechanics.{module_name}")
        
        # Create log path if needed
        if log_file_prefix:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("logs/mechanic_tests/units", exist_ok=True)
            log_path = f"logs/mechanic_tests/units/{log_file_prefix}_{timestamp}.txt"
        else:
            log_path = None
        
        # Run the test
        print(f"Running {module_name} test...")
        module.run_test(log_path)
        print(f"✅ {module_name} test completed")
        return True
    except ImportError as e:
        print(f"❌ Error importing {module_name}: {e}")
    except AttributeError as e:
        print(f"❌ Error: {module_name} module does not have a run_test function: {e}")
    except Exception as e:
        print(f"❌ Error running {module_name} test: {e}")
    
    return False

def run_retreat_mechanics_test():
    """Run retreat mechanics test (if module exists) or create a mock test."""
    # Check if we have a dedicated retreat module
    try:
        return run_test_module("retreat", "retreat_mechanics")
    except ImportError:
        print("No dedicated retreat module found, running mock test...")
        
        # Create a basic mock test using death.py as template
        # In a real implementation, we'd create a proper retreat test
        print("Mock retreat test functionality not implemented yet")
        return False

def run_all_tests():
    """Run all unit mechanics tests."""
    success_count = 0
    total_tests = 4
    
    # Run death mechanics test
    if run_test_module("death", "death_mechanics"):
        success_count += 1
    
    # Run retreat mechanics test
    if run_retreat_mechanics_test():
        success_count += 1
    
    # Run rescue mechanics test
    if run_test_module("rescue", "rescue_mechanics"):
        success_count += 1
    
    # Run promotion mechanics test
    if run_test_module("promotion", "promotion_mechanics"):
        success_count += 1
    
    # Print summary
    print(f"\nUnit mechanics tests completed: {success_count}/{total_tests} successful")
    
    return success_count == total_tests

if __name__ == "__main__":
    run_all_tests() 