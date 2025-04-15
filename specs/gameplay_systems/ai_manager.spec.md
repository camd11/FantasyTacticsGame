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
    action_type: Enum(MOVE, ATTACK, CAPTURE, USE_ITEM, USE_STAFF, WAIT, TRADE, ESCAPE, VISIT, TALK, INTERACT_MAP, STEAL) // Added INTERACT_MAP (Chests/Doors), STEAL
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
    -   Interacting with map objects (Chests, Doors).
    -   Stealing from adjacent enemies.
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
-   **FR-AI-016 (Thief Loot):** Units with this archetype shall prioritize identifying and moving towards reachable chests, locked doors (especially those blocking paths to objectives/chests), and enemies with stealable items. They will evaluate the utility of opening chests/doors or attempting to steal against standard actions like attacking or waiting, favoring loot acquisition and access. If no thief-specific targets are available or reachable, they should default to avoiding combat and moving towards map objectives or escape points, or waiting in a safe location.
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
        // TDD_ANCHOR: Test generation includes Interact Map actions (Chest/Door) if profile is THIEF_LOOT and targets exist
        // TDD_ANCHOR: Test generation includes Steal actions if profile is THIEF_LOOT and targets exist

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

        // Generate Interact Map actions (Chests/Doors) - Primarily for THIEF_LOOT
        if profile.behavior_archetype == THIEF_LOOT:
            map_interactables = find_map_interactables_from(unit, coord) // Finds adjacent chests/doors
            for interactable_coord, interactable_type in map_interactables:
                if (interactable_type == CHEST and unit.can_open_chest()) or \
                   (interactable_type == DOOR and unit.can_open_door()):
                    action = create_interact_map_action(unit, interactable_coord, interactable_type, move_coord)
                    possible_actions.append(action)
                    // TDD_ANCHOR: Test Interact Map action generation finds adjacent chests/doors for Thief

        // Generate Steal actions - Primarily for THIEF_LOOT
        if profile.behavior_archetype == THIEF_LOOT:
            steal_targets = find_steal_targets_from(unit, coord) // Finds adjacent enemies with stealable items
            for target_unit, stealable_item in steal_targets:
                if StealingSystem.can_steal(unit, target_unit, stealable_item): // Checks Speed, inventory space etc.
                    action = create_steal_action(unit, target_unit, stealable_item, move_coord)
                    possible_actions.append(action)
                    // TDD_ANCHOR: Test Steal action generation finds valid targets and items

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
                case INTERACT_MAP:
                    // Consider type (Chest > Door?), necessity (door blocking path?)
                    utility = calculate_interact_map_utility(action, unit, profile)
                    // TDD_ANCHOR: Test Interact Map utility is high for chests/blocking doors for Thief
                case STEAL:
                    // Consider item value, success chance, risk from target
                    utility = calculate_steal_utility(action, unit, profile)
                    // TDD_ANCHOR: Test Steal utility considers item value and success chance

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
    function calculate_interact_map_utility(...) -> Float: ...
    function calculate_steal_utility(...) -> Float: ...
    // ... etc ...

    function find_attack_targets_from(unit: Unit, coord: Coordinate) -> List[Unit]: ...
    function find_capture_targets_from(unit: Unit, coord: Coordinate) -> List[Unit]: ...
    function can_capture(unit: Unit, target: Unit) -> Boolean: ...
    function find_heal_targets_for_staff(...) -> List[Unit]: ...
    function find_status_targets_for_staff(...) -> List[Unit]: ...
    function find_map_interactables_from(unit: Unit, coord: Coordinate) -> List[(Coordinate, MapObjectType)]: ... // Finds adjacent chests/doors
    function find_steal_targets_from(unit: Unit, coord: Coordinate) -> List[(Unit, Item)]: ... // Finds adjacent units with stealable items

    function create_wait_action(unit: Unit) -> AIAction: ...
    function create_move_action(unit: Unit, target_coord: Coordinate) -> AIAction: ...
    function create_attack_action(...) -> AIAction: ...
    function create_capture_action(...) -> AIAction: ...
    function create_use_item_action(...) -> AIAction: ...
    function create_use_staff_action(...) -> AIAction: ...
    function create_escape_action(...) -> AIAction: ...
    function create_interact_map_action(...) -> AIAction: ...
    function create_steal_action(...) -> AIAction: ...

end class

### 5.1. Archetype-Specific Logic: HEAL_SUPPORT

