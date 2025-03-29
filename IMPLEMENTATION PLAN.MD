Implementation Plan: Thracia 776 Text-Based Simulation

Version: 1.0 (Following Iteration 10)
Date: 2023-10-27

1. Introduction

    1.1. Goal: To enhance the existing Python text-based Thracia 776 simulation (Iteration 10) by implementing missing core mechanics, improving AI, polishing existing features, and structuring the code for better maintainability, moving closer to a complete Chapter 1 experience.

    1.2. Current State: Functioning simulation with grid map, units, combat (incl. WT, Crit, PCC, Wrath, Vantage, Adept), inventory, capture, fatigue (accumulation + action denial), leadership stars, basic events (houses, reinforcements), escape objective, and heuristic-based AI.

2. Methodology

    2.1. Iterative Development: Continue implementing features in focused iterations or modules.

    2.2. Testing: Heavy emphasis on manual playtesting after each significant change due to lack of automated tests. Test core combat, AI decisions, skill triggers, fatigue effects, events, and commands.

    2.3. Version Control: Strongly recommend using Git for tracking changes, branching for new features, and merging upon successful testing.

3. Proposed Phases & Modules

Development can be broken down into these logical areas, which can be tackled somewhat independently or sequentially:

    Phase 1: Core Mechanic Polish & Refinement (High Priority)

    Phase 2: AI Enhancement (High Priority)

    Phase 3: Advanced Thracia Mechanics (Medium Priority)

    Phase 4: Event System & Chapter Flow (Medium Priority)

    Phase 5: UI/UX & Code Quality (Medium/Low Priority)

4. Detailed Tasks

(Priority: H=High, M=Medium, L=Low. Complexity: S=Simple, M=Medium, H=High)

Phase 1: Core Mechanic Polish & Refinement

    Task 1.1: Implement Fatigue Penalty (Stat Halving). (Priority: H, Complexity: M)

        Modify Unit effective stat properties (Str, Mag, Skl, Spd, Def, Res) to also check is_exhausted and return halved base stats if true.

        Update display_map and handle_info_command to clearly show when stats are halved due to fatigue.

        Test combat performance of exhausted units.

    Task 1.2: Fully Implement handle_info_command. (Priority: M, Complexity: S)

        Ensure all relevant data (base/eff stats, status, skills, fatigue, PCC, Ldr, items) is displayed clearly.

    Task 1.3: Fully Implement handle_targets_command. (Priority: M, Complexity: M)

        Ensure combat preview is accurate, including all bonuses/penalties (WT, Terrain, Ldr, PCC, potential skill effects like Wrath?).

        Consider adding predicted HP remaining.

    Task 1.4: Implement basic Weapon Triangle for Magic (Anima > Light > Dark > Anima). (Priority: L, Complexity: M)

        Requires adding Magic Weapon types.

        Update _resolve_attack WT logic.

    Task 1.5: Add "Effective Damage" (e.g., Bows vs Fliers, specific weapons). (Priority: L, Complexity: M)

        Requires adding unit types/attributes (e.g., 'Flier', 'Armor').

        Requires adding effective_vs property to Weapon.

        Modify damage calculation in _resolve_attack.

Phase 2: AI Enhancement

    Task 2.1: Implement A* Pathfinding for AI Movement. (Priority: H, Complexity: H)

        Replace find_best_move_towards_target's Manhattan distance heuristic.

        Create A* algorithm implementation that takes start, goal, terrain costs (Game.get_terrain_props), and unit movement type (future) into account.

        decide_enemy_action should use A* path cost to evaluate movement options when not attacking.

    Task 2.2: Improve AI Combat Prediction (predict_combat). (Priority: H, Complexity: M)

        Factor in critical hit chance/damage (average expected damage?).

        Factor in Adept chance/damage.

        Improve survival prediction (consider follow-ups more accurately).

    Task 2.3: Improve AI Scoring Heuristic (decide_enemy_action). (Priority: M, Complexity: M)

        Refine weights for damage, risk, terrain, skills based on playtesting.

        Consider target unit's threat level (e.g., prioritize units that can kill the AI unit).

        Consider "setup" moves (moving to a better position for next turn).

    Task 2.4: Implement AI Item Usage (Basic Healing). (Priority: M, Complexity: M)

        In decide_enemy_action, if HP is low and has a healing item, evaluate using it vs attacking/moving. Add a 'use_item' action type.

    Task 2.5: Implement AI Capture Attempts (Basic). (Priority: L, Complexity: H)

        AI needs to check CON, inventory space.

        Modify decide_enemy_action to consider capture as a high-priority action against valuable/weakened targets if conditions met. Requires predicting capture combat outcome.

