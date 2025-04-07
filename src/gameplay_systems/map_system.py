"""
Map System Module

This module manages the game board, including its dimensions, terrain properties, and the spatial
relationships between tiles. It provides essential functionalities like pathfinding for unit movement
and visibility calculations, particularly for Fog of War scenarios.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Callable
from unittest.mock import MagicMock

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager
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
    
    def __init__(self, get_cost_func: Callable):
        """
        Initialize the pathfinding algorithm with a cost function.
        
        Args:
            get_cost_func: Function that returns the movement cost for a position and unit
        """
        self.get_cost_callback = get_cost_func
    
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
        frontier = [(0, start_pos)]  # (cost, position)
        came_from = {}  # Position -> previous position (for path reconstruction)
        
        # Add starting position
        visited[start_pos] = 0
        
        # Process nodes in order of increasing cost
        while frontier:
            # Get the node with the lowest cost
            current_cost, current_pos = min(frontier)
            frontier.remove((current_cost, current_pos))
            
            # If we've already found a better path to this node, skip it
            if current_cost > visited.get(current_pos, IMPASSABLE):
                continue
            
            
            # Get neighbors (adjacent tiles)
            neighbors = self._get_adjacent_tiles(current_pos)
            
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
                if new_cost < visited.get(neighbor, IMPASSABLE) and new_cost <= movement_points:
                    logging.debug(f"Pathfinding: Found better path to {neighbor} (cost: {new_cost}, within movement limit: {movement_points})")
                    visited[neighbor] = new_cost
                    came_from[neighbor] = current_pos
                    frontier.append((new_cost, neighbor))
                else:
                    logging.debug(f"Pathfinding: No better path to {neighbor} (new cost: {new_cost}, existing cost: {visited.get(neighbor, IMPASSABLE)}, movement limit: {movement_points})")
        
        # Store the came_from dictionary for path reconstruction
        self.came_from = came_from
        
        return visited
    
    def reconstruct_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], unit_id: str) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start_pos to end_pos.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            unit_id: ID of the unit moving
            
        Returns:
            List of positions representing the path [start_pos, ..., end_pos]
        """
        # If we don't have a path to the end position, return an empty list
        if not hasattr(self, 'came_from') or end_pos not in self.came_from:
            # Try to find a path first
            self.find_reachable(start_pos, 99, unit_id)  # Use a large number for movement points
            
            # If we still don't have a path, return an empty list
            if end_pos not in self.came_from:
                return []
        
        # Reconstruct the path
        current = end_pos
        path = [current]
        
        while current != start_pos:
            current = self.came_from[current]
            path.append(current)
        
        # Reverse the path to get [start_pos, ..., end_pos]
        path.reverse()
        
        return path
    
    def _get_adjacent_tiles(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the adjacent tiles for a position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            List of adjacent positions
        """
        x, y = position
        return [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]


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
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider,
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
        self.pathfinder = PathfindingAlgorithm(self.get_movement_cost_func)
        
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
    
    # --- Terrain Queries ---
    
    def get_terrain_id_at(self, position: Tuple[int, int]) -> str:
        """
        Get the terrain ID at the specified position.
        
        Args:
            position: Position (x, y)
            
        Returns:
            Terrain ID as a string
        """
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
        
        # Check if tile is occupied by an enemy (impassable for movement)
        occupying_unit_id = self._get_unit_at(position)
        logging.debug(f"MapSystem.get_movement_cost: Occupying unit at {position} is {occupying_unit_id}")
        
        if occupying_unit_id and occupying_unit_id != unit_id:
            occupying_unit = self.gameStateManager.get_unit(occupying_unit_id)
            logging.debug(f"MapSystem.get_movement_cost: Checking if unit {occupying_unit_id} blocks movement")
            
            if occupying_unit.faction != unit.faction:  # Cannot move through enemies
                logging.debug(f"MapSystem.get_movement_cost: Enemy unit {occupying_unit_id} blocks movement, returning IMPASSABLE")
                return IMPASSABLE
            logging.debug(f"MapSystem.get_movement_cost: Allied unit {occupying_unit_id} does not block movement (Thracia 776 rule)")
            # Allow moving through allies (Thracia 776 rule)
        
        class_data = self.dataProvider.get_class_data(unit.class_id)
        movement_type = class_data.movement_type
        logging.debug(f"MapSystem.get_movement_cost: Unit {unit_id} has movement type {movement_type}")
        
        # Handle Dismount state affecting movement type
        is_mounted = self._is_class_mounted(unit.class_id)
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
        # This is a placeholder. The actual implementation would depend on how
        # the GameStateManager tracks unit positions.
        for unit_id, unit in self.gameStateManager.current_game_state.unit_states.items():
            if unit.position == position:
                return unit_id
        return None
    
    def _is_class_mounted(self, class_id: str) -> bool:
        """
        Check if a class is mounted.
        
        Args:
            class_id: ID of the class
            
        Returns:
            True if the class is mounted, False otherwise
        """
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