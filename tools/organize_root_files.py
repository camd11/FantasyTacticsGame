#!/usr/bin/env python3
"""
Script to organize files from the root directory into appropriate subdirectories.
This helps clean up the project structure by moving test files, utility scripts, and other
misplaced files into their proper locations.
"""

import os
import shutil
import sys
from pathlib import Path

# Ensure we're running from the project root
ROOT_DIR = Path(os.getcwd())
if not (ROOT_DIR / "src").exists() or not (ROOT_DIR / "tests").exists():
    print("This script must be run from the project root directory.")
    sys.exit(1)

# Create necessary directories if they don't exist
test_dirs = {
    'visual': ROOT_DIR / 'tests' / 'visual_tests',
    'mechanic': ROOT_DIR / 'tests' / 'mechanic_tests',
    'integration': ROOT_DIR / 'tests' / 'integration_tests',
    'renderer': ROOT_DIR / 'tests' / 'renderer_tests',
    'sound': ROOT_DIR / 'tests' / 'sound_tests',
    'selector': ROOT_DIR / 'tests' / 'ui_tests',
}

for dir_path in test_dirs.values():
    os.makedirs(dir_path, exist_ok=True)

# Ensure tools directory exists
tools_dir = ROOT_DIR / 'tools'
os.makedirs(tools_dir, exist_ok=True)

# Ensure logs directory exists
logs_dir = ROOT_DIR / 'logs'
os.makedirs(logs_dir, exist_ok=True)

# Categorize files to move
file_categories = {
    # Test files
    'visual_tests': [
        'test_visual_logger.py',
        'test_visual_logger_advanced.py',
        'test_improved_visuals.py',
        'test_enhanced_animations.py',
        'visual_test_runner.py',
        'visual_tests_gui.py',
        'run_visual_tests.py',
        'verify_visual_tests.py',
        'automated_visual_tests.py',
        'headless_visual_tests.py',
        'run_all_visual_tests.py',
    ],
    'mechanic_tests': [
        'test_attack_mechanics.py',
        'test_rescue_mechanics.py',
        'test_dismounting_mechanics.py',
        'test_simple_attack.py',
        'test_field_of_view.py',
    ],
    'renderer_tests': [
        'test_gui_renderer.py',
        'run_renderer_test.py',
    ],
    'sound_tests': [
        'test_sound_effects.py',
    ],
    'ui_tests': [
        'test_selector.py',
    ],
    # Utility/tools files
    'tools': [
        'cleanup_screenshots.py',
        'create_panel_texture.py',
        'create_sound_effects.py',
        'run_options.py',
    ],
    # Log files
    'logs': [
        'ai_behavior.log',
        'ai_vs_ai_simplified.log',
    ],
    # Files to keep in root
    'keep_in_root': [
        'run_game.py',
        'launch.sh',
        'Launch.bat',
        'setup_venv.bat',
        'setup_venv.sh',
        'requirements.txt',
        'pytest.ini',
        'run_mechanic_tests.sh',
        '.gitignore',
        'README.md',
    ]
}

# Directories to move files into
move_destinations = {
    'visual_tests': test_dirs['visual'],
    'mechanic_tests': test_dirs['mechanic'],
    'renderer_tests': test_dirs['renderer'],
    'sound_tests': test_dirs['sound'],
    'ui_tests': test_dirs['selector'],
    'tools': tools_dir,
    'logs': logs_dir,
}

def move_files():
    """Move files to their appropriate directories."""
    
    for category, files in file_categories.items():
        if category == 'keep_in_root':
            continue
            
        dest_dir = move_destinations[category]
        
        for filename in files:
            source_path = ROOT_DIR / filename
            dest_path = dest_dir / filename
            
            if source_path.exists():
                # Check if the destination file already exists
                if dest_path.exists():
                    print(f"Warning: {dest_path} already exists, skipping {source_path}")
                else:
                    try:
                        shutil.move(str(source_path), str(dest_path))
                        print(f"Moved {filename} to {dest_dir}")
                    except Exception as e:
                        print(f"Error moving {filename}: {str(e)}")
            else:
                print(f"File {filename} not found in root directory")

if __name__ == "__main__":
    print("Starting file organization...")
    move_files()
    print("File organization complete.") 