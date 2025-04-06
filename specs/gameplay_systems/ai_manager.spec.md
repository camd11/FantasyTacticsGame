# Specification: AI Manager (`ai_manager.spec.md`)

**Version:** 1.0
**Date:** 2025-04-05

## 1. Introduction

The AI Manager is responsible for controlling the behavior of non-player character (NPC) units, including both enemy (Red) and allied (Green) factions, during their respective phases. It determines the actions each AI-controlled unit will take based on their assigned AI profile, the current game state, map layout, and objectives. The design aims for modularity, allowing different AI behaviors (archetypes) to be defined and assigned, and testability to verify specific decision-making processes.

## 2. Dependencies

The AI Manager requires access to and interaction with the following systems:

-   **Game State Manager:** To query the current game state, including unit positions, stats, inventory, turn number, faction data, and map objectives.
-   **Unit System:** To get detailed information about specific units (stats, class, skills, inventory, status effects, AI profile).
-   **Map System:** To understand the map layout, terrain types, movement costs, line of sight, and locations of objectives or points of interest (e.g., villages, forts, escape points).
-   **Movement System:** To calculate valid movement ranges and paths for units.
-   **Combat System:** To predict combat outcomes (damage, hit chance, crit chance, doubling) for evaluating potential attack actions.
-   **Action Handler:** To execute the chosen actions (move, attack, capture, use item, wait, etc.).
-   **Data Provider:** To access unit AI profiles, potentially defined in chapter or unit data.

## 3. Data Structures

### 3.1. `AIProfile`

Defines the behavioral parameters for an AI unit. This could be stored within the Unit data or loaded per chapter/unit type.

```
AIProfile {
    behavior_archetype: Enum(CHARGE, GUARD, DEFEND_AREA, ESCAPE, HEAL_SUPPORT, CAPTURE_PRIORITY, THIEF_LOOT, BOSS_GUARD, FOLLOW_PLAYER, OBJECTIVE_ORIENTED) // Primary behavior mode
    aggression_level: Float // (0.0 to 1.0) Influences risk-taking
    target_preference: Enum(NEAREST, WEAKEST, HIGHEST_DAMAGE, HIGHEST_THREAT, CAPTURABLE, SPECIFIC_UNIT_TYPE) // How to prioritize targets
    movement_target: Coordinate or UnitID or None // Specific destination or unit to move towards/away from
    guard_radius: Integer or None // For GUARD/DEFEND_AREA: how far from the post to pursue
    heal_threshold_ally: Float // HP% below which allies are considered for healing
    heal_threshold_self: Float // HP% below which self-healing is prioritized
    retreat_threshold: Float // HP% below which retreat behavior might trigger
    capture_enabled: Boolean // Whether this unit will attempt captures
    use_status_staves: Boolean // Whether this unit will use offensive staves
    special_flags: List[String] // e.g., ["IGNORE_LOW_HIT_CHANCE", "PRIORITIZE_FLYERS", "TRADE_CAPTURED_ITEMS"]
}
```

### 3.2. `AIAction`

Represents a potential action sequence evaluated by the AI.

```
AIAction {
    unit_id: UnitID
    action_type: Enum(MOVE, ATTACK, CAPTURE, USE_ITEM, USE_STAFF, WAIT, TRADE, ESCAPE, VISIT, TALK)
    move_target_coord: Coordinate // Destination tile for movement
    action_target: Coordinate or UnitID or ItemID // Target of the action (enemy, ally, item, tile)
    predicted_utility: Float // Score representing the desirability of this action
    path: List[Coordinate] // The path taken to reach move_target_coord
}
```

## 4. Functional Requirements

### 4.1. Turn Processing

-   **FR-AI-001:** The `AIManager` shall iterate through all active units belonging to the current AI faction (Enemy or NPC) at the start of their phase.
-   **FR-AI-002:** For each active AI unit, the `AIManager` shall determine and execute the best possible action sequence (move + action, or just move/action/wait).
-   **FR-AI-003:** The order of AI unit processing within a phase should be deterministic (e.g., based on deployment order or internal list).

