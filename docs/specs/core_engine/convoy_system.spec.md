# Convoy/Supply System Specification

## 1. Overview

The Convoy system provides a shared inventory accessible to the player's party, allowing storage of items not currently carried by individual units. This system facilitates item management between battles and offers limited access during combat scenarios.

## 2. Data Structure

*   **Storage:** The convoy's inventory will be stored within the main `GameState` object.
*   **Representation:** A `LIST` data structure named `GameState.convoy` will hold `Item` objects.
*   **Item Instances:** Each entry in the list represents a single, distinct instance of an item.
*   **Stacking:** Stackable items (e.g., healing potions) will be represented as multiple separate entries in the list. For example, three Vulneraries will occupy three slots in the convoy list. This simplifies management at the cost of potentially using more slots for numerous stackable items. Future revisions could implement quantity tracking within `Item` objects if needed.
    *   *TDD Anchor: `test_convoy_initialization_empty`*
    *   *TDD Anchor: `test_convoy_stores_item_objects`*
    *   *TDD Anchor: `test_convoy_stackable_items_as_separate_entries`*

```pseudocode
CLASS GameState
    Properties:
        // ... other game state properties (current_turn, player_units, enemy_units, map_data, etc.)
        convoy: LIST of Item // The central convoy storage

    Methods:
        // ... methods to manage game flow, units, etc.
        FUNCTION get_player_lord() -> Unit // Returns the main player character unit
        FUNCTION get_units_with_trait(trait_name: STRING) -> LIST of Unit // Finds units with specific capabilities (e.g., 'Supply')
END CLASS

CLASS Item
    Properties:
        item_id: STRING // Unique identifier (e.g., "iron_sword", "vulnerary")
        name: STRING // Display name (e.g., "Iron Sword", "Vulnerary")
        type: STRING // (e.g., "Weapon", "Consumable", "Accessory")
        description: STRING
        // ... other relevant properties (stats, effects, uses, value, weight, weapon_rank, etc.)
        is_unique: BOOLEAN // Flag for story-critical or non-depositable items (Default: FALSE)
        // Note: is_equipped status is managed by the Unit holding the item, not the item itself.
END CLASS

// Assumes Unit class exists with an inventory
CLASS Unit
    Properties:
        // ... other unit properties (name, class, stats, position, etc.)
        inventory: Inventory // Manages the unit's held items
        // ... potentially flags or commands like 'CanAccessSupply'

    Methods:
        FUNCTION is_item_equipped(item: Item) -> BOOLEAN // Checks if the given item is equipped by this unit
        FUNCTION has_command(command_name: STRING) -> BOOLEAN // Checks if unit possesses a specific command ability
END CLASS

CLASS Inventory // Represents a unit's limited item storage
    Properties:
        items: LIST of Item
        capacity: INTEGER // Max items the unit can hold

    Methods:
        FUNCTION add_item(item: Item) -> BOOLEAN
        FUNCTION remove_item_at(index: INTEGER) -> Item // Removes and returns item at index
        FUNCTION get_item_at(index: INTEGER) -> Item
        FUNCTION size() -> INTEGER
        FUNCTION is_full() -> BOOLEAN
END CLASS
```

## 3. Accessing the Convoy

Access rules depend on the current game phase.

*   **Battle Preparation Phase (`PREPARATION_PHASE`):**
    *   Full, unrestricted access is granted via the pre-battle menu/UI.
    *   Players can freely deposit and withdraw items between any party unit's inventory and the convoy.
    *   *TDD Anchor: `test_convoy_access_allowed_in_prep_phase`*
*   **During Battle Phase (`BATTLE_PHASE`):**
    *   Access is restricted and conditional.
    *   **Method 1: Lord Adjacency:** Any player unit directly adjacent (up, down, left, right) to the designated player 'Lord' unit can access the convoy.
    *   **Method 2: Supply Unit Adjacency (Optional):** If dedicated 'Supply' units exist (e.g., a specific class or unit with a 'Supply' trait), units adjacent to them can access the convoy.
    *   **Method 3: 'Supply' Command (Optional):** A specific 'Supply' command might be available to the Lord or other designated units. Executing this command opens the convoy interface. This might require the unit to be stationary or fulfill other conditions.
    *   **Action Cost:** Accessing the convoy (initiating deposit/withdraw) during the battle phase typically consumes the unit's action for the current turn. This requires integration with the `ActionSystem`.
    *   *TDD Anchor: `test_convoy_access_denied_in_battle_by_default`*
    *   *TDD Anchor: `test_convoy_access_via_lord_adjacency`*
    *   *TDD Anchor: `test_convoy_access_via_supply_unit_adjacency`*
    *   *TDD Anchor: `test_convoy_access_via_supply_command`*
    *   *TDD Anchor: `test_convoy_access_costs_action_in_battle`*

