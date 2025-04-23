# Fantasy Tactics Game

A turn-based tactical RPG inspired by Fire Emblem: Thracia 776, featuring complex gameplay systems including combat, movement, skills, AI, and more.

## Overview

This project is a console-based tactical RPG built with Python. It features:

- Tactical turn-based combat with diverse units and classes
- Deep gameplay systems including fatigue, fog of war, capture, and more
- Advanced goal-oriented utility AI for compelling computer opponents
- ASCII display mode for testing and gameplay visualization
- Robust architecture with modular systems for extensibility
- Optional GUI mode with Pygame (experimental)

## Getting Started

### Prerequisites

- Python 3.7+
- Git (for cloning the repository)
- Pygame (for GUI mode)

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

# Run in GUI mode (experimental)
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

### GUI Mode (Experimental)
A new GUI mode is available that visualizes the game map and units using Pygame. Enable with the `--gui` flag.

## Documentation

For more detailed information about the game, please refer to these documentation files:

- [Status & Progress Log](docs/status.md) - Current development status and completed features
- [Technical Documentation](docs/technical.md) - Usage guide and technical details
- [AI Research Summary](docs/research/ai_research_summary.md) - Comprehensive documentation on the AI system
- [Game Mechanics Reference](research.md) - Detailed guide to the game mechanics implemented from Thracia 776
- [Changelog](CHANGELOG.md) - Record of significant changes and features

## Project Structure

- `src/` - Source code for the game
  - `core_engine/` - Core game engine components
  - `gameplay_systems/` - Individual gameplay systems
  - `data_structures/` - Data classes and containers
  - `ui/` - User interface components
- `data/` - Game data files (units, classes, items, chapters)
- `tests/` - Test suites for various components
- `docs/` - Documentation
- `tools/` - Utility scripts for development and testing

## Running Tests

To run the test suite:
```bash
python -m pytest
```

To run specific tests:
```bash
python -m pytest tests/gameplay_systems/
```

## Tools

Utility scripts to assist with development:

- `tools/convert_yaml_to_json.py` - Converts YAML data files to JSON format
- `tools/run_ai_vs_ai_test.py` - Runs AI vs AI simulations for testing 