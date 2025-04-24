#!/usr/bin/env python3
"""
Run Visual Tests

This script provides an easy way to run the various visual tests and demonstrations.
"""

import os
import sys
import argparse
import subprocess

# Set up Python path to include the project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

def run_demo(demo_name):
    """Run a specific visual demonstration.
    
    Args:
        demo_name: Name of the demonstration to run
    """
    # Create a mapping of demo names to their scripts
    demos = {
        "simple_attack": "test_simple_attack.py",
        "attack_mechanics": "test_attack_mechanics.py",
        "field_of_view": "test_field_of_view.py",
        "improved_visuals": "test_improved_visuals.py"
    }
    
    # Check if the demo exists
    if demo_name not in demos:
        print(f"Error: Demo '{demo_name}' not found")
        print("Available demos:")
        for name in demos.keys():
            print(f"  - {name}")
        return
    
    # Get the script path
    script_path = os.path.join(PROJECT_ROOT, demos[demo_name])
    
    # Run the script
    print(f"Running demo: {demo_name}")
    subprocess.run([sys.executable, script_path])

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run visual tests and demonstrations")
    parser.add_argument("demo", nargs="?", help="Name of the demo to run")
    parser.add_argument("--list", action="store_true", help="List available demos")
    
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    if args.list:
        print("Available demos:")
        print("  - simple_attack: Simple combat demonstration with particle effects")
        print("  - attack_mechanics: Full combat mechanics demonstration")
        print("  - field_of_view: Field of view visualization demonstration")
        print("  - improved_visuals: Improved visuals demonstration")
        return
    
    if args.demo:
        run_demo(args.demo)
    else:
        print("No demo specified. Use --list to see available demos")

if __name__ == "__main__":
    main() 