# Project Status & Progress Log

## Project Overview

A turn-based tactical RPG inspired by Fire Emblem: Thracia 776, featuring complex gameplay systems including combat, movement, skills, AI, and more.

## How to Update This Document

Please update this document after completing significant milestones or before handing off work. Add new entries under the appropriate sections chronologically. Keep the summary concise but informative.

## Completed

- **Documentation Organization Refinement:** Completed additional documentation organization by moving remaining markdown files to appropriate subdirectories. Created `docs/game_mechanics/rescue_system.md` from `rescue_system_changes.md`, added `docs/research/build_constitution_mechanics.md` from `summary_of_build_constitution.md`, created `docs/research/source_material_index.md` as an index to the large `research.md` file, ensured `docs/setup.md` and `docs/testing.md` are comprehensive, and updated cross-references. This completes the documentation organization phase started earlier. (2025-04-24)

- **Documentation Reorganization:** Completed comprehensive documentation restructuring to improve organization and accessibility. Created a hierarchical structure with dedicated directories (`docs/systems/`, `docs/development/`, `docs/research/`, `docs/game_mechanics/`), consolidated related files (visual system docs, AI research notes), standardized naming to lowercase, and updated cross-references. Created a central `docs/index.md` as a documentation hub and updated README links. (2025-04-22)

- **Visual Logger Fixes:** Corrected `VisualScenarioLogger` initialization order in `src/app.py` to occur after dependencies are ready. Refined logging calls within `EngineCore` to accurately capture turn starts, phase starts, actions, and end-of-turn states. Verified correct visual log output (`logs/visual_log_*.txt`) matches game flow observed in `ai_behavior.log` during AI vs AI simulation.

- **AI Tactical Executor Testing:** Resolved testing issues with the TacticalExecutor class by creating standalone tests that properly mock dependencies. All goal handling functions now have comprehensive tests that verify proper action selection logic for various game scenarios including position securing, attacking, healing, advancing to objectives, and seizing tiles.

- **Fixed VisualScenarioLogger initialization**: Corrected initialization order in `src/app.py` to ensure dependencies (game state manager and display) are ready when the logger is instantiated. Refined logging calls in `EngineCore` to track more logical points in the game flow. Verified that visual log output matches observed game flow in `ai_behavior.log` during AI vs AI simulation. (2025-04-22)

- **Fixed TacticalExecutor tests**: Created standalone tests that properly mock dependencies and exercise all primary goal handling functions in the TacticalExecutor. Tests now cover secure position, heal unit, attack unit, and move to safety scenarios with appropriate assertions to validate AI behavior. (2025-04-22)

- **Fixed AI vs AI simulation**: Resolved issues with pathfinding access in AI components. Added `get_movement_system()` method to `GameStateManager` class, modified AI components to use this method instead of directly accessing `pathfinding`. Updated the initialization sequence in `EngineCore` to properly link the movement system to the game state manager. The AI vs AI simulation now runs successfully with units able to move across the map. (2025-04-22)

- **Added map dimension methods**: Added missing `get_width()`, `get_height()`, and `get_map_dimensions()` methods to the MapSystem class in `src/gameplay_systems/map_system.py`. This resolved an AttributeError where the code was trying to access `map_width` and `map_height` attributes directly during AI simulation. The fix ensures proper access to map dimensions through accessor methods with appropriate error handling.

