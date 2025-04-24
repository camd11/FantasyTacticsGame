#!/usr/bin/env python
"""
Screenshot Cleanup Utility

This script deletes old screenshots to save disk space.
It:
1. Removes all PNG screenshots (replacing them with JPG)
2. Only keeps the latest screenshots with fixed filenames

Usage:
    python cleanup_screenshots.py [--all-screenshots]

Options:
    --all-screenshots    Remove ALL screenshots (including JPGs)
"""

import os
import glob
import shutil
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("CleanupUtil")

# Define screenshot directories
SCREENSHOT_DIRS = [
    "logs/test_selector/screenshots",
    "logs/visual_tests/screenshots",
    "logs/headless_tests"
]

def main():
    """Main cleanup function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Clean up screenshot files")
    parser.add_argument("--all-screenshots", action="store_true", 
                        help="Remove ALL screenshots (including JPGs)")
    args = parser.parse_args()
    
    total_png_removed = 0
    total_jpg_removed = 0
    total_space_freed = 0
    
    logger.info("Starting screenshot cleanup...")
    
    # Process each screenshot directory
    for dir_path in SCREENSHOT_DIRS:
        dir_path = Path(dir_path)
        
        # Skip if directory doesn't exist
        if not dir_path.exists():
            logger.info(f"Directory not found: {dir_path}")
            continue
            
        logger.info(f"Processing directory: {dir_path}")
        
        # Count and list all files for information
        all_files = list(dir_path.glob("**/*.*"))
        logger.info(f"Found {len(all_files)} total files")
        
        # Delete all PNG screenshots (recursive)
        png_files = list(dir_path.glob("**/*.png"))
        if png_files:
            png_size = sum(f.stat().st_size for f in png_files)
            logger.info(f"Found {len(png_files)} PNG files ({png_size/1024:.1f} KB)")
            
            for png_file in png_files:
                print(f"Removing: {png_file}")
                os.remove(png_file)
            
            total_png_removed += len(png_files)
            total_space_freed += png_size
        else:
            logger.info("No PNG files found in this directory")
        
        # Handle JPG files
        jpg_files = list(dir_path.glob("**/*.jpg"))
        if jpg_files:
            jpg_size = sum(f.stat().st_size for f in jpg_files)
            
            if args.all_screenshots:
                # Delete all JPG files if requested
                logger.info(f"Removing {len(jpg_files)} JPG files ({jpg_size/1024:.1f} KB)")
                for jpg_file in jpg_files:
                    print(f"Removing: {jpg_file}")
                    os.remove(jpg_file)
                total_jpg_removed += len(jpg_files)
                total_space_freed += jpg_size
            else:
                # Just list and keep JPG files
                logger.info(f"Keeping {len(jpg_files)} JPG files ({jpg_size/1024:.1f} KB)")
                for jpg_file in jpg_files:
                    print(f"Keeping: {jpg_file}")
        else:
            logger.info("No JPG files found in this directory")
    
    # Log results
    logger.info(f"Cleanup completed!")
    logger.info(f"Removed {total_png_removed} PNG files")
    if args.all_screenshots:
        logger.info(f"Removed {total_jpg_removed} JPG files")
    logger.info(f"Total space freed: {total_space_freed/1024/1024:.2f} MB")

if __name__ == "__main__":
    main() 