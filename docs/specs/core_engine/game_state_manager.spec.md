# Specification: Game State Manager

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Game State Manager is responsible for holding and managing all dynamic data related to the current game session. This includes the state of the map, all units (player, enemy, NPC), turn information, fatigue levels, event flags, and inventory. It provides interfaces for the Engine Core and other components to query and modify this data safely and consistently.

## 2. Functional Requirements

### 2.1. Map State Management
    - Store the current chapter's map layout (grid dimensions, terrain types per tile).
    - Store the position of all units on the map.
    - Store the state of interactable map objects (e.g., villages visited, doors opened, chests looted).
    - Provide functions to query terrain type, movement cost, and bonuses for a given tile.
    - Provide functions to check if a tile is occupied.
    - Provide functions to update the state of map objects.

### 2.2. Unit State Management
    - Store a collection of all units currently active in the chapter (player, enemy, NPC).
    - For each unit, store:
        - Unique ID, Name, Class ID, Faction (Player/Enemy/NPC).
        - Current Position (x, y).
        - Current HP, Max HP.
        - Base Stats (Str, Mag, Skl, Spd, Luk, Def, Con, Mov).
        - Calculated Combat Stats (Atk, AS, Hit, Avo, Crit, Ddg, Rng, FCM/PCC) - potentially recalculated on demand or cached.
        - Inventory (list of Item IDs and current durability). Equipped weapon index.
        - Weapon Ranks and current WExp for each weapon type.
        - Current Fatigue level.
        - Current Status Effects (list of active statuses like Poison, Sleep).
        - Action State (has_moved, has_acted).
        - Support Partner IDs.
        - Leadership Stars.
        - Captured State (is_captured, is_carrying_captured_unit_id, is_rescuing_ally_id).
        - Alive/Dead/Escaped status.
        - Growth Rates (for level ups).
        - Current Level and Experience points.
    - Provide functions to get/set unit properties (HP, position, status, fatigue, inventory, etc.).
    - Provide functions to add/remove units (e.g., reinforcements, death).
    - Provide functions to calculate derived stats based on base stats, items, status, terrain, supports, leadership (or delegate to a calculator module).
    - Provide functions to handle level ups (apply growths, check caps).
    - Provide functions to handle promotions.

### 2.3. Turn and Phase State
    - Store the current turn number.
    - Store the current phase (Player, Enemy, NPC).
    - Store the currently selected unit (for player phase).

### 2.4. Fatigue Management
    - Store and update the fatigue level for each player unit.
    - Provide a function to check if a unit is fatigued beyond their Max HP threshold.
    - Provide a function to reset fatigue for units benched or using an S-Drink.
    - Provide a function to finalize fatigue status at the end of a chapter.

### 2.5. Event State
    - Store the state of event flags (e.g., `event_X_triggered = true`).
    - Provide functions to get/set event flags.

### 2.6. Inventory and Item Management
    - Manage unit inventories (adding, removing, swapping items).
    - Track item durability and handle item breaking.
    - Provide functions for trading items between units (including captured units).
    - Provide functions for using consumable items and applying their effects.

### 2.7. Persistence (Optional)
    - Provide functions to serialize the current game state for saving (e.g., suspend saves, chapter saves).
    - Provide functions to deserialize game state from saved data.

## 3. Data Structures (Conceptual)

