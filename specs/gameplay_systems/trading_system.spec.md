# Specification: Trading System

**Version:** 1.0
**Date:** 2025-04-07

## 1. Overview

This document outlines the pseudocode specification for the Trading system in the Fantasy Tactics Game, based on mechanics observed in Fire Emblem: Thracia 776. The Trading system allows adjacent allied units (or a unit adjacent to an ally holding a captive) to exchange items between their inventories. Trading is a "free" action, meaning it does not consume the unit's primary action for the turn.

## 2. Dependencies

*   **Unit System:** Provides unit data (position, inventory, stats, status like `is_holding_captive`, `captive_unit`, `has_acted`).
*   **Item System:** Provides item data (weight, `is_tradeable` flag, `is_equipped` status).
*   **Map System:** Provides adjacency checks.
*   **Action System:** Manages unit actions per turn, integrates Trade as a free action.
*   **UI System:** Displays the trading interface.
*   **AI System:** Incorporates trading logic for non-player units.
*   **Capture System:** Trading interacts with captured units held by allies.

## 3. Constants

```pseudocode
MAX_INVENTORY_SIZE = 7 // Standard inventory limit per Thracia 776
```

## 4. Data Structures

```pseudocode
// Assumed from Unit System
Unit {
    ID unit_id
    Position position
    Inventory inventory // List of Item objects, size <= MAX_INVENTORY_SIZE
    Stats stats // Includes CON
    Boolean is_holding_captive
    Unit captive_unit // Reference to the captive unit, if any
    Boolean has_acted // Flag indicating if the unit performed a major action this turn
    Faction faction // Player, Enemy, Ally(NPC)
    // ... other unit properties
}

// Assumed from Item System
Item {
    ID item_id
    String name
    Integer weight
    Boolean is_tradeable // Flag: Can this item be traded? (Default: TRUE, FALSE for unique/story items)
    Boolean is_equipped
    Integer uses
    Integer max_uses
    // ... other item properties
}

Inventory {
    List<Item> items
    Function add(item)
    Function remove(item)
    Function remove_at(index)
    Function count()
    Function is_full() { RETURN count() >= MAX_INVENTORY_SIZE }
    // ... other inventory methods
}
```

## 5. Core Logic: TradingSystem Module

