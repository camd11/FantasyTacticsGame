#!/usr/bin/env python3
"""
Run script for Fantasy Tactics Game with various command line options
Provides a simple menu to select different running configurations
"""

import sys
import os
import subprocess

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_menu():
    """Display the main menu."""
    clear_screen()
    print("=== Fantasy Tactics Game Runner ===")
    print("Select an option to run the game:")
    print("1. Run with GUI (Recommended)")
    print("2. Run with Console (ASCII Display)")
    print("3. Run AI vs AI Simulation with GUI")
    print("4. Run AI vs AI Simulation with ASCII Display")
    print("5. Test Renderer Only")
    print("6. Test Enhanced Renderer with Interaction")
    print("7. Visual Tests with GUI Renderer")
    print("8. Run Custom Command")
    print("9. Exit")
    return input("\nEnter your choice (1-9): ")

def run_game(args):
    """Run the game with the given command line arguments."""
    cmd = [sys.executable, "src/main.py"] + args
    print(f"\nRunning command: {' '.join(cmd)}")
    print("Press Ctrl+C to exit the game...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nGame terminated by user.")
    
    input("\nPress Enter to continue...")

def run_renderer_test():
    """Run the renderer test script."""
    cmd = [sys.executable, "run_renderer_test.py"]
    print(f"\nRunning command: {' '.join(cmd)}")
    print("Press Ctrl+C to exit the test...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nRenderer test terminated by user.")
    
    input("\nPress Enter to continue...")

def run_enhanced_renderer_test():
    """Run the enhanced renderer test script."""
    cmd = [sys.executable, "test_gui_renderer.py"]
    print(f"\nRunning command: {' '.join(cmd)}")
    print("Press Ctrl+C to exit the test...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nEnhanced renderer test terminated by user.")
    
    input("\nPress Enter to continue...")

def run_visual_tests_gui():
    """Run the visual tests with GUI renderer."""
    cmd = [sys.executable, "visual_tests_gui.py"]
    print(f"\nRunning command: {' '.join(cmd)}")
    print("Press Ctrl+C to exit the tests...\n")
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nVisual tests terminated by user.")
    
    input("\nPress Enter to continue...")

def get_custom_command():
    """Get custom command line arguments from user."""
    print("\n=== Custom Command ===")
    print("Available options:")
    print("  --gui             Enable GUI mode with Pygame")
    print("  --ascii-display   Enable ASCII map display in console")
    print("  --ai-vs-ai        Enable AI vs AI mode")
    print("  --chapter N       Load chapter N (e.g., --chapter 2)")
    
    args_input = input("\nEnter command line arguments: ")
    return args_input.split()

def main():
    """Main function."""
    while True:
        choice = display_menu()
        
        if choice == '1':
            run_game(['--gui'])
        elif choice == '2':
            run_game(['--ascii-display'])
        elif choice == '3':
            run_game(['--gui', '--ai-vs-ai'])
        elif choice == '4':
            run_game(['--ascii-display', '--ai-vs-ai'])
        elif choice == '5':
            run_renderer_test()
        elif choice == '6':
            run_enhanced_renderer_test()
        elif choice == '7':
            run_visual_tests_gui()
        elif choice == '8':
            custom_args = get_custom_command()
            run_game(custom_args)
        elif choice == '9':
            print("\nExiting... Goodbye!")
            break
        else:
            input("\nInvalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main() 