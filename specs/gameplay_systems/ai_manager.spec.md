# Specification: AI Manager (`AIManager`)

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The `AIManager` controls the behavior of non-player character (NPC) and enemy units during their respective phases. It analyzes the game state, considers each unit's assigned AI profile and objectives, evaluates potential actions (movement, attacks, captures, item use, etc.), and selects the best action according to predefined logic. It then uses the `ActionHandler` to execute the chosen action for each AI-controlled unit.

## 2. Responsibilities

-   Receive notification from the `TurnManager` or main game loop when an AI phase (Enemy or NPC) begins.
-   Iterate through all active units belonging to the current AI faction.
-   For each AI unit:
    -   Determine the unit's current AI profile/behavior (e.g., Charge, Guard, Escape, Target Specific Unit, Use Staff). This is often based on AI flags associated with the unit (Ref `research.md` Sec 6).
    -   Analyze the surrounding map state, potential targets, and objectives.
    -   Evaluate possible actions (Move, Attack, Capture, Use Item/Staff, Wait, etc.) based on the AI profile.
    -   Score potential actions/targets based on criteria like:
        -   Damage potential (prioritizing kills or high damage).
        -   Hit probability.
        -   Target vulnerability (low HP, low defense).
        -   Capture potential (prioritizing capturable units if AI allows, Ref `research.md` Sec 6).
        -   Threat level (prioritizing dangerous player units).
        -   Objective fulfillment (moving towards escape point, guarding a location).
        -   Self-preservation (healing if low HP, retreating).
    -   Select the highest-scoring valid action.
    -   Determine the optimal movement path to execute the chosen action (using `MovementSystem` for pathfinding).
-   Execute the chosen move and action sequence for the unit via the `ActionHandler`.
-   Handle specific Thracia AI behaviors like:
    -   Attempting capture instead of kill based on Con and target state (Ref `research.md` Sec 6).
    -   Trading items with nearby allies (especially after capturing a player unit, Ref `research.md` Sec 6).
    -   Using status staves aggressively (Ref `research.md` Sec 6).
    -   Responding to Leadership/Charisma bonuses.
-   Manage the sequence of AI unit actions within a phase (order determined by `TurnManager` or internal list).

## 3. Dependencies

-   `TurnManager`: To know the current phase and potentially the order of AI units.
-   `GameStateManager`: To query the overall game state, flags, and objectives.
-   `UnitSystem`: To get data for AI units and potential targets (stats, position, inventory, status, AI flags).
-   `MapSystem`: To get terrain data, check visibility (Fog of War), distances, line of sight.
-   `MovementSystem`: To find valid movement ranges and calculate optimal paths for potential actions.
-   `CombatSystem`: To get combat predictions (damage, hit, crit) for evaluating attack/capture actions.
-   `InventorySystem`: To check available items/staves and their uses for AI actions.
-   `ActionHandler`: To execute the final chosen action for the AI unit.
-   `DataProvider`: To fetch AI profile definitions, potentially target priorities, item/staff data.
-   `EventHandler`: AI actions might trigger events, or events might change AI behavior.

## 4. Core Concepts

-   **AI Profile/Flags:** Data associated with a unit defining its general behavior (e.g., `AI_CHARGE`, `AI_GUARD_POSITION`, `AI_PRIORITIZE_CAPTURE`, `AI_ESCAPE`). Thracia uses AI bytes for this (Ref `research.md` Sec 6).
-   **Action Evaluation:** The process of identifying all possible actions a unit can take from its current position and after potential moves.
-   **Targeting Logic:** Rules determining which enemy units are prioritized based on factors like threat, vulnerability, or capturability.
-   **Action Scoring:** Assigning a numerical score to potential actions based on their expected outcome (damage dealt, objective progress, risk involved).
-   **Pathfinding:** Determining the optimal sequence of tiles to move along to reach a desired position for an action (handled by `MovementSystem`).
-   **Decision Tree/State Machine:** The underlying logic structure that guides the AI's choice based on its profile and the current situation.

## 5. Pseudocode

