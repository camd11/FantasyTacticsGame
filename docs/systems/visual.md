# Visual System

This document provides comprehensive information about the visual system and testing framework used in the Fantasy Tactics Game.

## Overview

The visual system provides the graphical representation of the game, including rendering the game map, units, animations, and effects. It is a core component of the game's three-component testing vision, providing interactive visual feedback for gameplay mechanics.

## Animation System

The game features a robust animation system built on the following components:

### Base Animation Classes

- **Animation**: Base class for all animations with timing, progression, and completion handling
- **MoveAnimation**: Animates unit movement along a path
- **AttackAnimation**: Shows attack lines between units
- **DamageAnimation**: Displays damage numbers with fade effects
- **StatusEffectAnimation**: Shows status effects being applied/removed
- **HighlightTilesAnimation**: Highlights tiles with pulsing effects

### Enhanced Animation Features

#### Fade Animations

The `FadeAnimation` class provides smooth transitions between scenes:

```python
# Example: Fade in from black
renderer.play_animation(AnimationType.FADE, 
                      fade_in=True,      # True for fade in, False for fade out
                      color=(0, 0, 0),   # RGB color to fade from/to
                      duration=1000)     # Duration in milliseconds
```

#### Particle Effects

The `ParticleEffectAnimation` class creates dynamic particle-based visual effects:

```python
# Example: Create an explosion effect
renderer.play_animation(AnimationType.PARTICLE_EFFECT,
                      position=(5, 5),        # Grid position
                      effect_type="explosion", # Effect type (explosion, sparks, smoke)
                      num_particles=30,        # Number of particles
                      duration=1000)           # Duration in milliseconds
```

Available particle effect types:
- **explosion**: Orange-red particles radiating outward
- **sparks**: Bright yellow particles moving upward
- **smoke**: Gray particles rising slowly

#### Animation Chaining

Animations can be chained together to create complex sequences:

```python
# Chain multiple animations to play sequentially
fade_in = renderer.play_animation(AnimationType.FADE, fade_in=True, duration=1000)

# Chain an explosion after the fade completes
explosion = fade_in.chain(
    renderer.play_animation(AnimationType.PARTICLE_EFFECT, 
                         position=(5, 5), 
                         effect_type="explosion")
)

# Chain movement after the explosion
movement = explosion.chain(
    renderer.play_animation(AnimationType.MOVE, 
                          unit_id="player1", 
                          path=[(1,1), (2,2), (3,3)])
)
```

## Visual Testing System

The visual testing system allows developers to run and validate visual components of the game, especially animations and rendering. It is designed to be flexible, allowing for both manual and automated testing.

### Available Testing Tools

| Tool | Description | Use Case |
|------|-------------|----------|
| `automated_visual_tests.py` | Runs all tests with a visible window | Manual verification of visual elements |
| `headless_visual_tests.py` | Runs all tests without a visible window | CI/CD integration and automated testing |
| `visual_test_runner.py` | Unified tool supporting both visible and headless modes | General-purpose testing |
| `test_selector.py` | Interactive tool for running specific tests | Debugging and focused testing |
| `verify_visual_tests.py` | Simple verification script | Quick check that system is working |

### Test Categories

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

### Running Tests

#### Using the Test Selector (Interactive Mode)

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

#### Automated Visual Tests

For comprehensive testing with a visible window:

```bash
python automated_visual_tests.py
```

Features:
- Runs through all test categories and individual tests sequentially
- Each test runs for a configurable duration (default: 6 seconds)
- Automatically takes screenshots of each test
- Logs all test execution information and any errors

#### Headless Visual Tests (Automated Mode)

Headless tests run all tests in sequence without a visible window:

```bash
# Run all tests with default settings
python headless_visual_tests.py

# Run all tests with custom duration
python headless_visual_tests.py --duration 3
```