```pseudocode
MODULE TradingSystem

    // --- 5.1. Initiation ---

    // Checks if unit1 can initiate a trade with target_unit.
    // target_unit can be another allied unit or a captive held by an adjacent ally.
    FUNCTION can_initiate_trade(unit1: Unit, target_unit: Unit): Boolean
        // [TDD: Test adjacent allied units can trade]
        IF NOT MapSystem.are_adjacent(unit1.position, target_unit.position) THEN
            RETURN FALSE // [TDD: Test non-adjacent units cannot trade]

        // Check if target is an ally OR if target is a captive held by unit1
        is_target_ally = (target_unit.faction == unit1.faction)
        is_target_captive_held_by_unit1 = (unit1.is_holding_captive AND unit1.captive_unit.unit_id == target_unit.unit_id)

        IF NOT (is_target_ally OR is_target_captive_held_by_unit1) THEN
             // [TDD: Test enemy units cannot trade directly]
             // [TDD: Test unit cannot trade with captive held by non-adjacent unit]
            RETURN FALSE

        // Note: Thracia allows trade before or after moving, as long as no major action was taken.
        // ActionSystem should handle availability based on 'has_acted' if needed,
        // but the trade itself doesn't set has_acted = TRUE.
        // IF unit1.has_acted THEN RETURN FALSE // This check might be in ActionSystem instead

        RETURN TRUE
    END FUNCTION

    // Initiates the trade process, typically triggering the UI.
    // target_unit can be an adjacent ally or the captive held by unit1.
    FUNCTION initiate_trade(unit1: Unit, target_unit: Unit)
        IF NOT can_initiate_trade(unit1, target_unit) THEN
            PRINT "Cannot initiate trade."
            RETURN

        inventory1 = unit1.inventory
        inventory2 = target_unit.inventory // Assumes captive unit has an inventory accessible

        // [TDD: Test initiating trade opens the trade UI]
        UISystem.display_trade_screen(unit1, target_unit, inventory1, inventory2)
        // UI System will handle user input and call execute_trade upon confirmation.
    END FUNCTION


    // --- 5.2. Item Selection & Execution ---

    // Executes the item transfer based on UI selection.
    // unit1 is the initiator.
    // target_unit is the other participant (ally or captive).
    // index1: Index in unit1's inventory to give/swap (-1 if only receiving).
    // index2: Index in target_unit's inventory to receive/swap (-1 if only giving).
    FUNCTION execute_trade(unit1: Unit, target_unit: Unit, index1: Integer, index2: Integer): Boolean
        inventory1 = unit1.inventory
        inventory2 = target_unit.inventory

        item1 = NULL
        item2 = NULL

        // --- Validation ---
        IF index1 >= 0 THEN
            IF index1 >= inventory1.count() THEN RETURN FALSE // Invalid index
            item1 = inventory1.items[index1]
            IF item1.is_tradeable == FALSE THEN
                PRINT "Item " + item1.name + " cannot be traded."
                // [TDD: Test trading fails if trying to trade non-tradeable item (e.g., unique weapon)]
                RETURN FALSE
        END IF

        IF index2 >= 0 THEN
            IF index2 >= inventory2.count() THEN RETURN FALSE // Invalid index
            item2 = inventory2.items[index2]
            IF item2.is_tradeable == FALSE THEN
                PRINT "Item " + item2.name + " cannot be traded."
                // [TDD: Test trading fails if trying to trade non-tradeable item from target]
                RETURN FALSE
        END IF

        // Check inventory space if not a direct swap
        is_giving = (index1 >= 0 AND index2 == -1)
        is_receiving = (index1 == -1 AND index2 >= 0)
        is_swapping = (index1 >= 0 AND index2 >= 0)

        IF is_giving AND inventory2.is_full() THEN
            PRINT target_unit.name + "'s inventory is full."
            // [TDD: Test giving an item fails if recipient inventory is full]
            RETURN FALSE
        END IF

        IF is_receiving AND inventory1.is_full() THEN
            PRINT unit1.name + "'s inventory is full."
            // [TDD: Test receiving an item fails if initiator inventory is full]
            RETURN FALSE
        END IF

        // --- Execution ---

        // Handle unequipping if necessary BEFORE the swap/transfer
        IF item1 != NULL AND item1.is_equipped THEN
            UnitSystem.unequip_item(unit1, item1)
            // [TDD: Test trading equipped item unequips it from initiator]
        END IF
        IF item2 != NULL AND item2.is_equipped THEN
            UnitSystem.unequip_item(target_unit, item2)
             // [TDD: Test trading equipped item unequips it from target]
        END IF

        // Perform the transfer
        IF is_swapping THEN
            // [TDD: Test swapping two items between units]
            // [TDD: Test swapping item with captive unit]
            temp_item = inventory1.remove_at(index1)
            temp_item2 = inventory2.remove_at(index2)
            inventory1.add(temp_item2)
            inventory2.add(temp_item)
            PRINT "Swapped " + item1.name + " and " + item2.name + "."

        ELSE IF is_giving THEN
            // [TDD: Test giving an item from unit1 to unit2 with space]
            // [TDD: Test giving item to captive unit]
            item_to_give = inventory1.remove_at(index1)
            inventory2.add(item_to_give)
            PRINT "Gave " + item_to_give.name + " to " + target_unit.name + "."

        ELSE IF is_receiving THEN
            // [TDD: Test taking an item from unit2 to unit1 with space]
            // [TDD: Test taking item from captive unit]
            item_to_receive = inventory2.remove_at(index2)
            inventory1.add(item_to_receive)
            PRINT "Took " + item_to_receive.name + " from " + target_unit.name + "."

        ELSE // Both indices are -1, invalid operation
            RETURN FALSE
        END IF

        // Optional: Update UI after successful trade
        UISystem.refresh_inventories()

        RETURN TRUE
    END FUNCTION


    // --- 5.3. Action Cost ---

    // Trading does NOT consume the unit's main action.
    // This logic is primarily enforced by the ActionSystem.
    // When execute_trade returns TRUE, the ActionSystem should NOT set unit1.has_acted = TRUE.
    // The unit should remain selectable for other actions (Wait, Attack, Item use, etc.)
    // if they haven't performed one already this turn.
    // [TDD: Test unit can move, trade, then attack]
    // [TDD: Test unit can trade, then wait]
    // [TDD: Test unit can trade, then use item]
    // Canto interaction: If unit is mounted and performs Trade, CantoSystem should allow remaining movement.


    // --- 5.4. AI Considerations ---

    // Function called by AI system to determine if an AI unit should trade.
    FUNCTION ai_consider_trade(ai_unit: Unit)
        // Scenario 1: Distribute loot from captured player unit
        IF ai_unit.is_holding_captive AND ai_unit.captive_unit.faction == Faction.Player THEN
            captive_inventory = ai_unit.captive_unit.inventory
            IF captive_inventory.count() > 0 THEN
                // Find adjacent AI ally with space
                adjacent_allies = MapSystem.get_adjacent_units(ai_unit.position, Faction.Enemy) // Assuming AI is Enemy
                best_ally_target = NULL
                FOR EACH ally IN adjacent_allies:
                    IF NOT ally.inventory.is_full() THEN
                        best_ally_target = ally
                        BREAK // Take the first available ally for simplicity
                    END IF
                END FOR

                IF best_ally_target != NULL THEN
                    // Try to transfer the first valuable item (e.g., non-broken weapon)
                    item_to_transfer = NULL
                    index_in_captive = -1
                    FOR i FROM 0 TO captive_inventory.count() - 1:
                        IF captive_inventory.items[i].is_tradeable AND captive_inventory.items[i].value > 0 THEN // Assuming items have value
                           item_to_transfer = captive_inventory.items[i]
                           index_in_captive = i
                           BREAK
                        END IF
                    END FOR

                    IF item_to_transfer != NULL THEN
                        // AI takes item from captive first (into own potentially full inventory temporarily?)
                        // Simpler: Assume AI can directly facilitate transfer if adjacent
                        // Need clarification on exact mechanics: Can AI directly move item from captive to ally?
                        // Assuming simpler model: AI takes, then gives. Requires AI to have space.
                        IF NOT ai_unit.inventory.is_full() THEN
                            success_take = execute_trade(ai_unit, ai_unit.captive_unit, -1, index_in_captive)
                            IF success_take THEN
                                // Find the taken item in ai_unit's inventory
                                index_in_self = ai_unit.inventory.find_index(item_to_transfer.item_id)
                                IF index_in_self >= 0 THEN
                                     // [TDD: Test AI trades captured player items to allies]
                                    execute_trade(ai_unit, best_ally_target, index_in_self, -1)
                                    PRINT "AI " + ai_unit.name + " transferred captured item " + item_to_transfer.name + " to " + best_ally_target.name
                                    RETURN // AI performed a trade action
                                END IF
                            END IF
                        END IF
                    END IF
                END IF
            END IF
        END IF

        // Scenario 2: Arm self or ally
        IF UnitSystem.is_unarmed(ai_unit) THEN
            adjacent_allies = MapSystem.get_adjacent_units(ai_unit.position, Faction.Enemy)
            FOR EACH ally IN adjacent_allies:
                spare_weapon_index = ally.inventory.find_spare_weapon_index(ai_unit.weapon_proficiencies) // Find first usable spare weapon
                IF spare_weapon_index >= 0 THEN
                    // [TDD: Test unarmed AI receives weapon from adjacent ally]
                    success_receive = execute_trade(ally, ai_unit, spare_weapon_index, -1) // Ally gives weapon to ai_unit
                    IF success_receive THEN
                         PRINT "AI " + ai_unit.name + " received weapon from " + ally.name
                         // AI should equip the weapon if possible in a later step
                         RETURN // AI performed a trade action
                    END IF
                END IF
            END FOR
        END IF

        // Add other AI trading logic if needed (e.g., trading vulneraries)
    END FUNCTION

END MODULE
```

