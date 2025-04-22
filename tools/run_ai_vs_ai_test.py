"""
Script to run the AI vs AI test with the modified files.
"""

import sys
import os
import shutil
import subprocess

# Backup original files
if os.path.exists('src/gameplay_systems/ai_system.py'):
    shutil.copy('src/gameplay_systems/ai_system.py', 'src/gameplay_systems/ai_system.py.bak')

if os.path.exists('test_ai_vs_ai.py'):
    shutil.copy('test_ai_vs_ai.py', 'test_ai_vs_ai.py.bak')

# Replace with modified files
# shutil.copy('src/gameplay_systems/ai_system_fixed.py', 'src/gameplay_systems/ai_system.py') # Commented out to prevent overwrite
# shutil.copy('test_ai_vs_ai_fixed.py', 'test_ai_vs_ai.py') # Commented out to use the manually modified test file

try:
    # Run the test
    print("Running AI vs AI test with modified files...")
    # Ensure the environment is set up
    os.environ['PYTHONPATH'] = os.getcwd()
    # os.environ['LOG_LEVEL'] = 'DEBUG' # Removed DEBUG override
    
    result = subprocess.run(['pytest', 'test_ai_vs_ai.py', '-v', '-s'], # Removed --log-cli-level=DEBUG override
                           capture_output=True, text=True)
    
    print("\nTest Output:")
    print(result.stdout)
    
    if result.stderr:
        print("\nErrors:")
        print(result.stderr)
    
    # Check if ai_behavior.log was created
    if os.path.exists('ai_behavior.log'):
        print("\nai_behavior.log was created!")
        with open('ai_behavior.log', 'r') as f:
            log_content = f.read()
            print("\nFirst 1000 characters of ai_behavior.log:")
            print(log_content[:1000])
    else:
        print("\nai_behavior.log was not created.")
    
    # Check if ai_vs_ai_test.log was created
    if os.path.exists('ai_vs_ai_test.log'):
        print("\nai_vs_ai_test.log was created!")
        with open('ai_vs_ai_test.log', 'r') as f:
            log_content = f.read()
            print("\nFirst 1000 characters of ai_vs_ai_test.log:")
            print(log_content[:1000])
    else:
        print("\nai_vs_ai_test.log was not created.")
    
finally:
    # Restore original files
    if os.path.exists('src/gameplay_systems/ai_system.py.bak'):
        shutil.copy('src/gameplay_systems/ai_system.py.bak', 'src/gameplay_systems/ai_system.py')
        os.remove('src/gameplay_systems/ai_system.py.bak')
    
    if os.path.exists('test_ai_vs_ai.py.bak'):
        shutil.copy('test_ai_vs_ai.py.bak', 'test_ai_vs_ai.py')
        os.remove('test_ai_vs_ai.py.bak')