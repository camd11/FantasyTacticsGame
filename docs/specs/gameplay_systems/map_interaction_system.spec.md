# Specification: Map Interaction System (Doors &amp; Chests)

## 1. Overview

This system handles unit interactions with interactive map elements, specifically Doors and Chests, common in tactical RPGs like Fire Emblem. It defines how these objects are represented, the conditions for interaction, the effects of interaction, and integration with other game systems (Units, Items, AI, Actions).

## 2. Data Structures

### 2.1. Map Tile / Map Object Representation

```pseudocode
// Existing Map System provides Tile data
Tile {
    coordinates: (x, y)
    terrain_type: TerrainType // e.g., Plain, Forest, Wall, Floor
    map_object: Optional<MapObject> // Reference to an object on this tile
    // ... other properties like movement cost, bonuses
}

// New structure for interactive objects
MapObject {
    object_id: UniqueID
    object_type: Enum { Door, Chest }
    position: (x, y)
    state: Enum { Locked, Unlocked, Opened, Empty } // Opened for Doors, Empty for Chests
    // For Chests:
    content_type: Optional<Enum { Item, Gold }>
    content_value: Optional<Variant<ItemID, Amount>> // ItemID or Gold amount
    // For Doors:
    linked_door_id: Optional<UniqueID> // For paired doors, if applicable
}

// Add specific TerrainTypes if needed, or handle via MapObject
TerrainType {
    // ... existing types
    ClosedDoor // Impassable
    OpenDoor // Passable, like Floor
    Chest // Impassable (unit stands adjacent)
    OpenedChest // Impassable or becomes Floor? (Design decision)
}
```
*   **TDD Anchor:** `Test_MapObject_Initialization`: Ensure Doors and Chests initialize in 'Locked' state with correct content/linkage.
*   **TDD Anchor:** `Test_Tile_Object_Association`: Verify `MapObject` is correctly linked to its `Tile`.

### 2.2. Item Representation (Integration with Item System)

```pseudocode
// Assumes an existing Item System
Item {
    item_id: UniqueID
    name: String
    type: Enum { Weapon, Consumable, Key, ... }
    // For Keys:
    key_type: Optional<Enum { DoorKey, ChestKey, MasterKey }> // MasterKey could open both
    uses: Integer // Typically 1 for FE keys, but could be > 1
    // ... other item properties
}
```
*   **TDD Anchor:** `Test_Item_Is_Correct_Key_Type`: Check if an item is the required key type (Door, Chest).

### 2.3. Unit Representation (Integration with Unit System)

```pseudocode
// Assumes an existing Unit System
Unit {
    unit_id: UniqueID
    position: (x, y)
    inventory: List<ItemID>
    skills: List<SkillID> // e.g., Locktouch
    // ... other unit properties (stats, class, etc.)
}

// Assumes a Skill System
Skill {
    skill_id: UniqueID
    name: String // e.g., "Locktouch"
    // ... skill properties/effects
}
```
*   **TDD Anchor:** `Test_Unit_Has_Skill`: Check if a unit possesses a specific skill (e.g., Locktouch).
*   **TDD Anchor:** `Test_Unit_Has_Item`: Check if a unit possesses a specific item (e.g., Door Key).

## 3. Core Logic: Interaction Checks

### 3.1. `CanInteractWithObject(unit_id, object_id)` -> Boolean

Determines if a unit *can potentially* interact with a door/chest (basic checks).

```pseudocode
FUNCTION CanInteractWithObject(unit_id, object_id):
    unit = GetUnit(unit_id)
    map_object = GetMapObject(object_id)

    IF map_object IS NULL OR unit IS NULL THEN RETURN FALSE

    // 1. Check Adjacency
    IF NOT IsAdjacent(unit.position, map_object.position) THEN RETURN FALSE
        // TDD Anchor: Test_CanInteract_Requires_Adjacency

    // 2. Check Object State
    IF map_object.state IS Opened OR map_object.state IS Empty THEN RETURN FALSE
        // TDD Anchor: Test_CanInteract_Requires_Locked_State

    // 3. Check Unit Type/Class Restrictions (Optional, e.g., only certain classes can interact)
    // IF NOT CanUnitClassInteract(unit.class, map_object.type) THEN RETURN FALSE

    // 4. Check if interaction is possible via *any* means (key or skill)
    has_key = HasRequiredKey(unit, map_object)
    has_skill = HasRequiredSkill(unit, map_object)
    IF NOT (has_key OR has_skill) THEN RETURN FALSE
        // TDD Anchor: Test_CanInteract_Requires_Key_Or_Skill

    RETURN TRUE
ENDFUNCTION
```

