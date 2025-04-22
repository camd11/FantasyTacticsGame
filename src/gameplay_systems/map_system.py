"""
Map System Module

This module manages the game board, including its dimensions, terrain properties, and the spatial
relationships between tiles. It provides essential functionalities like pathfinding for unit movement
and visibility calculations, particularly for Fog of War scenarios.
"""

import logging
import heapq
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from unittest.mock import MagicMock

# Import necessary modules/classes
# Removed: from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum
from src.gameplay_systems.fog_of_war_system import FogOfWarSystem, TileVisibilityState, UnitVisibilityData, LightSource

# Constants
IMPASSABLE = float('inf')
TERRAIN_INVALID = TerrainTypeEnum.INVALID

# Stat constants
MOV = "MOV"
TORCH_VISION = "TORCH_VISION"

# Item type constants
WEAPON = "WEAPON"

class PathfindingAlgorithm:
    """
    Implementation of a pathfinding algorithm (Dijkstra's algorithm) for calculating
    reachable tiles and optimal paths.
    """
    
    def __init__(self, get_cost_func: Callable, get_adjacent_func: Callable):
        """
        Initialize the pathfinding algorithm with a cost function and an adjacent tiles function.
        
        Args:
            get_cost_func: Function that returns the movement cost for a position and unit
            get_adjacent_func: Function that returns valid adjacent tiles for a position
        """
        self.get_cost_callback = get_cost_func
        self.get_adjacent_callback = get_adjacent_func # Store the callback
    
    def find_reachable(self, start_pos: Tuple[int, int], movement_points: int, unit_id: str) -> Dict[Tuple[int, int], int]:
        """
        Find all tiles reachable within the given movement points.
        
        Args:
            start_pos: Starting position (x, y)
            movement_points: Available movement points
            unit_id: ID of the unit moving
            
        Returns:
            Dictionary mapping reachable positions to their movement cost
        """
        # Implementation of Dijkstra's algorithm
        visited = {}  # Position -> cost
        # Use heapq: store (cost, position)
        frontier = [(0, start_pos)]
        heapq.heapify(frontier) # Not strictly necessary as it starts with one element
        came_from = {}  # Position -> previous position (for path reconstruction)
        
        # Add starting position
        visited[start_pos] = 0
        
        # Process nodes in order of increasing cost
        while frontier:
            # Get the node with the lowest cost using heapq
            current_cost, current_pos = heapq.heappop(frontier)
            
            # If we've already found a better path to this node, skip it
            # Optimization: If we found a shorter path already, skip
            # This is important with heapq as duplicates might exist
            if current_cost > visited.get(current_pos, IMPASSABLE):
                 continue
            
            # Use the callback to get neighbors
            neighbors = self.get_adjacent_callback(current_pos)
            
            for neighbor in neighbors:
                # Log current position and cost
                logging.debug(f"Pathfinding: Current position {current_pos}, current cost {current_cost}")
                logging.debug(f"Pathfinding: Considering neighbor {neighbor}")
                
                # Get the cost to move to this neighbor
                tile_cost = self.get_cost_callback(neighbor, unit_id)
                logging.debug(f"Pathfinding: Tile cost for {neighbor} is {tile_cost}")
                
                # If the tile is impassable, skip it
                if tile_cost == IMPASSABLE:
                    logging.debug(f"Pathfinding: Neighbor {neighbor} is impassable, skipping")
                    continue
                
                # Calculate the total cost to reach this neighbor
                new_cost = current_cost + tile_cost
                logging.debug(f"Pathfinding: New cost to reach {neighbor} is {new_cost}")
                
                # If we've found a better path to this neighbor, update it
                # Check if within movement range AND is a better path
                if new_cost <= movement_points and new_cost < visited.get(neighbor, IMPASSABLE):
                    logging.debug(f"Pathfinding: Found better path to {neighbor} (cost: {new_cost}, within movement limit: {movement_points})")
                    visited[neighbor] = new_cost
                    came_from[neighbor] = current_pos
                    # Add to frontier using heapq
                    heapq.heappush(frontier, (new_cost, neighbor))
                else:
                    logging.debug(f"Pathfinding: No better path to {neighbor} (new cost: {new_cost}, existing cost: {visited.get(neighbor, IMPASSABLE)}, movement limit: {movement_points})")
        
        # Store the came_from dictionary for path reconstruction
        self.came_from = came_from
        
        return visited
    
    def reconstruct_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], unit_id: str) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start_pos to end_pos using the results from find_reachable.
        Ensures find_reachable is called first if necessary.

        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            unit_id: ID of the unit moving
            
        Returns:
            List of positions representing the path [start_pos, ..., end_pos], or empty list if unreachable.
        """
        # Always run find_reachable to populate came_from for the specific unit and start position.
        # Use a very large movement range to check general reachability.
        # This also calculates self.came_from internally.
        visited_nodes = self.find_reachable(start_pos, 999, unit_id) 

        # Check if the end position is reachable at all (present in visited nodes)
        if end_pos not in visited_nodes:
            logging.debug(f"Pathfinding reconstruct_path: Target {end_pos} is not reachable from {start_pos} for unit {unit_id}.")
            return []
            
        # Check if came_from was actually populated (should be if find_reachable ran)
        if not hasattr(self, 'came_from'):
             logging.error(f"Pathfinding reconstruct_path: came_from dictionary not found after find_reachable for unit {unit_id}.")
             return []

        # Reconstruct the path safely
        path = []
        current = end_pos
        # Add a safeguard against infinite loops (e.g., max path length)
        max_steps = 1000 # Arbitrarily large number
        steps = 0

        while current != start_pos and steps < max_steps:
            path.append(current)
            # Check if current node is in came_from before accessing
            if current not in self.came_from:
                 logging.error(f"Pathfinding reconstruct_path: Node {current} not found in came_from during reconstruction from {start_pos} to {end_pos} for unit {unit_id}. came_from: {self.came_from}")
                 return [] # Path reconstruction failed
            current = self.came_from[current]
            steps += 1

        if steps >= max_steps:
            logging.error(f"Pathfinding reconstruct_path: Exceeded max steps ({max_steps}) during reconstruction from {start_pos} to {end_pos} for unit {unit_id}. Potential loop?")
            return []
            
        # Add the start position
        path.append(start_pos)
        
        # Reverse the path to get [start_pos, ..., end_pos]
        path.reverse()
        
        return path
    
    def find_path_to_nearest_attack_position(self, attacker_unit, target_unit, movement_points: int) -> Optional[List[Tuple[int, int]]]:
        """
        Find the shortest path to a tile adjacent to the target unit that is reachable by the attacker.

        Args:
            attacker_unit: The attacking unit's state object.
            target_unit: The target unit's state object.
            movement_points: The attacker's available movement points.

        Returns:
            The shortest path list to a valid adjacent tile, or None if no such path exists.
        """
        attacker_id = attacker_unit.unit_id
        start_pos = attacker_unit.position
        target_pos = target_unit.position
        
        # 1. Find all tiles adjacent to the target using the callback
        adjacent_tiles = self.get_adjacent_callback(target_pos)
        
        # 2. Find all reachable tiles for the attacker
        reachable_tiles = self.find_reachable(start_pos, movement_points, attacker_id)
        
        # 3. Find adjacent tiles that are also reachable
        valid_attack_positions = []
        for adj_tile in adjacent_tiles:
            if adj_tile in reachable_tiles:
                # Optional: Check if the tile itself is passable (redundant if find_reachable handles this)
                cost_to_reach = reachable_tiles[adj_tile]
                # Optional: Check if tile is occupied by an *ally* (enemies usually okay to path through)
                # Requires GameStateManager access - potentially add check here if needed.
                valid_attack_positions.append((adj_tile, cost_to_reach))
        
        if not valid_attack_positions:
            logging.debug(f"Pathfinding: No reachable tiles adjacent to target {target_pos} found for {attacker_id}.")
            return None
            
        # 4. Sort valid positions by cost (shortest path first)
        valid_attack_positions.sort(key=lambda x: x[1])
        
        # 5. Reconstruct path to the nearest valid position
        nearest_pos, cost = valid_attack_positions[0]
        path = self.reconstruct_path(start_pos, nearest_pos, attacker_id)
        
        if path:
            logging.debug(f"Pathfinding: Found path to nearest attack position {nearest_pos} for {attacker_id}: {path}")
            return path
        else:
            # This should ideally not happen if the tile was in reachable_tiles
            logging.warning(f"Pathfinding: Could not reconstruct path to {nearest_pos} for {attacker_id}, even though it was found reachable.")
            return None
    
    def find_path_towards_target(self, unit_state, target_pos: Tuple[int, int], movement_points: int) -> Optional[List[Tuple[int, int]]]:
        """
        Find the path to the reachable tile that is closest to the target position.

        Args:
            unit_state: The unit's state object.
            target_pos: The target coordinate (x, y).
            movement_points: The unit's available movement points.

        Returns:
            The path to the closest reachable tile, or None if no path exists or no tiles are reachable.
        """
        unit_id = unit_state.unit_id
        start_pos = unit_state.position

        # 1. Find all reachable tiles
        reachable_tiles = self.find_reachable(start_pos, movement_points, unit_id)

        if not reachable_tiles:
            logging.debug(f"Pathfinding: No reachable tiles found for {unit_id} from {start_pos}.")
            return None

        # 2. Find the reachable tile closest to the target position
        closest_tile = None
        min_dist = float('inf')

        for tile in reachable_tiles.keys():
            # Using Manhattan distance for simplicity
            dist = abs(tile[0] - target_pos[0]) + abs(tile[1] - target_pos[1])
            if dist < min_dist:
                min_dist = dist
                closest_tile = tile

        if not closest_tile:
            # Should not happen if reachable_tiles is not empty
            logging.warning(f"Pathfinding: Could not determine closest reachable tile to {target_pos} for {unit_id}.")
            return None

        # 3. Reconstruct the path to this closest tile
        path = self.reconstruct_path(start_pos, closest_tile, unit_id)

        if path:
            logging.debug(f"Pathfinding: Found path towards {target_pos} (closest reachable is {closest_tile}) for {unit_id}: {path}")
            return path
        else:
            logging.warning(f"Pathfinding: Could not reconstruct path to closest tile {closest_tile} for {unit_id}.")
            return None
    
    def _get_adjacent_tiles(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the valid adjacent tiles for a position, checking map boundaries.

        Args:
            position: Position (x, y)

        Returns:
            List of valid adjacent positions within map bounds.
        """
        from src.core_engine.game_state import GameStateManager # Moved import here

        x, y = position
        adjacent = []
        potential_neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        if not self.gameStateManager or not self.gameStateManager.current_game_state:
             logging.warning("_get_adjacent_tiles: GameStateManager or current_game_state not available.")
             return []

        # Access map dimensions through map_state
        if not self.gameStateManager.current_game_state.map_state:
            logging.error("_get_adjacent_tiles: current_game_state has no map_state!")
            return []
            
        # Get map dimensions directly from map_state attributes
        map_width = self.gameStateManager.current_game_state.map_state.dimensions[0]
        map_height = self.gameStateManager.current_game_state.map_state.dimensions[1]

        for nx, ny in potential_neighbors:
            if 0 <= nx < map_width and 0 <= ny < map_height:
                adjacent.append((nx, ny))

        return adjacent