```pseudocode
FUNCTION can_access_convoy(unit: Unit, game_state: GameState) -> BOOLEAN
    // Check 1: Preparation Phase
    IF game_state.current_phase == GamePhase.PREPARATION THEN
        RETURN TRUE
    END IF

    // Check 2: Battle Phase Conditions
    IF game_state.current_phase == GamePhase.BATTLE THEN
        // Condition A: Adjacency to Lord
        lord_unit = game_state.get_player_lord()
        IF lord_unit IS NOT NULL AND is_adjacent(unit.position, lord_unit.position, game_state.map_data) THEN
            RETURN TRUE
        END IF

        // Condition B: Adjacency to Supply Units (if implemented)
        supply_units = game_state.get_units_with_trait('Supply')
        FOR supply_unit IN supply_units DO
            IF is_adjacent(unit.position, supply_unit.position, game_state.map_data) THEN
                RETURN TRUE
            END IF
        END FOR

        // Condition C: Unit has 'Supply' command (check might be implicit in command execution)
        // If access is *only* via command, this function might always return FALSE in battle,
        // and the command execution logic handles the access check.
        // Assuming adjacency is the primary passive access method here.

    END IF

    // Default: No access
    RETURN FALSE
END FUNCTION

FUNCTION is_adjacent(pos1: Position, pos2: Position, map_data: Map) -> BOOLEAN
    // Calculates Manhattan distance for grid maps
    dx = ABS(pos1.x - pos2.x)
    dy = ABS(pos1.y - pos2.y)
    RETURN (dx + dy) == 1
END FUNCTION

// Enum for Game Phases (example)
ENUM GamePhase
    PREPARATION
    BATTLE
    PLAYER_TURN
    ENEMY_TURN
    // ... other phases
END ENUM
```

## 4. Depositing Items (`Deposit`)

This action moves an item from a unit's inventory to the convoy.

*   **Trigger:** Player selects 'Deposit' action/command when convoy access is permitted. Player selects an item from the unit's inventory.
*   **Pre-conditions:**
    1.  `can_access_convoy(unit, game_state)` must be TRUE.
    2.  The selected item slot in the unit's inventory must not be empty.
    3.  The convoy must not be full (if limits apply).
*   **Restrictions:**
    1.  Cannot deposit an item that is currently equipped by the unit (`unit.is_item_equipped(item)`).
    2.  Cannot deposit items marked as `is_unique`.
*   **Process:**
    1.  Verify all pre-conditions and restrictions.
    2.  If valid, remove the item from `unit.inventory`.
    3.  Add the removed item to `game_state.convoy`.
    4.  Provide feedback (success message, UI update).
    5.  If in battle phase, potentially consume the unit's action (handled by `ActionSystem` or calling function).
*   **Failure:** If any check fails, display an appropriate error message (e.g., "Cannot deposit equipped item.", "Convoy is full.", "Cannot deposit unique item.") and do not modify inventories.
*   *TDD Anchor: `test_deposit_item_successful`*
*   *TDD Anchor: `test_deposit_item_fail_if_no_access`*
*   *TDD Anchor: `test_deposit_item_fail_if_equipped`*
*   *TDD Anchor: `test_deposit_item_fail_if_unique`*
*   *TDD Anchor: `test_deposit_item_fail_if_convoy_full`*
*   *TDD Anchor: `test_deposit_item_updates_unit_inventory`*
*   *TDD Anchor: `test_deposit_item_updates_convoy_inventory`*