This section details the specific logic applied when a unit's `AIProfile.behavior_archetype` is `HEAL_SUPPORT`. This logic primarily influences `evaluate_action_utility` and `filter_actions_by_archetype`.

```pseudocode
// --- Within AIManager class ---

function evaluate_action_utility(actions: List[AIAction], unit: Unit, profile: AIProfile):
    // ... (existing utility calculations) ...

    // Specific calculation for HEAL_SUPPORT archetype
    if profile.behavior_archetype == HEAL_SUPPORT:
        for action in actions:
            if action.action_type == USE_STAFF and action.target.is_ally():
                action.predicted_utility = calculate_ally_heal_utility(action, unit, profile)
                // TDD_ANCHOR: Healer calculates heal utility based on HP restored and target HP%
            elif action.action_type == ATTACK:
                 // Heavily penalize attacking unless necessary (e.g., self-defense)
                 // This might be better handled in filter_actions_by_archetype
                 action.predicted_utility *= 0.1 // Example penalty
            // Add utility for moving towards injured allies even if not in range yet? (Future enhancement)

function calculate_ally_heal_utility(action: AIAction, healer: Unit, profile: AIProfile) -> Float:
    target_ally = action.target_unit // Assuming action structure holds the target Unit object
    staff = action.item // Assuming action structure holds the staff Item object used

    base_utility = 100.0 // High base utility to prioritize healing

    // Calculate potential HP restored (consider staff power, healer magic, target resistance if applicable)
    potential_heal_amount = StaffSystem.predict_heal_amount(healer, staff, target_ally)
    actual_heal_amount = min(potential_heal_amount, target_ally.max_hp - target_ally.current_hp)

    // Bonus based on how much HP is missing (higher bonus for lower HP%)
    hp_percentage_missing = 1.0 - (target_ally.current_hp / target_ally.max_hp)
    missing_hp_bonus = hp_percentage_missing * 150.0 // Scale bonus significantly

    // Bonus for amount healed (healing 1 HP is less valuable than 20 HP)
    amount_healed_bonus = actual_heal_amount * 2.0

    // (Optional) Bonus for curing status effects if using Restore/etc.
    status_cure_bonus = 0.0
    if staff.cures_status() and target_ally.has_negative_status():
        // Prioritize dangerous statuses?
        status_cure_bonus = 50.0 // Flat bonus for curing any status
        // TDD_ANCHOR: Healer prioritizes Restore for specific status effects if enabled.

    // Penalty for staff uses remaining? (Lower utility if staff is almost broken?) - Optional
    staff_uses_penalty = 0.0
    # if staff.uses < 3: staff_uses_penalty = -20.0

    total_utility = base_utility + missing_hp_bonus + amount_healed_bonus + status_cure_bonus + staff_uses_penalty

    // TDD_ANCHOR: Healer utility increases significantly for low HP% targets.
    // TDD_ANCHOR: Healer utility scales with the amount of HP actually restored.

    return total_utility


function filter_actions_by_archetype(actions: List[AIAction], profile: AIProfile) -> List[AIAction]:
    if profile.behavior_archetype == HEAL_SUPPORT:
        heal_actions = [a for a in actions if a.action_type == USE_STAFF and a.target.is_ally()]
        self_heal_actions = [a for a in actions if a.action_type == USE_ITEM and a.target == unit] # Assuming target is unit for self-use

        # Priority 1: Heal Allies if possible
        if heal_actions:
             # Return only the best healing actions? Or all valid ones? Let's return all for now.
             # Maybe also include safe moves/waits if the heal isn't critical?
             # For simplicity: prioritize healing above all else if available.
             # TDD_ANCHOR: Healer selects healing action over low-utility attack/wait.
             return heal_actions

        # Priority 2: Self Heal if needed
        if self_heal_actions and unit.current_hp / unit.max_hp <= profile.heal_threshold_self:
             return self_heal_actions

        # Priority 3: Default Behavior (No healing needed/possible)
        # Avoid combat unless directly threatened? Or follow a simple pattern?
        # Option A: Minimal action - Wait or move to safest adjacent tile.
        # Option B: Move towards nearest ally group center.
        # Option C: Basic Guard behavior around current position.

        # Let's implement Option A: Prefer Wait/Safe Move, avoid attacks unless high utility (self-preservation)
        safe_actions = []
        for action in actions:
            if action.action_type == WAIT:
                safe_actions.append(action)
            elif action.action_type == MOVE:
                 # Evaluate safety of destination tile (e.g., terrain bonus, distance from enemies)
                 if MapSystem.is_tile_safe(action.move_target_coord, unit.faction): # Needs is_tile_safe logic
                     safe_actions.append(action)
            elif action.action_type == ATTACK:
                 # Only consider attack if utility is very high (e.g., finishing off a major threat, self-defense)
                 # The utility penalty in evaluate_action_utility helps here.
                 # We might still include high-utility attacks if no safe moves exist.
                 pass # Let utility decide if attack is worth it vs. just waiting

        # If safe moves/waits exist, prefer them. Otherwise, consider other actions based on utility.
        if safe_actions:
             # TDD_ANCHOR: Healer defaults to safe movement/waiting when no healing targets are available.
             return safe_actions
        else:
             # If no explicitly "safe" actions, return all non-heal actions for utility comparison
             # This allows attacking if cornered and waiting isn't safe either.
             return [a for a in actions if not (a.action_type == USE_STAFF and a.target.is_ally())]

    else:
        // Apply filters for other archetypes or return all actions
        return actions


// --- Helper functions potentially needed ---

function find_heal_targets_for_staff(unit: Unit, staff: Item, coord: Coordinate) -> List[Unit]:
    // Finds allies within staff range from 'coord' who are injured
    potential_targets = []
    allies = game_state.get_allied_units(unit.faction)
    staff_range = StaffSystem.get_staff_range(unit, staff) // e.g., 1 for Heal, 1-Mag/2 for Physic

    for ally in allies:
        if ally.current_hp < ally.max_hp:
            distance = MapSystem.calculate_distance(coord, ally.position)
            if distance <= staff_range:
                 potential_targets.append(ally)
                 // TDD_ANCHOR: Healer considers different staff ranges (Heal vs. Physic).

    // TDD_ANCHOR: Healer identifies allies below HP threshold within move+staff range. (Combined check needed in generate_potential_actions)
    return potential_targets

// Need to ensure generate_potential_actions correctly considers movement *then* staff range.
// The existing pseudocode seems to do this by checking actions at each reachable_tile.

```

