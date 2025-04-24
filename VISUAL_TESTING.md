# Visual Testing System

This document provides an overview of the visual testing system for the Fantasy Tactics Game.

## Overview

The visual testing system allows automated testing of the game's visual elements and animations. It provides three main ways to run tests:

1. **Test Selector** - Interactive tool to run individual tests in visible mode
2. **Automated Visual Tests** - Runs all tests in sequence with a visible window
3. **Headless Visual Tests** - Runs all tests without a visible window (for CI/CD)

All testing methods capture screenshots automatically, using a fixed-filename approach to avoid hard drive bloat.

## Test Categories

The visual tests are organized into categories:

1. **Core Mechanics**
   - movement
   - combat
   - terrain
   - inventory

2. **Unit Mechanics**
   - recruitment
   - death
   - rescue
   - status_effects
   - promotion

3. **Special Mechanics**
   - weather
   - events
   - objectives
   - reinforcements

4. **Integrated Scenarios**
   - simple_battle
   - tactical_challenge
   - strategic_battle

## Running Tests

### Test Selector (Interactive Mode)

The Test Selector allows you to run individual tests in visible mode:

```bash
# Run a specific test
python test_selector.py --mode visible --test movement --duration 5

# Interactive mode (select from a menu)
python test_selector.py --mode visible --duration 5
```

Options:
- `--mode {visible,headless}` - Test mode (default: visible)
- `--test TEST_NAME` - Specific test to run (e.g., "movement")
- `--duration SECONDS` - Test duration in seconds (default: 8)
- `--no-screenshots` - Disable screenshot capture

### Headless Visual Tests (Automated Mode)

Headless tests run all tests in sequence without a visible window:

```bash
# Run all tests with default settings
python headless_visual_tests.py

# Run all tests with custom duration
python headless_visual_tests.py --duration 3
```

Options:
- `--duration SECONDS` - Duration to run each test (default: 5)
- `--output-dir DIR` - Directory to save test results (default: logs/headless_tests)
- `--no-screenshots` - Disable screenshot capture

### Running the Renderer Test

For basic renderer testing:

```bash
python run_renderer_test.py
```

## Screenshots Management

The system is configured to save screenshots as JPG files with fixed filenames, ensuring only the latest screenshots are kept.

### Screenshot Locations

Screenshots are saved to the following locations:

1. Test Selector: `logs/test_selector/screenshots/`
2. Automated Visual Tests: `logs/visual_tests/screenshots/`
3. Headless Visual Tests: `logs/headless_tests/{Category_Name}/`

### Screenshot Cleanup Utility

A cleanup utility is provided to manage screenshots and prevent disk space issues:

```bash
# Remove all PNG files (keep JPGs)
python cleanup_screenshots.py

# Remove ALL screenshots (PNGs and JPGs)
python cleanup_screenshots.py --all-screenshots
```

This utility helps keep your disk space clean by:
1. Removing old PNG screenshots (now replaced with JPG format)
2. Optionally removing all screenshots when needed

## Implementation Details

### File Structure

- `test_selector.py` - Interactive UI for running individual tests
- `automated_visual_tests.py` - Framework for running visual tests
- `headless_visual_tests.py` - Headless version for CI/CD
- `run_renderer_test.py` - Simple script for testing the basic renderer
- `cleanup_screenshots.py` - Utility for managing screenshot files

### Adding New Tests

To add a new test category or test:

1. Update the `MECHANIC_CATEGORIES` list in `automated_visual_tests.py`
2. Implement the corresponding test animations in `schedule_test_animations()`

### Screenshot Format

All screenshots are now saved as JPG files with fixed filenames for each test, ensuring:
- Only the latest screenshot for each test persists
- Disk space is conserved
- Screenshots can be easily referenced

## Troubleshooting

### No Screenshots Being Saved

- Ensure the screenshot directories exist
- Check for permission issues in the logs directory
- Make sure `--no-screenshots` flag is not set

### Headless Tests Failing

- Ensure pygame is properly installed with SDL support
- Check for X server issues on Linux systems
- Review logs for specific errors

## Summary

The visual testing system provides a comprehensive way to test the game's visual elements and animations. By using the test selector for interactive testing and the headless tests for automation, you can ensure visual consistency across development changes. 