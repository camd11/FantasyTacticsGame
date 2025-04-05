# Thracia 776 Recreation

A Python-based recreation of Fire Emblem: Thracia 776, a tactical role-playing game originally released for the Super Famicom. This project aims to implement the core mechanics of the game with a command-line interface initially, with plans to add graphical elements in later development stages.

## Project Structure

```
thracia776/
├── core/             # Core game engine components
│   └── __init__.py
├── data/             # Data management components
│   ├── __init__.py
│   ├── models.py     # Core data classes (Unit, Item, MapTile, GameState)
│   ├── unit_manager.py
│   ├── item_manager.py
│   ├── map_manager.py
│   └── static_data_loader.py
├── cli/              # Command-line interface components
│   └── __init__.py
├── ai/               # AI components
│   └── __init__.py
├── assets/           # Static game data (JSON/YAML files)
│   └── data/         # Created automatically with test data on first run
├── tests/            # Unit tests
│   └── __init__.py
├── main.py           # Main entry point
└── README.md         # This file
```

## Features

The project implements the following key features from Thracia 776:

- **Turn-Based Structure**: Player Phase, Enemy Phase, and NPC/Ally Phase
- **Fatigue System**: Units accumulate fatigue through actions and must rest when fatigued
- **Capture and Rescue System**: Units can capture enemies to obtain their equipment
- **Dismounting System**: Mounted units can dismount, changing their capabilities
- **Combat System**: Implements Thracia 776's unique combat mechanics, including PCC (Pursuit Critical Coefficient)
- **Fog of War**: Limited visibility in certain maps
- **Status Effects**: Various status conditions that affect units

## Getting Started

### Prerequisites

- Python 3.7 or higher

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/thracia776.git
   cd thracia776
   ```

2. Run the game:
   ```
   python -m thracia776.main
   ```

On first run, the game will automatically create test data in the `assets/data` directory.

## Development Status

This project is in early development. Currently implemented:

- Core data models (Unit, Item, MapTile, GameState)
- Data management components (UnitManager, ItemManager, MapManager, StaticDataLoader)
- Basic test scenario in main.py

Next steps:

- Implement the core game engine
- Develop the command-line interface
- Implement AI for enemy and NPC units
- Add chapter progression and story elements

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Based on Fire Emblem: Thracia 776, developed by Intelligent Systems and published by Nintendo
- This is a fan project for educational purposes