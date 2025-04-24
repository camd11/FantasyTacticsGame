#!/usr/bin/env python
"""
Headless Visual Tests Runner

This script runs all visual tests without requiring user interaction.
It automatically:
- Iterates through all test categories and tests
- Captures screenshots of test results (optional)
- Logs performance metrics and errors
- Terminates when complete

Usage:
    python headless_visual_tests.py [--duration SECONDS] [--output-dir DIR] [--no-screenshots]

Options:
    --duration SECONDS    Duration to run each test (default: 5)
    --output-dir DIR      Directory to save test results (default: logs/headless_tests)
    --no-screenshots      Disable screenshot capture
"""

import os
import sys
import time
import argparse
import logging
import pygame
from datetime import datetime
from pathlib import Path

# Set up Python path to include the project root
sys.path.insert(0, str(Path(__file__).parent))

# Import required modules
from automated_visual_tests import (
    MECHANIC_CATEGORIES, 
    AutomatedTestRunner,
    TestGameRenderer,
    AnimationType,
    logger
)

# Configure logging
log_dir = Path("logs/headless_tests")
log_dir.mkdir(parents=True, exist_ok=True)

file_handler = logging.FileHandler(log_dir / f"headless_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class HeadlessTestRunner:
    """
    Runs all visual tests automatically without user interaction.
    Takes screenshots of each test and logs results.
    """
    
    def __init__(self, test_duration=5, output_dir=None, capture_screenshots=True):
        """
        Initialize the headless test runner.
        
        Args:
            test_duration: Seconds to run each test
            output_dir: Directory to save test results
            capture_screenshots: Whether to capture screenshots
        """
        self.test_duration = test_duration
        self.output_dir = Path(output_dir) if output_dir else log_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capture_screenshots = capture_screenshots
        
        # Initialize pygame in headless mode
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.init()
        pygame.display.set_mode((1, 1), pygame.HIDDEN)
        
        # Create a proper surface for rendering
        self.surface = pygame.Surface((1024, 768))
        
        # Track timing for test runs
        self.current_test_start_time = 0
        self.completed_tests = 0
        self.total_tests = sum(len(category["tests"]) for category in MECHANIC_CATEGORIES)
        
        logger.info(f"Initialized HeadlessTestRunner with test_duration={test_duration}s")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Capture screenshots: {self.capture_screenshots}")
        logger.info(f"Total tests to run: {self.total_tests}")
    
    def run_all_tests(self):
        """Run all test categories sequentially."""
        overall_start_time = time.time()
        
        logger.info("Starting headless visual tests")
        
        try:
            for category in MECHANIC_CATEGORIES:
                category_name = category["name"]
                logger.info(f"Running category: {category_name}")
                
                # Create category directory if capturing screenshots
                category_dir = None
                if self.capture_screenshots:
                    category_dir = self.output_dir / category_name.replace(" ", "_")
                    category_dir.mkdir(exist_ok=True)
                
                for test_name in category["tests"]:
                    self.run_test(test_name, category_name, category_dir)
        except Exception as e:
            logger.error(f"Error running tests: {e}", exc_info=True)
        
        # Calculate total time
        total_time = time.time() - overall_start_time
        
        logger.info(f"All tests completed in {total_time:.2f} seconds")
        logger.info(f"Completed {self.completed_tests}/{self.total_tests} tests")
        
        # Clean up pygame
        pygame.quit()
    
    def run_test(self, test_name, category_name, category_dir=None):
        """
        Run a single test and save its screenshot.
        
        Args:
            test_name: Name of the test to run
            category_name: Name of the category this test belongs to
            category_dir: Directory to save test results (if screenshots enabled)
        """
        logger.info(f"Running test: {category_name} - {test_name}")
        
        try:
            # Create test runner specifically for this test
            test_runner = AutomatedTestRunner(window_size=(1024, 768), test_duration=self.test_duration)
            
            # Create game state for this test
            gsm = test_runner.create_test_game_state(test_name)
            
            # Create renderer
            test_runner.current_renderer = TestGameRenderer(
                gsm,
                window_size=(1024, 768),
                title=f"Headless Test: {test_name}",
                screen=self.surface
            )
            
            # Center camera on player if available
            if "player1" in gsm.units:
                unit = gsm.units["player1"]
                test_runner.current_renderer.center_camera_on_position(unit.position[0], unit.position[1])
            
            # Schedule test animations
            test_runner.schedule_test_animations(test_name, gsm)
            
            # Set timer
            self.current_test_start_time = time.time()
            test_end_time = self.current_test_start_time + self.test_duration
            
            # Screenshots tracking (only if enabled)
            screenshot_stages = {1.0: False} if self.capture_screenshots else {}
            
            # Run the test for the specified duration
            while time.time() < test_end_time:
                # Process events to prevent pygame from hanging
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                
                # Update the test
                test_runner.current_renderer.update()
                
                # Render the test
                self.surface.fill((0, 0, 0))
                test_runner.current_renderer.render()
                
                # Calculate progress
                progress = (time.time() - self.current_test_start_time) / self.test_duration
                
                # Take screenshots at specific progress points (if enabled)
                if self.capture_screenshots and category_dir:
                    for stage, taken in list(screenshot_stages.items()):
                        if not taken and progress >= stage:
                            if stage == 1.0:
                                label = "final"
                            else:
                                label = f"{int(stage * 100)}"
                            
                            self.save_screenshot(test_name, category_dir, label)
                            screenshot_stages[stage] = True
                
                # Small delay to not overload CPU
                time.sleep(0.01)
            
            # Close the renderer
            test_runner.current_renderer.close()
            
            # Log completion
            logger.info(f"Test completed: {category_name} - {test_name}")
            self.completed_tests += 1
        
        except Exception as e:
            logger.error(f"Error running test {category_name} - {test_name}: {e}", exc_info=True)
    
    def save_screenshot(self, test_name, directory, label):
        """
        Save a screenshot of the current test state.
        
        Args:
            test_name: Name of the current test
            directory: Directory to save the screenshot
            label: Label for this screenshot (e.g., "25", "50", "75", "final")
        """
        # Use a fixed filename without timestamp to ensure only latest persists
        filename = f"{test_name}_{label}.jpg"
        filepath = directory / filename
        
        # Save as JPG (no quality parameter as it's not supported)
        pygame.image.save(self.surface, str(filepath))
        logger.info(f"Saved screenshot: {filepath}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run headless visual tests")
    parser.add_argument("--duration", type=int, default=5,
                        help="Duration to run each test in seconds (default: 5)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save test results (default: logs/headless_tests)")
    parser.add_argument("--no-screenshots", action='store_true',
                        help="Disable screenshot capture")
    return parser.parse_args()

def main():
    """Main entry point for headless visual tests."""
    args = parse_args()
    
    logger.info("Starting headless visual tests")
    
    # Create and run the headless test runner
    test_runner = HeadlessTestRunner(
        test_duration=args.duration,
        output_dir=args.output_dir,
        capture_screenshots=not args.no_screenshots
    )
    test_runner.run_all_tests()
    
    logger.info("Headless visual tests completed")

if __name__ == "__main__":
    main() 