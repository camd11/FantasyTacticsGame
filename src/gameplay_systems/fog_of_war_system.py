"""
Fog of War System Module

This module implements the Fog of War (FoW) system for the Fantasy Tactics Game,
based on mechanics observed in Fire Emblem: Thracia 776. It manages tile visibility
on designated FoW maps, controlling what the player can see and when enemy units
are displayed.
"""

import logging
from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider


class TileVisibilityState(Enum):
    """
    Defines the possible visibility states for a map tile from the player's perspective.
    """
    Unknown = "Unknown"  # Tile has never been revealed. Rendered as black/obscured.
    Fog = "Fog"          # Tile was previously visible but is currently outside vision. Rendered as shrouded/dimmed.
    Visible = "Visible"  # Tile is currently within the vision range of a player unit or light source. Rendered normally.


class LightSource:
    """
    Represents a temporary light source on the map, such as from a Torch Staff.
    """
    def __init__(self, source_position: Tuple[int, int], radius: int, duration: int):
        """
        Initialize a light source.
        
        Args:
            source_position: Center of the light source (x, y)
            radius: Radius of illumination
            duration: Turns remaining for this light source
        """
        self.source_position = source_position
        self.radius = radius
        self.duration = duration


class UnitVisibilityData:
    """
    Component added to each Unit entity to track its specific vision properties.
    """
    def __init__(self, base_vision_range: int = 3, class_vision_bonus: int = 0):
        """
        Initialize unit visibility data.
        
        Args:
            base_vision_range: Default vision range (default: 3)
            class_vision_bonus: Bonus vision from class (e.g., Thief +2) (default: 0)
        """
        self.base_vision_range = base_vision_range
        self.class_vision_bonus = class_vision_bonus
        self.temporary_vision_bonus = 0
        self.bonus_duration = 0