### 4.2. Behavior Determination

-   **FR-AI-004:** The `AIManager` shall retrieve the `AIProfile` associated with the current unit.
-   **FR-AI-005:** The unit's primary action selection logic shall be driven by the `behavior_archetype` defined in its `AIProfile`.

### 4.3. Action Evaluation & Selection

-   **FR-AI-006:** For a given unit, the `AIManager` shall generate a list of potential `AIAction` sequences available from its current position and within its movement range. This includes:
    -   Moving to different reachable tiles.
    -   Attacking reachable targets from potential move destinations.
    -   Capturing reachable and eligible targets.
    -   Using items (e.g., Vulneraries) on self.
    -   Using staves on valid targets (allies for healing, enemies for status).
    -   Waiting.
    -   Escaping (if applicable).
    -   Visiting/Talking (if applicable for NPCs).
-   **FR-AI-007:** Each potential `AIAction` shall be evaluated and assigned a `predicted_utility` score based on the unit's `AIProfile` and the current game state. Utility calculation should consider:
    -   Damage dealt / Kill potential (for offensive actions).
    -   Damage taken / Survival risk.
    -   Objective contribution (moving towards goal, seizing, escaping).
    -   Healing provided / Status inflicted.
    -   Capture success chance and value of captured items.
    -   Resource cost (item uses).
    -   Positioning benefits (terrain bonuses, blocking chokes).
-   **FR-AI-008:** The `AIManager` shall select the `AIAction` with the highest `predicted_utility` score. Ties can be broken deterministically (e.g., prioritize attack > capture > wait).
-   **FR-AI-009:** The selected `AIAction` shall be passed to the `Action Handler` for execution.

### 4.4. Specific AI Behaviors (based on `research.md`)

-   **FR-AI-010 (Charge):** Units shall prioritize moving towards and engaging the nearest/most threatening player units, considering damage output and survival.
-   **FR-AI-011 (Guard/Hold):** Units shall remain stationary unless a player unit enters their defined range (or a specified `guard_radius`). If a target enters range, they attack; they may pursue briefly but return to their post. Bosses on thrones typically use this.
-   **FR-AI-012 (Defend Area):** Similar to Guard, but may move within a larger designated area to intercept threats.
-   **FR-AI-013 (Escape):** Units shall prioritize moving towards the nearest designated escape point, avoiding combat unless necessary for survival or to clear a path.
-   **FR-AI-014 (Heal Support):** Units (typically with staves) shall prioritize healing allied units below the `heal_threshold_ally`. May also use restorative items/staves on self if below `heal_threshold_self`. Will attack if no healing targets are available/reachable.
-   **FR-AI-015 (Capture Priority):** Units with `capture_enabled` shall evaluate capture actions against eligible targets (considering Con difference, target HP, target armament). Capture utility should be weighed against kill utility, potentially prioritizing capture for disarming or if the target is weak/unarmed.
-   **FR-AI-016 (Thief Loot):** Units shall prioritize moving towards and interacting with chests or specific loot objectives. Once loot is obtained, behavior may switch to ESCAPE.
-   **FR-AI-017 (Retreat):** If HP drops below `retreat_threshold`, the unit may prioritize moving towards a safe location (e.g., fort, healer) over engaging enemies.
-   **FR-AI-018 (Status Staff Usage):** Units with `use_status_staves` enabled shall evaluate using offensive staves (Sleep, Silence, Berserk) against high-priority player targets (e.g., healers, mages, strong combat units), considering staff hit chance.
-   **FR-AI-019 (Item Trading):** AI units shall be capable of trading items with adjacent allies, particularly to distribute captured items or arm unarmed allies (requires specific flag/logic).

### 4.5. Targeting Logic

-   **FR-AI-020:** Target selection shall be configurable via `target_preference` in the `AIProfile`.
-   **FR-AI-021:** When evaluating targets, the AI shall use the `Combat System` to predict outcomes (damage, hit, crit, double).
-   **FR-AI-022:** The AI should consider target vulnerabilities (e.g., effectiveness bonuses, low HP, status effects, being unarmed).
-   **FR-AI-023:** The AI should factor in terrain bonuses/penalties for both itself and the target when evaluating actions.