```pseudocode
FUNCTION deposit_item(unit: Unit, item_index_in_unit_inventory: INTEGER, game_state: GameState) -> BOOLEAN
    // 1. Check Access
    IF NOT can_access_convoy(unit, game_state) THEN
        DISPLAY_ERROR("Convoy access not available.")
        RETURN FALSE
    END IF

    // 2. Validate Item Selection
    IF item_index_in_unit_inventory < 0 OR item_index_in_unit_inventory >= unit.inventory.size() THEN
        DISPLAY_ERROR("Invalid item slot selected.")
        RETURN FALSE
    END IF
    item_to_deposit = unit.inventory.get_item_at(item_index_in_unit_inventory)
    IF item_to_deposit IS NULL THEN
        DISPLAY_ERROR("Selected item slot is empty.") // Should ideally not happen if index is valid
        RETURN FALSE
    END IF

    // 3. Check Restrictions
    IF unit.is_item_equipped(item_to_deposit) THEN
        DISPLAY_ERROR("Cannot deposit an equipped item.")
        RETURN FALSE
    END IF
    IF item_to_deposit.is_unique THEN
        DISPLAY_ERROR("Cannot deposit this unique item.")
        RETURN FALSE
    END IF

    // 4. Check Convoy Limit
    IF convoy_is_full(game_state.convoy) THEN
        DISPLAY_ERROR("The convoy is full.")
        RETURN FALSE
    END IF

    // 5. Perform Transfer
    removed_item = unit.inventory.remove_item_at(item_index_in_unit_inventory)
    IF removed_item IS NOT NULL THEN // Ensure removal was successful
        game_state.convoy.add(removed_item)
        DISPLAY_MESSAGE(removed_item.name + " deposited into convoy.")
        // Trigger action cost if in battle (external system call)
        // game_state.action_system.consume_action(unit)
        RETURN TRUE
    ELSE
        // Should not happen with prior checks, indicates internal logic error
        DISPLAY_ERROR("Internal error: Failed to remove item from unit.")
        RETURN FALSE
    END IF
END FUNCTION
```

## 5. Withdrawing Items (`Withdraw`)

This action moves an item from the convoy to a unit's inventory.

*   **Trigger:** Player selects 'Withdraw' action/command when convoy access is permitted. Player selects an item from the convoy list.
*   **Pre-conditions:**
    1.  `can_access_convoy(unit, game_state)` must be TRUE.
    2.  The selected item slot in the convoy must not be empty.
    3.  The unit's inventory must not be full (`unit.inventory.is_full()`).
*   **Process:**
    1.  Verify all pre-conditions.
    2.  If valid, remove the item from `game_state.convoy` at the selected index.
    3.  Add the removed item to `unit.inventory`.
    4.  Provide feedback (success message, UI update).
    5.  If in battle phase, potentially consume the unit's action.
*   **Failure:** If any check fails, display an appropriate error message (e.g., "Unit inventory is full.") and do not modify inventories. If adding to the unit inventory fails unexpectedly after removal from convoy, attempt to add the item back to the convoy to maintain state consistency.
*   *TDD Anchor: `test_withdraw_item_successful`*
*   *TDD Anchor: `test_withdraw_item_fail_if_no_access`*
*   *TDD Anchor: `test_withdraw_item_fail_if_unit_inventory_full`*
*   *TDD Anchor: `test_withdraw_item_updates_unit_inventory`*
*   *TDD Anchor: `test_withdraw_item_updates_convoy_inventory`*
*   *TDD Anchor: `test_withdraw_item_handles_failed_add_to_unit`*

