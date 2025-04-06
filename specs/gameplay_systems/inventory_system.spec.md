# Specification: Inventory System

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Inventory System manages all aspects of items held by units and potentially a shared convoy. This includes adding, removing, equipping, using, and trading items, as well as tracking item durability and handling special item interactions like repair and the unique "Broken" state in Thracia 776. It interacts closely with the `GameStateManager` to modify unit inventories (`UnitState.inventory`) and the `DataProvider` to retrieve static item properties (`ItemData`).

## 2. Functional Requirements

### 2.1. Inventory Structure
    - Each unit possesses an inventory represented by `UnitState.inventory`, a list of `ItemInstance` objects (Ref: `GameStateManager`).
    - Thracia 776 typically limits unit inventory size (e.g., 7 items). This limit should be enforced.
    - Each `ItemInstance` stores the `item_id` (linking to `DataProvider.ItemData`) and `current_durability`.
    - `UnitState` stores the `equipped_weapon_index`, pointing to the item in the inventory list currently equipped (-1 if none).

### 2.2. Item Management
    - **Adding Items:**
        - Provide functions to add an `ItemInstance` to a unit's inventory.
        - Handle cases like receiving items from villages, chests, events, or trades.
        - Ensure inventory capacity is not exceeded.
        - `add_item_to_inventory(unit_id, item_id, durability=None)`: Adds item, uses max durability from `DataProvider` if not specified. Returns success/failure.
    - **Removing Items:**
        - Provide functions to remove an item from a unit's inventory (by index or `ItemInstance`).
        - Handle dropping items (item is lost).
        - Handle trading items away (item moves to another inventory).
        - `remove_item_from_inventory(unit_id, item_index)`: Removes item. Returns the removed `ItemInstance` or null.
    - **Equipping Items:**
        - Provide a function `equip_item(unit_id, item_index)` to set `UnitState.equipped_weapon_index`.
        - Validate that the item at `item_index` is equippable (is a weapon).
        - Validate that the unit meets the weapon rank requirement (`UnitState.weapon_ranks` vs `ItemData.required_rank`).
        - Unequip any previously equipped weapon.
    - **Unequipping Items:**
        - Provide a function `unequip_item(unit_id)` to set `UnitState.equipped_weapon_index` to -1.

### 2.3. Item Usage
    - **Using Consumables:**
        - Provide `use_consumable_item(unit_id, item_index, target_id=None)` function.
        - Retrieve item effects from `DataProvider.get_item_data(item_id).effects`.
        - Apply effects (e.g., healing via `GameStateManager.apply_healing`, stat boosts via `GameStateManager.apply_stat_boost`, status cure via `GameStateManager.remove_status_effect`).
        - Decrement durability via `decrement_item_durability`. If durability reaches 0, remove the item from inventory.
        - Consumes the unit's action (`GameStateManager.set_unit_acted(unit_id)`).
    - **Using Keys:**
        - Provide `use_key(unit_id, item_index, target_tile)` function.
        - Check if the target tile contains a locked door/chest compatible with the key type.
        - Update the map state (`GameStateManager.set_object_state(target_tile, OPENED)`).
        - Decrement key durability via `decrement_item_durability`. If durability reaches 0, remove the item.
        - Consumes the unit's action.
    - **Using Staves:** (Handled primarily by Combat System for targeting/accuracy, but inventory updates happen here)
        - Decrement staff durability via `decrement_item_durability` after successful use.
        - Handle staff breaking.

### 2.4. Durability and Breaking
    - Provide `decrement_item_durability(unit_id, item_index, amount=1)` function.
    - Reduces `ItemInstance.current_durability`.
    - **Breaking:** If `current_durability` reaches 0:
        - Retrieve `ItemData` from `DataProvider`.
        - If the item is repairable (most weapons/staves in Thracia):
            - Replace the `ItemInstance` with a "Broken" version (e.g., `item_id = 'BROKEN_SWORD'`, durability = 0 or N/A). (Ref: `research.md`, Sec 13). Need specific "Broken" item IDs in `DataProvider`.
        - If the item is not repairable (e.g., consumables, keys), remove the `ItemInstance` from inventory.
        - Log the item breaking event.
        - Ensure the unit's `equipped_weapon_index` is updated if the equipped item broke.

