# GUI System

This document provides comprehensive information about the Pygame-based GUI system used in the Fantasy Tactics Game.

## Overview

The GUI system provides a visual representation of the game state, including:
- Map rendering and unit visualization
- Animation system for movements, combat, and effects
- User interface for player interaction
- Integration with the game's core logic

As part of the project's three-component testing vision, the GUI system serves as the visual component that complements standard logging and visual text logs.

## Architecture

### Core Components

- **`GameRenderer` Class:** Manages the Pygame window, asset loading (tiles, sprites, effects), drawing the map and units, and playing animations. It holds a reference to the `GameStateManager` to access the current game state.

- **Decoupling:** The game logic (`GameStateManager`, `CombatSystem`, `MovementSystem`, etc.) remains independent of the GUI. The GUI reads the game state but does not modify it directly (except for relaying user input).

- **View System:** The renderer uses a camera/view system to handle scrolling, zooming, and positioning game elements on screen.

### Integration with Testing

Tests can run in "visual mode" (`--visual` flag). In this mode, test actions trigger calls to the `GameRenderer` to display corresponding visuals and animations alongside log generation. This allows for comprehensive testing that includes:

1. Standard logging of game state changes
2. Visual log text output documenting turn-by-turn changes
3. Pygame visualization showing the actual gameplay elements

## Running with GUI Visualization

To run the game with GUI visualization:

```bash
python src/main.py --gui
```

To run tests with GUI visualization:

```bash
# Run a specific test with visualization
python run_visual_tests.py simple_attack

# Run mechanic tests with visualization
bash tests/mechanic_tests/movement/run_movement_tests.sh --visual
```

## Asset Management

- **Location:** All visual assets (images, sound files) reside in the `assets/` directory in the project root.
- **Subdirectories:**
  - `assets/tiles` - Map tile graphics
  - `assets/sprites/units` - Unit character sprites
  - `assets/sprites/effects` - Visual effect sprites
  - `assets/sounds` - Sound effects (see [Audio System](audio.md))

## Animation System

The animation system is a core part of the GUI that provides visual feedback for game actions. For detailed information on the animation system, see the [Visual System documentation](visual.md).

### Key Features

- **Animation Types:** The system supports various animation types including movement, attacks, damage, status effects, and particle effects.
- **Animation Chaining:** Animations can be sequenced to create complex visual feedback.
- **Integration with Game Logic:** Game actions automatically trigger appropriate animations.
- **Sound Integration:** Animations can trigger sound effects for complete audiovisual feedback.

## User Interface

The GUI provides an interface for player interaction including:

- **Unit Selection:** Click or keyboard selection of units
- **Movement Range Display:** Visual indication of where units can move
- **Action Menus:** Menus for selecting actions after movement
- **Combat Previews:** Pre-combat information about potential outcomes
- **Information Panels:** Unit stats, terrain information, and game status

## Future Development

Planned improvements to the GUI system include:

- Enhanced UI elements for better player experience
- More detailed animation sequences for skills and special actions
- Improved asset loading and management for better performance
- Additional visual effects for weather, terrain interactions, and status changes
- Customizable visual settings for accessibility

## Implementation Notes

- The GUI system is built on Pygame for cross-platform compatibility
- Rendering is optimized for grid-based tactical gameplay
- The system supports both mouse and keyboard input
- Animation timing is frame-rate independent
- Asset loading is handled lazily to improve startup time 