### 4.6. Movement Logic

-   **FR-AI-024:** Movement paths shall be calculated using the `Movement System`, considering terrain costs and unit movement type.
-   **FR-AI-025:** Movement goals shall align with the `behavior_archetype` (e.g., move towards enemy, move towards escape point, move to healing target, hold position).
-   **FR-AI-026:** The AI should avoid moving into obviously dangerous positions unless aggression level is high or the potential reward is significant.

## 5. Pseudocode

```pseudocode
class AIManager:
    // Dependencies injected (GameStateManager, UnitManager, MapSystem, etc.)
    game_state: GameStateManager
    unit_manager: UnitManager
    map_system: MapSystem
    movement_system: MovementSystem
    combat_system: CombatSystem
    action_handler: ActionHandler

    function process_ai_turn(faction: Faction):
        // Get list of active units for the current AI faction
        ai_units = game_state.get_active_units_for_faction(faction)
        // Sort units for deterministic processing order
        sorted_units = sort_units_by_processing_order(ai_units)

        for unit in sorted_units:
            if unit.can_act(): // Check status effects like Sleep, etc.
                best_action = determine_unit_action(unit)
                if best_action is not None:
                    action_handler.execute_action(best_action)
                else:
                    // If no action found (should ideally always find at least WAIT)
                    action_handler.execute_action(create_wait_action(unit))
            // TDD_ANCHOR: Test AI skips turn if unit has status preventing action (Sleep, Petrify)

    function determine_unit_action(unit: Unit) -> AIAction or None:
        ai_profile = unit.get_ai_profile()
        potential_actions = generate_potential_actions(unit, ai_profile)
        // TDD_ANCHOR: Test generation of basic actions (Move, Wait, Attack nearby)

        if not potential_actions:
            return create_wait_action(unit)

        evaluate_action_utility(potential_actions, unit, ai_profile)
        // TDD_ANCHOR: Test utility calculation for simple attack vs wait

        best_action = select_best_action(potential_actions, ai_profile)
        // TDD_ANCHOR: Test selection prioritizes higher utility action

        return best_action

    function generate_potential_actions(unit: Unit, profile: AIProfile) -> List[AIAction]:
        actions = []
        reachable_tiles = movement_system.get_reachable_tiles(unit)

        // 1. Consider actions from current position
        actions.extend(get_actions_at_coord(unit, unit.position, profile))

        // 2. Consider actions after moving
        for coord in reachable_tiles:
            // Simulate move to coord (temporarily update unit position for evaluation)
            // Note: Need careful state management or predictive functions
            actions.extend(get_actions_at_coord(unit, coord, profile, move_coord=coord))
            // Add simple MOVE action to this coord
            actions.append(create_move_action(unit, coord))

        // 3. Always add WAIT action
        actions.append(create_wait_action(unit))

        // TDD_ANCHOR: Test generation includes Capture actions if profile allows and target is valid
        // TDD_ANCHOR: Test generation includes Heal actions if profile allows and target is valid
        // TDD_ANCHOR: Test generation includes Escape actions if profile allows and on escape map

        return actions

    function get_actions_at_coord(unit: Unit, coord: Coordinate, profile: AIProfile, move_coord: Coordinate = None) -> List[AIAction]:
        // Generate actions possible if the unit were at 'coord'
        // (Attack, Capture, Use Item, Use Staff, Visit, Talk)
        possible_actions = []

        // Generate Attack actions
        targets = find_attack_targets_from(unit, coord)
        for target_unit in targets:
            // Predict combat
            prediction = combat_system.predict_combat(unit, target_unit, coord) // Assumes unit is at coord
            action = create_attack_action(unit, target_unit, prediction, move_coord)
            possible_actions.append(action)
            // TDD_ANCHOR: Test attack action generation finds valid targets in range

        // Generate Capture actions (if profile allows)
        if profile.capture_enabled:
            capture_targets = find_capture_targets_from(unit, coord)
            for target_unit in capture_targets:
                 if can_capture(unit, target_unit): // Check Con, mount status, etc.
                    prediction = combat_system.predict_capture_combat(unit, target_unit, coord) // Uses halved stats
                    action = create_capture_action(unit, target_unit, prediction, move_coord)
                    possible_actions.append(action)
                    // TDD_ANCHOR: Test capture action generation checks Con and target eligibility

        // Generate Use Item actions (Self-heal)
        usable_items = unit.inventory.get_usable_items()
        for item in usable_items:
            if item.is_healing_item() and unit.current_hp < unit.max_hp:
                 // Check if healing is needed based on profile threshold
                 if unit.current_hp / unit.max_hp <= profile.heal_threshold_self:
                     action = create_use_item_action(unit, item, unit, move_coord)
                     possible_actions.append(action)
                     // TDD_ANCHOR: Test self-heal action generation checks HP threshold

        // Generate Use Staff actions (Heal Ally / Status Enemy)
        usable_staves = unit.inventory.get_usable_staves()
        for staff in usable_staves:
            if staff.is_healing_staff():
                heal_targets = find_heal_targets_for_staff(unit, staff, coord)
                for target_ally in heal_targets:
                     if target_ally.current_hp / target_ally.max_hp <= profile.heal_threshold_ally:
                         action = create_use_staff_action(unit, staff, target_ally, move_coord)
                         possible_actions.append(action)
                         // TDD_ANCHOR: Test ally heal action generation checks range and HP threshold
            elif staff.is_status_staff() and profile.use_status_staves:
                status_targets = find_status_targets_for_staff(unit, staff, coord)
                for target_enemy in status_targets:
                     action = create_use_staff_action(unit, staff, target_enemy, move_coord)
                     possible_actions.append(action)
                     // TDD_ANCHOR: Test status staff action generation finds valid enemy targets

        // Generate Visit/Talk actions (mainly for NPCs or specific AI)
        // ...

        return possible_actions


    function evaluate_action_utility(actions: List[AIAction], unit: Unit, profile: AIProfile):
        // Assign a score to each action based on profile and game state
        for action in actions:
            utility = 0.0
            switch action.action_type:
                case ATTACK:
                    // Consider damage dealt, kill potential, damage taken, hit chance, crit chance
                    // Factor in target priority (weakest, highest threat etc.)
                    utility = calculate_attack_utility(action, unit, profile)
                    // TDD_ANCHOR: Test attack utility increases with damage dealt and kill potential
                    // TDD_ANCHOR: Test attack utility decreases with damage taken
                case CAPTURE:
                    // Consider success chance, value of items obtained, risk
                    utility = calculate_capture_utility(action, unit, profile)
                    // TDD_ANCHOR: Test capture utility is high for unarmed/weak targets if enabled
                case USE_ITEM: // Self Heal
                    // Consider HP restored, current HP vs threshold
                    utility = calculate_self_heal_utility(action, unit, profile)
                case USE_STAFF: // Heal Ally / Status Enemy
                    if action.target.is_ally():
                        utility = calculate_ally_heal_utility(action, unit, profile)
                    else:
                        utility = calculate_status_utility(action, unit, profile)
                case MOVE:
                    // Consider proximity to objective/target, terrain safety, positioning
                    utility = calculate_move_utility(action, unit, profile)
                    // TDD_ANCHOR: Test move utility increases when moving towards objective/target
                case WAIT:
                    // Base utility, maybe higher if on defensive terrain or guarding
                    utility = calculate_wait_utility(action, unit, profile)
                case ESCAPE:
                    // High utility if objective is escape and near exit
                    utility = calculate_escape_utility(action, unit, profile)

            action.predicted_utility = utility


    function select_best_action(actions: List[AIAction], profile: AIProfile) -> AIAction or None:
        if not actions:
            return None

        // Filter actions based on archetype constraints (e.g., Guard AI won't choose distant move)
        valid_actions = filter_actions_by_archetype(actions, profile)

        if not valid_actions:
             // Fallback if filtering removes everything (e.g., find best wait/nearby action)
             valid_actions = actions // Or just return best wait?

        // Find action with max utility
        best_action = max(valid_actions, key=lambda a: a.predicted_utility)
        // TDD_ANCHOR: Test Guard AI selects Wait or Attack-in-range over moving far

        return best_action

    // --- Helper functions for utility calculation, target finding, etc. ---
    function calculate_attack_utility(...) -> Float: ...
    function calculate_capture_utility(...) -> Float: ...
    function calculate_move_utility(...) -> Float: ...
    function calculate_wait_utility(...) -> Float: ...
    // ... etc ...

    function find_attack_targets_from(unit: Unit, coord: Coordinate) -> List[Unit]: ...
    function find_capture_targets_from(unit: Unit, coord: Coordinate) -> List[Unit]: ...
    function can_capture(unit: Unit, target: Unit) -> Boolean: ...
    function find_heal_targets_for_staff(...) -> List[Unit]: ...
    function find_status_targets_for_staff(...) -> List[Unit]: ...

    function create_wait_action(unit: Unit) -> AIAction: ...
    function create_move_action(unit: Unit, target_coord: Coordinate) -> AIAction: ...
    function create_attack_action(...) -> AIAction: ...
    function create_capture_action(...) -> AIAction: ...
    function create_use_item_action(...) -> AIAction: ...
    function create_use_staff_action(...) -> AIAction: ...
    function create_escape_action(...) -> AIAction: ...

end class
```

