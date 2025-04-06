# Project Status

## Completed Work

- **Core Gameplay Systems:**
    - AI System
    - Combat System
    - Fatigue System
    - Event System
    - Status Effects System
    - Dismounting System
    - Support/Leadership System
- **Initial Data Population:**
    - Units (`units.yaml`)
    - Items (`items.yaml`)
    - Classes (`classes.yaml`)
    - Skills (`skills.yaml`)
- **CLI Enhancements:**
    - Basic command-line interface implemented.
- **Bug Fixes:**
    - Resolved module import issues.
    - Corrected `class_id` attribute handling.
- **AI & Testing Features:**
    - Implemented AI vs AI testing mode via `--ai-vs-ai` flag.
    - Implemented optional ASCII map display via `--ascii-display` flag.
    - Adjusted AI vs AI turn limit to 10 for testing.
    - Enhanced AI action logging for better simulation visibility.
    - Fixed runtime errors related to ASCII display (`get_map_dimensions`, `turn_manager` access).
- **Testing & Integration:**
    - Resolved 6 integration test failures related to `DataProvider`, `Engine`, `EventHandler`, and `GameState`. All unit tests are now passing.
- **Configuration:**
    - Created placeholder map files (`layouts.yaml`, `placements.yaml`, `events.yaml`) in `data/maps/test_chapter/` to resolve startup warnings related to missing default chapter data.

## Remaining Tasks

- **Data Population:**
    - Populate core data files: `terrain.yaml`, `supports.yaml`, `promotions.yaml`.
    - Add more units, items, classes, and skills.
    - Create chapter-specific data (layouts, placements, events).
- **CLI Development:**
    - Implement fully interactive turn-by-turn gameplay via CLI.
- **Testing:**
    - Develop more comprehensive testing scenarios.
- **Future Enhancements:**
    - Potential GUI implementation.
- **Bug Fixing:**
    - Address any remaining warnings or bugs as they arise.

## Known Issues

- AI Movement Range Bug: The movement range calculation currently only returns the starting tile, preventing AI units from moving in simulations. This requires further debugging of the pathfinding logic in `MovementSystem`/`MapSystem`. (See TODO comment in `src/gameplay_systems/movement_system.py`)
- ASCII Display Update Bug: The ASCII map display (`--ascii-display`) does not update unit positions correctly after they move. The rendering call has been temporarily disabled in `src/core_engine/engine.py`. Needs debugging of the rendering logic and/or unit state updates. (See TODO comment in `src/core_engine/engine.py`)