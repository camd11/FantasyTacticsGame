#!/usr/bin/env python
"""
Visual Test Selector

This script provides a way to run individual visual tests for debugging.
It lists all available tests and allows you to select one to run in 
either visible or headless mode.

Usage:
    python test_selector.py [--mode {visible,headless}] [--test TEST_NAME] [--duration SECONDS] [--no-screenshots]

Options:
    --mode {visible,headless}  Test mode (default: visible)
    --test TEST_NAME           Specific test to run (e.g., "movement")
    --duration SECONDS         Test duration in seconds (default: 8)
    --no-screenshots           Disable screenshot capture
"""

import os
import sys
import time
import argparse
import logging
import pygame
from pathlib import Path
from datetime import datetime

# Set up Python path to include the project root
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import required modules
from automated_visual_tests import (
    MECHANIC_CATEGORIES,
    TestGameRenderer,
    AnimationType,
    logger
)

# Configure logging
LOG_DIR = os.path.join(PROJECT_ROOT, "logs", "test_selector")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"test_selector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class TestSelector:
    """Tool to run individual visual tests for debugging."""
    
    def __init__(self, mode="visible", test_duration=8, capture_screenshots=True):
        """Initialize the test selector.
        
        Args:
            mode: Test mode - 'visible' or 'headless'
            test_duration: How long to run each test in seconds
            capture_screenshots: Whether to capture screenshots
        """
        self.mode = mode
        self.test_duration = test_duration
        self.capture_screenshots = capture_screenshots
        self.window_size = (1024, 768)
        self.screen = None
        self.clock = pygame.time.Clock()
        
        # Available tests (flattened for easier selection)
        self.available_tests = self.get_available_tests()
        
        # Initialize pygame
        pygame.init()
        
        if mode == "visible":
            self.screen = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption("Fantasy Tactics - Test Selector")
        else:  # headless mode
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            self.screen = pygame.Surface(self.window_size)
            pygame.display.init()
            pygame.display.set_mode((1, 1), pygame.HIDDEN)
        
        logger.info(f"Initialized TestSelector with mode={mode}, test_duration={test_duration}s")
        logger.info(f"Capture screenshots: {self.capture_screenshots}")
    
    def get_available_tests(self):
        """Get a flattened list of all available tests."""
        tests = []
        for category in MECHANIC_CATEGORIES:
            for test_name in category["tests"]:
                tests.append({
                    "name": test_name,
                    "category": category["name"]
                })
        return tests
    
    def list_available_tests(self):
        """Print a list of all available tests."""
        print("\nAvailable tests:")
        print("-" * 50)
        
        current_category = None
        for i, test in enumerate(self.available_tests):
            if current_category != test["category"]:
                current_category = test["category"]
                print(f"\n{current_category}:")
            
            print(f"  {i+1}. {test['name']}")
        
        print("\n" + "-" * 50)
    
    def run_test(self, test_name):
        """Run a specific test.
        
        Args:
            test_name: Name of the test to run
        """
        # Find matching test
        matching_tests = [t for t in self.available_tests if t["name"] == test_name]
        
        if not matching_tests:
            logger.error(f"Test '{test_name}' not found")
            print(f"Error: Test '{test_name}' not found")
            self.list_available_tests()
            return
        
        test = matching_tests[0]
        category_name = test["category"]
        
        logger.info(f"Running test: {category_name} - {test_name}")
        print(f"Running test: {category_name} - {test_name}")
        
        try:
            # Import only when needed to avoid circular imports
            from automated_visual_tests import AutomatedTestRunner
            
            # Create test runner for this test
            test_runner = AutomatedTestRunner(
                window_size=self.window_size,
                test_duration=self.test_duration
            )
            
            # We need to manually reset certain attributes that might be set
            # by previous test runs
            test_runner.screen = self.screen
            test_runner.current_renderer = None
            
            # Create game state for this test
            gsm = test_runner.create_test_game_state(test_name)
            
            # Create renderer
            test_runner.current_renderer = TestGameRenderer(
                gsm,
                window_size=self.window_size,
                title=f"Visual Test: {test_name}",
                screen=self.screen
            )
            
            # Center camera on player if available
            if "player1" in gsm.units:
                unit = gsm.units["player1"]
                test_runner.current_renderer.center_camera_on_position(unit.position[0], unit.position[1])
            
            # Schedule animations based on test type
            test_runner.schedule_test_animations(test_name, gsm)
            
            # Create a header text for the test
            status_font = pygame.font.SysFont("Arial", 20)
            status_text = f"{category_name} - {test_name}"
            text_surface = status_font.render(status_text, True, (255, 255, 255), (0, 0, 0))
            
            # Run test for the specified duration
            start_time = time.time()
            frame_count = 0
            
            # Setup for screenshot (if enabled)
            screenshot_path = None
            screenshot_taken = False
            
            if self.capture_screenshots:
                # Save screenshot path (with fixed filename, no timestamp)
                screenshot_dir = os.path.join(LOG_DIR, "screenshots")
                os.makedirs(screenshot_dir, exist_ok=True)
                screenshot_path = os.path.join(
                    screenshot_dir, 
                    f"{category_name.replace(' ', '_')}_{test_name}.jpg"
                )
            
            logger.info(f"Test started: {test_name}")
            
            while time.time() - start_time < self.test_duration:
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt("User closed the window")
                
                # Update renderer
                test_runner.current_renderer.update()
                
                # Clear screen (only needed in headless mode)
                if self.mode == "headless":
                    self.screen.fill((0, 0, 0))
                
                # Render
                test_runner.current_renderer.render()
                
                # Add status text at the top
                self.screen.blit(text_surface, (10, 10))
                
                # Take a screenshot after a couple of seconds (when animations have started)
                if self.capture_screenshots and not screenshot_taken and time.time() - start_time > 0.5:  # Reduced delay for testing
                    try:
                        # Create screenshot directory if it doesn't exist
                        screenshot_dir = os.path.dirname(screenshot_path)
                        if not os.path.exists(screenshot_dir):
                            os.makedirs(screenshot_dir, exist_ok=True)
                            logger.info(f"Created screenshot directory: {screenshot_dir}")
                        
                        # Debug info
                        print(f"Screen surface info: {self.screen}")
                        print(f"Screenshot path: {screenshot_path}")
                        
                        # Save as JPG for better compression
                        logger.info(f"Attempting to save screenshot to {screenshot_path}")
                        pygame.image.save(self.screen, screenshot_path)
                        logger.info(f"Successfully saved screenshot to {screenshot_path}")
                        print(f"Saved screenshot to {screenshot_path}")
                        screenshot_taken = True
                    except Exception as e:
                        logger.error(f"Error saving screenshot: {str(e)}")
                        print(f"Error saving screenshot: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        screenshot_taken = True  # Avoid retrying
                
                # Update display and control framerate
                if self.mode == "visible":
                    pygame.display.flip()
                    self.clock.tick(60)
                else:
                    # Small delay to not overload CPU in headless mode
                    time.sleep(0.01)
                
                frame_count += 1
            
            # Log performance info
            fps = frame_count / self.test_duration
            logger.info(f"Test {test_name} ran at {fps:.1f} FPS")
            print(f"Test completed at {fps:.1f} FPS")
            
            # Clean up renderer
            test_runner.current_renderer.close()
            test_runner.current_renderer = None
            
        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
            print("Test interrupted by user")
        except Exception as e:
            logger.error(f"Error running test {test_name}: {str(e)}", exc_info=True)
            print(f"Error running test {test_name}: {str(e)}")
    
    def cleanup(self):
        """Clean up resources."""
        pygame.quit()
        logger.info("Test selector closed")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run individual visual tests")
    parser.add_argument("--mode", type=str, choices=["visible", "headless"], default="visible",
                        help="Test mode: visible or headless (default: visible)")
    parser.add_argument("--test", type=str, default=None,
                        help="Specific test to run (e.g., 'movement')")
    parser.add_argument("--duration", type=int, default=8,
                        help="Test duration in seconds (default: 8)")
    parser.add_argument("--no-screenshots", action='store_true',
                        help="Disable screenshot capture")
    return parser.parse_args()

def main():
    """Main entry point for test selector."""
    args = parse_args()
    
    logger.info("Starting test selector")
    
    test_selector = TestSelector(
        mode=args.mode,
        test_duration=args.duration,
        capture_screenshots=not args.no_screenshots
    )
    
    try:
        if args.test:
            # Run specific test
            test_selector.run_test(args.test)
        else:
            # Show available tests
            test_selector.list_available_tests()
            
            # Simple command line interface
            print("\nEnter test name or number to run (q to quit):")
            while True:
                choice = input("> ").strip()
                
                if choice.lower() in ['q', 'quit', 'exit']:
                    break
                
                # Handle numeric selection
                if choice.isdigit():
                    num = int(choice)
                    if 1 <= num <= len(test_selector.available_tests):
                        test = test_selector.available_tests[num-1]
                        test_selector.run_test(test["name"])
                    else:
                        print(f"Invalid selection: {choice}")
                        test_selector.list_available_tests()
                else:
                    # Assume it's a test name
                    test_selector.run_test(choice)
    
    finally:
        test_selector.cleanup()

if __name__ == "__main__":
    main() 