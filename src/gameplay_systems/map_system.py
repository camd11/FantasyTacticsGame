"""
Map System Module

This module manages the game board, including its dimensions, terrain properties, and the spatial
relationships between tiles. It provides essential functionalities like pathfinding for unit movement
and visibility calculations, particularly for Fog of War scenarios.
"""

import logging
from typing import Dict, List, Set, Tuple, Optional, Any, Callable

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum

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
                # Get the cost to move to this neighbor
                tile_cost = self.get_cost_callback(neighbor, unit_id)
                
                # If the tile is impassable, skip it
                if tile_cost == IMPASSABLE:
                    continue
                
                # Calculate the total cost to reach this neighbor
                new_cost = current_cost + tile_cost
                
                # If we've found a better path to this neighbor, update it
                if new_cost < visited.get(neighbor, IMPASSABLE) and new_cost <= movement_points:
                    visited[neighbor] = new_cost
                    came_from[neighbor] = current_pos
                    frontier.append((new_cost, neighbor))
        
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
        self.dataProvider = None
        self.pathfinder = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider) -> None:
        """
        Initialize the MapSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.pathfinder = PathfindingAlgorithm(self.get_movement_cost_func)
        logging.info("MapSystem initialized.")
    
    # --- Terrain Queries ---
    
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
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return IMPASSABLE
        
        terrain_type = self.gameStateManager.get_terrain_type(position)
        if terrain_type == TERRAIN_INVALID:
            return IMPASSABLE
        
        # Check if tile is occupied by an enemy (impassable for movement)
        occupying_unit_id = self._get_unit_at(position)
        if occupying_unit_id and occupying_unit_id != unit_id:
            occupying_unit = self.gameStateManager.get_unit(occupying_unit_id)
            if occupying_unit.faction != unit.faction:  # Cannot move through enemies
                return IMPASSABLE
            # Allow moving through allies (Thracia 776 rule)
        
        class_data = self.dataProvider.get_class_data(unit.class_id)
        movement_type = class_data.movement_type
        
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
        
        cost = self.dataProvider.get_terrain_cost(terrain_type, movement_type)
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
        if hasattr(unit, 'stats') and MOV in unit.stats:
            movement_points = unit.stats[MOV]
        elif hasattr(unit, 'base_stats') and MOV in unit.base_stats:
            movement_points = unit.base_stats[MOV]
        
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
        
        visible_set = set()
        units = self.gameStateManager.get_units_by_faction(faction)
        
        for unit in units:
            base_vision = self._get_class_vision_range(unit.class_id)
            # Check for Torch item effect
            torch_bonus = self._get_status_effect_bonus(unit, TORCH_VISION)
            vision_range = base_vision + torch_bonus
            
            # Add tiles within vision range, considering line of sight
            unit_visible = self.calculate_line_of_sight_area(unit.position, vision_range)
            visible_set.update(unit_visible)
        
        # Add vision from Torch Staff effects (need state for active torch staves)
        # torch_staff_areas = self.gameStateManager.get_active_torch_staff_areas()
        # for area in torch_staff_areas: visible_set.update(area)
        
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
        visible_tiles = self.get_visible_tiles(faction)
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
        # Basic check: Assume true for now.
        # Implement Bresenham's line algorithm or similar, checking terrain properties of intermediate tiles.
        # Return False if a blocking terrain type (e.g., High Wall, Peak) is encountered.
        # Need terrain property 'blocks_line_of_sight' from DataProvider.
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
        cx, cy = center_pos
        
        for x in range(max(0, cx - range_val), min(map_width, cx + range_val + 1)):
            for y in range(max(0, cy - range_val), min(map_height, cy + range_val + 1)):
                if self.calculate_manhattan_distance(center_pos, (x, y)) <= range_val:
                    if self.has_line_of_sight(center_pos, (x, y)):  # Check LoS
                        visible_area.add((x, y))
        
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
        # This is a placeholder. The actual implementation would depend on how
        # the GameStateManager tracks Fog of War state.
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