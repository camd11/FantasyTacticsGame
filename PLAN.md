# Thracia 776 ASCII Recreation - Chapter 1 Plan

**Goal:** Create a functional ASCII representation of Thracia 776 Chapter 1, including basic movement, combat, capture, items, a 'Seize' objective, and simple enemy AI.

**Technology:** Python 3

## Core Components & Data Structures:

1.  **`GameState`:** A central object holding the current state, including:
    *   `Map`: Grid representation, terrain types.
    *   `Units`: List/dictionary of all `Unit` objects (player & enemy).
    *   `TurnManager`: Tracks current turn (player/enemy), turn count.
    *   `ObjectiveStatus`: Tracks if the 'Seize' point is captured.
2.  **`Unit`:** Represents a character on the map.
    *   Attributes: HP, Str, Mag, Skl, Spd, Lck, Def, Bld, Mv, Con, current HP, position (x, y), affiliation (player/enemy), inventory (`Item` list), status (e.g., `is_captured`, `carrying_unit`).
    *   Methods: `move()`, `attack()`, `capture()`, `drop()`, `trade()`, `use_item()`.
3.  **`Item`:** Represents weapons, consumables, etc.
    *   Attributes: Name, type (weapon, usable), stats (Mt, Hit, Wt), effects.
4.  **`Map`:** Represents the game board.
    *   Attributes: Dimensions (width, height), grid (2D array of terrain types), unit locations.
    *   Methods: `get_tile()`, `is_valid_coordinate()`, `get_unit_at()`, `calculate_move_range()`.

## Core Systems/Modules:

1.  **`RenderEngine`:** Takes the `GameState` and renders it as ASCII text to the terminal. Needs to display the map, units (using different characters/colors for player/enemy), cursor, potentially basic stats of the selected unit.
2.  **`InputHandler`:** Captures keyboard input for cursor movement, unit selection, action selection (Move, Attack, Item, Capture, Wait, Seize), target selection.
3.  **`MapEngine`:** Handles pathfinding (e.g., A* or Dijkstra for movement range), validating moves based on terrain and unit positions.
4.  **`CombatEngine`:** Calculates battle outcomes based on unit stats, weapon stats, potentially weapon triangle (though maybe simplified initially). Handles HP updates, unit death.
5.  **`CaptureEngine`:** Implements the logic for the 'Capture' command: checking build difference, updating unit status (carrying/captured), transferring items, stat penalties. Handles 'Drop' and potentially 'Rescue'.
6.  **`ItemEngine`:** Manages inventory, equipping weapons, using consumable items.
7.  **`AIEngine`:** Controls enemy units during their phase. Logic:
    *   Identify nearest player unit.
    *   Calculate path towards that unit.
    *   Move adjacent if possible.
    *   Attack if adjacent. (Simplification: Doesn't consider capture initially, just attacks).
8.  **`GameLoop`:** The main orchestrator:
    *   Initializes the game (loads map, units for Chapter 1).
    *   Starts Player Phase:
        *   Renders state.
        *   Waits for input via `InputHandler`.
        *   Executes player actions using relevant engines (`MapEngine`, `CombatEngine`, `CaptureEngine`, `ItemEngine`).
        *   Checks for objective completion ('Seize').
    *   Starts Enemy Phase:
        *   Iterates through enemy units.
        *   Uses `AIEngine` to determine and execute actions.
        *   Renders state changes (optional, could just happen at start of player turn).
        *   Checks for loss conditions (e.g., Leif defeated).
    *   Repeats turns.

## High-Level Component Interaction Diagram:

```mermaid
graph TD
    subgraph User Interface
        InputHandler
        RenderEngine --> TerminalDisplay[ASCII Terminal Output]
    end

    subgraph Game Logic
        GameLoop
        AIEngine
        MapEngine
        CombatEngine
        CaptureEngine
        ItemEngine
    end

    subgraph Game Data
        GameState
        MapData[Map/Terrain Data (Ch1)]
        UnitData[Unit Definitions (Ch1)]
        ItemData[Item Definitions]
    end

    InputHandler -- User Input --> GameLoop
    GameLoop -- Controls --> PlayerTurnActions
    GameLoop -- Controls --> EnemyTurnActions

    subgraph PlayerTurnActions
        direction LR
        P_Input[Get Input] --> P_Validate[Validate Action] --> P_Execute[Execute Action]
        P_Execute -- Uses --> MapEngine
        P_Execute -- Uses --> CombatEngine
        P_Execute -- Uses --> CaptureEngine
        P_Execute -- Uses --> ItemEngine
    end

    subgraph EnemyTurnActions
        direction LR
        E_Decide[Decide Action (AIEngine)] --> E_Execute[Execute Action]
        E_Execute -- Uses --> MapEngine
        E_Execute -- Uses --> CombatEngine
    end

    PlayerTurnActions -- Updates --> GameState
    EnemyTurnActions -- Updates --> GameState
    AIEngine -- Reads --> GameState
    MapEngine -- Reads --> GameState & MapData
    CombatEngine -- Reads --> GameState & UnitData & ItemData
    CaptureEngine -- Reads --> GameState & UnitData
    ItemEngine -- Reads --> GameState & ItemData

    GameLoop -- Requests Render --> RenderEngine
    RenderEngine -- Reads --> GameState
```

## Proposed Implementation Phases:

1.  **Foundation:** Setup project structure, Git, basic `GameState`, `Map`, `Unit` classes. Load Chapter 1 map data (hardcoded or simple file). Basic `RenderEngine` to show the map.
2.  **Movement:** Implement `InputHandler` for cursor movement and unit selection. Implement `MapEngine` for calculating valid moves and updating unit positions in `GameState`. Update `RenderEngine` to show units and cursor.
3.  **Combat:** Add stats to `Unit`, define basic `Item` (weapons). Implement `CombatEngine`. Update `InputHandler` and `GameLoop` to handle the 'Attack' command flow.
4.  **Items & Capture:** Implement inventory in `Unit`. Implement `ItemEngine` (equip/use). Implement `CaptureEngine`. Update `InputHandler` and `GameLoop` for 'Item' and 'Capture' commands.
5.  **Objective & AI:** Implement 'Seize' objective check in `GameLoop`. Implement `AIEngine` with the specified logic. Integrate AI into the enemy phase of the `GameLoop`.
6.  **Polish:** Add win/loss conditions, refine rendering, basic menus (if needed), testing.