Features:
- **Fully Automated**: Runs without any user input or interaction
- **Headless Mode**: Uses a minimal hidden Pygame display
- **Comprehensive Testing**: Iterates through all test categories and tests
- **Multiple Screenshots**: Captures images at 25%, 50%, 75%, and 100% completion for each test
- **Organized Output**: Saves results in a structured directory format

#### Unified Visual Test Runner

The unified runner combines features of both automated and headless test runners:

```bash
# Run tests in visible mode (default)
python visual_test_runner.py

# Run tests in headless mode
python visual_test_runner.py --mode headless

# Run tests with 8 seconds per test
python visual_test_runner.py --duration 8
```

Features:
- **Multiple Modes**: Run tests in either visible or headless mode
- **Code Reuse**: Uses the same core testing logic for both modes
- **Automatic Screenshots**: Takes snapshots at key stages of each test
- **Performance Metrics**: Logs FPS and test duration information

### Screenshots Management

The system is configured to save screenshots as JPG files with fixed filenames, ensuring only the latest screenshots are kept.

#### Screenshot Locations

Screenshots are saved to the following locations:

1. Test Selector: `logs/test_selector/screenshots/`
2. Automated Visual Tests: `logs/visual_tests/screenshots/`
3. Headless Visual Tests: `logs/headless_tests/{Category_Name}/`

#### Screenshot Cleanup Utility

A cleanup utility is provided to manage screenshots and prevent disk space issues:

```bash
# Remove all PNG files (keep JPGs)
python cleanup_screenshots.py

# Remove ALL screenshots (PNGs and JPGs)
python cleanup_screenshots.py --all-screenshots
```

### Adding New Tests

To add a new test category or test:

1. Update the `MECHANIC_CATEGORIES` list in `automated_visual_tests.py`
2. Implement test-specific game state in `create_test_game_state()`
3. Add test-specific animations in `schedule_test_animations()`

## Recent Visualization Improvements

### Field of View Visualization

The field of view (FOV) visualization has been enhanced with:

- **Improved Visual Clarity**
  - Added a directional arrow that indicates which way the unit is looking
  - Created a small circular indicator at the unit's position
  - Applied gradual opacity to particles (closer particles are more opaque)

- **Depth Perception**
  - Applied size variations to particles based on distance
  - Strategically distributed particles to create a stronger visual cone shape
  - Added subtle outward movement to particles to enhance the "vision" effect

### Movement Animations

Movement has been improved to better match Fire Emblem-style grid-based tactical gameplay:

- **Grid-Based Movement**
  - Eliminated diagonal movements in all patrol and movement paths
  - Ensured units only move along cardinal directions (north, south, east, west)
  - Created smoother transitions between grid cells

- **Animation System Integration**
  - Fixed teleportation issues by properly using the MoveAnimation system
  - Added sequential animations that properly chain movement and field of view effects
  - Improved code structure for managing animations with proper timing

## Extending the Animation System

### Creating New Animation Types

1. Add a new animation type to the `AnimationType` enum
2. Create a new animation class that extends `Animation`
3. Implement the `update()` and `draw()` methods
4. Add handling for the new animation type in `play_animation()`

### Adding New Particle Effects

To add a new particle effect type:

1. Add a new case in the `spawn_particles()` method of `ParticleSystemEffect`
2. Configure the particle properties (color, speed, size, etc.)
3. Use the new effect type when creating a `ParticleEffectAnimation`

## Notes for Developers

- All animations initialize the `progress` attribute to 0.0 in their constructors
- Chained animations are added to the animation queue when their parent completes
- Particle effects use randomization to create organic-looking visuals
- For performance reasons, limit the number of simultaneous particle effects
- Consider the three-component testing vision when developing or modifying visual elements

## Future Improvements

Potential areas for further enhancement:

- Add unit-specific field of view ranges (knights see further than infantry)
- Implement terrain-aware field of view (blocked by mountains, reduced in forests)
- Add more visual feedback during combat interactions
- Improve animation chaining for more complex tactical scenarios
- Add more particle effect types for diverse visual feedback 