### 3.2. `HasRequiredKey(unit, map_object)` -> Boolean

Checks if the unit possesses the necessary key in their inventory.

```pseudocode
FUNCTION HasRequiredKey(unit, map_object):
    required_key_type = NULL
    IF map_object.object_type IS Door THEN
        required_key_type = DoorKey
    ELSE IF map_object.object_type IS Chest THEN
        required_key_type = ChestKey
    ELSE
        RETURN FALSE // Unknown object type

    FOR item_id IN unit.inventory:
        item = GetItem(item_id)
        IF item IS NOT NULL AND item.type IS Key THEN
            IF item.key_type IS required_key_type OR item.key_type IS MasterKey THEN
                IF item.uses > 0 THEN
                    RETURN TRUE // Found a valid key with uses remaining
                    // TDD Anchor: Test_HasRequiredKey_Finds_Correct_Key
                    // TDD Anchor: Test_HasRequiredKey_Finds_MasterKey
                    // TDD Anchor: Test_HasRequiredKey_Requires_Uses
    RETURN FALSE // No suitable key found
        // TDD Anchor: Test_HasRequiredKey_Handles_No_Key
ENDFUNCTION
```

### 3.3. `HasRequiredSkill(unit, map_object)` -> Boolean

Checks if the unit possesses the necessary skill (e.g., Locktouch).

```pseudocode
FUNCTION HasRequiredSkill(unit, map_object):
    IF map_object.object_type IS Door OR map_object.object_type IS Chest THEN
        FOR skill_id IN unit.skills:
            skill = GetSkill(skill_id)
            IF skill IS NOT NULL AND skill.name IS "Locktouch" THEN // Or check by SkillID
                // Optional: Check skill limitations (e.g., Locktouch might have level/stat req?)
                // IF LocktouchSkillHasLimitations(unit, skill) THEN CONTINUE
                RETURN TRUE
                // TDD Anchor: Test_HasRequiredSkill_Finds_Locktouch
    RETURN FALSE
        // TDD Anchor: Test_HasRequiredSkill_Handles_No_Skill
ENDFUNCTION
```

## 4. Core Logic: Performing Interaction

### 4.1. `AttemptInteraction(unit_id, object_id)` -> InteractionResult

Executes the interaction if possible, consuming keys/actions and updating state.

```pseudocode
// Result structure
InteractionResult {
    success: Boolean
    message: String // e.g., "Door opened.", "Chest contained 500 Gold.", "No key found."
    consumed_key_id: Optional<ItemID>
    gained_item_id: Optional<ItemID>
    gained_gold: Optional<Amount>
}

FUNCTION AttemptInteraction(unit_id, object_id):
    result = InteractionResult(success=FALSE)
    unit = GetUnit(unit_id)
    map_object = GetMapObject(object_id)

    IF NOT CanInteractWithObject(unit_id, object_id) THEN
        result.message = "Cannot interact with object."
        RETURN result // Basic checks failed

    // Determine interaction method: Prioritize Skill (Locktouch) over Key? (Design Decision)
    used_skill = FALSE
    consumed_key_id = NULL

    IF HasRequiredSkill(unit, map_object) THEN
        used_skill = TRUE
        // TDD Anchor: Test_Interaction_Prioritizes_Skill
    ELSE IF HasRequiredKey(unit, map_object) THEN
        // Find the specific key to consume
        key_to_consume = FindKeyInInventory(unit, map_object) // Helper function
        IF key_to_consume IS NOT NULL THEN
            ConsumeItemUse(key_to_consume.item_id) // Decrement uses or remove if 0
            consumed_key_id = key_to_consume.item_id
            // TDD Anchor: Test_Interaction_Consumes_Key_Use
        ELSE
            result.message = "Error: Key check passed but no key found to consume."
            RETURN result // Should not happen if CanInteract logic is correct
    ELSE
        result.message = "No key or skill available." // Should be caught by CanInteract
        RETURN result

    // Perform the action based on object type
    IF map_object.object_type IS Door THEN
        result = OpenDoor(unit, map_object, used_skill)
    ELSE IF map_object.object_type IS Chest THEN
        result = OpenChest(unit, map_object, used_skill)

    result.consumed_key_id = consumed_key_id
    IF result.success THEN
        // Mark unit action as complete for the turn (Integration with Action System)
        MarkUnitActionComplete(unit_id)
        // TDD Anchor: Test_Interaction_Consumes_Unit_Action
    ENDIF

    RETURN result
ENDFUNCTION

// Helper to find the first valid key
FUNCTION FindKeyInInventory(unit, map_object):
    required_key_type = (DoorKey IF map_object.object_type IS Door ELSE ChestKey)
    FOR item_id IN unit.inventory:
        item = GetItem(item_id)
        IF item IS NOT NULL AND item.type IS Key AND item.uses > 0 THEN
            IF item.key_type IS required_key_type OR item.key_type IS MasterKey THEN
                RETURN item
    RETURN NULL
ENDFUNCTION
```