```pseudocode
class AIManager:
    // Dependencies
    turnManager: TurnManager
    gameStateManager: GameStateManager
    unitSystem: UnitSystem
    mapSystem: MapSystem
    movementSystem: MovementSystem
    combatSystem: CombatSystem
    inventorySystem: InventorySystem
    actionHandler: ActionHandler
    dataProvider: DataProvider

    // TDD Anchor: test_ai_manager_initialization
    function initialize(dependencies...):
        // Store dependencies
        print("AIManager initialized.")

    // TDD Anchor: test_process_phase_iterates_units
    // Called when an AI phase starts
    function process_phase(phase: Phase):
        print("AI Manager processing phase: ", phase)
        ai_faction = phase.to_faction()
        active_ai_units = unitSystem.get_units_by_faction(ai_faction) # Get in activation order

        for unit_id in active_ai_units:
            # Check if unit can act (not dead, slept, etc.)
            if unitSystem.can_act(unit_id) and not unitSystem.has_acted(unit_id):
                process_unit_turn(unit_id)
            # Small delay maybe for visual pacing?

        # Signal phase end? Or TurnManager handles this.
        print("AI Manager finished phase: ", phase)

    // TDD Anchor: test_process_unit_turn_selects_best_action
    function process_unit_turn(unit_id: String):
        unit = unitSystem.get_unit(unit_id)
        ai_profile = unitSystem.get_ai_profile(unit_id) # Gets flags/behavior type
        print("Processing AI turn for: ", unit.name, " (AI: ", ai_profile, ")")

        possible_actions = find_possible_actions(unit_id, ai_profile)
        best_action = select_best_action(unit_id, possible_actions, ai_profile)

        if best_action:
            print("AI ", unit.name, " chose action: ", best_action.type, " Target: ", best_action.target_info)
            # Execute Move first if needed
            if best_action.move_path:
                 move_outcome = actionHandler.perform_action(unit_id, ActionType.MOVE, {'path': best_action.move_path})
                 if not move_outcome.success:
                      print("AI move failed for ", unit.name)
                      # Fallback? Maybe just wait?
                      actionHandler.perform_action(unit_id, ActionType.WAIT, {})
                      return

            # Execute the main action
            action_outcome = actionHandler.perform_action(unit_id, best_action.type, best_action.target_info)
            if not action_outcome.success:
                 print("AI action failed for ", unit.name, ": ", action_outcome.message)
                 # If action failed after move, unit might just wait there.
                 # Ensure unit is marked as acted even if action fails post-move.
                 if not unitSystem.has_acted(unit_id): # Check if move already marked acted
                      actionHandler.perform_action(unit_id, ActionType.WAIT, {}) # Explicit wait if action failed

        else:
            # No viable action found, just wait
            print("AI ", unit.name, " found no action, waiting.")
            actionHandler.perform_action(unit_id, ActionType.WAIT, {})

    // TDD Anchor: test_find_possible_actions_considers_range_and_targets
    function find_possible_actions(unit_id: String, ai_profile: AIProfile) -> List[PotentialAction]:
        actions = []
        unit = unitSystem.get_unit(unit_id)
        current_pos = unit.position
        movement_range = movementSystem.get_reachable_tiles(unit_id)

        # Consider actions from current position
        actions.extend(evaluate_actions_from_tile(unit_id, current_pos, ai_profile, is_current_pos=True))

        # Consider actions after moving
        for tile in movement_range:
            if tile != current_pos:
                actions.extend(evaluate_actions_from_tile(unit_id, tile, ai_profile, is_current_pos=False))

        # Add Wait action as a fallback
        actions.append(PotentialAction(type=ActionType.WAIT, score=0)) # Lowest priority

        return actions

    // TDD Anchor: test_evaluate_actions_from_tile_finds_attacks_captures_items
    function evaluate_actions_from_tile(unit_id: String, tile: Coordinate, ai_profile: AIProfile, is_current_pos: Boolean) -> List[PotentialAction]:
        evaluated_actions = []
        unit = unitSystem.get_unit(unit_id)
        potential_targets = unitSystem.get_units_in_potential_target_range(unit_id, tile) # Units reachable by weapons/staves from 'tile'

        # Evaluate Attack actions
        weapon = inventorySystem.get_equipped_weapon(unit_id)
        if weapon:
            for target_unit in potential_targets:
                 if unitSystem.is_enemy(unit.faction, target_unit.faction): # Check if valid target faction
                     distance = mapSystem.distance(tile, target_unit.position)
                     if distance in weapon.range:
                         # Check Line of Sight if needed
                         # Score the attack action
                         score = score_attack_action(unit_id, target_unit.id, tile, weapon, ai_profile)
                         move_path = None if is_current_pos else movementSystem.find_path(unit_id, tile)
                         evaluated_actions.append(PotentialAction(type=ActionType.ATTACK, target_info={'target_unit_id': target_unit.id}, score=score, move_path=move_path))

        # Evaluate Capture actions (if AI profile allows)
        if ai_profile.can_capture:
             weapon = inventorySystem.get_equipped_weapon(unit_id) # Need weapon for capture attempt
             if weapon:
                 for target_unit in potential_targets:
                      if unitSystem.is_enemy(unit.faction, target_unit.faction):
                          distance = mapSystem.distance(tile, target_unit.position)
                          if distance in weapon.range:
                              # Check if capture is possible (Con, target immunity, etc.)
                              if unitSystem.can_unit_capture_target(unit_id, target_unit.id):
                                   # Score the capture action (might be high priority for Thracia AI)
                                   score = score_capture_action(unit_id, target_unit.id, tile, ai_profile)
                                   move_path = None if is_current_pos else movementSystem.find_path(unit_id, tile)
                                   evaluated_actions.append(PotentialAction(type=ActionType.CAPTURE, target_info={'target_unit_id': target_unit.id}, score=score, move_path=move_path))

        # Evaluate Staff/Item actions (Heal, Status, Buff)
        items = inventorySystem.get_usable_items(unit_id)
        for item in items:
             item_data = dataProvider.get_item_data(item.type)
             if item_data.is_staff or item_data.is_usable_item:
                 # Find potential targets for this item/staff from 'tile'
                 item_targets = find_item_targets(unit_id, tile, item, item_data, potential_targets)
                 for item_target_id in item_targets:
                      # Score the item/staff action
                      score = score_item_action(unit_id, item_target_id, tile, item, item_data, ai_profile)
                      move_path = None if is_current_pos else movementSystem.find_path(unit_id, tile)
                      evaluated_actions.append(PotentialAction(type=ActionType.ITEM, target_info={'item_id': item.id, 'target_unit_id': item_target_id}, score=score, move_path=move_path))

        # Evaluate other actions based on AI profile (Escape, Guard, Interact)
        # ...

        return evaluated_actions

    // TDD Anchor: test_select_best_action_prioritizes_correctly
    function select_best_action(unit_id: String, possible_actions: List[PotentialAction], ai_profile: AIProfile) -> PotentialAction | None:
        if not possible_actions:
            return None

        # Filter out invalid actions (e.g., path not found for move-actions)
        valid_actions = [a for a in possible_actions if a.type == ActionType.WAIT or a.move_path is not None or a.is_current_pos_action] # Crude check

        # Sort actions by score (descending)
        valid_actions.sort(key=lambda a: a.score, reverse=True)

        # Apply AI profile specifics (e.g., Guard AI might prefer Wait if no threat)
        if ai_profile.behavior == AIBehavior.GUARD and not is_threatened(unit_id):
             # Prefer waiting unless a good opportunity arises
             wait_action = next((a for a in valid_actions if a.type == ActionType.WAIT), None)
             if valid_actions[0].score < ai_profile.guard_action_threshold: # Only act if score is high enough
                  return wait_action

        # Return the highest scoring valid action
        return valid_actions[0] if valid_actions else None


    // --- Scoring Functions --- (Placeholders, need detailed logic)

    // TDD Anchor: test_score_attack_action_considers_damage_hit_kill
    function score_attack_action(unit_id: String, target_id: String, from_tile: Coordinate, weapon, ai_profile: AIProfile) -> Float:
        # Use CombatSystem.predict_combat(...)
        prediction = combatSystem.predict_combat(unit_id, target_id, from_tile, is_capture=False)
        score = 0.0
        # Factors: Damage dealt, chance to hit, can it kill?, does target counter?, weapon triangle?
        score += prediction.expected_damage * prediction.hit_chance
        if prediction.target_hp_after <= 0:
             score += 50 # Bonus for kill
        # Penalty if attacker takes significant damage
        score -= prediction.expected_damage_taken * 0.5
        # Adjust based on AI profile (e.g., aggressive AI values damage more)
        return score

    // TDD Anchor: test_score_capture_action_prioritizes_capturable
    function score_capture_action(unit_id: String, target_id: String, from_tile: Coordinate, ai_profile: AIProfile) -> Float:
        # Capture is high priority in Thracia AI if possible
        # Use CombatSystem.predict_combat(..., is_capture=True)
        prediction = combatSystem.predict_combat(unit_id, target_id, from_tile, is_capture=True)
        score = 0.0
        if prediction.target_hp_after <= 0: # Can we secure the capture this turn?
             score += 100 # High base score for successful capture
             # Bonus if target has valuable items? (Needs inventory check)
             # score += inventorySystem.get_inventory_value(target_id) * 0.1
        # Penalty for damage taken during capture attempt (stats are halved)
        score -= prediction.expected_damage_taken * 1.0 # Higher penalty due to vulnerability
        return score

    // TDD Anchor: test_score_item_action_values_healing_and_status
    function score_item_action(unit_id: String, target_id: String, from_tile: Coordinate, item, item_data, ai_profile: AIProfile) -> Float:
        score = 0.0
        target_unit = unitSystem.get_unit(target_id)
        # Healing: Score based on HP restored, prioritize low HP allies
        if item_data.heals_hp:
             hp_missing = target_unit.max_hp - target_unit.current_hp
             hp_to_restore = min(hp_missing, item_data.heal_amount)
             score += hp_to_restore * 2 # Value healing
             if target_unit.current_hp / target_unit.max_hp < 0.3: # Critically wounded
                  score += 30
        # Status Staff: Score based on target impact (e.g., sleeping a strong enemy)
        elif item_data.inflicts_status:
             # Score based on target's threat level and status effect severity
             # score += unitSystem.get_threat_level(target_id) * dataProvider.get_status_severity(item_data.status_effect)
             score += 20 # Placeholder for status effects
        # Buffs: Score based on usefulness
        # ...
        return score

    // Helper to find targets for items/staves
    function find_item_targets(unit_id: String, from_tile: Coordinate, item, item_data, potential_targets) -> List[String]:
        targets = []
        item_range = item_data.range # e.g., 1 for Heal, 1-Mag/2 for status staves?
        unit_faction = unitSystem.get_unit(unit_id).faction

        for target_unit in potential_targets: # potential_targets are units near 'from_tile'
             distance = mapSystem.distance(from_tile, target_unit.position)
             if distance in item_range:
                 is_ally = not unitSystem.is_enemy(unit_faction, target_unit.faction)
                 # Check if item targets allies or enemies
                 if (item_data.targets_allies and is_ally) or \
                    (item_data.targets_enemies and not is_ally):
                      # Check specific need (e.g., ally needs healing, enemy is valid status target)
                      if item_data.heals_hp and target_unit.current_hp < target_unit.max_hp:
                           targets.append(target_unit.id)
                      elif item_data.inflicts_status and not unitSystem.has_status(target_unit.id, item_data.status_effect): # Check immunity?
                           targets.append(target_unit.id)
                      # Add other item target conditions
        return targets

end class

class AIProfile:
    behavior: AIBehavior # CHARGE, GUARD, ESCAPE, etc.
    target_priority: List[TargetType] # e.g., [LOW_HP, HIGH_DAMAGE, CAPTURABLE]
    can_capture: Boolean = False
    uses_items: Boolean = True
    retreat_hp_threshold: Float = 0.3 # Retreat if HP < 30%
    guard_action_threshold: Float = 20.0 # Score needed to act instead of wait when guarding

enum AIBehavior:
    CHARGE, GUARD_POSITION, GUARD_AREA, ESCAPE, TARGET_UNIT, FOLLOW_UNIT, HEALER_SUPPORT

enum TargetType:
    LOW_HP, HIGH_DAMAGE, CAN_KILL, CAPTURABLE, LEAST_DEFENSE, HIGHEST_THREAT, LORD

class PotentialAction:
    type: ActionType
    target_info: Dict = {} # e.g., {'target_unit_id': '...'}, {'item_id': '...'}
    score: Float = 0.0
    move_path: List[Coordinate] | None = None # Path to move before action
    is_current_pos_action: Boolean = False # If action is taken from current tile (no move)

```

