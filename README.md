# Fantasy Tactics Game

A text-based recreation of Fire Emblem: Thracia 776, with plans for graphical enhancements in later phases.

## Project Overview

This project aims to recreate the gameplay mechanics of Fire Emblem: Thracia 776, starting with a command-line interface and gradually adding graphical elements. The implementation prioritizes testability and accuracy to the original game's mechanics.

## Current Status

The project is currently in Phase 1 of development (Core Engine & Data Structures). Basic data structures, game state management, and a simple CLI have been implemented. See [Implementation Status](docs/implementation_status.md) for details on current progress.

## Features

- Turn-based tactical RPG gameplay
- Faithful recreation of Thracia 776's unique mechanics:
  - Capture system
  - Fatigue system
  - PCC (Pursuit Critical Coefficient)
  - Movement stars
  - Dismounting
  - Fog of War
- Command-line interface for testing and gameplay
- (Planned) Graphical interface

## Project Structure

```
/
├── docs/                  # Documentation
│   ├── architecture/      # System architecture documentation
│   ├── systems/           # Individual system documentation
│   └── reference/         # Reference materials
├── src/                   # Source code
│   ├── core/              # Core data structures
│   ├── systems/           # Game systems (combat, map, etc.)
│   └── cli/               # Command-line interface
├── data/                  # Game data (maps, units, items)
└── tests/                 # Test suite
```

## Setup and Installation

### Prerequisites

- Python 3.10 or higher

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fantasy-tactics-game.git
   cd fantasy-tactics-game
   ```

2. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies (when requirements.txt is available):
   ```
   pip install -r requirements.txt
   ```

### Running the Game

```
python main.py
```

## CLI Commands

The game currently supports these basic commands:

- `map` - Display the current map
- `move <unit_id> <x> <y>` - Move a unit to a position
- `wait <unit_id>` - End a unit's turn
- `end` - End the current player phase
- `quit` - Exit the game

More commands will be implemented as development progresses. See [CLI Design](docs/cli_design.md) for the planned command set.

## Development

### Documentation

- [Design Document](docs/design_document.md) - Overall project design
- [Architecture Overview](docs/architecture/overview.md) - System architecture
- [Implementation Plan](docs/implementation_plan.md) - Phased development plan
- [Implementation Status](docs/implementation_status.md) - Current progress
- [CLI Design](docs/cli_design.md) - Command-line interface design

### System Documentation

- [Game State System](docs/systems/game_state.md)
- [Unit System](docs/systems/unit_system.md)
- [Combat System](docs/systems/combat_system.md)
- [Map System](docs/systems/map_system.md)

## Contributing

This project is currently in early development. Contribution guidelines will be added in the future.

## License

[Add license information here]