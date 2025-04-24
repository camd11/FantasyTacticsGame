#!/usr/bin/env python
"""
Visual Test Runner

This script combines the functionality of both automated_visual_tests.py and headless_visual_tests.py
to provide a unified test runner with multiple modes:

1. Visible Mode: Shows visual tests in a window (like automated_visual_tests.py)
2. Headless Mode: Runs tests without a visible display (like headless_visual_tests.py)

Usage:
    python visual_test_runner.py [--mode {visible,headless}] [--duration SECONDS] [--output-dir DIR] [--no-screenshots]

Options:
    --mode {visible,headless}  Test mode: visible or headless (default: visible)
    --duration SECONDS         Duration to run each test in seconds (default: 5)
    --output-dir DIR           Directory to save test results (default: logs/visual_tests)
    --no-screenshots           Disable screenshot capture
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
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import required modules
from automated_visual_tests import (
    MECHANIC_CATEGORIES,
    AutomatedTestRunner,
    TestGameRenderer,
    AnimationType,
    logger
)

# Configure logging
def setup_logging(mode, output_dir):
    """Set up logging based on the selected mode."""
    log_dir = Path(output_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"{mode}_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    logger.info(f"Starting {mode} visual tests")
    logger.info(f"Log file: {log_file}")

class UnifiedTestRunner:
    """
    Unified test runner that supports both visible and headless modes.
    """
    
    def __init__(self, mode="visible", test_duration=5, output_dir=None, capture_screenshots=True):
        """
        Initialize the test runner.
        
        Args:
            mode: Test mode - 'visible' or 'headless'
            test_duration: Seconds to run each test
            output_dir: Directory to save test results
            capture_screenshots: Whether to capture screenshots
        """
        self.mode = mode
        self.test_duration = test_duration
        self.output_dir = Path(output_dir or f"logs/visual_tests/{mode}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capture_screenshots = capture_screenshots
        
        self.window_size = (1024, 768)
        self.surface = None
        self.screen = None
        self.clock = pygame.time.Clock()
        
        # Track timing for test runs
        self.current_test_start_time = 0
        self.completed_tests = 0
        self.total_tests = sum(len(category["tests"]) for category in MECHANIC_CATEGORIES)
        
        # Initialize pygame
        pygame.init()
        
        if mode == "visible":
            self.screen = pygame.display.set_mode(self.window_size)
            pygame.display.set_caption("Fantasy Tactics - Visual Tests")
            self.surface = self.screen
        else:  # headless mode
            pygame.display.set_mode((1, 1), pygame.HIDDEN)
            self.surface = pygame.Surface(self.window_size)
        
        logger.info(f"Initialized {mode} test runner with test_duration={test_duration}s")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Capture screenshots: {self.capture_screenshots}")
        logger.info(f"Total tests to run: {self.total_tests}")
    
    def run_all_tests(self):
        """Run all test categories sequentially."""
        overall_start_time = time.time()
        
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
                    
                    # Process events to keep window responsive
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise KeyboardInterrupt("User closed the window")
        except KeyboardInterrupt:
            logger.info("Test run interrupted by user")
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
        Run a single test and save its screenshots.
        
        Args:
            test_name: Name of the test to run
            category_name: Name of the category this test belongs to
            category_dir: Directory to save test results (if screenshots enabled)
        """
        progress = f"({self.completed_tests + 1}/{self.total_tests})"
        logger.info(f"Running test {progress}: {category_name} - {test_name}")
        
        try:
            # Create test runner specifically for this test
            test_runner = AutomatedTestRunner(window_size=self.window_size, test_duration=self.test_duration)
            
            # Create game state for this test
            gsm = test_runner.create_test_game_state(test_name)
            
            # Create renderer
            self.create_renderer(test_runner, gsm)
            
            # Schedule test animations
            test_runner.schedule_test_animations(test_name, gsm)
            
            # Create status text if in visible mode
            status_text = None
            if self.mode == "visible":
                status_font = pygame.font.SysFont("Arial", 20)
                status_text = status_font.render(
                    f"{category_name} - {test_name} {progress}", 
                    True, (255, 255, 255), (0, 0, 0)
                )
            
            # Set timer
            self.current_test_start_time = time.time()
            test_end_time = self.current_test_start_time + self.test_duration
            
            # Screenshots tracking (only if enabled)
            screenshot_stages = {0.25: False, 0.5: False, 0.75: False, 1.0: False} if self.capture_screenshots else {}
            
            # Run the test for the specified duration
            frame_count = 0
            
            while time.time() < test_end_time:
                # Process events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt("User closed the window")
                
                # Update the test
                test_runner.current_renderer.update()
                
                # Render the test
                if self.mode == "headless":
                    self.surface.fill((0, 0, 0))
                
                test_runner.current_renderer.draw(self.surface)
                
                # Add status text in visible mode
                if self.mode == "visible" and status_text:
                    self.surface.blit(status_text, (10, 10))
                
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
                
                # Update display in visible mode
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
            
            # Close the renderer
            test_runner.current_renderer.close()
            
            # Log completion
            logger.info(f"Test completed: {category_name} - {test_name}")
            self.completed_tests += 1
        
        except Exception as e:
            logger.error(f"Error running test {category_name} - {test_name}: {e}", exc_info=True)
    
    def create_renderer(self, test_runner, gsm):
        """Create a renderer for the test."""
        # Create renderer with our surface
        test_runner.current_renderer = TestGameRenderer(
            gsm,
            window_size=self.window_size,
            title=f"Visual Test: {self.mode}",
            screen=self.surface
        )
        
        # Center camera on player if available
        if "player1" in gsm.units:
            unit = gsm.units["player1"]
            test_runner.current_renderer.center_camera_on_position(unit.position[0], unit.position[1])
    
    def save_screenshot(self, test_name, directory, label):
        """
        Save a screenshot of the current test state.
        
        Args:
            test_name: Name of the current test
            directory: Directory to save the screenshot
            label: Label for this screenshot (e.g., "25", "50", "75", "final")
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{test_name}_{label}_{timestamp}.png"
        filepath = directory / filename
        
        pygame.image.save(self.surface, str(filepath))
        logger.info(f"Saved screenshot: {filepath}")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run visual tests")
    parser.add_argument("--mode", type=str, choices=["visible", "headless"], default="visible",
                        help="Test mode: visible or headless (default: visible)")
    parser.add_argument("--duration", type=int, default=5,
                        help="Duration to run each test in seconds (default: 5)")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Directory to save test results")
    parser.add_argument("--no-screenshots", action='store_true',
                        help="Disable screenshot capture")
    return parser.parse_args()

def main():
    """Main entry point for visual tests."""
    args = parse_args()
    
    # Set up output directory
    output_dir = args.output_dir or f"logs/visual_tests/{args.mode}"
    
    # Set up logging
    setup_logging(args.mode, output_dir)
    
    # Create and run the test runner
    test_runner = UnifiedTestRunner(
        mode=args.mode,
        test_duration=args.duration,
        output_dir=output_dir,
        capture_screenshots=not args.no_screenshots
    )
    test_runner.run_all_tests()
    
    logger.info(f"{args.mode.capitalize()} visual tests completed")

if __name__ == "__main__":
    main() 