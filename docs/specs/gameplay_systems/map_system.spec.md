# Specification: Map System

**Version:** 1.0
**Date:** 2025-04-05

## 1. Overview

The Map System manages the game board, including its dimensions, terrain properties, and the spatial relationships between tiles. It provides essential functionalities like pathfinding for unit movement and visibility calculations, particularly for Fog of War scenarios. It relies heavily on the `GameStateManager` for current map data and unit positions, and the `DataProvider` for static terrain characteristics.

## 2. Functional Requirements

### 2.1. Map Data Representation
    - Access map dimensions (width, height) from `GameStateManager`.
    - Access terrain type for any given coordinate (x, y) from `GameStateManager`.
    - Access the state of interactable objects (doors, villages) at specific coordinates from `GameStateManager`.

### 2.2. Terrain Information
    - Provide functions to query terrain properties for a given tile using `DataProvider`:
        - Movement cost for a specific unit type/movement type (Ref: `research.md`, Sec 8).
        - Defensive bonus (Def).
        - Avoidance bonus (Avo).
        - Healing properties (+Life) (Ref: `research.md`, Sec 1, 5.6).
        - Special properties (e.g., Seize Point, Escape Point, Village, Chest, Door, Wall).
        - Indoor/Outdoor status (Ref: `research.md`, Sec 3, 8).

### 2.3. Pathfinding
    - Calculate valid movement paths for a selected unit based on:
        - Unit's Movement stat (`GameStateManager`).
        - Unit's movement type and current state (mounted/dismounted) (`GameStateManager`, `DataProvider`).
        - Terrain movement costs (`DataProvider`).
        - Occupied tiles (units cannot pass through enemy units) (`GameStateManager`).
    - Implement an efficient pathfinding algorithm (e.g., A*, Dijkstra) to determine reachable tiles within the unit's movement range.
    - Provide functions to:
        - `get_reachable_tiles(unit_id)`: Returns a set of coordinates the unit can move to.
        - `get_path(unit_id, start_pos, end_pos)`: Returns the sequence of coordinates for a valid path (optional, useful for visualizing movement).

### 2.4. Attack Range Calculation
    - Calculate valid attack targets for a selected unit based on:
        - Unit's equipped weapon range (`GameStateManager`, `DataProvider`).
        - Unit's current position (`GameStateManager`).
        - Line of sight rules (terrain like walls might block attacks, though FE typically allows attacking over low obstacles).
    - Provide functions to:
        - `get_attackable_tiles(unit_id)`: Returns a set of coordinates the unit can target.
        - `get_units_in_attack_range(unit_id)`: Returns a list of enemy unit IDs within attack range.

### 2.5. Visibility (Fog of War)
    - If Fog of War is active for the chapter:
        - Calculate the visible tiles based on player unit positions and their vision range (base vision + Torch item bonus) (Ref: `research.md`, Sec 8, 13).
        - Consider Thieves' extended vision range (`DataProvider`).
        - Consider Torch staff effects (`GameStateManager`).
        - Terrain that blocks line of sight (e.g., high walls, peaks) should limit vision.
    - Provide functions to:
        - `get_visible_tiles(faction)`: Returns the set of coordinates currently visible to the specified faction (primarily Player).
        - `is_tile_visible(position, faction)`: Checks if a specific tile is visible.

## 3. Pseudocode (map_system.py)

