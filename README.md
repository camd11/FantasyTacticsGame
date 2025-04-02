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
    *   Implemented Support, Leadership, and Charisma bonuses affecting Hit/Avoid/Crit/CritEvade (`src/game/models.py`, `src/game/combat.py`).
    *   Added `equip` command to CLI (`src/cli.py`).
    *   Added `inventory` command to view unit items (`src/cli.py`).
    *   Added `use <item_index>` command to use consumable items (e.g., Vulnerary) (`src/cli.py`, `src/game/models.py`).
    *   Added `steal <x> <y> [item_index]` command for units with `can_steal=True`, checking AS and Con vs item weight (`src/cli.py`, `src/game/models.py`, `src/game/combat.py`).
    *   Implemented basic Enemy AI: find closest player, move adjacent, attack if possible. Added checks to prevent Sleep/Berserk units from acting (`src/game/ai.py`, `src/cli.py`).
    *   Refined Capture mechanics: Added immunity checks (Con>=20, Mounted Target), verified stat penalties (`src/game/combat.py`).
    *   Implemented basic Unit Skills: Wrath (guaranteed counter crit), Adept (extra attack chance), Miracle (avoid boost at low HP), Nihil (negate enemy crits) (`src/game/models.py`, `src/game/combat.py`, `src/cli.py`).
    *   Implemented basic Status Effects: Poison (damage at turn start), Silence (prevents magic use). Refined Sleep/Berserk to prevent action and apply combat stat penalties (Str/Mag/Skl/Spd/Def = 0). Statuses persist until cured (no auto-recovery implemented yet). (`src/game/models.py`, `src/game/combat.py`, `src/cli.py`).
    *   Implemented Movement Stars: Units have a chance (5% per star) to act again after completing an action (`src/game/models.py`, `src/cli.py`).
    *   Implemented Canto: Mounted units can use remaining movement after non-combat actions (`src/game/movement.py`, `src/cli.py`, `src/game/display.py`).
    *   Implemented basic Staff usage: Added `staff <x> <y>` command. Implemented Heal staff effect (Range 1, Heals 10 + User Mag), fatigue cost, use consumption, and Canto prevention (`src/cli.py`, `test_staff_commands.txt`). Other staff effects are pending.
*   **Testing (Refactored Approach):**
    *   Automated testing uses command file input piped to `src/cli.py`.
    *   `src/cli.py` now accepts a `--setup <setup_name>` argument to load specific initial game states defined within `cli.py` (e.g., `setup_combat_test_state()`). This isolates test setups from the core CLI logic, improving stability.
    *   The random number generator is seeded (`random.seed(42)`) at the start of `run_cli` for deterministic test results.
    *   Test files (`test_*.txt`) cover various mechanics: `mvp`, `combat`, `crit`, `magic_attack`, `effectiveness`, `item`, `fatigue`, `staff`, `ai`, `bonus`, `canto`, `capture`, `steal`, `terrain`, `skills`, `status`, `movestars`, `triangle`, `magic_crit`. All tests now use the `--setup` argument in `src/cli.py`.
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
4.  Alternatively, run the automated test sequences using the `--setup` argument:
    ```bash
    # Test basic movement/turns (MVP)
    cat test_mvp_commands.txt | python3 src/cli.py --setup mvp

    # Test combat
    cat test_combat_commands.txt | python3 src/cli.py --setup combat

    # Test critical hits
    cat test_crit_commands.txt | python3 src/cli.py --setup crit

    # Test magic attacks
    cat test_magic_attack.txt | python3 src/cli.py --setup magic_attack

    # Test weapon effectiveness
    cat test_effectiveness.txt | python3 src/cli.py --setup effectiveness

    # Test item usage
    cat test_item_commands.txt | python3 src/cli.py --setup item

    # Test fatigue mechanics
    cat test_fatigue_commands_v2.txt | python3 src/cli.py --setup fatigue

    # Test staff usage
    cat test_staff_commands.txt | python3 src/cli.py --setup staff

    # Test basic AI
    cat test_ai_commands.txt | python3 src/cli.py --setup ai

    # Test combat bonuses
    cat test_bonus_commands.txt | python3 src/cli.py --setup bonus

    # Test Canto
    cat test_canto_commands.txt | python3 src/cli.py --setup canto

    # Test Capture/Release (Case 1 & 7)
    cat test_capture_commands.txt | python3 src/cli.py --setup capture

    # Test steal mechanics
    cat test_steal_commands.txt | python3 src/cli.py --setup steal

    # Test terrain movement costs
    cat test_terrain_commands.txt | python3 src/cli.py --setup terrain

    # Test unit skills
    cat test_skills_commands.txt | python3 src/cli.py --setup skills

    # Test status effects
    cat test_status_commands.txt | python3 src/cli.py --setup status

    # Test movement stars
    cat test_movestars_commands.txt | python3 src/cli.py --setup movestars

    # Test weapon triangle
    cat test_triangle.txt | python3 src/cli.py --setup triangle

    # Test magic critical hits
    cat test_magic_crit_commands.txt | python3 src/cli.py --setup magic_crit
    ```

## Development Workflow

Follow this cycle for development:

1.  **Code:** Implement the desired feature or fix.
2.  **Test:** Create or update test files (e.g., `test_*.txt`). Add a corresponding `setup_<test_name>_state()` function in `src/cli.py` and run the test using `cat <test_file> | python3 src/cli.py --setup <test_name>` to verify changes.
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

*   Implement remaining Staff effects (Restore, status staves, utility staves like Torch/Repair).
*   Implement Staff WExp gain.
*   Implement Status Effect recovery (Restore staff, potentially map end clearing).
*   Refine AI to use staves effectively.
*   Add more complex map scenarios and unit types.
*   Address potential bug observed in initial Heal staff test output.