## 6. Integration Points

*   **Action System:**
    *   Must present "Trade" as an option when a unit is adjacent to a valid trade partner (ally or captive held by ally).
    *   Must correctly handle the "free action" nature of trading, allowing subsequent actions (Attack, Item, Wait, etc.) if the unit hasn't already performed one.
    *   Must integrate with Canto for mounted units trading.
*   **UI System:**
    *   Needs `display_trade_screen` to show two inventories side-by-side.
    *   Must handle user input for selecting items to swap/give/take.
    *   Must call `execute_trade` with the correct parameters upon confirmation.
    *   Should provide feedback on success or failure (e.g., "Inventory full", "Item cannot be traded").
*   **Unit System:**
    *   Must provide access to unit inventories, position, faction, captive status, and stats (especially CON for potential future weight checks, though not strictly needed for basic trade).
    *   Needs `unequip_item` functionality called by `execute_trade`.
*   **Item System:**
    *   Items need an `is_tradeable` flag.
    *   Items need an `is_equipped` status.
*   **Capture System:**
    *   `execute_trade` must correctly identify and access the inventory of a captive unit.
    *   AI trading logic relies heavily on the `is_holding_captive` status and accessing the `captive_unit`.
*   **AI System:**
    *   Must incorporate calls to `ai_consider_trade` during an AI unit's turn processing, likely before deciding on movement or attack if a trade opportunity exists (like distributing loot).

## 7. Edge Cases & Considerations

*   **Full Inventories:** Trade should only allow 1-for-1 swaps if both inventories are full. Giving or taking requires space. `execute_trade` handles this.
*   **Non-Tradeable Items:** Unique story items or personal weapons should be flagged `is_tradeable = FALSE`. `execute_trade` checks this.
*   **Equipped Items:** Trading an equipped item should automatically unequip it. `execute_trade` handles this.
*   **Trading with Captives:** Accessing the captive's inventory needs careful handling.
*   **AI Trade Priority:** How important is trading vs. attacking for the AI? The current pseudocode prioritizes distributing loot and arming unarmed units.
*   **Multi-Unit Trading Chain:** Thracia allows items to pass through multiple units in one turn via sequential trades. The current spec focuses on a single trade action; implementing chains would require the ActionSystem to allow multiple trades per turn if desired, or rely on sequential player actions. The "free action" nature supports this.