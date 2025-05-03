# Specification: Action Handler (`ActionHandler`)

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The `ActionHandler` processes requests for units to perform actions on the map. It validates the legality of requested actions based on the current game state, unit status, rules, and context (e.g., terrain, target eligibility). If valid, it executes the action, coordinating with other systems (like `CombatSystem`, `MovementSystem`, `InventorySystem`, `TurnManager`) to update the game state and trigger consequences (e.g., consuming movement, using items, gaining EXP, accumulating fatigue).

## 2. Responsibilities

-   Receive action requests (e.g., `perform_action(unit_id, action_type, target_data)`).
-   Validate the requested action against game rules and current state:
    -   Can the unit perform this action type? (e.g., Does the unit have the 'Steal' skill?)
    -   Is the unit in the correct state? (e.g., Not already acted, not asleep/berserk?)
    -   Is the target valid? (e.g., Correct range for attack, valid target for Talk?)
    -   Are prerequisites met? (e.g., Enough Con to Capture, Key for Door?)
-   Execute valid actions by invoking appropriate subsystems:
    -   `MovementSystem` for Move actions.
    -   `CombatSystem` for Attack and Capture actions.
    -   `InventorySystem` for Item use, Trade, Equip, Steal.
    -   `UnitSystem` for status changes, EXP gain, Dismount/Mount.
    -   `MapSystem` for interacting with terrain features (Visit, Seize, Open Door).
    -   `EventHandler` for triggering events linked to actions (e.g., Talk conversations).
-   Update unit state after action (e.g., mark as acted, consume movement).
-   Notify `TurnManager` to record fatigue for actions that incur it.
-   Handle Canto movement for mounted units after specific non-combat actions.
-   Return success/failure status and potentially results of the action (e.g., combat outcome).

## 3. Dependencies

-   `GameStateManager`: To query current game state (phase, turn, unit states).
-   `UnitSystem`: To get unit data (stats, status, skills, inventory, position, faction, action state).
-   `MapSystem`: To get terrain data, check tile occupancy, interact with map objects (doors, villages).
-   `MovementSystem`: To validate movement paths and ranges.
-   `CombatSystem`: To execute combat simulations (Attack, Capture).
-   `InventorySystem`: To manage item usage, trading, equipping, stealing.
-   `TurnManager`: To record fatigue and potentially check for Movement Star activation post-action.
-   `EventHandler`: To trigger action-related events (Talk, Visit, Seize).
-   `DataProvider`: To fetch rules, item data, class data, skill effects.

## 4. Core Concepts

-   **Action Request:** A command specifying the acting unit, the type of action, and any necessary target information (coordinates, target unit ID, item ID).
-   **Validation:** The process of checking if an action request is legal according to game rules and the current state.
-   **Execution:** The process of carrying out a validated action, involving calls to other systems.
-   **Consequences:** The effects of an action, such as state changes (HP loss, EXP gain, item use), status effects, fatigue gain, or triggering events.
-   **Canto:** The ability for mounted units to use remaining movement after certain non-combat actions.
-   **Free Actions:** Actions like Trading that do not consume the unit's main action for the turn.

## 5. Pseudocode