```python
# --- map_system.py ---

# Import necessary modules/classes (GameStateManager, DataProvider, PathfindingAlgorithm)
# Import enums (TerrainTypeEnum, MovementTypeEnum, FactionEnum)

class MapSystem:
    gameStateManager = null
    dataProvider = null
    pathfinder = null # Instance of a pathfinding algorithm implementation

    function initialize(gameStateManager_instance, dataProvider_instance):
        gameStateManager = gameStateManager_instance
        dataProvider = dataProvider_instance
        pathfinder = PathfindingAlgorithm(self.get_movement_cost_func) # Pass cost function
        log("MapSystem initialized.")

    # --- Terrain Queries ---

    # TDD: Test get_terrain_properties returns correct data for various terrain types
    function get_terrain_properties(position):
        terrain_type = gameStateManager.get_terrain_type(position)
        if terrain_type == TERRAIN_INVALID:
            return null
        
        properties = {}
        terrain_data = dataProvider.get_terrain_data(terrain_type) # Assumes DP caches this
        if terrain_data:
            properties['type'] = terrain_type
            properties['name'] = terrain_data.name
            properties['bonuses'] = terrain_data.bonuses # {def: X, avo: Y}
            properties['is_healing'] = terrain_data.is_healing
            properties['is_indoor'] = terrain_data.is_indoor
            # Add other relevant properties like is_seize_point, is_village etc. based on terrain_data
        return properties

    # TDD: Test get_movement_cost returns correct cost for different units/terrain/states
    function get_movement_cost(position, unit_id):
        # This function is used by the pathfinder
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return IMPASSABLE 

        terrain_type = gameStateManager.get_terrain_type(position)
        if terrain_type == TERRAIN_INVALID: return IMPASSABLE

        # Check if tile is occupied by an enemy (impassable for movement)
        occupying_unit_id = gameStateManager.get_unit_at(position)
        if occupying_unit_id and occupying_unit_id != unit_id:
             occupying_unit = gameStateManager.get_unit(occupying_unit_id)
             if occupying_unit.faction != unit.faction: # Assuming cannot move through enemies
                  return IMPASSABLE
             # Allow moving through allies? FE5 rule check needed. Assume yes for now.

        class_data = dataProvider.get_class_data(unit.class_id)
        movement_type = class_data.movement_type

        # Handle Dismount state affecting movement type
        is_mounted = dataProvider.is_class_mounted(unit.class_id) # Need this helper in DP
        is_dismounted = unit.is_dismounted() # Need state flag on UnitState
        
        if is_mounted and is_dismounted:
             # Use dismounted movement type (likely infantry or specific dismount type)
             dismount_class_id = class_data.dismount_class_id
             if dismount_class_id:
                  dismount_class_data = dataProvider.get_class_data(dismount_class_id)
                  movement_type = dismount_class_data.movement_type
             else: # Default to infantry if no specific dismount class?
                  movement_type = MOVEMENT_INFANTRY 
        elif is_mounted and not is_dismounted and self.get_terrain_properties(position).get('is_indoor', False):
             # Mounted unit cannot enter indoor tile
             return IMPASSABLE

        cost = dataProvider.get_terrain_cost(terrain_type, movement_type)
        return cost # Returns numeric cost or IMPASSABLE constant

    # --- Pathfinding ---

    # TDD: Test get_reachable_tiles calculates correct range considering terrain and movement points
    function get_reachable_tiles(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return set()

        start_pos = unit.position
        movement_points = unit.base_stats.get(MOV, 0) # Get current Mov stat

        # Use the pathfinder instance
        reachable_nodes = pathfinder.find_reachable(start_pos, movement_points, unit_id) 
        
        # reachable_nodes might be {pos: cost}, convert to just set of positions
        reachable_tiles = set(reachable_nodes.keys())
        return reachable_tiles

    # TDD: Test get_path returns a valid sequence of coordinates
    function get_path(unit_id, end_pos):
        # Optional: If path visualization is needed
        unit = gameStateManager.get_unit(unit_id)
        if not unit: return []
        start_pos = unit.position
        # May need to call pathfinder again or store path info during get_reachable_tiles
        path = pathfinder.reconstruct_path(start_pos, end_pos, unit_id) # Assumes pathfinder stores parent pointers
        return path

    # --- Attack Range ---

    # TDD: Test get_attackable_tiles calculates range correctly for different weapons/positions
    function get_attackable_tiles(unit_id):
        unit = gameStateManager.get_unit(unit_id)
        if not unit or unit.equipped_weapon_index < 0: return set()

        weapon = unit.inventory[unit.equipped_weapon_index]
        item_data = dataProvider.get_item_data(weapon.item_id)
        if not item_data or item_data.type != WEAPON: return set()

        min_range = item_data.range_min
        max_range = item_data.range_max
        start_pos = unit.position
        
        attackable_tiles = set()
        map_width, map_height = gameStateManager.get_map_dimensions()

        for x in range(map_width):
            for y in range(map_height):
                pos = (x, y)
                distance = calculate_manhattan_distance(start_pos, pos) # Or appropriate distance metric
                if min_range <= distance <= max_range:
                    # Add line-of-sight check if necessary (e.g., cannot shoot through thick walls)
                    if self.has_line_of_sight(start_pos, pos):
                         attackable_tiles.add(pos)
        
        return attackable_tiles

    # TDD: Test get_units_in_attack_range finds correct enemy units
    function get_units_in_attack_range(unit_id):
        attacker = gameStateManager.get_unit(unit_id)
        if not attacker: return []

        attackable_tiles = self.get_attackable_tiles(unit_id)
        target_units = []
        for tile in attackable_tiles:
            target_id = gameStateManager.get_unit_at(tile)
            if target_id:
                target_unit = gameStateManager.get_unit(target_id)
                # Check if target is an enemy
                if target_unit and target_unit.faction != attacker.faction and target_unit.disposition == ACTIVE:
                     target_units.append(target_id)
        return target_units

    # --- Visibility (Fog of War) ---

    # TDD: Test get_visible_tiles calculates vision correctly with units, torches, fog
    function get_visible_tiles(faction):
        if not gameStateManager.is_fog_of_war_active(): # Check global state
             # If no fog, all tiles are visible
             map_width, map_height = gameStateManager.get_map_dimensions()
             return set([(x,y) for x in range(map_width) for y in range(map_height)])

        visible_set = set()
        units = gameStateManager.get_units_by_faction(faction)
        
        for unit in units:
            base_vision = dataProvider.get_class_data(unit.class_id).vision_range # Base vision per class/unit? FE5 uses 3 base?
            # Check for Torch item effect
            torch_bonus = unit.get_status_effect_bonus(TORCH_VISION) # Check active statuses
            vision_range = base_vision + torch_bonus
            
            # Add tiles within vision range, considering line of sight
            unit_visible = self.calculate_line_of_sight_area(unit.position, vision_range)
            visible_set.update(unit_visible)

        # Add vision from Torch Staff effects (need state for active torch staves)
        # torch_staff_areas = gameStateManager.get_active_torch_staff_areas()
        # for area in torch_staff_areas: visible_set.update(area)

        return visible_set

    # TDD: Test is_tile_visible checks against the calculated visible set
    function is_tile_visible(position, faction):
        # Simple check against the pre-calculated set for the frame/turn
        visible_tiles = self.get_visible_tiles(faction) # Might cache this per turn start
        return position in visible_tiles

    # --- Helper Functions ---

    function get_movement_cost_func(position, unit_id):
        # Wrapper to pass the method to the pathfinder instance
        return self.get_movement_cost(position, unit_id)

    function calculate_manhattan_distance(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # TDD: Test line of sight is blocked correctly by walls/terrain
    function has_line_of_sight(start_pos, end_pos):
        # Basic check: Assume true for now.
        # Implement Bresenham's line algorithm or similar, checking terrain properties of intermediate tiles.
        # Return False if a blocking terrain type (e.g., High Wall, Peak) is encountered.
        # Need terrain property 'blocks_line_of_sight' from DataProvider.
        return True 

    # TDD: Test line of sight area calculation handles range and obstacles
    function calculate_line_of_sight_area(center_pos, range_val):
        # Use a visibility algorithm (e.g., shadow casting, recursive shadowcasting)
        # Start from center_pos and explore outwards up to range_val.
        # Check has_line_of_sight for each tile relative to the center.
        # Return set of visible coordinates.
        # Simple placeholder: return all tiles within manhattan distance for now
        visible_area = set()
        map_width, map_height = gameStateManager.get_map_dimensions()
        cx, cy = center_pos
        for x in range(max(0, cx - range_val), min(map_width, cx + range_val + 1)):
             for y in range(max(0, cy - range_val), min(map_height, cy + range_val + 1)):
                  if calculate_manhattan_distance(center_pos, (x,y)) <= range_val:
                       if self.has_line_of_sight(center_pos, (x,y)): # Check LoS
                            visible_area.add((x,y))
        return visible_area

```

```python
# --- pathfinding_algorithm.py (Conceptual Example) ---

IMPASSABLE = float('inf')

class PathfindingAlgorithm: # e.g., A*
    get_cost_callback = null

    function initialize(get_cost_func):
        get_cost_callback = get_cost_func # Function(position, unit_id) -> cost

    # TDD: Test find_reachable explores correctly based on cost and movement points
    function find_reachable(start_pos, movement_points, unit_id):
        # Implementation of A* or Dijkstra's algorithm
        # Use get_cost_callback(neighbor_pos, unit_id) to get edge weights
        # Keep track of visited nodes and cost_so_far
        # Return dictionary {position: cost} for all reachable nodes within movement_points
        pass

    # TDD: Test reconstruct_path builds the path correctly from parent pointers
    function reconstruct_path(start_pos, end_pos, unit_id):
        # Backtrack from end_pos using parent pointers stored during find_reachable
        # Return list of coordinates [start_pos, ..., end_pos]
        pass