### 2.5. Repairing Items
    - Provide `repair_item(unit_id, item_index)` function (typically called when a Repair Staff is used).
    - Check if the item at `item_index` is a "Broken" item or a damaged repairable item.
    - Retrieve the original `item_id` from the broken item's data or determine the base item type.
    - Retrieve the original `max_durability` from `DataProvider`.
    - Replace the `ItemInstance` with a fully repaired version (`item_id` = original ID, `current_durability` = `max_durability`). (Ref: `research.md`, Sec 4).

### 2.6. Trading
    - Provide `initiate_trade(unit1_id, unit2_id)` function.
        - Verify units are adjacent (`MapSystem`).
        - Verify `unit2` is an ally OR `unit1` is carrying `unit2` as a captive (Ref: `research.md`, Sec 4, 5.5).
        - Return the inventories of both units (and the captive's inventory if applicable) for UI display.
    - Provide `execute_trade(unit1_id, unit2_id, item_transfers)` function.
        - `item_transfers` specifies which items move between `unit1`, `unit2`, and potentially a captive held by `unit1`.
        - Validate the proposed transfers (inventory limits, item existence).
        - Update `UnitState.inventory` for `unit1` and `unit2` (and captive if involved) via `GameStateManager`.
        - Trading is a free action in Thracia (does not consume the unit's action) (Ref: `research.md`, Sec 4).

### 2.7. Convoy Access (Thracia Specifics)
    - Thracia has limited convoy mechanics compared to later games. (Ref: `research.md`, Sec 13).
    - Access might be limited to Leif or specific map locations/prep screens.
    - If implemented:
        - Store convoy items (`List[ItemInstance]`) potentially within `GameState`.
        - Provide functions `access_convoy(unit_id)` (check conditions like Leif adjacent to supply point/base).
        - Provide functions `deposit_to_convoy(unit_id, item_index)` and `withdraw_from_convoy(unit_id, convoy_item_index)`.
        - Manage convoy capacity if applicable.
    - **Initial Scope:** May defer full convoy implementation, focusing on unit-to-unit trading and item acquisition/use first.

## 4. Data Structures (References)

- Relies on `UnitState`, `ItemInstance` from `GameStateManager`.
- Relies on `ItemData` from `DataProvider`.
- Needs definition for "Broken" item types in `DataProvider`.

## 5. Pseudocode (inventory_system.py)

```python
# --- inventory_system.py ---

# Import necessary modules (GameStateManager, DataProvider)
# Import enums (ItemTypeEnum, RankEnum)

class InventorySystem:
    gameStateManager = null
    dataProvider = null

    function initialize(gameStateManager_instance, dataProvider_instance):
        gameStateManager = gameStateManager_instance
        dataProvider = dataProvider_instance
        log("InventorySystem initialized.")

    # --- Item Management ---

    # TDD: Test adding item respects inventory limit, uses correct durability
    function add_item_to_inventory(unit_id, item_id, durability=None):
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return False
        
        # Check inventory limit (e.g., 7 items)
        MAX_INVENTORY_SIZE = 7 
        if len(unit.inventory) >= MAX_INVENTORY_SIZE:
            log(f"Inventory full for unit {unit_id}.")
            return False

        item_data = dataProvider.get_item_data(item_id)
        if not item_data:
            log(f"Invalid item_id {item_id} for add_item.")
            return False

        instance = ItemInstance()
        instance.item_id = item_id
        instance.current_durability = durability if durability is not None else item_data.max_durability
        
        unit.inventory.append(instance)
        log(f"Added item {item_data.name} to unit {unit_id}.")
        return True

    # TDD: Test removing item handles valid/invalid index, returns correct item
    function remove_item_from_inventory(unit_id, item_index):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            return null
        
        removed_instance = unit.inventory.pop(item_index)
        
        # If equipped item was removed, unequip
        if unit.equipped_weapon_index == item_index:
            self.unequip_item(unit_id)
        # Adjust equipped index if item removed was before it
        elif unit.equipped_weapon_index > item_index:
             unit.equipped_weapon_index -= 1
             
        log(f"Removed item at index {item_index} from unit {unit_id}.")
        return removed_instance

    # TDD: Test equipping valid weapon updates index, unequips previous
    # TDD: Test equipping invalid item fails
    # TDD: Test equipping weapon with unmet rank requirement fails
    function equip_item(unit_id, item_index):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            return False

        item_instance = unit.inventory[item_index]
        item_data = dataProvider.get_item_data(item_instance.item_id)

        # Check if item is a weapon
        if item_data.type not in [WEAPON, STAFF]: # Or specific check
             log(f"Cannot equip item type {item_data.type}.")
             return False

        # Check weapon rank requirement
        required_rank = item_data.required_rank
        unit_rank = unit.weapon_ranks.get(item_data.weapon_type, E_RANK) # Default to E if no rank
        if dataProvider.is_rank_higher(required_rank, unit_rank) > 0: # if required > unit's rank
             log(f"Unit {unit_id} rank {unit_rank} too low for {item_data.name} (requires {required_rank}).")
             return False

        unit.equipped_weapon_index = item_index
        log(f"Unit {unit_id} equipped {item_data.name}.")
        return True

    # TDD: Test unequipping sets index to -1
    function unequip_item(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        if unit:
            unit.equipped_weapon_index = -1
            log(f"Unit {unit_id} unequipped item.")
            return True
        return False

    # --- Durability ---

    # TDD: Test decrement durability reduces count correctly
    # TDD: Test decrement durability handles breaking repairable items (becomes BROKEN_*)
    # TDD: Test decrement durability removes non-repairable items at 0
    # TDD: Test decrement durability unequips item if equipped weapon breaks
    function decrement_item_durability(unit_id, item_index, amount=1):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            return False # Item not found

        item_instance = unit.inventory[item_index]
        item_data = dataProvider.get_item_data(item_instance.item_id)
        
        if item_data.max_durability <= 0: # Indestructible item
             return True 

        item_instance.current_durability -= amount
        log(f"Item {item_data.name} durability reduced to {item_instance.current_durability}/{item_data.max_durability} for unit {unit_id}.")

        if item_instance.current_durability <= 0:
            log(f"Item {item_data.name} broke for unit {unit_id}.")
            
            broken_item_id = dataProvider.get_broken_item_id(item_instance.item_id) # Helper needed in DP
            
            if broken_item_id: # Item is repairable, becomes broken version
                 item_instance.item_id = broken_item_id
                 item_instance.current_durability = 0 # Or specific value for broken items?
                 log(f"Item replaced with {broken_item_id}.")
                 # If equipped, it remains "equipped" but is now broken
            else: # Item is not repairable, remove it
                 self.remove_item_from_inventory(unit_id, item_index)
                 # Note: remove_item handles un-equipping if needed
            return False # Item broke or was removed
            
        return True # Item still has uses

    # --- Repair ---

    # TDD: Test repair restores correct item ID and full durability
    # TDD: Test repair fails on non-broken/non-repairable items
    function repair_item(unit_id, item_index):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            return False

        item_instance = unit.inventory[item_index]
        
        original_item_id = dataProvider.get_original_item_id_from_broken(item_instance.item_id) # Helper needed in DP
        
        if not original_item_id:
             # Maybe allow repairing damaged (non-broken) items too? Check FE5 rules. Assume only broken for now.
             log(f"Item {item_instance.item_id} is not a known broken item.")
             return False

        original_item_data = dataProvider.get_item_data(original_item_id)
        if not original_item_data:
             log(f"Cannot find original item data for {original_item_id}.")
             return False

        item_instance.item_id = original_item_id
        item_instance.current_durability = original_item_data.max_durability
        log(f"Repaired item for unit {unit_id} to {original_item_data.name} ({item_instance.current_durability}/{original_item_data.max_durability}).")
        return True

    # --- Trading ---

    # TDD: Test trade initiation validates adjacency and target type (ally/captive)
    function initiate_trade(unit1_id, unit2_id):
        unit1 = gameStateManager.get_unit(unit1_id)
        unit2 = gameStateManager.get_unit(unit2_id)
        if not unit1 or not unit2: return None # Units not found

        # Check adjacency (using MapSystem or GameStateManager)
        if not gameStateManager.are_units_adjacent(unit1_id, unit2_id):
             log("Units not adjacent for trade.")
             return None

        is_target_captive = (unit1.carrying_unit_id == unit2_id and unit2.is_captured) # Check if unit1 carries unit2 as captive
        is_target_ally = (unit2.faction == unit1.faction) # Or check alliance status

        if not is_target_ally and not is_target_captive:
             log("Cannot trade with target unit (not ally or captive).")
             return None

        trade_data = {
            'unit1_inventory': unit1.inventory,
            'unit2_inventory': unit2.inventory,
            'captive_inventory': None
        }

        if is_target_captive:
             # In Thracia, you access the captive's inventory directly
             trade_data['captive_inventory'] = unit2.inventory # Captive's items are still on them
             # Clear unit2's inventory display for clarity? Or show it as the captive source? UI decision.
             trade_data['unit2_inventory'] = [] # Show unit2 slot as empty, use captive slot

        log(f"Initiating trade between {unit1_id} and {unit2_id}" + (" (accessing captive)" if is_target_captive else ""))
        return trade_data

    # TDD: Test trade execution moves items correctly between unit1, unit2, captive
    # TDD: Test trade execution respects inventory limits
    function execute_trade(unit1_id, unit2_id, item_transfers):
        # item_transfers = list of tuples: (source_unit_id/CAPTIVE, source_index, dest_unit_id/CAPTIVE, dest_index)
        # Need robust validation of transfers against current inventories and limits
        unit1 = gameStateManager.get_unit(unit1_id)
        unit2 = gameStateManager.get_unit(unit2_id)
        captive_unit = None
        if unit1.carrying_unit_id == unit2_id and unit2.is_captured:
             captive_unit = unit2 # Unit2 is the captive

        # 1. Simulate transfers to check validity (inventory limits)
        # 2. If valid, apply changes to unit1.inventory, unit2.inventory (or captive_unit.inventory)
        #    - Use remove_item_from_inventory and add_item_to_inventory logic carefully
        #    - Remember to adjust equipped indices if traded items were equipped
        
        log(f"Executing trade between {unit1_id} and {unit2_id}.")
        # Return success/failure
        pass 

    # --- Item Usage (Called by Engine Core/Action Handler) ---

    # TDD: Test using consumable applies effect, decrements/removes item
    # TDD: Test using key opens door, decrements/removes item
    function use_item(unit_id, item_index, target=None):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            return False # Invalid item

        item_instance = unit.inventory[item_index]
        item_data = dataProvider.get_item_data(item_instance.item_id)
        if not item_data: return False

        success = False
        if item_data.type == CONSUMABLE:
            # Apply effect (heal, boost, cure) to unit_id or target_id
            effect_applied = gameStateManager.apply_item_effect(unit_id, item_data.effects, target)
            if effect_applied:
                 success = self.decrement_item_durability(unit_id, item_index)
        elif item_data.type == KEY:
            if target and gameStateManager.is_tile_lock(target): # Check if target is a lock
                 lock_opened = gameStateManager.open_lock(target, item_data.key_type) # Check key type match
                 if lock_opened:
                      success = self.decrement_item_durability(unit_id, item_index)
        # Add other usable item types (Scrolls? Stat boosters are consumables)

        if success:
            gameStateManager.set_unit_acted(unit_id) # Using item costs action
            log(f"Unit {unit_id} used item {item_data.name}.")
        else:
            log(f"Unit {unit_id} failed to use item {item_data.name}.")
            
        return success

```

## 6. Integration Points

- **GameStateManager:** Reads/Writes `UnitState.inventory`, `UnitState.equipped_weapon_index`. Calls `apply_healing`, `apply_stat_boost`, `remove_status_effect`, `set_object_state`, `set_unit_acted`.
- **DataProvider:** Reads `ItemData` (properties, effects, durability, rank, type, broken/original IDs), `UnitState.weapon_ranks`.
- **UnitSystem:** May trigger item usage effects that modify unit stats or status. Relies on inventory for stat calculations (equipped weapon).
- **CombatSystem:** Decrements weapon/staff durability after combat/use via `decrement_item_durability`. Reads equipped weapon data.
- **EngineCore/ActionHandler:** Initiates `use_item`, `equip_item`, `initiate_trade`, `execute_trade` based on player commands.

## 7. Open Questions/Future Considerations

- Finalize Convoy implementation details if needed. How is it accessed? Is it per-chapter or persistent?
- Define specific "Broken" item IDs and their properties in `DataProvider`.
- Clarify rules for repairing non-broken but damaged items.
- Refine `execute_trade` logic for robustness, especially handling captive inventory access.
- How are scrolls handled? Are they "used" or passively equipped in inventory? (Research suggests passive effect when held - Sec 4). No specific "use" action needed, just presence in inventory checked by other systems (Combat for crit negation, UnitSystem for growth boosts).