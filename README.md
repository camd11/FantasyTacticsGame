# Fantasy Tactics Game (Thracia 776 Recreation)

This project aims to recreate the gameplay mechanics of Fire Emblem: Thracia 776 in a text-based CLI format first, eventually leading to a graphical implementation.

## Current Status: MVP Phase 1 Complete

The initial Minimum Viable Product (MVP) focusing on foundational map and unit representation is complete.

**Features Implemented:**

*   Basic data structures for Game State, Map, Tiles, and Units (`src/game/models.py`).
*   Text-based map rendering in the CLI (`src/game/display.py`).
*   Calculation of basic movement range on plain terrain, avoiding other units (`src/game/movement.py`).
*   Core CLI application (`src/cli.py`) supporting:
    *   Displaying the game map and unit positions.
    *   Selecting player units (`select x y`).
    *   Displaying unit info (`info [x y]`).
    *   Moving selected units within range (`move x y`).
    *   Waiting with a selected unit (`wait`).
    *   Ending the player turn (`endturn`) and cycling through a basic turn structure.
    *   Quitting the application (`quit`).
*   Automated testing via command file input (`test_mvp_commands.txt`).

**Design Document:**

*   The plan for this phase is documented in `DESIGN_MVP_PHASE1.md`.
*   The original research and detailed mechanics specification is in `research.md`.

## How to Run

1.  Ensure you have Python 3 installed.
2.  Navigate to the project's root directory (`/home/ryan/StudioProjects/FantasyTacticsGame`).
3.  Run the CLI application directly:
    ```bash
    python3 src/cli.py
    ```
4.  Alternatively, run the automated test sequence:
    ```bash
    cat test_mvp_commands.txt | python3 src/cli.py
    ```

## Next Steps

*   Implement Phase 2: Core Combat Loop (Attack command, basic damage/hit calculation, doubling).
*   Expand data structures to include more unit stats (Str, Def, Skl, Luk, Con).
*   Refine movement to include terrain costs.
*   Implement more unit actions (Attack, Item, etc.).
*   Develop more sophisticated Enemy AI.