- **Core Gameplay Systems:**
    - AI System
    - Combat System
    - Fatigue System
    - Event System
    - Status Effects System
    - **Two-Phase Goal-Oriented Utility AI (v2)** (Implementation Complete)
        - Replaces the previous monolithic/archetype-based AI system.
        - Separates decision-making into Strategic Goal Selection (`StrategicEvaluator`) and Tactical Action Execution (`TacticalExecutor`).
        - **Enhanced Tactical Execution:** `TacticalExecutor` now intelligently handles movement towards targets when direct actions (attack, skill) are not immediately possible, improving goal pursuit (e.g., closing distance to attack). This includes specific enhancements for `MoveToSafetyGoal` and `SeizeTileGoal` when targets are not immediately reachable.
        - **Implemented Goals:** Expanded initial goal library (e.g., `HealUnitGoal`, `MoveToSafetyGoal`, `SeizeTileGoal`, `AttackUnitGoal`, `AdvanceToObjectiveGoal`, `SecurePositionGoal`).
        - **Utility & Tactical Refinement:** Integrated AI Personas into `UtilityScorer` (weighting considerations) and `TacticalExecutor` (influencing action scoring).
        - **Initial Scenario Testing:** Validated core logic using specific test scenarios.
        - **Improved Logging:** Dedicated `AILogger` provides detailed insights into goal selection and action evaluation.
        - **Increased Robustness:** The AI v2 system is now more robust in handling various tactical situations due to these enhancements.
        - Implemented core status effects (Poison, Sleep, Petrify, Paralysis, Berserk, Silence).
    - Dismounting System
    - Support/Leadership System
    - Fog of War System
        - Calculates visibility based on unit vision range and terrain.
        - Maintains different map states (visible, explored, hidden).
        - Updates visibility dynamically on unit movement or phase changes.
        - Handles enemy unit visibility and actions within the fog.
        - Incorporates effects like Torches or Light spells to temporarily increase vision.
    - Capture System
    - Stealing System
    - Rescue/Drop/Take System
    - Door/Chest Interaction System
    - Enhanced Terrain Effects
    - Trading System
    - Talk System
    - Chapter Loader
    - Event Manager
    - Ballista System
    - Combat Skills (Astra, Sol, Luna, Pavise, Nihil, Charge)
    - Pursuit Critical Coefficient (PCC)
    - Prf Weapon Effects System
    - Expanded Staff System
    - Move Again (Dance/Play) Skill
    - Shop/Armory System
    - Save/Load System
    - Convoy/Supply System

- **Initial Data Population:**
    - Units (`units.yaml`): Added Mareeta, Nanna, Saias.
    - Items (`items.yaml`): Added Short Lance, Rapier, Physic, Killer Lance, Hand Axe.
    - Classes (`classes.yaml`): Added Myrmidon, Troubadour, Bishop.
    - Skills (`skills.yaml`): Added Astra, Sol, Luna, Pavise, Canto+.
    - Promotions (`promotions.yaml`): Added Myrmidon->Swordmaster, Troubadour->Valkyrie/Paladin.
    - Supports (`supports.yaml`): Added initial support pairs (e.g., Leif/Nanna, Othin/Tanya).
    - Terrain (`terrain.yaml`)
    - Chapter 1 Data (`data/chapters/chapter_1/`): Initial map, units, objectives, and events created.

- **CLI Enhancements:**
    - Basic command-line interface implemented.

- **Bug Fixes:**
    - Resolved module import issues.
    - Corrected `class_id` attribute handling.
    - Fixed runtime errors related to ASCII display (`get_map_dimensions`, `turn_manager` access).
    - Fixed persistent AI movement range bug (corrected terrain cost lookup in `DataProvider`).
    - Fixed `AttributeError` by adding `get_units_in_range` method to `UnitSystem`.
    - Fixed phase/faction mismatch warnings and processing logic in `EngineCore`.
    - Fixed `AttributeError` by adding `get_unit` method to `UnitSystem`.
    - **AI v2 Integration Fixes:** Resolved various `AttributeError` issues and engine integration problems encountered during AI v2 development and testing.

- **AI & Testing Features:**
    - Implemented optional ASCII map display via `--ascii-display` flag.
    - Adjusted AI vs AI turn limit for testing.
    - Enhanced AI action logging for better simulation visibility.
    - **AI vs AI Testing Framework:** Successfully implemented (`run_ai_vs_ai_test.py`, `test_ai_vs_ai_fixed.py`) allowing for full AI-controlled simulations and behavior observation.
    - **AI Action Execution Pipeline Debugged:** The core AI action execution loop (Goal Selection -> Tactical Execution -> Action Handling -> System Execution -> Game State Update) is now functioning correctly.
    - Enhanced ASCII Display
        - Improved rendering of units and terrain features.
        - Integrated Fog of War visualization (showing visible, explored, hidden tiles).
        - Added a status panel displaying key unit information.

- **UI/Interaction:**
    - Interactive Player Input System
        - Allows direct player control of units via keyboard during the Player Phase.
        - Handles unit selection, movement range display, move confirmation, action menu navigation, targeting, and turn management through a state-based system.
        - Replaces previous scenario-driven execution for player actions.

- **AI Refinement (Pre-v2):**
    - Improved AI target prioritization logic.
    - Implemented basic AI archetypes (Aggressive/CHARGE, Defensive/GUARD).
    - Healer (HEAL_SUPPORT) AI Archetype
    - Thief (THIEF_LOOT) AI Archetype