class FogOfWarSystem:
    """
    Manages the Fog of War system, including visibility calculations, map state updates,
    and integration with other game systems.
    """
    
    def __init__(self):
        """Initialize the FogOfWarSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.unitSystem = None
        self.turnManager = None
    
    def initialize(self, gameStateManager_instance, dataProvider_instance, mapSystem_instance, unitSystem_instance, turnManager_instance) -> None:
        """
        Initialize the FogOfWarSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            unitSystem_instance: Instance of the UnitSystem
            turnManager_instance: Instance of the TurnManager
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.unitSystem = unitSystem_instance
        self.turnManager = turnManager_instance
        logging.info("FogOfWarSystem initialized.")
    
    # --- Visibility Calculation Module ---
    
    def get_unit_vision_range(self, unit) -> int:
        """
        Calculate the total current vision range for a given unit.
        
        Args:
            unit: The unit to calculate vision range for
            
        Returns:
            Total vision range including base, class bonus, and temporary bonuses
        """
        vis_data = unit.get_component(UnitVisibilityData)
        base_range = vis_data.base_vision_range
        class_bonus = vis_data.class_vision_bonus
        temp_bonus = 0
        
        if vis_data.bonus_duration > 0:
            temp_bonus = vis_data.temporary_vision_bonus
        
        return base_range + class_bonus + temp_bonus
    
    def is_tile_visible_to_player(self, target_tile_pos: Tuple[int, int], map_visibility_data, player_units, map_data) -> bool:
        """
        Check if a specific tile is currently visible to the player faction.
        
        Args:
            target_tile_pos: Position of the target tile (x, y)
            map_visibility_data: Map visibility data
            player_units: List of player units
            map_data: Map data
            
        Returns:
            True if the tile is visible, False otherwise
        """
        # Check vision from player units
        for player_unit in player_units:
            # Skip units being carried (rescued/captured) - they provide no vision
            if player_unit.is_being_carried():
                continue
            
            vision_range = self.get_unit_vision_range(player_unit)
            distance = self.calculate_manhattan_distance(player_unit.position, target_tile_pos)
            
            if distance <= vision_range:
                if self.has_line_of_sight(player_unit.position, target_tile_pos, map_data):
                    return True
        
        # Check vision from temporary light sources (Torch Staff)
        for light_source in map_visibility_data.light_sources:
            if light_source.duration > 0:
                distance = self.calculate_manhattan_distance(light_source.source_position, target_tile_pos)
                if distance <= light_source.radius:
                    # Assumption: Torch staff light ignores LoS blockers within its radius.
                    return True
        
        return False
    
    def has_line_of_sight(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], map_data) -> bool:
        """
        Determine if there is an unobstructed line of sight between two points.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            map_data: Map data
            
        Returns:
            True if there is a line of sight, False otherwise
        """
        # If positions are adjacent, always have line of sight
        if self.calculate_manhattan_distance(start_pos, end_pos) <= 1:
            return True
        
        # Get tiles on the line between start_pos and end_pos
        intermediate_tiles = self.get_tiles_on_line(start_pos, end_pos)
        
        for tile_pos in intermediate_tiles:
            terrain = map_data.get_terrain_at(tile_pos)
            if terrain.properties.blocks_vision:
                return False
        
        return True
    
    def get_tiles_on_line(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Get the tiles on a line between two positions using Bresenham's line algorithm.
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
            
        Returns:
            List of positions on the line
        """
        # Implementation of Bresenham's line algorithm
        x0, y0 = start_pos
        x1, y1 = end_pos
        tiles = []
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while x0 != x1 or y0 != y1:
            tiles.append((x0, y0))
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        
        # Add the end position
        tiles.append(end_pos)
        
        return tiles
    
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
    
    # --- Map State Update Module ---
    
    def update_map_visibility(self, map_visibility_data, player_units, map_data) -> None:
        """
        Update the visibility state of each tile on the map.
        
        Args:
            map_visibility_data: Map visibility data
            player_units: List of player units
            map_data: Map data
        """
        map_height, map_width = map_data.get_dimensions()
        
        for y in range(map_height):
            for x in range(map_width):
                tile_pos = (x, y)
                current_state = map_visibility_data.visibility_grid[y][x]
                is_currently_visible = self.is_tile_visible_to_player(tile_pos, map_visibility_data, player_units, map_data)
                
                if is_currently_visible:
                    map_visibility_data.visibility_grid[y][x] = TileVisibilityState.Visible
                else:
                    # If it was visible before, transition to Fog (shroud)
                    if current_state == TileVisibilityState.Visible:
                        map_visibility_data.visibility_grid[y][x] = TileVisibilityState.Fog
                    # Otherwise (if Unknown or already Fog), it remains in its current state.
                    # No change needed for Unknown -> Unknown or Fog -> Fog.
    
    def decrement_visibility_durations(self, map_visibility_data, player_units) -> None:
        """
        Decrement timers for temporary vision effects at the start of the player phase.
        
        Args:
            map_visibility_data: Map visibility data
            player_units: List of player units
        """
        # Decrement Torch item durations
        for unit in player_units:
            vis_data = unit.get_component(UnitVisibilityData)
            if vis_data.bonus_duration > 0:
                vis_data.bonus_duration -= 1
                if vis_data.bonus_duration == 0:
                    vis_data.temporary_vision_bonus = 0  # Reset bonus when duration expires
        
        # Decrement Torch Staff light source durations
        active_light_sources = []
        for light_source in map_visibility_data.light_sources:
            if light_source.duration > 0:
                light_source.duration -= 1
                if light_source.duration > 0:
                    active_light_sources.append(light_source)
        
        map_visibility_data.light_sources = active_light_sources  # Update list
    
    # --- Triggering Visibility Updates ---
    
    def on_player_phase_start(self, game_state) -> None:
        """
        Update visibility at the start of the player phase.
        
        Args:
            game_state: Current game state
        """
        self.decrement_visibility_durations(game_state.map_visibility_data, game_state.player_units)
        self.update_map_visibility(game_state.map_visibility_data, game_state.player_units, game_state.map_data)
        # UI Refresh needed here
    
    def on_unit_action_finish(self, unit, action_type, action_details, game_state) -> None:
        """
        Update visibility after a unit finishes an action that might affect visibility.
        
        Args:
            unit: The unit that performed the action
            action_type: Type of action performed
            action_details: Details of the action
            game_state: Current game state
        """
        visibility_needs_update = False
        
        if action_type == "Move" or action_type == "CantoMove":
            visibility_needs_update = True
        elif action_type == "UseItem" and self.item_used_was_torch(action_details):
            self.apply_torch_item_effect(unit, action_details)
            visibility_needs_update = True
        elif action_type == "UseStaff" and self.staff_used_was_torch(action_details):
            self.apply_torch_staff_effect(game_state.map_visibility_data, action_details)
            visibility_needs_update = True
        
        if visibility_needs_update:
            self.update_map_visibility(game_state.map_visibility_data, game_state.player_units, game_state.map_data)
            # UI Refresh needed here
    
    def apply_torch_item_effect(self, unit, item_details) -> None:
        """
        Apply the effect of using a Torch item.
        
        Args:
            unit: The unit using the Torch item
            item_details: Details of the Torch item
        """
        vis_data = unit.get_component(UnitVisibilityData)
        vis_data.temporary_vision_bonus = item_details.vision_bonus
        vis_data.bonus_duration = item_details.duration
    
    def apply_torch_staff_effect(self, map_visibility_data, staff_details) -> None:
        """
        Apply the effect of using a Torch staff.
        
        Args:
            map_visibility_data: Map visibility data
            staff_details: Details of the Torch staff
        """
        new_light_source = LightSource(
            source_position=staff_details.target_position,
            radius=staff_details.radius,
            duration=staff_details.duration
        )
        map_visibility_data.light_sources.append(new_light_source)
    
    # --- Enemy Units in Fog ---
    
    def should_display_unit(self, unit, map_visibility_data) -> bool:
        """
        Determine if a unit (typically an enemy) should be rendered on the map.
        
        Args:
            unit: The unit to check
            map_visibility_data: Map visibility data
            
        Returns:
            True if the unit should be displayed, False otherwise
        """
        tile_state = map_visibility_data.visibility_grid[unit.position[1]][unit.position[0]]
        return tile_state == TileVisibilityState.Visible
    
    # --- Helper Methods ---
    
    def item_used_was_torch(self, action_details) -> bool:
        """
        Check if the item used was a Torch.
        
        Args:
            action_details: Details of the action
            
        Returns:
            True if the item was a Torch, False otherwise
        """
        # This would check the item ID or name against known Torch items
        return hasattr(action_details, 'item_id') and action_details.item_id == "TORCH"
    
    def staff_used_was_torch(self, action_details) -> bool:
        """
        Check if the staff used was a Torch staff.
        
        Args:
            action_details: Details of the action
            
        Returns:
            True if the staff was a Torch staff, False otherwise
        """
        # This would check the staff ID or name against known Torch staves
        return hasattr(action_details, 'staff_id') and action_details.staff_id == "TORCH_STAFF"