### 4.2. `OpenDoor(unit, map_object, used_skill)` -> InteractionResult

Handles the specific logic for opening a door.

```pseudocode
FUNCTION OpenDoor(unit, map_object, used_skill):
    result = InteractionResult(success=TRUE)

    // Update Door State
    map_object.state = Opened
    // TDD Anchor: Test_OpenDoor_Updates_State

    // Update Map Terrain (if represented by terrain)
    tile = GetTileAt(map_object.position)
    IF tile.terrain_type IS ClosedDoor THEN
        tile.terrain_type = OpenDoor // Make passable
        UpdateMapPassability(tile.coordinates) // Notify pathfinding etc.
        // TDD Anchor: Test_OpenDoor_Updates_Terrain_Passability
    ENDIF

    // Handle linked doors (if applicable)
    IF map_object.linked_door_id IS NOT NULL THEN
        linked_door = GetMapObject(map_object.linked_door_id)
        IF linked_door IS NOT NULL AND linked_door.state IS Locked THEN
            linked_door.state = Opened
            linked_tile = GetTileAt(linked_door.position)
            IF linked_tile.terrain_type IS ClosedDoor THEN
                linked_tile.terrain_type = OpenDoor
                UpdateMapPassability(linked_tile.coordinates)
            ENDIF
            // TDD Anchor: Test_OpenDoor_Handles_Linked_Doors
        ENDIF
    ENDIF

    result.message = "Door opened."
    IF used_skill THEN result.message += " (Used Locktouch)"

    // Optional: Grant EXP for opening door with Locktouch? (Design Decision)
    // IF used_skill THEN GrantSkillExp(unit.unit_id, "Locktouch")

    RETURN result
ENDFUNCTION
```

### 4.3. `OpenChest(unit, map_object, used_skill)` -> InteractionResult

Handles the specific logic for opening a chest.

```pseudocode
FUNCTION OpenChest(unit, map_object, used_skill):
    result = InteractionResult(success=TRUE)

    // Check if chest is already empty (should be caught earlier, but double-check)
    IF map_object.state IS Empty THEN
        result.success = FALSE
        result.message = "Chest is already empty."
        RETURN result

    // Grant Content to Unit
    IF map_object.content_type IS Item THEN
        item_id = map_object.content_value
        IF CanUnitCarryItem(unit) THEN // Check inventory space
            AddItemToInventory(unit.unit_id, item_id)
            result.gained_item_id = item_id
            item_name = GetItem(item_id).name
            result.message = "Obtained " + item_name + "."
            // TDD Anchor: Test_OpenChest_Grants_Item
        ELSE
            result.success = FALSE // Cannot open if inventory full
            result.message = "Inventory is full."
            // TDD Anchor: Test_OpenChest_Handles_Full_Inventory
            RETURN result // Revert key consumption? Or leave key used but chest unopened? (Design Decision - typically key is lost)
        ENDIF
    ELSE IF map_object.content_type IS Gold THEN
        gold_amount = map_object.content_value
        AddGoldToParty(gold_amount) // Assuming party gold pool
        result.gained_gold = gold_amount
        result.message = "Obtained " + gold_amount + " Gold."
        // TDD Anchor: Test_OpenChest_Grants_Gold
    ELSE
        result.message = "Chest is empty." // No content defined
    ENDIF

    // Update Chest State
    map_object.state = Empty
    map_object.content_type = NULL
    map_object.content_value = NULL
    // TDD Anchor: Test_OpenChest_Updates_State_To_Empty

    // Update Map Terrain/Appearance (Optional)
    // tile = GetTileAt(map_object.position)
    // tile.terrain_type = OpenedChest // Or change sprite

    IF used_skill THEN result.message += " (Used Locktouch)"

    // Optional: Grant EXP for opening chest with Locktouch?
    // IF used_skill THEN GrantSkillExp(unit.unit_id, "Locktouch")

    RETURN result
ENDFUNCTION
```