```pseudocode
class ActionHandler:
    // Dependencies
    gameStateManager: GameStateManager
    unitSystem: UnitSystem
    mapSystem: MapSystem
    movementSystem: MovementSystem
    combatSystem: CombatSystem
    inventorySystem: InventorySystem
    turnManager: TurnManager
    eventHandler: EventHandler
    dataProvider: DataProvider

    // TDD Anchor: test_action_handler_initialization
    function initialize(dependencies...):
        // Store dependencies
        print("ActionHandler initialized.")

    // TDD Anchor: test_perform_action_valid_and_invalid_requests
    // Main entry point for handling actions
    function perform_action(unit_id: String, action_type: ActionType, target_data: Dict): ActionOutcome
        // 1. Basic Validation
        unit = unitSystem.get_unit(unit_id)
        if not unit or unitSystem.has_acted(unit_id) or not unitSystem.can_act(unit_id): // e.g., asleep, berserk
            return ActionOutcome(success=False, message="Unit cannot act.")

        if gameStateManager.get_current_phase() != unit.faction.to_phase():
             return ActionOutcome(success=False, message="Not the unit's phase.")

        // 2. Action-Specific Validation & Execution
        outcome: ActionOutcome
        match action_type:
            case ActionType.MOVE:
                outcome = handle_move(unit_id, target_data['path'])
            case ActionType.WAIT:
                outcome = handle_wait(unit_id)
            case ActionType.ATTACK:
                outcome = handle_attack(unit_id, target_data['target_unit_id'])
            case ActionType.CAPTURE:
                outcome = handle_capture(unit_id, target_data['target_unit_id'])
            case ActionType.ITEM:
                outcome = handle_item(unit_id, target_data['item_id'], target_data.get('target_unit_id'))
            case ActionType.TRADE:
                // Note: Trade is often handled differently, might not consume the main action
                outcome = handle_trade(unit_id, target_data['partner_unit_id'], target_data['item_transfers'])
            case ActionType.RESCUE:
                outcome = handle_rescue(unit_id, target_data['target_unit_id'])
            case ActionType.DROP:
                outcome = handle_drop(unit_id, target_data['target_tile'])
            case ActionType.TAKE:
                outcome = handle_take(unit_id, target_data['partner_unit_id'])
            case ActionType.RELEASE:
                outcome = handle_release(unit_id) // Release captured enemy
            case ActionType.DISMOUNT:
                outcome = handle_dismount(unit_id)
            case ActionType.MOUNT:
                outcome = handle_mount(unit_id)
            case ActionType.VISIT:
                outcome = handle_visit(unit_id, target_data['target_tile'])
            case ActionType.SEIZE:
                outcome = handle_seize(unit_id, target_data['target_tile'])
            case ActionType.TALK:
                outcome = handle_talk(unit_id, target_data['target_unit_id'])
            case ActionType.STEAL:
                outcome = handle_steal(unit_id, target_data['target_unit_id'], target_data['item_id'])
            case ActionType.OPEN_DOOR:
                outcome = handle_open_door(unit_id, target_data['target_tile'], target_data['key_item_id'])
            // ... other actions like Dance, Staff ...
            case _:
                outcome = ActionOutcome(success=False, message="Unknown action type.")

        // 3. Post-Action Processing (if successful and action consumes turn)
        if outcome.success and action_type not in [ActionType.TRADE]: // Trade is free
            unitSystem.mark_unit_as_acted(unit_id)
            turnManager.record_action_fatigue(unit_id, action_type)

            // Check for Canto
            if unitSystem.can_canto(unit_id) and action_type in dataProvider.get_canto_eligible_actions():
                 remaining_movement = unitSystem.get_remaining_movement(unit_id)
                 if remaining_movement > 0:
                     // Allow further movement input, don't fully mark as acted yet?
                     // Or: Mark as acted, but allow a subsequent 'Canto Move' action.
                     // Let's assume Canto allows a follow-up move action.
                     gameStateManager.set_unit_state(unit_id, UnitState.CANTO_MOVE_PENDING)
                     print(unit.name, " can Canto.")
                 else:
                     // No remaining movement, fully end action
                     pass // Already marked as acted
            else:
                 // Normal action end
                 pass // Already marked as acted

            // Check for Movement Star AFTER action completes (unless Canto is pending?)
            // Timing needs clarification: Does star check happen before or after Canto? Assume after full action sequence.
            // If not Canto pending:
            if not gameStateManager.get_unit_state(unit_id) == UnitState.CANTO_MOVE_PENDING:
                 if turnManager.check_movement_star(unit_id):
                     // Unit state is reset by TurnManager, allow another action
                     unitSystem.mark_unit_as_not_acted(unit_id) // Revert acted status
                     gameStateManager.set_unit_state(unit_id, UnitState.IDLE) // Ready for new action

        return outcome

    // --- Action Specific Handlers ---

    // TDD Anchor: test_handle_move_valid_path
    function handle_move(unit_id: String, path: List[Coordinate]): ActionOutcome
        // Assumes movement validation (range, terrain cost) happened during path selection UI
        // MovementSystem might perform the move and update unit position
        success = movementSystem.execute_move(unit_id, path)
        if success:
            # Movement itself doesn't consume the action; subsequent action does.
            # This function might just update position, main perform_action handles marking acted later.
            # Or, if Move is the *only* action (Move then Wait implicitly):
            # unitSystem.mark_unit_as_acted(unit_id) # If move IS the action
            # turnManager.record_action_fatigue(unit_id, ActionType.MOVE) # If move causes fatigue (it doesn't)
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Invalid move path.")

    // TDD Anchor: test_handle_wait
    function handle_wait(unit_id: String): ActionOutcome
        // No specific validation needed beyond basic checks
        print(unitSystem.get_unit(unit_id).name, " waits.")
        # Consequences (mark acted, fatigue) handled by perform_action caller
        return ActionOutcome(success=True)

    // TDD Anchor: test_handle_attack_valid_target_in_range
    // TDD Anchor: test_handle_attack_invalid_target_out_of_range
    function handle_attack(unit_id: String, target_unit_id: String): ActionOutcome
        attacker = unitSystem.get_unit(unit_id)
        defender = unitSystem.get_unit(target_unit_id)
        if not defender or not unitSystem.is_targetable(defender):
            return ActionOutcome(success=False, message="Invalid target.")

        weapon = inventorySystem.get_equipped_weapon(unit_id)
        if not weapon:
            return ActionOutcome(success=False, message="No weapon equipped.")

        distance = mapSystem.distance(attacker.position, defender.position)
        if distance not in weapon.range:
            return ActionOutcome(success=False, message="Target out of range.")

        // Execute combat
        combat_result = combatSystem.execute_combat(unit_id, target_unit_id, is_capture=False)
        # Consequences handled by perform_action caller
        return ActionOutcome(success=True, data={'combat_result': combat_result})

    // TDD Anchor: test_handle_capture_valid_target_and_conditions
    // TDD Anchor: test_handle_capture_fails_con_check
    // TDD Anchor: test_handle_capture_fails_target_immune
    function handle_capture(unit_id: String, target_unit_id: String): ActionOutcome
        attacker = unitSystem.get_unit(unit_id)
        target = unitSystem.get_unit(target_unit_id)

        if not target or target.faction == Faction.PLAYER or target.faction == Faction.NPC:
            return ActionOutcome(success=False, message="Cannot capture allies.")
        if not unitSystem.is_targetable(target): # e.g., already captured
             return ActionOutcome(success=False, message="Invalid target.")

        // Check capture immunity (Mounted or 20 Con) - Ref research.md Sec 5.5
        if unitSystem.is_mounted(target.id) or target.con >= 20:
            return ActionOutcome(success=False, message="Target cannot be captured.")

        // Check Con requirement (Attacker Con > Target Con OR Attacker is Mounted) - Ref research.md Sec 5.5
        can_capture_by_con = attacker.con > target.con
        can_capture_by_mount = unitSystem.is_mounted(unit_id)
        if not (can_capture_by_con or can_capture_by_mount):
            return ActionOutcome(success=False, message="Constitution too low to capture.")

        weapon = inventorySystem.get_equipped_weapon(unit_id)
        if not weapon:
            return ActionOutcome(success=False, message="No weapon equipped for capture attempt.")

        distance = mapSystem.distance(attacker.position, target.position)
        if distance not in weapon.range:
            return ActionOutcome(success=False, message="Target out of range for capture attempt.")

        // Check if target is unarmed or incapacitated (auto-capture) - Ref research.md Sec 5.5
        if not inventorySystem.get_equipped_weapon(target_unit_id) or not unitSystem.can_act(target_unit_id):
             print("Target is unarmed/incapacitated. Auto-capturing.")
             unitSystem.capture_unit(unit_id, target_unit_id) # Attacker now holds target
             # Consequences handled by perform_action caller
             return ActionOutcome(success=True, data={'auto_capture': True})
        else:
            // Execute capture combat (with penalties)
            combat_result = combatSystem.execute_combat(unit_id, target_unit_id, is_capture=True)
            if combat_result.target_defeated:
                unitSystem.capture_unit(unit_id, target_unit_id) # Attacker holds target
                # Consequences handled by perform_action caller
                return ActionOutcome(success=True, data={'combat_result': combat_result})
            else:
                # Capture failed (target survived combat)
                # Consequences (fatigue for attempt) handled by perform_action caller
                return ActionOutcome(success=False, message="Capture attempt failed.", data={'combat_result': combat_result})

    // TDD Anchor: test_handle_item_use_vulnerary
    // TDD Anchor: test_handle_item_use_stat_booster
    // TDD Anchor: test_handle_item_fails_no_uses_left
    function handle_item(unit_id: String, item_id: String, target_unit_id: String = None): ActionOutcome
        item = inventorySystem.get_item(unit_id, item_id)
        if not item or item.uses <= 0:
            return ActionOutcome(success=False, message="Item not available or no uses left.")

        item_data = dataProvider.get_item_data(item.type)
        if not item_data.is_usable:
            return ActionOutcome(success=False, message="Item is not usable.")

        target_id = unit_id if item_data.targets_self else target_unit_id
        if not target_id:
             return ActionOutcome(success=False, message="Target required for this item.")

        # Validate target range if applicable
        # ...

        success = inventorySystem.use_item(unit_id, item_id, target_id)
        if success:
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Failed to use item.") # e.g., target invalid

    // TDD Anchor: test_handle_trade_success
    // TDD Anchor: test_handle_trade_partner_out_of_range
    // TDD Anchor: test_handle_trade_access_captive_inventory
    function handle_trade(unit_id: String, partner_unit_id: String, item_transfers: List): ActionOutcome
        unit = unitSystem.get_unit(unit_id)
        partner = unitSystem.get_unit(partner_unit_id)
        captive_target_id = None

        if not partner:
            # Check if partner_unit_id refers to a captive held by unit_id
            captive = unitSystem.get_captive_unit(unit_id)
            if captive and captive.id == partner_unit_id:
                 partner = captive # Target is the captive
                 captive_target_id = partner.id
                 print("Trading with captive: ", partner.name)
            else:
                 return ActionOutcome(success=False, message="Trade partner not found.")

        if not captive_target_id and mapSystem.distance(unit.position, partner.position) != 1:
             return ActionOutcome(success=False, message="Trade partner not adjacent.")

        # Perform trade logic via InventorySystem
        success = inventorySystem.execute_trade(unit_id, partner_unit_id, item_transfers, is_captive_trade=(captive_target_id is not None))

        if success:
            # Trade is a FREE action in Thracia - does not consume the turn.
            # No fatigue recorded here. No marking as acted.
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Trade failed.") # e.g., inventory full

    // TDD Anchor: test_handle_rescue_valid
    // TDD Anchor: test_handle_rescue_fails_con_check
    function handle_rescue(unit_id: String, target_unit_id: String): ActionOutcome
        rescuer = unitSystem.get_unit(unit_id)
        target = unitSystem.get_unit(target_unit_id)

        if not target or target.faction != Faction.PLAYER: # Can only rescue player units? Or NPCs too? Assume player only for now.
            return ActionOutcome(success=False, message="Invalid rescue target.")
        if mapSystem.distance(rescuer.position, target.position) != 1:
            return ActionOutcome(success=False, message="Target not adjacent.")
        if unitSystem.is_carrying(unit_id) or unitSystem.is_carried(target_unit_id):
             return ActionOutcome(success=False, message="Rescuer or target already involved in carry.")

        // Check Con requirement (Rescuer Con > Target Con) - Ref research.md Sec 5.5
        if rescuer.con <= target.con: # Needs refinement for mounted rescue rules if any
            return ActionOutcome(success=False, message="Constitution too low to rescue.")

        success = unitSystem.rescue_unit(unit_id, target_unit_id)
        if success:
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Rescue failed.")

    // TDD Anchor: test_handle_dismount_valid
    // TDD Anchor: test_handle_dismount_fails_not_mounted_or_indoors
    function handle_dismount(unit_id: String): ActionOutcome
        if not unitSystem.is_mounted(unit_id):
            return ActionOutcome(success=False, message="Unit is not mounted.")
        # Add check if already dismounted? UnitSystem should handle state.

        success = unitSystem.dismount_unit(unit_id)
        if success:
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Dismount failed.") # e.g., indoors already

    // TDD Anchor: test_handle_mount_valid
    // TDD Anchor: test_handle_mount_fails_indoors
    function handle_mount(unit_id: String): ActionOutcome
        unit = unitSystem.get_unit(unit_id)
        if not unitSystem.can_mount(unit_id): # Check if class is mountable
             return ActionOutcome(success=False, message="Unit class cannot mount.")
        if unitSystem.is_mounted(unit_id):
             return ActionOutcome(success=False, message="Unit is already mounted.")

        # Check if indoors - Ref research.md Sec 8
        if mapSystem.is_indoor(unit.position):
             return ActionOutcome(success=False, message="Cannot mount indoors.")

        success = unitSystem.mount_unit(unit_id)
        if success:
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Mount failed.")

    // TDD Anchor: test_handle_visit_village_success
    // TDD Anchor: test_handle_visit_invalid_tile
    function handle_visit(unit_id: String, target_tile: Coordinate): ActionOutcome
        unit = unitSystem.get_unit(unit_id)
        if unit.position != target_tile: # Must be on the tile
             # Or should target_tile be adjacent? Assume must be ON the tile.
             # Let's assume movement puts them ON the tile first.
             pass # Assume unit is already on target_tile

        tile_feature = mapSystem.get_feature_at(target_tile)
        if not tile_feature or tile_feature.type != FeatureType.VILLAGE or tile_feature.is_visited:
            return ActionOutcome(success=False, message="Cannot visit this location.")

        # Trigger event associated with the village
        event_triggered = eventHandler.trigger_map_event(EventType.VISIT, unit_id, target_tile)
        if event_triggered:
            mapSystem.mark_feature_as_visited(target_tile)
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            # Should always trigger if valid village? Maybe event has conditions.
            return ActionOutcome(success=False, message="Visit event failed.")

    // TDD Anchor: test_handle_seize_success
    // TDD Anchor: test_handle_seize_fails_not_lord
    // TDD Anchor: test_handle_seize_fails_wrong_tile
    function handle_seize(unit_id: String, target_tile: Coordinate): ActionOutcome
        unit = unitSystem.get_unit(unit_id)
        if not unitSystem.is_lord(unit_id):
            return ActionOutcome(success=False, message="Only the Lord can seize.")
        if unit.position != target_tile:
             return ActionOutcome(success=False, message="Must be on the seize point.")

        tile_feature = mapSystem.get_feature_at(target_tile)
        if not tile_feature or not tile_feature.is_seize_point:
            return ActionOutcome(success=False, message="Not a valid seize point.")

        # Trigger seize event (usually ends chapter)
        event_triggered = eventHandler.trigger_map_event(EventType.SEIZE, unit_id, target_tile)
        if event_triggered:
            # Chapter end logic likely handled by EventHandler or GameStateManager
            # Consequences (mark acted, fatigue) handled by perform_action caller (though chapter ends)
            return ActionOutcome(success=True, data={'chapter_end': True})
        else:
            return ActionOutcome(success=False, message="Seize event failed.")

    // TDD Anchor: test_handle_talk_success
    // TDD Anchor: test_handle_talk_fails_no_target_or_range
    // TDD Anchor: test_handle_talk_fails_no_conversation
    function handle_talk(unit_id: String, target_unit_id: String): ActionOutcome
        talker = unitSystem.get_unit(unit_id)
        target = unitSystem.get_unit(target_unit_id)

        if not target:
            return ActionOutcome(success=False, message="Talk target not found.")
        if mapSystem.distance(talker.position, target.position) != 1:
            return ActionOutcome(success=False, message="Talk target not adjacent.")

        # Check if a conversation exists between these two units
        if eventHandler.has_talk_event(unit_id, target_unit_id):
            event_triggered = eventHandler.trigger_talk_event(unit_id, target_unit_id)
            if event_triggered:
                # Consequences handled by perform_action caller
                return ActionOutcome(success=True)
            else:
                 return ActionOutcome(success=False, message="Talk event failed to trigger.") # Should not happen if has_talk_event was true
        else:
            return ActionOutcome(success=False, message="No conversation available.")

    // TDD Anchor: test_handle_steal_success
    // TDD Anchor: test_handle_steal_fails_skill_check
    // TDD Anchor: test_handle_steal_fails_speed_check
    // TDD Anchor: test_handle_steal_fails_con_check
    // TDD Anchor: test_handle_steal_fails_inventory_full
    function handle_steal(unit_id: String, target_unit_id: String, item_id: String): ActionOutcome
        thief = unitSystem.get_unit(unit_id)
        target = unitSystem.get_unit(target_unit_id)

        if not unitSystem.has_skill(unit_id, Skill.STEAL): # Or check class == Thief
             return ActionOutcome(success=False, message="Unit cannot steal.")
        if not target or target.faction == Faction.PLAYER: # Cannot steal from player/NPCs
             return ActionOutcome(success=False, message="Invalid steal target.")
        if mapSystem.distance(thief.position, target.position) != 1:
             return ActionOutcome(success=False, message="Target not adjacent.")
        if inventorySystem.is_inventory_full(unit_id):
             return ActionOutcome(success=False, message="Inventory full.")

        item_to_steal = inventorySystem.get_item(target_unit_id, item_id)
        if not item_to_steal:
             return ActionOutcome(success=False, message="Target does not have that item.")

        item_data = dataProvider.get_item_data(item_to_steal.type)
        item_weight = item_data.weight

        // Check Speed requirement (Thief AS > Target AS) - Ref research.md Sec 13
        thief_as = unitSystem.get_attack_speed(unit_id)
        target_as = unitSystem.get_attack_speed(target_unit_id)
        if thief_as <= target_as:
            return ActionOutcome(success=False, message="Thief not fast enough to steal.")

        // Check Con requirement (Thief Con >= Item Weight) - Ref research.md Sec 13
        if thief.con < item_weight:
            return ActionOutcome(success=False, message="Item too heavy to steal.")

        // Execute steal
        success = inventorySystem.transfer_item(target_unit_id, unit_id, item_id)
        if success:
            # Consequences handled by perform_action caller
            return ActionOutcome(success=True)
        else:
            return ActionOutcome(success=False, message="Steal transfer failed.") # Should not happen if checks passed

    // ... other handlers for Staff, Dance, Open Door, etc. ...

end class

enum ActionType:
    MOVE, WAIT, ATTACK, CAPTURE, ITEM, TRADE, RESCUE, DROP, TAKE, RELEASE,
    DISMOUNT, MOUNT, VISIT, SEIZE, TALK, STEAL, STAFF, DANCE, OPEN_DOOR
    // ...

class ActionOutcome:
    success: Boolean
    message: String = ""
    data: Dict = {} // Optional data like combat results

```