```pseudocode
FUNCTION withdraw_item(unit: Unit, item_index_in_convoy: INTEGER, game_state: GameState) -> BOOLEAN
    // 1. Check Access
    IF NOT can_access_convoy(unit, game_state) THEN
        DISPLAY_ERROR("Convoy access not available.")
        RETURN FALSE
    END IF

    // 2. Validate Item Selection
    IF item_index_in_convoy < 0 OR item_index_in_convoy >= game_state.convoy.size() THEN
        DISPLAY_ERROR("Invalid item selected from convoy.")
        RETURN FALSE
    END IF
    item_to_withdraw = game_state.convoy.get_item_at(item_index_in_convoy) // Peek first
     IF item_to_withdraw IS NULL THEN
        DISPLAY_ERROR("Selected convoy slot is empty.") // Should not happen
        RETURN FALSE
    END IF

    // 3. Check Unit Inventory Space
    IF unit.inventory.is_full() THEN
        DISPLAY_ERROR(unit.name + "'s inventory is full.")
        RETURN FALSE
    END IF

    // 4. Perform Transfer
    // Remove from convoy first
    removed_item = game_state.convoy.remove_item_at(item_index_in_convoy)
    IF removed_item IS NOT NULL THEN
        // Try adding to unit
        was_added = unit.inventory.add_item(removed_item)
        IF was_added THEN
            DISPLAY_MESSAGE(removed_item.name + " withdrawn by " + unit.name + ".")
            // Trigger action cost if in battle (external system call)
            // game_state.action_system.consume_action(unit)
            RETURN TRUE
        ELSE
            // Critical error: Failed to add to unit after removing from convoy. Attempt rollback.
            game_state.convoy.insert_at(item_index_in_convoy, removed_item) // Put it back where it was
            DISPLAY_ERROR("Internal error: Could not add item to unit inventory. Reverted convoy change.")
            RETURN FALSE
        END IF
    ELSE
        // Should not happen with prior checks
        DISPLAY_ERROR("Internal error: Failed to remove item from convoy.")
        RETURN FALSE
    END IF
END FUNCTION
```

## 6. Convoy Limits

*   **Mechanism:** A configurable constant `MAX_CONVOY_SIZE` defines the maximum number of item *slots* the convoy can hold.
*   **Value:** Can be set to a specific number (e.g., 100, 500, 999) or a value indicating unlimited capacity (e.g., -1 or `Infinity`).
*   **Enforcement:** The `convoy_is_full()` check is performed before any item is deposited.
    *   *TDD Anchor: `test_convoy_is_full_false_when_below_limit`*
    *   *TDD Anchor: `test_convoy_is_full_true_when_at_limit`*
    *   *TDD Anchor: `test_convoy_is_full_false_when_unlimited`*

```pseudocode
CONSTANT MAX_CONVOY_SIZE = 500 // Example: Limit of 500 item slots. Set to -1 for unlimited.

FUNCTION convoy_is_full(convoy: LIST of Item) -> BOOLEAN
    IF MAX_CONVOY_SIZE < 0 THEN // Check for unlimited flag
        RETURN FALSE
    END IF
    RETURN convoy.size() >= MAX_CONVOY_SIZE
END FUNCTION
```

## 7. Integration Points

*   **`GameState`**: Central hub holding the `convoy` list, current game phase, unit list, map data, and potentially references to other systems.
*   **`UnitSystem` / `Unit` Class**: Manages unit data, including `inventory`, position, equipped items, stats, and potentially special traits/commands (`Supply`).
*   **`ItemSystem` / `Item` Class**: Defines item properties (`is_unique`, `name`, `type`, etc.). Data source for item details.
*   **`ActionSystem`**: (If implemented) Manages unit actions per turn. Called by `deposit_item`/`withdraw_item` during battle to consume a unit's action.
*   **`UISystem`**: Handles rendering the convoy interface, unit inventories, item selection, displaying messages/errors, and capturing player input.
*   **`MapSystem` / `Map` Class**: Provides map data and spatial functions like `is_adjacent`.
*   **`SaveLoadSystem`**: Must serialize and deserialize the `GameState.convoy` list along with the rest of the game state.

## 8. Edge Cases & Considerations

*   **Item Stacking Implementation:** The current spec assumes one slot per item instance. If item stacking (quantity > 1 per slot) is implemented later, the `deposit_item` and `withdraw_item` logic will need significant changes to handle merging stacks and splitting stacks.
*   **Convoy Sorting/Filtering:** The UI layer should implement sorting (by name, type, value) and filtering capabilities for the convoy display to improve usability, especially with large inventories. This doesn't affect the core logic defined here.
*   **Performance:** For extremely large convoys (thousands of items), using a simple list might have performance implications for searching/sorting in the UI. Data structure optimization (e.g., dictionary grouped by item ID) could be considered if performance becomes an issue, but adds complexity.
*   **Concurrency (Multiplayer):** Not applicable for the current single-player scope. If multiplayer were added, locking mechanisms or transactional updates would be needed for shared convoy access.
*   **Error Handling:** Robust error messages should guide the player. Internal error handling (like the rollback in `withdraw_item`) should prevent data loss or inconsistent states.