## 6. Data Structures

-   `AIProfile`: Defines the behavior and priorities for an AI unit. Could be represented by flags/bytes as in the original game.
-   `AIBehavior` Enum: High-level behavior modes.
-   `TargetType` Enum: Categories for prioritizing targets.
-   `PotentialAction`: Represents a possible action evaluated by the AI, including its score and required movement.

## 7. Edge Cases & Considerations

-   **No Valid Actions:** What does the AI do if no beneficial action can be found? (Usually 'Wait').
-   **Complex Objectives:** AI might need to handle multi-step objectives (e.g., move to switch, then attack).
-   **Fog of War:** AI in Thracia often ignores Fog of War for targeting, but visibility checks might be needed for certain actions or for a more 'fair' AI implementation. The spec assumes AI has full map knowledge unless specified otherwise by profile.
-   **Pathfinding Failure:** If `MovementSystem` cannot find a path for the desired action, the AI needs a fallback.
-   **AI vs AI:** How do enemy units interact with NPC units? (Usually treat NPCs as enemies unless specific AI dictates otherwise).
-   **Performance:** Evaluating all possible moves and actions for every unit can be computationally expensive. Heuristics and optimizations (e.g., limiting search depth, pruning low-score actions early) are crucial.
-   **Stuck Units:** AI might get stuck if pathfinding is imperfect or map design creates traps.
-   **Item Management:** AI needs logic for choosing which weapon to equip, when to use vulneraries, etc. (Ref `research.md` Sec 6 confirms enemy self-healing).
-   **Trading:** Implementing AI trading (especially post-capture) adds complexity.

## 8. Future Enhancements

-   More sophisticated scoring functions considering buffs, debuffs, terrain, support bonuses, weapon triangle.
-   Support for coordinated AI tactics (e.g., forming defensive lines, focusing fire).
-   Learning/Adaptive AI (beyond scope of faithful recreation).
-   More diverse AI profiles and behaviors (e.g., specialized staff users, thieves targeting chests).
-   Better Fog of War handling for AI perception.
-   Implement AI trading logic.