## 6. TDD Anchors

-   **TDD_ANCHOR: Test AI skips turn if unit has status preventing action (Sleep, Petrify).**
-   **TDD_ANCHOR: Test generation of basic actions (Move, Wait, Attack nearby).**
-   **TDD_ANCHOR: Test utility calculation for simple attack vs wait.**
-   **TDD_ANCHOR: Test selection prioritizes higher utility action.**
-   **TDD_ANCHOR: Test generation includes Capture actions if profile allows and target is valid.**
-   **TDD_ANCHOR: Test generation includes Heal actions if profile allows and target is valid.**
-   **TDD_ANCHOR: Test generation includes Escape actions if profile allows and on escape map.**
-   **TDD_ANCHOR: Test attack action generation finds valid targets in range.**
-   **TDD_ANCHOR: Test capture action generation checks Con and target eligibility.**
-   **TDD_ANCHOR: Test self-heal action generation checks HP threshold.**
-   **TDD_ANCHOR: Test ally heal action generation checks range and HP threshold.**
-   **TDD_ANCHOR: Test status staff action generation finds valid enemy targets.**
-   **TDD_ANCHOR: Test attack utility increases with damage dealt and kill potential.**
-   **TDD_ANCHOR: Test attack utility decreases with damage taken.**
-   **TDD_ANCHOR: Test capture utility is high for unarmed/weak targets if enabled.**
-   **TDD_ANCHOR: Test move utility increases when moving towards objective/target (for Charge/Escape AI).**
-   **TDD_ANCHOR: Test Guard AI selects Wait or Attack-in-range over moving far.**
-   **TDD_ANCHOR: Test Retreat AI prioritizes moving away from threats when HP is low.**
-   **TDD_ANCHOR: Test Heal Support AI prioritizes healing allies over attacking.**
-   **TDD_ANCHOR: Test AI considers terrain bonuses/penalties in utility calculation.**
-   **TDD_ANCHOR: Test AI correctly uses Combat Prediction for action evaluation.**
-   **TDD_ANCHOR: Test AI handles full inventory when considering item-related actions (steal, trade).**
-   **TDD_ANCHOR: Test AI item trading logic (if implemented).**

## 7. Open Questions / Future Considerations

-   How exactly are AI Profiles stored and assigned? (Unit data, chapter data?)
-   Detailed formulas for utility calculations need refinement.
-   Implementation of AI item trading requires careful design.
-   Handling complex objectives (e.g., multi-step goals).
-   Performance considerations for evaluating many actions on complex maps.
-   How to handle coordinated AI behavior (e.g., multiple units focusing fire)? Leadership stars provide stat boosts, but tactical coordination is harder.
-   Refining NPC AI behaviors (Follow Player, specific Talk interactions).