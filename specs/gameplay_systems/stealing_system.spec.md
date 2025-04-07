# Specification: Stealing System (Thracia 776 Style)

## 1. Overview
This document outlines the pseudocode for the 'Stealing' mechanic, allowing specific units (Thieves) to take items directly from adjacent enemies under certain conditions, without engaging in capture. This mechanic is crucial for acquiring items and disarming enemies in Thracia 776.

## 2. Modules Involved
- `UnitSystem`: Manages unit stats (Speed, Con), calculated stats (Attack Speed), inventory, class, skills, fatigue, position, and actions.
- `ItemSystem`: Manages item properties (Weight, Name, equipped status).
- `MapSystem`: Provides adjacency checks.
- `ActionSystem`: Handles unit commands, turn flow, and action resolution.
- `AISystem`: Governs AI decision-making (though AI doesn't use player-style stealing from units).
- `UISystem`: Presents the 'Steal' command and item selection interface to the player.

## 3. Data Structures
- `Unit`:
    - `id`: Unique identifier
    - `name`: String
    - `stats`: { `speed`: Integer, `con`: Integer, ... }
    - `calculated_stats`: { `attack_speed`: Integer }
    - `inventory`: List[`Item`] (max size, e.g., 7)
    - `cls_name`: String (e.g., "Thief")
    - `skills`: List[String] (e.g., ["Steal"])
    - `fatigue`: Integer
    - `position`: Tuple(x, y)
    - `has_acted`: Boolean
- `Item`:
    - `id`: Unique identifier
    - `name`: String
    - `weight`: Integer
    - `is_equipped`: Boolean

## 4. Core Logic: Stealing Action

### 4.1. Initiating Steal (`ActionSystem::can_initiate_steal`)
Determines if the 'Steal' command should be available for the attacker against the defender.

```pseudocode
FUNCTION can_initiate_steal(attacker: Unit, defender: Unit): Boolean
  // TDD Anchor: test_can_initiate_steal_valid_thief
  // Must have the Steal skill (typically granted by Thief class)
  IF NOT attacker.has_skill("Steal") THEN
    RETURN FALSE
  ENDIF

  // TDD Anchor: test_can_initiate_steal_adjacent
  // Must be adjacent
  IF NOT MapSystem.is_adjacent(attacker.position, defender.position) THEN
    RETURN FALSE
  ENDIF

  // TDD Anchor: test_can_initiate_steal_has_stealable_items
  // Must have inventory space AND defender must have at least one item potentially stealable
  IF attacker.inventory IS FULL THEN
      RETURN FALSE
  ENDIF
  IF NOT defender_has_any_stealable_item(attacker, defender) THEN
    RETURN FALSE
  ENDIF

  RETURN TRUE
ENDFUNCTION

FUNCTION defender_has_any_stealable_item(attacker: Unit, defender: Unit): Boolean
  // TDD Anchor: test_defender_has_any_stealable_item_empty_inventory
  IF defender.inventory IS EMPTY THEN
    RETURN FALSE
  ENDIF

  // TDD Anchor: test_defender_has_any_stealable_item_check
  // Check if *at least one* item meets the core steal conditions (AS and Con/Weight)
  FOR item IN defender.inventory:
    // Check AS condition (Attacker AS > Defender AS)
    is_faster = attacker.calculated_stats.attack_speed > defender.calculated_stats.attack_speed
    // Check Weight condition (Item Weight <= Attacker Con)
    can_carry = item.weight <= attacker.stats.con

    IF is_faster AND can_carry THEN
      RETURN TRUE // Found at least one potentially stealable item
    ENDIF
  ENDFOR

  RETURN FALSE // No items meet the core conditions
ENDFUNCTION
```

### 4.2. Target Item Selection (`UISystem::present_steal_item_selection`)
Presents the list of stealable items to the player for selection.

```pseudocode
FUNCTION present_steal_item_selection(attacker: Unit, defender: Unit): Item or NULL
  // TDD Anchor: test_present_steal_item_selection_ui_filtering
  eligible_items = []
  is_faster = attacker.calculated_stats.attack_speed > defender.calculated_stats.attack_speed
  has_space = NOT attacker.inventory IS FULL

  // Pre-calculate conditions that apply to all items for efficiency
  IF NOT is_faster OR NOT has_space THEN
      // If basic conditions fail, no items are eligible (UI shouldn't have called this ideally)
      display_message("Cannot steal: Attacker not fast enough or inventory full.")
      RETURN NULL
  ENDIF

  FOR item IN defender.inventory:
    // Check specific item weight condition
    can_carry = item.weight <= attacker.stats.con
    IF can_carry THEN // Already checked speed and space
      add item to eligible_items // Include equipped items if they meet criteria
    ENDIF
  ENDFOR

  // TDD Anchor: test_present_steal_item_selection_ui_no_eligible
  IF eligible_items IS EMPTY THEN
    // This might happen if all items are too heavy, even if speed/space is okay
    display_message("No items light enough to steal.")
    RETURN NULL
  ENDIF

  // UI presents eligible_items to the player
  // Player selects an item or cancels
  // TDD Anchor: test_present_steal_item_selection_ui_display
  selected_item = UISystem.show_item_selection_menu("Select item to steal:", eligible_items) // Returns selected Item or NULL if cancelled

  RETURN selected_item
ENDFUNCTION
```

### 4.3. Steal Outcome (`ActionSystem::execute_steal`)
Performs the item transfer and applies side effects.

```pseudocode
FUNCTION execute_steal(attacker: Unit, defender: Unit, item_to_steal: Item): Boolean
  // TDD Anchor: test_execute_steal_pre_check
  // Double-check all conditions before modifying state
  is_faster = attacker.calculated_stats.attack_speed > defender.calculated_stats.attack_speed
  can_carry = item_to_steal.weight <= attacker.stats.con
  has_space = NOT attacker.inventory IS FULL

  IF NOT (is_faster AND can_carry AND has_space) THEN
    // Should not happen if UI filtered correctly, but safety check
    log_error("Execute steal called with invalid conditions.")
    display_message("Cannot steal this item.") // Generic failure message
    RETURN FALSE
  ENDIF

  // TDD Anchor: test_execute_steal_item_transfer
  // 1. Remove item from defender's inventory
  success_remove = defender.inventory.remove(item_to_steal)
  IF NOT success_remove THEN
      log_error("Failed to remove item from defender inventory during steal.")
      RETURN FALSE // Abort if item wasn't found (unexpected state)
  ENDIF

  // 2. If item was equipped, defender might need to auto-equip next best weapon
  // TDD Anchor: test_defender_auto_equip_after_steal
  IF item_to_steal.is_equipped THEN
    defender.try_auto_equip_weapon() // Assumes a method exists in UnitSystem
  ENDIF

  // 3. Add item to attacker's inventory
  item_to_steal.is_equipped = FALSE // Stolen items are never equipped immediately
  success_add = attacker.inventory.add(item_to_steal)
   IF NOT success_add THEN
      log_error("Failed to add item to attacker inventory during steal (inventory check failed?).")
      // Attempt to rollback? Put item back? Difficult state. Log and potentially fail gracefully.
      // For simplicity, assume pre-check `has_space` prevents this.
      RETURN FALSE
  ENDIF

  // TDD Anchor: test_execute_steal_fatigue_increase
  // 4. Apply fatigue cost to attacker
  attacker.fatigue += 1
  UnitSystem.update_fatigue_display(attacker) // Update UI if needed

  // TDD Anchor: test_execute_steal_action_consumed
  // 5. Mark action as consumed for the turn
  attacker.has_acted = TRUE

  // TDD Anchor: test_execute_steal_success_message
  UISystem.display_event_message(f"{attacker.name} stole {item_to_steal.name} from {defender.name}!")
  RETURN TRUE
ENDFUNCTION
```

### 4.4. Failure Conditions
Stealing fails, and the turn is typically *not* consumed (allowing the player to choose another action), if:
1.  `can_initiate_steal` returns `FALSE`: The 'Steal' command won't be available in the UI.
2.  `present_steal_item_selection` returns `NULL`: Either no items were eligible (e.g., all too heavy), or the player cancelled the selection. The player returns to the action menu.
3.  `execute_steal` returns `FALSE`: An unexpected error occurred during the state change (e.g., item vanished from inventory between selection and execution). Log error, return player to action menu.

*Pseudocode for Failure Handling (Conceptual - Integrated into Action Loop):*
```pseudocode
// In the main action selection logic for a unit:
WHEN player selects 'Steal' command targeting 'defender':
  IF ActionSystem.can_initiate_steal(player_unit, defender):
    selected_item = UISystem.present_steal_item_selection(player_unit, defender)
    IF selected_item IS NOT NULL:
      // Attempt the steal
      success = ActionSystem.execute_steal(player_unit, defender, selected_item)
      IF success:
        // Steal successful, action is consumed, end turn for this unit
        end_unit_turn(player_unit)
      ELSE:
        // Steal execution failed unexpectedly (e.g., internal error)
        // Do NOT consume action, return to menu
        UISystem.display_error("Steal failed unexpectedly.")
        return_to_action_menu(player_unit)
      ENDIF
    ELSE:
      // Player cancelled selection OR no eligible items were presented
      // Do NOT consume action, return to menu
      return_to_action_menu(player_unit)
    ENDIF
  ELSE:
    // Cannot initiate steal (UI should ideally prevent this state)
    UISystem.display_error("Cannot initiate steal.") // Should not be reachable if UI is correct
    return_to_action_menu(player_unit) // Return to menu without consuming action
  ENDIF
```

### 4.5. AI Considerations (`AISystem`)
- **No Player-Style Stealing:** Enemy AI in Thracia 776 does *not* use the 'Steal' command against player units. They cannot initiate this specific action flow.
- **Map Interaction:** Enemy Thieves have separate AI logic focused on interacting with map objects like chests or potentially scripted events involving items. This is outside the scope of the unit-to-unit 'Steal' command specified here.
- **No AI Pseudocode Needed:** No pseudocode is required within this spec for AI attempting to steal items *from another unit*.

## 5. TDD Anchors Summary
- `test_can_initiate_steal_valid_thief`: Verify only units with "Steal" skill return true.
- `test_can_initiate_steal_adjacent`: Verify non-adjacent units return false.
- `test_can_initiate_steal_has_stealable_items`: Verify returns true only if defender has at least one item meeting core AS/Con criteria AND attacker has space.
- `test_defender_has_any_stealable_item_empty_inventory`: Check returns false if defender inventory is empty.
- `test_defender_has_any_stealable_item_check`: Test various scenarios of items meeting/failing AS and Con/Weight checks.
- `test_can_initiate_steal_attacker_inventory_full`: Verify returns false if attacker inventory is full.
- `test_present_steal_item_selection_ui_filtering`: Test UI correctly lists only items meeting AS, Con/Weight, and inventory space criteria.
- `test_present_steal_item_selection_ui_no_eligible`: Test returns NULL if no items meet all criteria.
- `test_present_steal_item_selection_ui_display`: Verify UI shows correct item names, potentially weight/stats.
- `test_execute_steal_pre_check`: Test the internal safety check within execute_steal.
- `test_execute_steal_item_transfer`: Verify item is removed from defender and added to attacker inventory.
- `test_defender_auto_equip_after_steal`: Verify defender attempts to equip another weapon if their equipped one was stolen.
- `test_execute_steal_fatigue_increase`: Verify attacker's fatigue increases by exactly 1 on success.
- `test_execute_steal_action_consumed`: Verify attacker's `has_acted` flag is set to true.
- `test_execute_steal_success_message`: Verify appropriate feedback message is displayed.
- `test_steal_failure_no_action_consumed`: Verify that if steal fails at selection or execution, the unit's action is not consumed.

## 6. Edge Cases & Notes
- **Stealing vs Capture:** Emphasize these are distinct actions. Stealing doesn't involve combat or HP reduction.
- **Equipped Items:** Stealing equipped items is a core, powerful feature. Ensure the defender's state (potentially becoming unarmed) is handled correctly, including attempting to auto-equip a replacement.
- **Inventory Full:** This check is critical both for command availability (`can_initiate_steal`) and execution (`execute_steal`).
- **Simultaneous Conditions:** All conditions (Skill, Adjacency, AS > AS, Item Weight <= Con, Inventory Space) must be met.
- **No Counterattack:** Stealing is a non-combat action.
- **Fatigue:** Only successful steals incur fatigue. Failed attempts or cancellations do not.
- **Zero Weight Items:** Items with 0 weight should always pass the Con/Weight check.
- **Stat Changes Mid-Turn:** If defender's AS changes mid-turn before the steal action resolves (e.g., due to a status effect wearing off?), the check should use the current values at the time of execution. (This is unlikely in standard FE turn structure but worth considering).