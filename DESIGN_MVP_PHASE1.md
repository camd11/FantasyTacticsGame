# Thracia 776 Recreation - MVP Plan (Phase 1)

**Focus:** Foundational Map & Unit Representation (Text-Based CLI)

**Goals:**

1.  Represent the game map and units within it.
2.  Allow basic unit selection and information display.
3.  Implement simple movement on plain terrain.
4.  Establish a basic turn structure (Player Phase -> End Turn -> rudimentary Enemy Phase -> Player Phase).
5.  Create a simple CLI for interaction and testing.
6.  Set up initial documentation structure.

**Implementation Steps:**

1.  **Data Structures Definition:**
    *   **`Map`:** Define a structure to hold the grid (e.g., a 2D array or list of lists). Each element will represent a `Tile`.
    *   **`Tile`:** Define a structure for map tiles. Initially, it only needs to know its terrain type (start with just `Plain`) and whether a `Unit` occupies it (e.g., storing a Unit ID or reference).
    *   **`Unit`:** Define a basic `Unit` structure. For the MVP, include:
        *   `id`: Unique identifier.
        *   `name`: Character name (e.g., "Leif").
        *   `faction`: Player, Enemy, Ally (start with just Player/Enemy).
        *   `position`: Coordinates (x, y) on the map.
        *   `hp`, `max_hp`: Basic health.
        *   `mov`: Movement stat.
        *   *(Other stats like Str, Def, etc., will be added in later phases)*.
    *   **`GameState`:** A central structure to hold the current `Map`, a list of all `Units`, the current turn number, the active faction (Player/Enemy), and potentially the currently selected unit.

2.  **Core Map Logic:**
    *   Implement functions to:
        *   Initialize a new `Map` of specified dimensions with `Plain` terrain.
        *   Place a `Unit` onto the `Map` at given coordinates, updating the relevant `Tile`.
        *   Retrieve the `Unit` occupying a specific `Tile` (if any).
        *   Update a `Unit`'s position on the `Map`.

3.  **CLI Display:**
    *   Create a function to render the current `Map` state to the console.
    *   Use simple characters: '.' for empty `Plain` tiles, 'P' for Player units, 'E' for Enemy units.
    *   Display basic game state info (e.g., "Turn 1 - Player Phase").

4.  **Basic Unit Movement:**
    *   Implement a function `calculate_move_range(unit)`:
        *   Takes a `Unit` as input.
        *   Performs a simple breadth-first search (BFS) or similar algorithm outwards from the unit's position.
        *   Considers only the `mov` stat and assumes all `Plain` tiles cost 1 movement point.
        *   Does not allow moving through tiles occupied by other units (enemy or ally).
        *   Returns a list of reachable coordinates `(x, y)`.
    *   Implement CLI commands:
        *   `select <x> <y>`: Selects the unit at the given coordinates. Display its movement range visually (e.g., changing reachable '.' to '*').
        *   `move <x> <y>`: If a unit is selected and the target coordinates are within its valid move range, update the unit's position in the `GameState` and on the `Map`. Deselect the unit (or mark as acted).

5.  **Basic Unit Actions:**
    *   Implement CLI commands:
        *   `info [x y]`: If coordinates are given, display basic info (Name, HP, Pos) for the unit at `(x, y)`. If no coordinates are given, display info for the currently selected unit.
        *   `wait`: Marks the currently selected unit as having finished its action for the turn. Deselect the unit.

6.  **Basic Turn Structure:**
    *   Implement a `TurnManager` that tracks the active faction.
    *   Keep track of which player units have acted.
    *   Implement CLI command:
        *   `endturn`:
            *   If in Player Phase, check if all player units have acted (or waited).
            *   Switch `GameState` to Enemy Phase.
            *   *(MVP Enemy Phase: Simply print "Enemy Phase" and immediately switch back to Player Phase, incrementing the turn counter and resetting the 'acted' status for player units.)*

7.  **Initial Testing & Documentation:**
    *   Define a simple test scenario (e.g., a small map with 1-2 player units and 1-2 stationary enemy units).
    *   Document the basic CLI commands (`select`, `move`, `wait`, `info`, `endturn`).
    *   Document the initial data structures (`Map`, `Tile`, `Unit`, `GameState`).
    *   Outline the procedure for running the test scenario via the CLI.
    *   Commit initial code structure and documentation to Git.

**Mermaid Diagram:**

```mermaid
graph TD
    subgraph "Phase 1: MVP"
        direction LR
        A[Define Data Structures: Map, Tile, Unit, GameState] --> B(Implement Map Logic: Init, Place, Get Unit, Update Pos);
        B --> C(Implement CLI Display: Render Map & Basic State);
        A --> D(Implement Basic Movement: Calc Range, CLI Select/Move);
        D --> B; D -- Updates --> A;
        A --> E(Implement Basic Actions: CLI Info/Wait);
        E -- Updates --> A;
        A --> F(Implement Basic Turn Structure: CLI EndTurn, Phase Switching);
        F -- Updates --> A;
        G(Setup Initial Testing & Documentation);
        C --> G; D --> G; E --> G; F --> G;
    end