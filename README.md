# Fantasy Tactics Game

A turn-based tactical RPG inspired by classic games like Fire Emblem and Final Fantasy Tactics.

## Project Overview

This project implements a complete tactical RPG engine with:

- **Core Engine**: Game state management, turn handling, events, and data providers
- **Gameplay Systems**: Combat, AI, movement, inventory, skills, status effects, and more
- **Data-Driven Design**: Game entities and scenarios defined in YAML files
- **Testing Framework**: Comprehensive unit and integration tests

## Project Structure

```
.
├── data/                     # Game data files (YAML)
│   ├── ai/                   # AI-specific data (personas)
│   ├── chapters/             # Chapter-specific data (maps, units, events)
│   ├── core/                 # Core game definitions (classes, items, skills, etc.)
│   └── scenarios/            # Test scenario data
├── docs/                     # Documentation
│   └── specs/                # System specifications
├── scripts/                  # Utility and standalone scripts
├── src/                      # Main Python source code
│   ├── fantasy_tactics_core/ # Core engine components
│   ├── fantasy_tactics_gameplay/ # Gameplay mechanics and systems
│   │   ├── ai/               # AI v2 system
│   │   ├── combat/           # Combat system
│   │   ├── systems/          # Various gameplay systems
│   │   └── special_mechanics/# Complex mechanics (capture, rescue, etc.)
│   ├── fantasy_tactics_data/ # Data loading and validation code
│   └── fantasy_tactics_ui/   # User interface components
│       ├── cli/              # Command Line Interface
│       └── gui/              # GUI (future development)
└── tests/                    # Unit and integration tests (mirroring src/)
    ├── core/
    ├── gameplay/
    ├── data/
    ├── ui/
    └── integration/
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Game

Currently, the game can be run in CLI mode:

```
python src/main.py
```

Optional flags:
- `--ascii-display`: Enable ASCII map display
- `--chapter <chapter_name>`: Load a specific chapter

## Running Tests

```
pytest tests/
```

## Development Status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed information about completed work and remaining tasks.

## License

[Specify license information here]