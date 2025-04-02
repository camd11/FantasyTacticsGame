# Fantasy Tactics Game (Thracia 776 Recreation)

This project aims to recreate the gameplay mechanics of Fire Emblem: Thracia 776 in a text-based CLI format first, eventually leading to a graphical implementation.

## Current Status: MVP Phase 1 & Basic Combat Complete

The initial Minimum Viable Product (MVP) focusing on foundational map/unit representation and the core combat loop is complete.

**Features Implemented:**

*   **Phase 1:**
    *   Basic data structures for Game State, Map, Tiles, and Units (`src/game/models.py`).
    *   Text-based map rendering in the CLI (`src/game/display.py`), including showing defeated units ('X').
    *   Calculation of movement range considering terrain costs and unit blocking (`src/game/movement.py`).
    *   Basic terrain types (Plain, Forest, Mountain) and movement costs implemented (`src/game/models.py`).
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
*   **Phase 3 (Core Combat Mechanics):**
    *   Refined Fatigue tracking: Added staff costs by rank, prevents action if `fatigue >= max_hp` (`src/game/models.py`, `src/cli.py`).
    *   Implemented Critical Hit calculation including Pursuit Critical Coefficient (PCC/FCM), 25% first-hit cap, and double damage (`src/game/combat.py`).
    *   Implemented Magic Damage calculation using Magic stat for offense/defense and separate Attack Speed calculation (`src/game/models.py`, `src/game/combat.py`).
    *   Implemented Terrain Combat Bonuses (DEF/AVO) (`src/game/models.py`, `src/game/combat.py`).
    *   Implemented Weapon Triangle bonuses (+/- 5 Hit) (`src/game/models.py`, `src/game/combat.py`).
    *   Implemented Weapon Effectiveness (3x Might) (`src/game/models.py`, `src/game/combat.py`).
    *   Added `equip` command to CLI (`src/cli.py`).
    *   Added `inventory` command to view unit items (`src/cli.py`).
    *   Added `use <item_index>` command to use consumable items (e.g., Vulnerary) (`src/cli.py`, `src/game/models.py`).
    *   Added `steal <x> <y> [item_index]` command for units with `can_steal=True`, checking AS and Con vs item weight (`src/cli.py`, `src/game/models.py`, `src/game/combat.py`).
    *   Implemented basic Enemy AI: find closest player, move adjacent, attack if possible (`src/game/ai.py`, `src/cli.py`).
    *   Refined Capture mechanics: Added immunity checks (Con>=20, Mounted Target), verified stat penalties (`src/game/combat.py`).
    *   Implemented basic Unit Skills: Wrath (guaranteed counter crit), Adept (extra attack chance), Miracle (avoid boost at low HP), Nihil (negate enemy crits) (`src/game/models.py`, `src/game/combat.py`, `src/cli.py`).
    *   Implemented basic Status Effects: Poison (damage at turn start), Sleep (prevents action, reduces stats), Silence (prevents magic use). Statuses persist until cured (no auto-recovery implemented yet). (`src/game/models.py`, `src/game/combat.py`, `src/cli.py`).
*   **Testing:**
    *   Automated testing via command file input (`test_mvp_commands.txt`, `test_combat_commands.txt`, `test_crit_commands.txt`, `test_magic_attack.txt`, `test_triangle.txt`, `test_effectiveness.txt`, `test_item_commands.txt`, `test_steal_commands.txt`, `test_ai_commands.txt`, `test_capture_commands.txt`, `test_terrain_commands.txt`, `test_fatigue_commands_v2.txt`, `test_skills_commands.txt`, `test_status_commands.txt`).

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

Follow this cycle for development:

1.  **Code:** Implement the desired feature or fix.
2.  **Test:** Create or update test files (e.g., `test_*.txt`) and run them using `cat <test_file> | python3 src/cli.py` to verify the changes work as expected and haven't broken existing functionality.
3.  **Update Documentation:** Ensure `README.md` (especially "Features Implemented") and any relevant design documents accurately reflect the current state of the project.
4.  **Commit:** Stage and commit your changes using Git.
    *   **Stage your changes:**
    ```bash
    # Stage specific files
    git add src/cli.py tests/my_new_test.txt
    # Or stage all tracked changes
    git add .
    ```
    *   **Commit your changes** with a clear, descriptive message (use conventional commit prefixes like `feat:`, `fix:`, `docs:`, `test:`, `refactor:`):
        ```bash
        git commit -m "Fix: Correctly parse commands with comments in pipe"
    # Or for more significant changes:
    git commit -m "Feat: Implement basic fatigue mechanic"
    ```
5.  **Push:** Push your changes to the remote repository (assuming one is configured):
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