### 5.2. Archetype-Specific Logic: THIEF_LOOT

This section details the specific logic applied when a unit's `AIProfile.behavior_archetype` is `THIEF_LOOT`. This logic influences action generation, utility evaluation, and potentially action filtering.

```pseudocode
// --- Within AIManager class ---

function generate_potential_actions(unit: Unit, profile: AIProfile) -> List[AIAction]:
    actions = []
    reachable_tiles = movement_system.get_reachable_tiles(unit)
    all_potential_targets = find_all_thief_targets(unit, profile) // Find all chests, doors, steal targets on map

    // 1. Generate standard actions (Move, Wait, Attack, etc.) as before
    // ... (call get_actions_at_coord for current pos and reachable tiles) ...
    // This already includes the generation logic added earlier for INTERACT_MAP and STEAL
    // if the target is adjacent to the evaluated 'coord'.

    // 2. Generate MOVE actions specifically towards non-adjacent thief targets
    for target_info in all_potential_targets:
        target_coord = target_info.coord // Coord of chest, door, or enemy unit
        target_type = target_info.type // CHEST, DOOR, STEAL_TARGET

        // Find path towards the target
        path = movement_system.find_path(unit.position, target_coord, unit)

        if path and len(path) > 1: // Path exists and target is not adjacent
            // Find the furthest reachable tile along the path
            best_move_coord = None
            for i in range(len(path) - 1, 0, -1):
                 tile = path[i]
                 if tile in reachable_tiles:
                     best_move_coord = tile
                     break

            if best_move_coord:
                 // Check if a simple move action to this tile already exists
                 move_exists = any(a.action_type == MOVE and a.move_target_coord == best_move_coord for a in actions)
                 if not move_exists:
                     action = create_move_action(unit, best_move_coord)
                     // Add context about *why* this move is being considered
                     action.context = {"target_type": target_type, "target_coord": target_coord}
                     actions.append(action)
                     // TDD_ANCHOR: Thief generates move actions towards distant chests/doors/steal targets.

    // 3. Always add WAIT action
    actions.append(create_wait_action(unit))

    return actions


function evaluate_action_utility(actions: List[AIAction], unit: Unit, profile: AIProfile):
    // ... (standard utility calculations for Attack, Heal, etc.) ...

    if profile.behavior_archetype == THIEF_LOOT:
        for action in actions:
            if action.action_type == INTERACT_MAP:
                action.predicted_utility = calculate_interact_map_utility(action, unit, profile)
            elif action.action_type == STEAL:
                action.predicted_utility = calculate_steal_utility(action, unit, profile)
            elif action.action_type == MOVE:
                // Boost utility if the move is towards a thief target
                if hasattr(action, 'context') and action.context.get("target_type") in [CHEST, DOOR, STEAL_TARGET]:
                    base_move_utility = calculate_move_utility(action, unit, profile) // Standard move utility (safety, terrain)
                    distance_to_target = MapSystem.calculate_distance(action.move_target_coord, action.context["target_coord"])
                    proximity_bonus = max(0, 10 - distance_to_target) * 10 // Higher bonus closer to target
                    action.predicted_utility = base_move_utility + proximity_bonus + 50 // Add flat bonus for moving towards goal
                    // TDD_ANCHOR: Thief move utility increases significantly when moving towards loot/steal targets.
                else:
                    // Standard move utility (likely low unless moving to safety)
                    action.predicted_utility = calculate_move_utility(action, unit, profile)
            elif action.action_type == ATTACK:
                 // Lower utility for attacking unless necessary (e.g., blocking enemy, self-defense)
                 base_attack_utility = calculate_attack_utility(action, unit, profile)
                 action.predicted_utility = base_attack_utility * 0.3 // Significantly reduce desire to fight
                 // TDD_ANCHOR: Thief attack utility is significantly lower than loot/steal actions unless critical.
            elif action.action_type == WAIT:
                 action.predicted_utility = calculate_wait_utility(action, unit, profile) * 0.5 // Prefer moving/acting


function calculate_interact_map_utility(action: AIAction, unit: Unit, profile: AIProfile) -> Float:
    target_coord = action.action_target // Coord of chest/door
    interact_type = action.context.get("interact_type") // CHEST or DOOR

    base_utility = 0.0
    if interact_type == CHEST:
        # Check if chest is already opened? MapSystem should handle this.
        # Assume higher value for chests
        base_utility = 200.0
        // TDD_ANCHOR: Thief utility for opening chests is very high.
    elif interact_type == DOOR:
        # Check if door is already open?
        # Check if door blocks path to objective/chest/escape?
        is_blocking = MapSystem.is_door_blocking_progress(target_coord, unit, profile) # Needs implementation
        if is_blocking:
            base_utility = 150.0 // High value if blocking progress
        else:
            base_utility = 50.0 // Lower value otherwise
        // TDD_ANCHOR: Thief utility for opening doors is high if blocking progress.

    # Consider risk? (e.g., opening door reveals strong enemies) - Future enhancement
    risk_penalty = 0.0

    return base_utility - risk_penalty


function calculate_steal_utility(action: AIAction, unit: Unit, profile: AIProfile) -> Float:
    target_unit = action.action_target_unit // The unit being stolen from
    item_to_steal = action.context.get("item") // The item being stolen

    base_utility = 100.0

    # Bonus based on item value (needs item valuation system)
    item_value_bonus = ItemSystem.get_item_value(item_to_steal) * 2.0 # Example scaling
    // TDD_ANCHOR: Thief steal utility scales with the value of the item.

    # Factor in success chance (based on Speed difference, skills?)
    success_chance = StealingSystem.predict_steal_chance(unit, target_unit, item_to_steal) # Needs implementation
    chance_bonus = success_chance * 100.0 # Max 100 bonus at 100% chance
    // TDD_ANCHOR: Thief steal utility scales with the predicted success chance.

    # Penalty based on risk (target retaliation?)
    # Predict counter-attack if steal fails? Or just general threat level?
    retaliation_risk = CombatSystem.predict_combat(target_unit, unit, target_unit.position).damage_taken # Damage unit would take if target attacked now
    risk_penalty = retaliation_risk * 1.5
    // TDD_ANCHOR: Thief steal utility decreases based on potential retaliation damage.

    # Check inventory space
    if not unit.inventory.has_space():
        return -1.0 // Cannot steal if inventory is full

    total_utility = base_utility + item_value_bonus + chance_bonus - risk_penalty

    return total_utility if success_chance > 0 else -1.0 // No utility if chance is 0


function filter_actions_by_archetype(actions: List[AIAction], profile: AIProfile) -> List[AIAction]:
    if profile.behavior_archetype == THIEF_LOOT:
        thief_actions = [a for a in actions if a.action_type in [INTERACT_MAP, STEAL]]
        move_to_thief_actions = [a for a in actions if a.action_type == MOVE and hasattr(a, 'context') and a.context.get("target_type") in [CHEST, DOOR, STEAL_TARGET]]

        # Priority 1: Perform Thief Actions if possible
        if thief_actions:
            # Also consider moving towards *other* thief targets if current ones aren't great
            # For now, prioritize immediate actions
            # TDD_ANCHOR: Thief prioritizes immediate Steal/Interact actions over moving if available.
            return thief_actions + move_to_thief_actions # Allow utility to decide between immediate action vs moving to better target

        # Priority 2: Move towards Thief Targets
        if move_to_thief_actions:
            # TDD_ANCHOR: Thief prioritizes moving towards loot/steal targets if no immediate action is possible.
            return move_to_thief_actions

        # Priority 3: Default Behavior (No thief targets reachable/exist)
        # Avoid combat, move towards objective/escape, or wait safely.
        safe_actions = []
        objective_moves = []
        for action in actions:
            if action.action_type == WAIT:
                 # Check safety of waiting tile
                 if MapSystem.is_tile_safe(unit.position, unit.faction):
                     safe_actions.append(action)
            elif action.action_type == MOVE:
                 # Check safety of destination
                 if MapSystem.is_tile_safe(action.move_target_coord, unit.faction):
                     # Check if move is towards objective/escape
                     if MapSystem.is_move_towards_objective(action.move_target_coord, unit, profile):
                         objective_moves.append(action)
                     else:
                         safe_actions.append(action)

        # Prefer moving towards objective > safe move > safe wait
        if objective_moves:
             # TDD_ANCHOR: Thief moves towards objective/escape if no loot targets available.
             return objective_moves
        elif safe_actions:
             # TDD_ANCHOR: Thief waits or moves safely if no loot targets and no objective path.
             return safe_actions
        else:
             # If nothing else, return all remaining actions (might include low-utility attacks if cornered)
             return [a for a in actions if a.action_type not in [INTERACT_MAP, STEAL] and not (a.action_type == MOVE and hasattr(a, 'context'))]


    else:
        // Apply filters for other archetypes or return all actions
        return actions


// --- Helper functions potentially needed ---

function find_all_thief_targets(unit: Unit, profile: AIProfile) -> List[TargetInfo]:
    // Scans the entire map for relevant chests, doors, and units with stealable items.
    // Returns a list of objects/structs containing target coordinates and type.
    targets = []
    # Find Chests
    chests = MapSystem.get_map_objects(type=CHEST, only_unopened=True)
    for chest_coord in chests:
        targets.append(TargetInfo(coord=chest_coord, type=CHEST))

    # Find Locked Doors
    doors = MapSystem.get_map_objects(type=DOOR, only_unopened=True)
    for door_coord in doors:
        targets.append(TargetInfo(coord=door_coord, type=DOOR))

    # Find Stealable Items on Enemies
    enemies = game_state.get_enemy_units(unit.faction)
    for enemy in enemies:
        stealable_items = StealingSystem.get_stealable_items(unit, enemy)
        if stealable_items:
             # For simplicity, just target the enemy unit. Utility calc can decide which item.
             # Or create a target for each item? Let's target the unit for now.
             targets.append(TargetInfo(coord=enemy.position, type=STEAL_TARGET, unit_id=enemy.id))

    // TDD_ANCHOR: Thief identifies all chests, locked doors, and enemies with stealable items on the map.
    return targets


function find_map_interactables_from(unit: Unit, coord: Coordinate) -> List[(Coordinate, MapObjectType)]:
    // Checks adjacent tiles to 'coord' for chests or doors.
    adjacent_interactables = []
    for neighbor_coord in MapSystem.get_adjacent_tiles(coord):
        map_object = MapSystem.get_object_at(neighbor_coord)
        if map_object:
             if map_object.type == CHEST and map_object.is_unopened():
                 adjacent_interactables.append((neighbor_coord, CHEST))
             elif map_object.type == DOOR and map_object.is_unopened() and map_object.is_locked():
                 adjacent_interactables.append((neighbor_coord, DOOR))
    return adjacent_interactables


function find_steal_targets_from(unit: Unit, coord: Coordinate) -> List[(Unit, Item)]:
    // Checks adjacent tiles to 'coord' for enemies with stealable items.
    adjacent_stealables = []
    enemies = game_state.get_enemy_units(unit.faction)
    for enemy in enemies:
        if MapSystem.calculate_distance(coord, enemy.position) == 1:
            stealable_items = StealingSystem.get_stealable_items(unit, enemy)
            for item in stealable_items:
                 adjacent_stealables.append((enemy, item))
    return adjacent_stealables


// Need definitions for MapSystem.is_door_blocking_progress, MapSystem.is_tile_safe,
// MapSystem.is_move_towards_objective, StealingSystem.get_stealable_items,
// StealingSystem.predict_steal_chance, ItemSystem.get_item_value

```