```python
# --- game_state_manager_datastructures.py ---

# Represents a single unit on the map
class UnitState:
    id: string
    name: string
    class_id: string
    faction: FactionEnum # PLAYER, ENEMY, NPC
    position: Tuple[int, int]
    
    current_hp: int
    max_hp: int
    
    # Base Stats (loaded from DataProvider initially)
    base_stats: Dict[StatEnum, int] # STR, MAG, SKL, SPD, LUK, DEF, CON, MOV
    
    # Growths (loaded from DataProvider)
    growth_rates: Dict[StatEnum, int] # Percentages
    
    level: int
    experience: int
    
    inventory: List[ItemInstance] # Max 7 items?
    equipped_weapon_index: int # -1 if none
    
    weapon_ranks: Dict[WeaponTypeEnum, RankEnum] # SWORD: C, LANCE: D, etc.
    weapon_exp: Dict[WeaponTypeEnum, int] # SWORD: 55, LANCE: 10, etc.
    
    current_fatigue: int
    
    status_effects: List[StatusEffectInstance] # e.g., [StatusEffect(POISON, duration=-1)] (-1 for permanent)
    
    # Action state for current turn
    has_moved: bool
    has_acted: bool
    
    # Relationships/Bonuses
    support_partner_ids: List[string] # Loaded from DataProvider
    leadership_stars: int # Loaded from DataProvider
    pcc: int # Pursuit Critical Coefficient (FCM), loaded from DataProvider
    
    # Capture/Rescue State
    is_captured: bool # If this unit has been captured by an enemy
    carrying_unit_id: string # ID of unit this unit is carrying (ally rescue or enemy capture)
    
    # Overall Status
    disposition: DispositionEnum # ACTIVE, DEAD, ESCAPED, CAPTURED_BY_ENEMY, BENCHED

# Represents an item instance in inventory
class ItemInstance:
    item_id: string # References static item data in DataProvider
    current_durability: int

# Represents an active status effect
class StatusEffectInstance:
    type: StatusEffectEnum # POISON, SLEEP, SILENCE, BERSERK, STAT_BOOST (e.g., M_UP)
    duration: int # Turns remaining, -1 for permanent until cured/chapter end
    # Optional: Store effect magnitude if needed (e.g., M_UP bonus amount)

# Represents the map state
class MapState:
    map_id: string
    dimensions: Tuple[int, int] # width, height
    terrain_grid: List[List[TerrainTypeEnum]] # Grid of terrain types
    unit_positions: Dict[string, Tuple[int, int]] # unit_id -> (x, y)
    object_states: Dict[Tuple[int, int], ObjectStateEnum] # (x, y) -> VISITED, OPENED, LOOTED

# Main Game State Container
class GameState:
    chapter_id: string
    current_turn: int
    current_phase: PhaseEnum
    
    map_state: MapState
    unit_states: Dict[string, UnitState] # unit_id -> UnitState
    
    event_flags: Dict[string, bool] # flag_name -> triggered_status
    
    # Potentially store player convoy/gold if applicable
    # player_gold: int
    # player_convoy: List[ItemInstance]
```

## 4. Pseudocode (game_state_manager.py)