## 5. Specific Mechanics Details

### 5.1. Locktouch Skill

*   Implemented via `HasRequiredSkill`.
*   Allows opening Doors and Chests without consuming a Key.
*   Priority: Typically checked before keys, saving key uses.
*   Limitations: Standard FE usually has no limitations (like uses per map or stat requirements) beyond needing the skill itself. Could add checks in `HasRequiredSkill` if desired.
*   EXP Gain: Consider granting skill EXP or regular EXP when Locktouch is used successfully.

### 5.2. Keys (Door Key, Chest Key, Master Key)

*   Represented as Items with `type = Key` and specific `key_type`.
*   Consumed on use (`ConsumeItemUse` function). Typically single-use in FE. If multi-use keys exist, decrement uses. Remove item if uses reach 0.
    *   **TDD Anchor:** `Test_Key_Consumption_Single_Use`: Verify key is removed after 1 use.
    *   **TDD Anchor:** `Test_Key_Consumption_Multi_Use`: Verify uses decrement correctly.
*   Master Keys can open both Doors and Chests (checked in `HasRequiredKey`).

## 6. AI Considerations

*   **Thieves:** AI logic should prioritize targeting reachable, unopened Chests.
    *   Check `CanInteractWithObject` for AI thieves.
    *   If interaction possible (usually via Locktouch for AI thieves), add "Open Chest" action to potential AI moves.
    *   Assign high priority/desire score to opening chests, especially if containing valuable items/gold.
    *   After opening, AI might change behavior (e.g., escape if objective was loot).
    *   **TDD Anchor:** `Test_AI_Thief_Prioritizes_Chests`
*   **Other Units:** Non-thief AI units typically ignore chests unless scripted.
*   **Doors:** AI might need to open doors to reach objectives (e.g., seize point, player units).
    *   If a path to an objective is blocked by a locked door, check if any AI unit possesses the required key *and* is adjacent.
    *   If so, consider "Open Door" as a potential action. Priority depends on the importance of the objective beyond the door.
    *   AI generally won't use keys wastefully; only if needed for pathing/objective.
    *   **TDD Anchor:** `Test_AI_Uses_DoorKey_For_Objective`

## 7. Integration Points

*   **Map System:** Reads `MapObject` data, updates `Tile` terrain type/passability when doors open.
*   **Item System:** Provides `Item` data (key types, uses), handles key consumption (`ConsumeItemUse`), adds items to inventory (`AddItemToInventory`).
*   **Unit System:** Provides `Unit` data (inventory, skills), checks for `Locktouch` skill, checks inventory space (`CanUnitCarryItem`).
*   **Action System:** Interaction consumes the unit's action for the turn (`MarkUnitActionComplete`).
*   **AI System:** Incorporates interaction checks and actions into AI decision-making routines.
*   **Event System:** Map events might lock/unlock doors, spawn chests, or give keys.

## 8. Edge Cases &amp; Design Decisions

*   **Inventory Full:** How to handle opening a chest with an item when the unit's inventory is full? (Current pseudocode: interaction fails, key might still be consumed - needs refinement based on desired behavior).
*   **Key Priority:** If a unit has both Locktouch and a Key, which is used? (Current pseudocode: Locktouch prioritized).
*   **Linked Doors:** Ensure robust handling of doors that open in pairs. What if one is already open?
*   **Terrain Representation:** Are Doors/Chests purely `MapObjects`, or also specific `TerrainTypes`? Affects passability rules. (Current pseudocode assumes both).
*   **EXP/Rewards:** Decide if using Locktouch grants EXP.
*   **AI Key Usage:** How smart should AI be about conserving limited keys vs. achieving objectives?
*   **Master Keys:** Ensure they work correctly for both doors and chests.