- **Testing & Integration:**
    - Resolved 6 integration test failures related to `DataProvider`, `Engine`, `EventHandler`, and `GameState`. All unit tests are now passing.
    - Created new test scenarios for:
        - Weapon Triangle (`test_weapon_triangle.py`)
        - Poison Status (`test_poison_status.py`)
        - Fatigue Accumulation (`test_fatigue_accumulation.py`)
        - Vantage Skill (`test_vantage_skill.py`)
        - Wrath Skill (`test_wrath_skill.py`)

- **Configuration:**
    - Created placeholder map files (`layouts.yaml`, `placements.yaml`, `events.yaml`) in `data/maps/test_chapter/` to resolve startup warnings related to missing default chapter data.

- **2025-04-05: Initial Discovery & Architecture Review:**
    - Reviewed original prompt and `research.md`.
    - Conducted detailed discovery of codebase (`specs/`, `src/`).
    - Confirmed modular architecture (State, Data, Actions, Turns, Events, Combat, Units, Map/Movement, Inventory, AI).

- **2025-04-05: System Implementation & Refinement:**
    - **`TurnManager`:** Refined Movement Star logic, fatigue costs/application, start-of-phase effects. Removed `EVENT_PHASE`, `check_pursuit_star`.
    - **`CombatSystem`:** Enhanced with skill activation logic (Adept, Miracle, Nihil, Sol/Luna, Pavise) and improved EXP/WExp calculations.
    - **`InventorySystem`:** Implemented item management, durability, breaking/repair mechanics, and trading.
    - **`AIManager`:** Implemented AI loop, action evaluation/scoring (placeholder), selection, and execution via `ActionHandler`. Includes capture prioritization.

- **2025-04-05: Test Chapter & Runnable Setup:**
    - Created `test_chapter` data files (`map.yaml`, `placements.yaml`, `events.yaml`) in `data/chapters/test_chapter/`.
    - Created main entry point `src/main.py`.
    - Created basic CLI handler `src/input/cli_input_handler.py`.

- **AI v2 Enhancements:** 
    - **Goal Library Expansion:** Implemented additional strategic goals (`UseItemGoal`, `SupportAllyGoal`) with corresponding tactical executors, completing the goal expansion task.
    - **UseItemGoal:** Allows AI units to intelligently use consumables, keys, and other items.
    - **SupportAllyGoal:** Enables AI units to provide tactical support to allies with support relationships or leadership capabilities.
    - **Thracia 776 AI Personas:** Implemented the four canonical AI behavior types from Fire Emblem: Thracia 776:
        - **AGGRESSIVE:** Moves towards and attacks the nearest player unit within range.
        - **STATIONARY_GUARD:** Does not move unless a player unit enters its attack range.
        - **PURSUIT:** Targets a specific unit or type of unit, potentially ignoring closer threats.
        - **FLEE:** Moves away from player units, especially when HP is low.
    - **Existing Personas Refinement:** Enhanced all existing personas (AGGRESSOR, DEFENDER, SUPPORT, OBJECTIVE-FOCUSED, BALANCED) with support for the new goal types.
    - **Refined Goal Implementations:** Enhanced the tactical execution of existing goals to improve AI decision-making:
        - **SecurePositionGoal:** Improved tile scoring with comprehensive tactical considerations including enemy threat, ally support, terrain advantages, and proximity to objectives. Incorporated persona-specific adjustments to scoring weights.
        - **AdvanceToObjectiveGoal:** Enhanced pathfinding with threat awareness, strategic waypoints, and multiple path evaluations. Added sophisticated decision-making for selecting routes based on unit health, threat level, and tactical objectives.

## In Progress

- **AI v2 Enhancements:**
    - Complex AI Testing: Develop more intricate AI vs AI scenarios to stress-test decision-making.

## Remaining Tasks

- **Data Population:**
    - Add more units, items, classes, skills, promotions, and supports.
    - Create data for subsequent chapters (Chapter 2 onwards: layouts, placements, events).
    - **Note:** Full implementation of subsequent chapters (beyond initial test/scenario chapters) is deferred pending GUI development.

- **CLI Development:**
    - Continue enhancing the command-line interface for better usability.

- **Testing:**
    - Develop more comprehensive testing scenarios covering edge cases and complex interactions.

- **Future Enhancements:**
    - Potential GUI implementation.

- **Bug Fixing:**
    - Address any remaining warnings or bugs as they arise.

## Known Issues

- None currently tracked