Phase 3: Advanced Thracia Mechanics

    Task 3.1: Implement More Skills. (Priority: M, Complexity: Varies)

        Charge: Attack again if unit moved max distance? Modify combat loop. (M)

        Prayer: Chance to survive lethal blow with 1 HP based on Luck. Modify take_damage. (M)

        Nihil: Nullifies enemy combat skills. Requires skill checks within combat logic. (H)

        Others as desired.

    Task 3.2: Implement Movement Stars. (Priority: M, Complexity: H)

        Add Move Stars stat to Unit.

        At end of unit's action (set_acted), roll chance (Stars * 5%?).

        If successful, reset has_moved and has_acted (but not fatigue gain?). Requires careful loop control in handle_player_turn.

    Task 3.3: Implement Dismount/Mount. (Priority: L, Complexity: H)

        Add is_mounted state to Unit.

        Add specific mounted/dismounted classes/stats/weapon access.

        Implement dismount/mount commands. Requires significant stat/class system changes.

    Task 3.4: Implement Status Effects (Sleep, Berserk, Silence). (Priority: L, Complexity: H)

        Add status effect tracking to Unit.

        Modify can_act and AI logic based on status.

        Implement Staves/items that inflict statuses. Requires magic system first.

Phase 4: Event System & Chapter Flow

    Task 4.1: Expand Event System Triggers. (Priority: M, Complexity: M)

        Allow events triggered by reaching a coordinate, defeating a specific unit, etc.

    Task 4.2: Implement Dialogue Display. (Priority: M, Complexity: S)

        Add simple display_dialogue(message) function.

        Allow events in EventManager to trigger dialogue.

    Task 4.3: Implement Map Changes via Events. (Priority: L, Complexity: M)

        Allow events to modify Game.map_layout (e.g., opening doors, destroying walls).

    Task 4.4: Refine Chapter 1 Objective/Events. (Priority: M, Complexity: M)

        Add specific house messages/items from Thracia Ch 1.

        Tune reinforcement timing/composition.

        Potentially add event for defeating Weissman?

Phase 5: UI/UX & Code Quality

    Task 5.1: Refactor Code into Modules. (Priority: M, Complexity: M)

        Split Unit, Item, Game, EventManager, AI logic into separate files (units.py, items.py, etc.).

    Task 5.2: Improve Text UI Readability. (Priority: L, Complexity: S)

        Better formatting, spacing, potentially use curses for more control (optional).

    Task 5.3: Add Save/Load Functionality. (Priority: L, Complexity: H)

        Use pickle or JSON serialization to save/load game state (Game object and its contents).

    Task 5.4: Implement Basic Unit Tests. (Priority: M, Complexity: M)

        Add tests for core calculations (combat stats, damage, hit/crit chance) using unittest or pytest.

5. Testing Strategy

    Manual Playtesting: Essential after every feature implementation or significant change. Test different scenarios:

        Combat matchups (WT advantage/disadvantage, skills).

        Capture attempts (success/fail).

        Fatigue effects.

        AI behavior (targeting, movement, reaction to threats).

        Event triggers (houses, reinforcements).

        Commands and UI responsiveness.

    Scenario Testing: Set up specific unit/item configurations to test edge cases (e.g., low HP Vantage vs Wrath, Adept follow-up interactions).

    Unit Tests (Future): Implement unit tests for pure functions (e.g., stat calculations, distance) to catch regressions.

6. Version Control

    Use Git. Create branches for new features/phases. Merge into main branch only after thorough testing. Commit frequently with clear messages.