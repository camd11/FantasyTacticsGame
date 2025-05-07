import sys
import os

# Add the project root directory (parent of 'tests') to the Python path.
# This allows tests to correctly import modules from the 'src' directory
# as 'src.module_name'.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))