### 5.3. Archetype-Specific Logic: HEAL_SUPPORT
(Existing HEAL_SUPPORT content remains here)
...

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
-   **TDD_ANCHOR: Healer identifies allies below HP threshold within move+staff range.**
-   **TDD_ANCHOR: Healer prioritizes ally with lowest HP percentage.** (Handled by selecting max utility heal action)
-   **TDD_ANCHOR: Healer calculates heal utility based on HP restored and target HP%.**
-   **TDD_ANCHOR: Healer utility increases significantly for low HP% targets.**
-   **TDD_ANCHOR: Healer utility scales with the amount of HP actually restored.**
-   **TDD_ANCHOR: Healer selects healing action over low-utility attack/wait.**
-   **TDD_ANCHOR: Healer moves to the optimal tile to heal the chosen target.** (Implicitly handled by selecting best AIAction)
-   **TDD_ANCHOR: Healer defaults to safe movement/waiting when no healing targets are available.**
-   **TDD_ANCHOR: Healer considers different staff ranges (Heal vs. Physic).**
-   **TDD_ANCHOR: Healer prioritizes Restore for specific status effects if enabled.**
-   **TDD_ANCHOR: Test generation includes Interact Map actions (Chest/Door) if profile is THIEF_LOOT and targets exist.**
-   **TDD_ANCHOR: Test generation includes Steal actions if profile is THIEF_LOOT and targets exist.**
-   **TDD_ANCHOR: Test Interact Map action generation finds adjacent chests/doors for Thief.**
-   **TDD_ANCHOR: Test Steal action generation finds valid targets and items.**
-   **TDD_ANCHOR: Test Interact Map utility is high for chests/blocking doors for Thief.**
-   **TDD_ANCHOR: Test Steal utility considers item value and success chance.**
-   **TDD_ANCHOR: Thief generates move actions towards distant chests/doors/steal targets.**
-   **TDD_ANCHOR: Thief move utility increases significantly when moving towards loot/steal targets.**
-   **TDD_ANCHOR: Thief attack utility is significantly lower than loot/steal actions unless critical.**
-   **TDD_ANCHOR: Thief utility for opening chests is very high.**
-   **TDD_ANCHOR: Thief utility for opening doors is high if blocking progress.**
-   **TDD_ANCHOR: Thief steal utility scales with the value of the item.**
-   **TDD_ANCHOR: Thief steal utility scales with the predicted success chance.**
-   **TDD_ANCHOR: Thief steal utility decreases based on potential retaliation damage.**
-   **TDD_ANCHOR: Thief prioritizes immediate Steal/Interact actions over moving if available.**
-   **TDD_ANCHOR: Thief prioritizes moving towards loot/steal targets if no immediate action is possible.**
-   **TDD_ANCHOR: Thief moves towards objective/escape if no loot targets available.**
-   **TDD_ANCHOR: Thief waits or moves safely if no loot targets and no objective path.**
-   **TDD_ANCHOR: Thief identifies all chests, locked doors, and enemies with stealable items on the map.**

## 7. Open Questions / Future Considerations

-   How exactly are AI Profiles stored and assigned? (Unit data, chapter data?)
-   Detailed formulas for utility calculations need refinement.
-   Implementation of AI item trading requires careful design.
-   Handling complex objectives (e.g., multi-step goals).
-   Performance considerations for evaluating many actions on complex maps.
-   How to handle coordinated AI behavior (e.g., multiple units focusing fire)? Leadership stars provide stat boosts, but tactical coordination is harder.
-   Refining NPC AI behaviors (Follow Player, specific Talk interactions).