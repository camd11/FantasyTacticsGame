# Fantasy Tactics Game

A turn-based tactical RPG inspired by Fire Emblem: Thracia 776, featuring complex gameplay systems including combat, movement, skills, AI, and more.

## Overview

This project is a tactical RPG built with Python. It features:

- Tactical turn-based combat with diverse units and classes
- Deep gameplay systems including fatigue, fog of war, capture, and more
- Advanced goal-oriented utility AI for compelling computer opponents
- Comprehensive three-component testing system
- Pygame-based visualization with animations and effects
- Robust architecture with modular systems for extensibility

## Getting Started

### Prerequisites

- Python 3.7+
- Git (for cloning the repository)
- Pygame (for GUI visualization)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FantasyTacticsGame.git
   cd FantasyTacticsGame
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

To start the game with default settings:
```bash
python src/main.py
```

With additional options:
```bash
# Run AI vs AI simulation
python src/main.py --ai-vs-ai

# Enable ASCII display
python src/main.py --ascii-display

# Load a specific chapter
python src/main.py --chapter 2

# Run with Pygame visualization
python src/main.py --gui
```

## Game Features

### Command Line Interface
The game features a rich command-line interface with the following actions:
- Unit movement and positioning
- Combat with various weapons
- Item usage from inventory
- Trading items between units
- Capturing enemy units
- Visiting locations for rewards and story elements
- Seizing objectives to complete chapters

### Pygame Visualization
The game includes a Pygame-based visualization system that shows:
- Game map with terrain and units
- Unit movement and combat animations
- Particle effects for spells and actions
- Status effect indicators
- Menu interfaces for action selection

### Enhanced Animation System
The game features a sophisticated animation system including:
- Smooth movement and combat animations
- Particle effects (explosions, sparks, smoke)
- Screen transitions with fade in/out
- Animation chaining for coordinated sequences

## Three-Component Testing Vision

The project follows a comprehensive testing approach with three essential components:

1. **Standard Logging:** Console output and error logs for basic verification
2. **Visual Logs:** Text-based and HTML visual logs documenting turn-by-turn game state
3. **Pygame Visuals:** Interactive graphical display showing gameplay mechanics

This approach ensures every aspect of the game is thoroughly validated across logic, behavior, and visual presentation.

## Documentation

For more detailed information about the game, please refer to these documentation files:

- [Documentation Index](docs/index.md) - Central hub and starting point for all documentation
- [Setup Guide](docs/setup.md) - Instructions for setting up the development environment
- [Testing Guide](docs/testing.md) - Comprehensive guide to the three-component testing system
- [Game Mechanics](docs/game_mechanics/) - Detailed explanations of gameplay mechanics
- [System Documentation](docs/systems/) - Documentation for specific systems:
  - [Visual System](docs/systems/visual.md) - Visual testing and animation framework
  - [Audio System](docs/systems/audio.md) - Sound effects implementation
  - [GUI System](docs/systems/gui.md) - Pygame-based GUI system
  - [Usage Guide](docs/systems/usage.md) - How to run the game and use its features
- [Development Plan](docs/development/plan.md) - Roadmap for future development
- [Project Status](docs/status.md) - Current state of the project
- [Technical Guide](docs/technical.md) - Technical details and usage instructions
- [AI Research](docs/archive/ai_research_summary.md) - Documentation on the AI system

## Project Structure

The project has been organized into a clear directory structure:

- `src/`: Core source code
- `tests/`: Test cases organized by type (visual, mechanic, etc.)
- `tools/`: Utility scripts for development
- `docs/`: Documentation files
- `assets/`: Game assets (sprites, sounds, etc.)
- `data/`: Game data files in YAML/JSON format

For more details on the project organization, see [docs/organization.md](docs/organization.md).

# How to Run

```bash
# Set up the virtual environment (first time only)
./setup_venv.sh  # On Linux/Mac
# OR
setup_venv.bat   # On Windows

# Run the game
python run_game.py

# Run mechanic tests
./run_mechanic_tests.sh

# Run visual tests
python tests/visual_tests/run_visual_tests.py [demo_name]
```

## Running Tests

### Standard Tests (pytest)
```bash
# Run all tests
python -m pytest

# Run specific tests
python -m pytest tests/gameplay_systems/
```

### Visual Log Tests
```bash
# Run all visual log tests
python tests/visual_tests/run_all_visual_tests.py

# Run specific visual logger test
python tests/visual_tests/test_visual_logger.py
```

### Visual Pygame Tests
```bash
# Run specific visual demo
python tests/visual_tests/run_visual_tests.py simple_attack

# Run mechanic test with visual display
bash tests/mechanic_tests/movement/run_movement_tests.sh --visual
```

## Tools

Utility scripts to assist with development:

- `tools/convert_yaml_to_json.py` - Converts YAML data files to JSON format
- `tools/run_ai_vs_ai_test.py` - Runs AI vs AI simulations for testing 

## AI Testing and Simulation

The game includes a robust AI system that can be tested and evaluated through AI vs AI simulations:

```bash
# Run AI vs AI simulation with default settings
python src/main.py --ai-vs-ai

# Run AI vs AI with visual logging
python src/main.py --ai-vs-ai --ascii-display
```

### AI Scenario Guidelines
- AI scenarios are designed to test specific tactical situations
- Each AI scenario should be limited to a maximum of 5 turns for performance reasons
- Scenarios focus on specific tactical challenges like chokepoint control, target prioritization, or resource management
- Test cases in `tests/gameplay_systems/ai/` demonstrate how to set up and run AI scenarios