## 6. Data Structures

-   `ActionType` Enum: Defines all possible actions.
-   `ActionOutcome` Class: Standardized return type indicating success/failure and optional data.
-   `target_data` Dictionary: Flexible structure to pass necessary info for each action (e.g., `{ 'target_unit_id': 'enemy_soldier_1' }`, `{ 'item_id': 'vulnerary_1', 'target_unit_id': 'ally_fighter_2' }`).

## 7. Edge Cases & Considerations

-   **Action Interruption:** Can actions be interrupted (e.g., by traps, counter-attacks)? The handler assumes atomicity for now but might need refinement.
-   **AI Action Requests:** The AI Manager will also use this handler. Validation must apply equally to AI requests.
-   **Free Actions (Trade):** Trading doesn't consume the unit's main action. The `perform_action` logic correctly skips marking the unit as acted and recording fatigue for trades.
-   **Canto Timing:** The exact timing of Canto activation (before or after Movement Star check) needs clarification. Assumed here that Canto allows a follow-up move, and Movement Star check happens after the *entire* action sequence (including Canto move) is complete.
-   **Inventory Full:** Actions like Steal or receiving items from Trade/Visit must handle cases where the recipient's inventory is full.
-   **Target Eligibility:** Robust checks needed for target validity (e.g., cannot attack allies, cannot capture immune units, correct range).
-   **Stat Penalties (Capture/Rescue):** The `CombatSystem` handles capture penalties during combat. The `UnitSystem` needs to apply/remove carry penalties when a unit starts/stops carrying another.
-   **Implicit Actions:** Some actions might be implicit (e.g., moving onto a village tile might automatically trigger Visit if no other action is chosen). The current design assumes explicit action commands.

## 8. Future Enhancements

-   Implement handlers for remaining actions (Staff, Dance, etc.).
-   Refine Canto and Movement Star interaction timing.
-   Add support for multi-tile units if applicable.
-   Integrate checks for skills that modify actions (e.g., Pass skill allowing movement through enemies).
-   More detailed ActionOutcome data for UI feedback.