```python
# --- game_state_manager.py ---

# Import data structures (UnitState, MapState, GameState, etc.)
# Import enums (FactionEnum, PhaseEnum, StatEnum, StatusEffectEnum, etc.)

class GameStateManager:
    current_game_state = null # Instance of GameState

    # TDD: Test loading map data populates terrain_grid and dimensions
    function load_map(map_data):
        state = GameState()
        state.map_state = MapState()
        state.map_state.map_id = map_data.id
        state.map_state.dimensions = map_data.dimensions
        state.map_state.terrain_grid = map_data.terrain_grid
        state.map_state.unit_positions = {}
        state.map_state.object_states = {}
        state.unit_states = {}
        state.event_flags = {}
        current_game_state = state
        log("Map loaded: " + map_data.id)

    # TDD: Test deploying units creates UnitState objects with correct initial data
    function deploy_units(unit_placements, dataProvider):
        for placement in unit_placements:
            unit_id = placement.unit_id
            base_data = dataProvider.get_unit_base_data(unit_id) # Gets class, base stats, growths, skills, etc.
            
            unit = UnitState()
            unit.id = unit_id
            unit.name = base_data.name
            unit.class_id = base_data.class_id
            unit.faction = placement.faction # Player, Enemy, NPC
            unit.position = placement.position
            
            unit.max_hp = base_data.stats[HP] # Assuming base stats include HP
            unit.current_hp = unit.max_hp
            
            unit.base_stats = base_data.stats
            unit.growth_rates = base_data.growths
            unit.level = placement.level # Starting level for this chapter
            unit.experience = 0
            
            unit.inventory = []
            for item_id in placement.start_inventory:
                 item_data = dataProvider.get_item_data(item_id)
                 unit.inventory.append(ItemInstance(item_id=item_id, current_durability=item_data.max_durability))
            unit.equipped_weapon_index = find_initial_equipped_weapon(unit.inventory, dataProvider)

            unit.weapon_ranks = base_data.base_weapon_ranks
            unit.weapon_exp = {wt: 0 for wt in unit.weapon_ranks}
            
            unit.current_fatigue = placement.starting_fatigue # Usually 0, but could carry over
            unit.status_effects = []
            
            unit.has_moved = False
            unit.has_acted = False
            
            unit.support_partner_ids = dataProvider.get_support_partners(unit_id)
            unit.leadership_stars = base_data.leadership_stars
            unit.pcc = base_data.pcc
            
            unit.is_captured = False
            unit.carrying_unit_id = null
            unit.disposition = ACTIVE
            
            # Handle autoleveling if needed (Ref: research.md Sec 10)
            if placement.needs_autolevel:
                 autolevel_unit(unit, placement.target_level, dataProvider)

            current_game_state.unit_states[unit_id] = unit
            current_game_state.map_state.unit_positions[unit_id] = unit.position
        log("Units deployed.")

    # --- Query Functions ---

    # TDD: Test get_unit returns correct UnitState object
    function get_unit(unit_id):
        return current_game_state.unit_states.get(unit_id, null)

    # TDD: Test get_units_by_faction returns correct list of units
    function get_units_by_faction(faction):
        return [u for u in current_game_state.unit_states.values() if u.faction == faction and u.disposition == ACTIVE]

    # TDD: Test get_units_within_range returns units correctly based on distance
    function get_units_within_range(position, range_val, include_faction=ALL):
        # Calculate distances and filter units
        pass 

    # TDD: Test get_terrain_type returns correct type for a coordinate
    function get_terrain_type(position):
        x, y = position
        if 0 <= x < current_game_state.map_state.dimensions[0] and 0 <= y < current_game_state.map_state.dimensions[1]:
            return current_game_state.map_state.terrain_grid[y][x]
        return TERRAIN_INVALID

    # TDD: Test get_terrain_movement_cost calculates cost based on unit type and terrain
    function get_terrain_movement_cost(position, unit_id, dataProvider):
        unit = get_unit(unit_id)
        terrain_type = get_terrain_type(position)
        class_data = dataProvider.get_class_data(unit.class_id)
        movement_type = class_data.movement_type # Need to handle dismounted state
        # Handle dismount: if unit is mounted and terrain is indoor, use infantry movement type
        if is_unit_mounted(unit_id) and is_terrain_indoor(terrain_type):
             movement_type = MOVEMENT_INFANTRY # Or specific dismounted type
        
        cost = dataProvider.get_terrain_cost(terrain_type, movement_type)
        return cost # Returns cost or IMPASSABLE

    # TDD: Test get_terrain_bonus returns correct Def/Avo bonus
    function get_terrain_bonus(position, dataProvider):
        terrain_type = get_terrain_type(position)
        return dataProvider.get_terrain_bonuses(terrain_type) # Returns {def: X, avo: Y}

    # TDD: Test is_tile_occupied checks unit_positions correctly
    function is_tile_occupied(position):
        return position in current_game_state.map_state.unit_positions.values()

    # TDD: Test get_unit_movement_stars returns correct value
    function get_unit_movement_stars(unit_id):
        # Movement stars are inherent, maybe stored in base_stats or separate field? Assume base_stats for now.
        unit = get_unit(unit_id)
        return unit.base_stats.get(MOV_STARS, 0) 

    # TDD: Test is_unit_fatigued_for_deployment checks fatigue vs max HP (considering Leif's exemption)
    function is_unit_fatigued_for_deployment(unit_id):
        if unit_id == LEIF_ID: return False # Leif is exempt
        unit = get_unit(unit_id)
        # Fatigue check only applies from Chapter 8 onwards (need chapter info or flag)
        if current_game_state.chapter_id >= CHAPTER_8_ID: # Assuming chapter IDs are comparable
             return unit.current_fatigue >= unit.max_hp
        return False

    # --- Modification Functions ---

    # TDD: Test move_unit updates unit position and map state
    function move_unit(unit_id, new_position):
        unit = get_unit(unit_id)
        old_position = unit.position
        unit.position = new_position
        # Update map_state.unit_positions dictionary
        del current_game_state.map_state.unit_positions[unit_id] # Or update if unit_id is key
        current_game_state.map_state.unit_positions[unit_id] = new_position 
        log("Unit " + unit_id + " moved from " + old_position + " to " + new_position)

    # TDD: Test apply_damage reduces HP correctly, handles death/capture state
    function apply_damage(unit_id, damage, is_capture_attempt=False):
        unit = get_unit(unit_id)
        unit.current_hp = max(0, unit.current_hp - damage)
        log("Unit " + unit_id + " takes " + damage + " damage. HP: " + unit.current_hp + "/" + unit.max_hp)
        if unit.current_hp <= 0:
            if is_capture_attempt:
                 # Unit is captured by the attacker (need attacker info passed in or handled by caller)
                 log("Unit " + unit_id + " was captured!")
                 # Need to set state on the *capturing* unit and this unit
                 # unit.disposition = CAPTURED_BY_ENEMY # Or similar flag
            else:
                 unit.disposition = DEAD
                 log("Unit " + unit_id + " has fallen!")
                 # Remove unit from map positions?
                 del current_game_state.map_state.unit_positions[unit_id]

    # TDD: Test apply_healing increases HP correctly, respects max HP
    function apply_healing(unit_id, amount):
        unit = get_unit(unit_id)
        unit.current_hp = min(unit.max_hp, unit.current_hp + amount)
        log("Unit " + unit_id + " healed for " + amount + ". HP: " + unit.current_hp + "/" + unit.max_hp)

    # TDD: Test add_status_effect adds status correctly, handles duplicates/stacking if applicable
    function add_status_effect(unit_id, status_type, duration):
        unit = get_unit(unit_id)
        # Check if already present, maybe refresh duration? FE5 statuses are permanent until cured.
        if not unit.has_status(status_type):
             unit.status_effects.append(StatusEffectInstance(type=status_type, duration=duration))
             log("Unit " + unit_id + " afflicted with " + status_type)

    # TDD: Test remove_status_effect removes specified status
    function remove_status_effect(unit_id, status_type):
        unit = get_unit(unit_id)
        unit.status_effects = [s for s in unit.status_effects if s.type != status_type]
        log("Unit " + unit_id + " cured of " + status_type)

    # TDD: Test update_fatigue increases fatigue correctly
    function update_fatigue(unit_id, amount):
        unit = get_unit(unit_id)
        unit.current_fatigue += amount
        log("Unit " + unit_id + " fatigue increased by " + amount + ". Current: " + unit.current_fatigue)

    # TDD: Test use_item decrements durability, handles breaking, applies effects
    function use_item(unit_id, item_index, target_id=null):
        # Get item, check durability, apply effect (heal, stat boost, status cure), decrement durability, handle break
        pass

    # TDD: Test trade_items moves items between inventories correctly
    function trade_items(unit1_id, unit2_id, item_transfers):
        # Validate trade, move items between unit1.inventory and unit2.inventory
        # Handle trading with captured units (accessing captive's inventory)
        pass

    # TDD: Test apply_combat_results updates HP, EXP, WExp, status, fatigue based on CombatResult object
    function apply_combat_results(combat_result):
        # Apply damage/healing to attacker/defender
        # Grant EXP to attacker/defender
        # Grant WExp to attacker/defender
        # Apply status effects if any occurred
        # Update fatigue for participants
        # Handle unit death/capture state changes
        pass

    # TDD: Test finalize_chapter_fatigue correctly marks units as fatigued if threshold met
    function finalize_chapter_fatigue():
        # Iterate player units, check fatigue vs max HP, set disposition/flag if needed
        pass

    # TDD: Test finalize_escape_map_captures marks units left on map as captured if Leif escaped
    function finalize_escape_map_captures():
        # Check if map was escape type and Leif escaped
        # If so, iterate remaining player units and set disposition to CAPTURED_BY_ENEMY
        pass

    # ... other modification functions (set_event_flag, level_up_unit, promote_unit, etc.)