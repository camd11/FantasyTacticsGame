# Fantasy Tactics Game (Thracia 776 Recreation)

This project aims to recreate the gameplay mechanics of Fire Emblem: Thracia 776 in a text-based CLI format first, eventually leading to a graphical implementation.

## Current Status: MVP Phase 1 & Basic Combat Complete

The initial Minimum Viable Product (MVP) focusing on foundational map/unit representation and the core combat loop is complete.

**Features Implemented:**

*   **Phase 1:**
    *   Basic data structures for Game State, Map, Tiles, and Units (`src/game/models.py`).
    *   Text-based map rendering in the CLI (`src/game/display.py`), including showing defeated units ('X').
    *   Calculation of basic movement range on plain terrain, avoiding other units (`src/game/movement.py`).
    *   Core CLI application (`src/cli.py`) supporting basic commands (`select`, `move`, `wait`, `info`, `endturn`, `quit`).
*   **Phase 2 (Basic Combat):**
    *   Added core combat stats (Str, Skl, Spd, Lck, Def) and basic `Weapon` class to `models.py`.
    *   Implemented combat calculation logic (`src/game/combat.py`) including:
        *   Simplified Attack Speed (AS), Hit Rate, Avoid.
        *   Simplified physical Damage calculation (Str+Mt - Def).
        *   Attack resolution with hit check (1-100 roll).
        *   Basic doubling check (Attacker AS >= Defender AS + 4).
        *   Attack/Counter-attack sequence simulation.
        *   Unit death handling (sets `is_alive=False`, removes from map tile).
    *   Integrated `attack x y` command into `cli.py`.
    *   Updated `info` command to show combat stats.
*   **Testing:**
    *   Automated testing via command file input (`test_mvp_commands.txt`, `test_combat_commands.txt`).

**Design Documents:**

*   Phase 1 plan: `DESIGN_MVP_PHASE1.md`.
*   Original research: `research.md`.

## How to Run

1.  Ensure you have Python 3 installed.
2.  Navigate to the project's root directory (`/home/ryan/StudioProjects/FantasyTacticsGame`).
3.  Run the CLI application directly:
    ```bash
    python3 src/cli.py
    ```
4.  Alternatively, run the automated test sequences:
    ```bash
    # Test basic movement/turns
    cat test_mvp_commands.txt | python3 src/cli.py

    # Test combat
    cat test_combat_commands.txt | python3 src/cli.py
    ```

## Development Workflow

It's important to maintain good version control practices. After making changes and verifying they work (e.g., by running relevant test files):

1.  **Stage your changes:**
    ```bash
    # Stage specific files
    git add src/cli.py tests/my_new_test.txt
    # Or stage all tracked changes
    git add .
    ```
2.  **Commit your changes** with a clear, descriptive message:
    ```bash
    git commit -m "Fix: Correctly parse commands with comments in pipe"
    # Or for more significant changes:
    git commit -m "Feat: Implement basic fatigue mechanic"
    ```
3.  **Push your changes** to the remote repository (assuming one is configured):
    ```bash
    git push
    ```

Commit frequently with focused changes to make tracking history easier.

## Next Steps (Potential)

*   Refine combat calculations closer to Thracia's formulas (Con impact on AS, 1-99% hit cap, terrain bonuses, magic damage, crits, PCC, skills).
*   Implement terrain costs for movement.
*   Implement inventory management and item usage (Vulneraries).
*   Implement unique mechanics (Capture, Steal, Fatigue).
*   Implement basic Enemy AI for the Enemy Phase.
*   Add more complex map scenarios and unit types.