class MapSystem:
    """
    Manages the game board, including its dimensions, terrain properties, and the spatial
    relationships between tiles. Provides pathfinding and visibility calculations.
    """
    
    def __init__(self):
        """Initialize the MapSystem."""
        self.gameStateManager = None
        self.fogOfWarSystem = None
        self.dataProvider = None
        self.pathfinder = None
        self._map_objects = {}  # id -> object
        self._map_objects_by_position = {}  # (x, y) -> [objects]
        self._map_objects_by_type = {}  # type -> [objects]
    
    def initialize(self, gameStateManager_instance: 'GameStateManager', dataProvider_instance: DataProvider,
                  unitSystem_instance=None, turnManager_instance=None) -> None:
        """
        Initialize the MapSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            unitSystem_instance: Instance of the UnitSystem (optional)
            turnManager_instance: Instance of the TurnManager (optional)
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        # Pass both callbacks to the PathfindingAlgorithm constructor
        self.pathfinder = PathfindingAlgorithm(self.get_movement_cost_func, self._get_adjacent_tiles)
        
        # Initialize the FogOfWarSystem
        self.fogOfWarSystem = FogOfWarSystem()
        self.fogOfWarSystem.initialize(
            gameStateManager_instance,
            dataProvider_instance,
            self,  # Pass self as the mapSystem_instance
            unitSystem_instance,
            turnManager_instance
        )
        
        logging.info("MapSystem initialized.")
        
        # Initialize map objects collections
        self._map_objects = {}
        self._map_objects_by_position = {}
        self._map_objects_by_type = {}
    
    # --- Terrain Queries ---
    
    def get_terrain_id_at(self, position: Tuple[int, int]) -> str:
        """
        Get the terrain ID at the specified position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Terrain ID as a string
        """
        from src.core_engine.game_state import GameStateManager # Moved import here
        terrain_type = self.gameStateManager.get_terrain_type(position)
        if terrain_type == TERRAIN_INVALID:
            return "INVALID"
        
        # Convert TerrainTypeEnum to string ID if needed
        if isinstance(terrain_type, TerrainTypeEnum):
            if terrain_type == TerrainTypeEnum.PLAIN:
                return "PLAINS"
            return terrain_type.name
        
        return terrain_type
    
    def get_terrain_data_at(self, position: Tuple[int, int]) -> Optional[Any]:
        """
        Get the terrain data at the specified position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            TerrainData object or None if invalid
        """
        terrain_id = self.get_terrain_id_at(position)
        if terrain_id == "INVALID":
            return None
        
        return self.dataProvider.get_terrain_data(terrain_id)
    
    def get_terrain_properties(self, position: Tuple[int, int]) -> Optional[Dict[str, Any]]:
        """
        Get the properties of the terrain at the specified position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Dictionary of terrain properties or None if invalid
        """
        terrain_type = self.gameStateManager.get_terrain_type(position)
        if terrain_type == TERRAIN_INVALID:
            return None
        
        properties = {}
        terrain_data = self.dataProvider.get_terrain_data(terrain_type)
        if terrain_data:
            properties['type'] = terrain_type
            properties['name'] = terrain_data.name
            properties['bonuses'] = terrain_data.bonuses
            properties['is_healing'] = terrain_data.is_healing
            properties['is_indoor'] = terrain_data.is_indoor
            # Add other relevant properties
        
        return properties
    
    def get_movement_cost(self, position: Tuple[int, int], unit_id: str) -> int:
        """
        Get the movement cost for a unit to move to a specific position.
        
        Args:
            position: Position (x, y)
            unit_id: ID of the unit moving
            
        Returns:
            Movement cost (IMPASSABLE if the tile is impassable)
        """
        from src.core_engine.game_state import GameStateManager # Moved import here
        # Log input parameters
        logging.debug(f"MapSystem.get_movement_cost: Calculating cost for position {position}, unit_id {unit_id}")
        
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            logging.debug(f"MapSystem.get_movement_cost: Unit {unit_id} not found, returning IMPASSABLE")
            return IMPASSABLE
        
        terrain_type = self.gameStateManager.get_terrain_type(position)
        logging.debug(f"MapSystem.get_movement_cost: Terrain type at {position} is {terrain_type}")
        
        if terrain_type == TERRAIN_INVALID:
            logging.debug(f"MapSystem.get_movement_cost: Invalid terrain at {position}, returning IMPASSABLE")
            return IMPASSABLE
        
        # Check if the tile is occupied by another unit
        occupying_unit_id = None
        if self.gameStateManager and self.gameStateManager.current_game_state and self.gameStateManager.current_game_state.map_state:
            for uid, pos in self.gameStateManager.current_game_state.map_state.unit_positions.items():
                if pos == position and uid != unit_id:
                    occupying_unit_id = uid
                    break
        
        if occupying_unit_id:
            occupying_unit = self.gameStateManager.get_unit(occupying_unit_id)
            if occupying_unit:
                # Check if the occupying unit is an ally
                occupying_unit_faction = occupying_unit.faction
                unit_faction = unit.faction
                
                # Allow moving through enemies, but not allies
                if occupying_unit_faction == unit_faction:
                    logging.debug(f"MapSystem.get_movement_cost: Tile {position} is occupied by ally {occupying_unit.id}, impassable for {unit_id}")
                    return IMPASSABLE
                # else: # Tile occupied by an enemy - allow passage
                #    logging.debug(f"MapSystem.get_movement_cost: Tile {position} is occupied by enemy {occupying_unit.id}, allowing passage for {unit_id}")

        # Get unit's movement type
        unit_class_id = unit.class_id
        
        class_data = self.dataProvider.get_class_data(unit_class_id)
        movement_type = class_data.movement_type
        logging.debug(f"MapSystem.get_movement_cost: Unit {unit_id} has movement type {movement_type}")
        
        # Handle Dismount state affecting movement type
        is_mounted = self._is_class_mounted(unit_class_id)
        is_dismounted = self._is_unit_dismounted(unit)
        
        if is_mounted and is_dismounted:
            # Use dismounted movement type (likely infantry or specific dismount type)
            dismount_class_id = class_data.dismount_class_id
            if dismount_class_id:
                dismount_class_data = self.dataProvider.get_class_data(dismount_class_id)
                movement_type = dismount_class_data.movement_type
            else:  # Default to infantry if no specific dismount class
                movement_type = MovementTypeEnum.INFANTRY
        elif is_mounted and not is_dismounted and self._is_terrain_indoor(position):
            # Mounted unit cannot enter indoor tile
            return IMPASSABLE
        # Log the terrain_type enum value before calling get_terrain_cost
        logging.debug(f"MapSystem.get_movement_cost: Target ({position[0]},{position[1]}), TerrainType: {terrain_type}")
        
        cost = self.dataProvider.get_terrain_cost(terrain_type, movement_type)
        logging.debug(f"MapSystem.get_movement_cost: Final cost for {unit_id} to move to {position} is {cost}")
        return cost
    
    # --- Pathfinding ---
    
    def _get_adjacent_tiles(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the valid adjacent tiles for a position, checking map boundaries.

        Args:
            position: Position (x, y)

        Returns:
            List of valid adjacent positions within map bounds.
        """
        from src.core_engine.game_state import GameStateManager # Moved import here

        x, y = position
        adjacent = []
        potential_neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        if not self.gameStateManager or not self.gameStateManager.current_game_state:
             logging.warning("_get_adjacent_tiles: GameStateManager or current_game_state not available.")
             return []

        # Access map dimensions through map_state
        if not self.gameStateManager.current_game_state.map_state:
            logging.error("_get_adjacent_tiles: current_game_state has no map_state!")
            return []
            
        # Get map dimensions directly from map_state attributes
        map_width = self.gameStateManager.current_game_state.map_state.dimensions[0]
        map_height = self.gameStateManager.current_game_state.map_state.dimensions[1]

        for nx, ny in potential_neighbors:
            if 0 <= nx < map_width and 0 <= ny < map_height:
                adjacent.append((nx, ny))

        return adjacent

    def get_reachable_tiles(self, unit_id: str) -> Set[Tuple[int, int]]:
        """
        Get the set of tiles that a unit can reach with its movement points.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Set of reachable positions
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return set()
        
        start_pos = unit.position
        # Check both stats and base_stats for MOV to handle different unit representations
        movement_points = 0
        if hasattr(unit, 'stats') and "MOV" in unit.stats:
            movement_points = unit.stats["MOV"]
        elif hasattr(unit, 'base_stats') and "MOV" in unit.base_stats:
            movement_points = unit.base_stats["MOV"]
        
        # Use the pathfinder instance
        reachable_nodes = self.pathfinder.find_reachable(start_pos, movement_points, unit_id)
        
        # Convert to just set of positions
        reachable_tiles = set(reachable_nodes.keys())
        return reachable_tiles
    
    def get_path(self, unit_id: str, end_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the path from a unit's current position to a target position.
        
        Args:
            unit_id: ID of the unit
            end_pos: Target position (x, y)
            
        Returns:
            List of positions representing the path
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return []
        
        start_pos = unit.position
        path = self.pathfinder.reconstruct_path(start_pos, end_pos, unit_id)
        return path
    
    # --- Attack Range ---
    
    def get_attackable_tiles(self, unit_id: str) -> Set[Tuple[int, int]]:
        """
        Get the set of tiles that a unit can attack with its equipped weapon.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Set of attackable positions
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or unit.equipped_weapon_index < 0:
            return set()
        
        weapon = unit.inventory[unit.equipped_weapon_index]
        item_data = self.dataProvider.get_item_data(weapon.item_id)
        if not item_data or item_data.type != WEAPON:
            return set()
        
        min_range = item_data.range_min
        max_range = item_data.range_max
        start_pos = unit.position
        
        attackable_tiles = set()
        map_width, map_height = self.gameStateManager.get_map_dimensions()
        
        for x in range(map_width):
            for y in range(map_height):
                pos = (x, y)
                distance = self.calculate_manhattan_distance(start_pos, pos)
                if min_range <= distance <= max_range:
                    # Add line-of-sight check if necessary
                    if self.has_line_of_sight(start_pos, pos):
                        attackable_tiles.add(pos)
        
        return attackable_tiles
    
    def get_units_in_attack_range(self, unit_id: str) -> List[str]:
        """
        Get the list of enemy units that a unit can attack with its equipped weapon.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of enemy unit IDs within attack range
        """
        attacker = self.gameStateManager.get_unit(unit_id)
        if not attacker:
            return []
        
        attackable_tiles = self.get_attackable_tiles(unit_id)
        target_units = []
        
        for tile in attackable_tiles:
            target_id = self._get_unit_at(tile)
            if target_id:
                target_unit = self.gameStateManager.get_unit(target_id)
                # Check if target is an enemy and active
                if target_unit and target_unit.faction != attacker.faction and target_unit.disposition == "ACTIVE":
                    target_units.append(target_id)
        
        return target_units
    
    # --- Visibility (Fog of War) ---
    
    def get_visible_tiles(self, faction) -> Set[Tuple[int, int]]:
        """
        Get the set of tiles that are visible to a faction.
        
        Args:
            faction: The faction to check visibility for
            
        Returns:
            Set of visible positions
        """
        if not self._is_fog_of_war_active():
            # If no fog, all tiles are visible
            map_width, map_height = self.gameStateManager.get_map_dimensions()
            return set([(x, y) for x in range(map_width) for y in range(map_height)])
        
        # Get all units of the faction
        units = self.gameStateManager.get_units_by_faction(faction)
        
        # Calculate visible tiles based on unit positions and vision ranges
        visible_set = set()
        
        for unit in units:
            # Get the unit's vision range (base + any bonuses from status effects)
            vision_range = self._get_class_vision_range(unit.class_id)
            torch_bonus = self._get_status_effect_bonus(unit, TORCH_VISION)
            total_vision = vision_range + torch_bonus
            
            # Calculate the visible area for this unit
            unit_visible_area = self.calculate_line_of_sight_area(unit.position, total_vision)
            
            # Add to the overall visible set
            visible_set.update(unit_visible_area)
        
        return visible_set
    
    def is_tile_visible(self, position: Tuple[int, int], faction) -> bool:
        """
        Check if a tile is visible to a faction.
        
        Args:
            position: Position (x, y)
            faction: The faction to check visibility for
            
        Returns:
            True if the tile is visible, False otherwise
        """
        if not self._is_fog_of_war_active():
            return True
            
        # Get the set of visible tiles for this faction
        visible_tiles = self.get_visible_tiles(faction)
        
        # Check if the position is in the visible set
        return position in visible_tiles
    
    # --- Helper Functions ---
    
    def get_movement_cost_func(self, position: Tuple[int, int], unit_id: str) -> int:
        """
        Wrapper function to pass to the pathfinder instance.
        
        Args:
            position: Position (x, y)
            unit_id: ID of the unit moving
            
        Returns:
            Movement cost
        """
        return self.get_movement_cost(position, unit_id)
    
    def calculate_manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def has_line_of_sight(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> bool:
        """
        Check if there is a line of sight between two positions.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            
        Returns:
            True if there is a line of sight, False otherwise
        """
        # Basic implementation that always returns True
        # In a real implementation, this would check for obstacles between the positions
        # For now, we'll assume there's always line of sight
        return True
    
    def calculate_line_of_sight_area(self, center_pos: Tuple[int, int], range_val: int) -> Set[Tuple[int, int]]:
        """
        Calculate the area that is visible from a position within a certain range.
        
        Args:
            center_pos: Center position (x, y)
            range_val: Vision range
            
        Returns:
            Set of visible positions
        """
        visible_area = set()
        map_width, map_height = self.gameStateManager.get_map_dimensions()
        
        # Add the center position itself
        visible_area.add(center_pos)
        
        # Check all positions within the map boundaries
        for x in range(max(0, center_pos[0] - range_val), min(map_width, center_pos[0] + range_val + 1)):
            for y in range(max(0, center_pos[1] - range_val), min(map_height, center_pos[1] + range_val + 1)):
                pos = (x, y)
                # Calculate Manhattan distance
                distance = self.calculate_manhattan_distance(center_pos, pos)
                # Add position if within range and has line of sight
                if distance <= range_val and self.has_line_of_sight(center_pos, pos):
                    visible_area.add(pos)
        
        return visible_area
    
    # --- Private Helper Methods ---
    
    def _get_unit_at(self, position: Tuple[int, int]) -> Optional[str]:
        """
        Get the ID of the unit at a position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Unit ID or None if no unit is present
        """
        from src.core_engine.game_state import GameStateManager # Moved import here
        # This is a placeholder. The actual implementation would depend on how
        # the GameStateManager tracks unit positions.
        unit_info = self.gameStateManager.get_unit_at(position)
        return unit_info[0] if unit_info else None
    
    def _is_class_mounted(self, class_id: str) -> bool:
        """
        Check if a class is mounted.
        
        Args:
            class_id: ID of the class
            
        Returns:
            True if the class is mounted, False otherwise
        """
        from src.core_engine.game_state import GameStateManager # Moved import here
        class_data = self.dataProvider.get_class_data(class_id)
        return class_data and class_data.dismount_class_id is not None
    
    def _is_unit_dismounted(self, unit) -> bool:
        """
        Check if a unit is dismounted.
        
        Args:
            unit: Unit object
            
        Returns:
            True if the unit is dismounted, False otherwise
        """
        # This is a placeholder. The actual implementation would depend on how
        # the UnitState tracks dismounted state.
        return hasattr(unit, 'is_dismounted') and unit.is_dismounted
    
    def _is_terrain_indoor(self, position: Tuple[int, int]) -> bool:
        """
        Check if the terrain at a position is indoor.
        
        Args:
            position: Position (x, y)
            
        Returns:
            True if the terrain is indoor, False otherwise
        """
        terrain_type = self.gameStateManager.get_terrain_type(position)
        return self.dataProvider.is_terrain_indoor(terrain_type)
    
    def _is_fog_of_war_active(self) -> bool:
        """
        Check if Fog of War is active for the current chapter.
        
        Returns:
            True if Fog of War is active, False otherwise
        """
        from src.core_engine.game_state import GameStateManager # Moved import here
        # Check if the current chapter has Fog of War enabled
        current_chapter = self.gameStateManager.get_current_chapter()
        if current_chapter and hasattr(current_chapter, 'fog_of_war_enabled'):
            return current_chapter.fog_of_war_enabled
        return False
    
    def _get_class_vision_range(self, class_id: str) -> int:
        """
        Get the vision range for a class.
        
        Args:
            class_id: ID of the class
            
        Returns:
            Vision range
        """
        # This is a placeholder. The actual implementation would depend on how
        # the DataProvider stores class vision range.
        class_data = self.dataProvider.get_class_data(class_id)
        return getattr(class_data, 'vision_range', 3)  # Default to 3
    
    def _get_status_effect_bonus(self, unit, effect_type: str) -> int:
        """
        Get the bonus from a status effect on a unit.
        
        Args:
            unit: Unit object
            effect_type: Type of status effect
            
        Returns:
            Bonus value
        """
        # This is a placeholder. The actual implementation would depend on how
        # the UnitState tracks status effects.
        for status in getattr(unit, 'status_effects', []):
            if status.type == effect_type:
                return status.magnitude
        return 0
    
    def update_tile_terrain(self, position: Tuple[int, int], new_terrain_type: str) -> bool:
        """
        Update the terrain type of a tile.
        
        Args:
            position: Position (x, y)
            new_terrain_type: New terrain type
            
        Returns:
            True if the terrain was updated successfully, False otherwise
        """
        # Check if the position is valid
        map_width, map_height = self.gameStateManager.get_map_dimensions()
        if position[0] < 0 or position[0] >= map_width or position[1] < 0 or position[1] >= map_height:
            logging.warning(f"Cannot update terrain: Position {position} is out of bounds")
            return False
        
        # Update the terrain type in the game state
        self.gameStateManager.set_terrain_type(position, new_terrain_type)
        logging.info(f"Updated terrain at {position} to {new_terrain_type}")
        return True
    
    def update_map_passability(self, position: Tuple[int, int]) -> None:
        """
        Update the passability of a tile and notify pathfinding.
        
        Args:
            position: Position (x, y)
        """
        # This method would typically update any cached pathfinding data
        # For now, we'll just log the update
        logging.info(f"Updated map passability at {position}")
        
    def are_units_adjacent(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """
        Check if two positions are adjacent.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            True if the positions are adjacent, False otherwise
        """
        # Calculate Manhattan distance
        distance = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Positions are adjacent if Manhattan distance is 1
        return distance == 1
    
    # --- Map Objects ---
    
    def add_map_object(self, obj) -> bool:
        """
        Add an object to the map.
        
        Args:
            obj: The object to add (must have id and position attributes)
            
        Returns:
            True if the object was added successfully, False otherwise
        """
        if not hasattr(obj, 'id') or not hasattr(obj, 'position'):
            logging.error("Cannot add map object: Object must have id and position attributes")
            return False
        
        obj_id = obj.id
        position = obj.position
        obj_type = obj.__class__.__name__
        
        # Add to main dictionary
        self._map_objects[obj_id] = obj
        
        # Add to position dictionary
        if position not in self._map_objects_by_position:
            self._map_objects_by_position[position] = []
        self._map_objects_by_position[position].append(obj)
        
        # Add to type dictionary
        if obj_type not in self._map_objects_by_type:
            self._map_objects_by_type[obj_type] = []
        self._map_objects_by_type[obj_type].append(obj)
        
        logging.info(f"Added map object {obj_id} at {position}")
        return True
    
    def remove_map_object(self, obj_id: str) -> bool:
        """
        Remove an object from the map.
        
        Args:
            obj_id: ID of the object to remove
            
        Returns:
            True if the object was removed successfully, False otherwise
        """
        if obj_id not in self._map_objects:
            return False
        
        obj = self._map_objects[obj_id]
        position = obj.position
        obj_type = obj.__class__.__name__
        
        # Remove from main dictionary
        del self._map_objects[obj_id]
        
        # Remove from position dictionary
        if position in self._map_objects_by_position:
            self._map_objects_by_position[position] = [o for o in self._map_objects_by_position[position] if o.id != obj_id]
            if not self._map_objects_by_position[position]:
                del self._map_objects_by_position[position]
        
        # Remove from type dictionary
        if obj_type in self._map_objects_by_type:
            self._map_objects_by_type[obj_type] = [o for o in self._map_objects_by_type[obj_type] if o.id != obj_id]
            if not self._map_objects_by_type[obj_type]:
                del self._map_objects_by_type[obj_type]
        
        logging.info(f"Removed map object {obj_id}")
        return True
    
    def get_object_by_id(self, obj_id: str) -> Optional[Any]:
        """
        Get a map object by ID.
        
        Args:
            obj_id: ID of the object
            
        Returns:
            The object or None if not found
        """
        return self._map_objects.get(obj_id)
    
    def get_object_at(self, position: Tuple[int, int], type: Optional[str] = None) -> Optional[Any]:
        """
        Get an object at a specific position, optionally of a specific type.
        
        Args:
            position: Position (x, y)
            type: Optional type of object to get
            
        Returns:
            The object or None if not found
        """
        if position not in self._map_objects_by_position:
            return None
        
        objects = self._map_objects_by_position[position]
        
        if type:
            # Filter by type
            objects = [obj for obj in objects if obj.__class__.__name__ == type]
        
        # Return the first object (or None if no objects)
        return objects[0] if objects else None
    
    def get_all_objects_of_type(self, type_class) -> List[Any]:
        """
        Get all objects of a specific type.
        
        Args:
            type_class: Class or string name of the type
            
        Returns:
            List of objects of the specified type
        """
        type_name = type_class if isinstance(type_class, str) else type_class.__name__
        return self._map_objects_by_type.get(type_name, [])
    
    def get_los_checker(self) -> Callable:
        """
        Get a function that checks line of sight between two positions.
        
        Returns:
            Function that takes two positions and returns True if there is line of sight
        """
        return self.has_line_of_sight
    
    def calculate_tiles_in_range(self, origin: Tuple[int, int], min_range: int, max_range: int,
                                map_data=None, los_checker=None) -> Set[Tuple[int, int]]:
        """
        Calculate tiles within a range, respecting line of sight.
        
        Args:
            origin: Origin position (x, y)
            min_range: Minimum range
            max_range: Maximum range
            map_data: Optional map data
            los_checker: Optional line of sight checker function
            
        Returns:
            Set of positions within range
        """
        if los_checker is None:
            los_checker = self.has_line_of_sight
            
        valid_tiles = set()
        map_width, map_height = self.get_map_dimensions()
        
        for x in range(max(0, origin[0] - max_range), min(map_width, origin[0] + max_range + 1)):
            for y in range(max(0, origin[1] - max_range), min(map_height, origin[1] + max_range + 1)):
                pos = (x, y)
                distance = self.calculate_manhattan_distance(origin, pos)
                
                if min_range <= distance <= max_range and los_checker(origin, pos):
                    valid_tiles.add(pos)
        
        return valid_tiles
    
    def distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate the Manhattan distance between two positions.
        
        Args:
            pos1: First position (x, y)
            pos2: Second position (x, y)
            
        Returns:
            Manhattan distance
        """
        return self.calculate_manhattan_distance(pos1, pos2)

    def get_width(self) -> int:
        """
        Get the width of the current map.
        
        Returns:
            Width of the map
        """
        if not self.gameStateManager or not self.gameStateManager.current_game_state or not self.gameStateManager.current_game_state.map_state:
            return 0
        
        return self.gameStateManager.current_game_state.map_state.dimensions[0]
    
    def get_height(self) -> int:
        """
        Get the height of the current map.
        
        Returns:
            Height of the map
        """
        if not self.gameStateManager or not self.gameStateManager.current_game_state or not self.gameStateManager.current_game_state.map_state:
            return 0
        
        return self.gameStateManager.current_game_state.map_state.dimensions[1]
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """
        Get the dimensions of the current map (width, height).
        
        Returns:
            Tuple of (width, height)
        """
        return (self.get_width(), self.get_height())