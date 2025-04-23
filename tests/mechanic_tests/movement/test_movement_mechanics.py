#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for movement mechanics.
This test covers movement range calculation, terrain costs, and unit movement.
"""

import os
import sys
import random
import datetime
import heapq
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any, Set

# Setup paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, PROJECT_ROOT)

# Define enums
class FactionEnum(Enum):
    PLAYER = 1
    ENEMY = 2
    NPC = 3

class DispositionEnum(Enum):
    ACTIVE = 1
    DEAD = 2
    ESCAPED = 3
    RETREATED = 4

class TerrainType(Enum):
    PLAIN = 1
    FOREST = 2
    MOUNTAIN = 3
    RIVER = 4
    FORT = 5
    WALL = 6  # Impassable

class MovementType(Enum):
    INFANTRY = 1
    CAVALRY = 2
    FLIER = 3
    ARMOR = 4

# Define simplified state classes
class UnitState:
    """Simplified unit state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.faction = None
        self.position = (0, 0)
        self.movement_type = MovementType.INFANTRY
        self.movement_stars = 0  # Bonus movement
        self.movement = 5  # Base movement range
        self.current_hp = 0
        self.max_hp = 0
        self.base_stats = {}
        self.status_effects = []
        self.disposition = DispositionEnum.ACTIVE
    
    def get_movement_range(self):
        """Get the unit's movement range including stars."""
        return self.movement + self.movement_stars

class GameStateManager:
    """Simplified game state manager for testing."""
    def __init__(self):
        self.units = {}
        self.map_width = 10
        self.map_height = 10
        self.terrain_grid = [[TerrainType.PLAIN for _ in range(self.map_width)] for _ in range(self.map_height)]
    
    def get_unit(self, unit_id):
        """Get a unit by ID."""
        return self.units.get(unit_id)
    
    def get_map_dimensions(self):
        """Get the dimensions of the map."""
        return (self.map_width, self.map_height)
    
    def get_terrain_at(self, position):
        """Get the terrain type at a position."""
        x, y = position
        if 0 <= x < self.map_width and 0 <= y < self.map_height:
            return self.terrain_grid[y][x]
        return TerrainType.WALL  # Outside map is impassable
    
    def is_tile_occupied(self, position):
        """Check if a tile is occupied by a unit."""
        for unit in self.units.values():
            if unit.disposition == DispositionEnum.ACTIVE and unit.position == position:
                return True
        return False
    
    def get_movement_cost(self, terrain_type, movement_type):
        """Get the movement cost for a terrain type and movement type."""
        movement_costs = {
            # Infantry movement costs
            (TerrainType.PLAIN, MovementType.INFANTRY): 1,
            (TerrainType.FOREST, MovementType.INFANTRY): 2,
            (TerrainType.MOUNTAIN, MovementType.INFANTRY): 3,
            (TerrainType.RIVER, MovementType.INFANTRY): 2,
            (TerrainType.FORT, MovementType.INFANTRY): 1,
            
            # Cavalry movement costs
            (TerrainType.PLAIN, MovementType.CAVALRY): 1,
            (TerrainType.FOREST, MovementType.CAVALRY): 3,
            (TerrainType.MOUNTAIN, MovementType.CAVALRY): 999,  # Impassable
            (TerrainType.RIVER, MovementType.CAVALRY): 3,
            (TerrainType.FORT, MovementType.CAVALRY): 1,
            
            # Flier movement costs
            (TerrainType.PLAIN, MovementType.FLIER): 1,
            (TerrainType.FOREST, MovementType.FLIER): 1,
            (TerrainType.MOUNTAIN, MovementType.FLIER): 1,
            (TerrainType.RIVER, MovementType.FLIER): 1,
            (TerrainType.FORT, MovementType.FLIER): 1,
            
            # Armor movement costs
            (TerrainType.PLAIN, MovementType.ARMOR): 1,
            (TerrainType.FOREST, MovementType.ARMOR): 2,
            (TerrainType.MOUNTAIN, MovementType.ARMOR): 999,  # Impassable
            (TerrainType.RIVER, MovementType.ARMOR): 999,    # Impassable
            (TerrainType.FORT, MovementType.ARMOR): 1,
        }
        
        cost = movement_costs.get((terrain_type, movement_type), 999)
        return cost if cost < 999 else float('inf')  # Convert to infinity for impassable

class MovementSystem:
    """Simplified movement system for testing."""
    def __init__(self):
        self.game_state_manager = None
    
    def initialize(self, game_state_manager):
        """Initialize the movement system with a game state manager."""
        self.game_state_manager = game_state_manager
    
    def get_reachable_tiles(self, unit_id):
        """Get all tiles a unit can reach with its movement points."""
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return set()
        
        movement_range = unit.get_movement_range()
        start_pos = unit.position
        reachable = self._pathfinding(start_pos, movement_range, unit.movement_type)
        
        # Remove starting position and occupied tiles
        reachable.discard(start_pos)
        reachable = {pos for pos in reachable if not self.game_state_manager.is_tile_occupied(pos)}
        
        return reachable
    
    def get_path_to(self, unit_id, target_pos):
        """Get the shortest path from a unit to a target position."""
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return []
        
        movement_range = unit.get_movement_range()
        start_pos = unit.position
        
        # Use A* pathfinding to find the shortest path
        return self._a_star(start_pos, target_pos, unit.movement_type, movement_range)
    
    def move_unit(self, unit_id, target_pos):
        """Move a unit to a target position."""
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if the position is reachable
        reachable_tiles = self.get_reachable_tiles(unit_id)
        if target_pos not in reachable_tiles:
            return False
        
        # Check if the position is occupied
        if self.game_state_manager.is_tile_occupied(target_pos):
            return False
        
        # Move the unit
        unit.position = target_pos
        return True
    
    def _pathfinding(self, start_pos, movement_points, movement_type):
        """Find all reachable tiles within movement points."""
        # Dictionary to store the minimum cost to reach each position
        cost_so_far = {start_pos: 0}
        
        # Priority queue for frontier
        frontier = [(0, start_pos)]
        
        # Set of reachable positions
        reachable = {start_pos}
        
        map_width, map_height = self.game_state_manager.get_map_dimensions()
        
        while frontier:
            current_cost, current_pos = heapq.heappop(frontier)
            
            # If we've used more movement points than available, skip
            if current_cost > movement_points:
                continue
            
            # Try all four directions
            x, y = current_pos
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            
            for next_pos in neighbors:
                nx, ny = next_pos
                
                # Check if within map bounds
                if not (0 <= nx < map_width and 0 <= ny < map_height):
                    continue
                
                # Get the terrain type and movement cost
                terrain = self.game_state_manager.get_terrain_at(next_pos)
                move_cost = self.game_state_manager.get_movement_cost(terrain, movement_type)
                
                # Skip impassable terrain
                if move_cost == float('inf'):
                    continue
                
                # Calculate new cost
                new_cost = current_cost + move_cost
                
                # If this position is newly discovered or cheaper to reach
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    
                    # If we still have movement points, add to frontier
                    if new_cost <= movement_points:
                        heapq.heappush(frontier, (new_cost, next_pos))
                        reachable.add(next_pos)
        
        return reachable
    
    def _a_star(self, start, goal, movement_type, max_movement):
        """A* pathfinding algorithm."""
        # Priority queue for frontier
        frontier = [(0, start)]
        
        # Dictionary to store where we came from for each position
        came_from = {start: None}
        
        # Dictionary to store the cost to reach each position
        cost_so_far = {start: 0}
        
        map_width, map_height = self.game_state_manager.get_map_dimensions()
        
        while frontier:
            _, current = heapq.heappop(frontier)
            
            # If we've reached the goal, reconstruct the path
            if current == goal:
                path = []
                while current != start:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            # Try all four directions
            x, y = current
            neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            
            for next_pos in neighbors:
                nx, ny = next_pos
                
                # Check if within map bounds
                if not (0 <= nx < map_width and 0 <= ny < map_height):
                    continue
                
                # Get the terrain type and movement cost
                terrain = self.game_state_manager.get_terrain_at(next_pos)
                move_cost = self.game_state_manager.get_movement_cost(terrain, movement_type)
                
                # Skip impassable terrain
                if move_cost == float('inf'):
                    continue
                
                # Calculate new cost
                new_cost = cost_so_far[current] + move_cost
                
                # If the path would exceed max movement, skip
                if new_cost > max_movement:
                    continue
                
                # If this position is newly discovered or cheaper to reach
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self._heuristic(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current
        
        # No path found
        return []
    
    def _heuristic(self, a, b):
        """Manhattan distance heuristic for A*."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

class MockGameStateManager(GameStateManager):
    """Mock game state manager for testing movement mechanics."""
    def __init__(self):
        super().__init__()
        self.units = {}
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.units[unit.id] = unit
        return unit.id
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.units.values())
    
    def setup_terrain(self, terrain_grid):
        """Set up terrain for testing."""
        self.terrain_grid = terrain_grid
        self.map_height = len(terrain_grid)
        self.map_width = len(terrain_grid[0]) if self.map_height > 0 else 0

class VisualScenarioLogger:
    """Simplified logger for tests."""
    def __init__(self, game_state_manager, log_dir=None):
        self.game_state_manager = game_state_manager
        self.log_dir = log_dir
        self.log_file = None
        self.log_buffer = []
    
    def set_log_file(self, log_path):
        """Set the log file path and write any buffered logs."""
        self.log_file = log_path
        # Write any buffered logs
        if self.log_buffer:
            with open(self.log_file, 'w') as f:
                f.write('\n'.join(self.log_buffer))
            self.log_buffer = []
    
    def log(self, message):
        """Log a message."""
        if self.log_file:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        else:
            self.log_buffer.append(message)
    
    def log_initial_state(self, title):
        """Log the initial state of the game."""
        self.log(f"=== {title} ===")
        self.log(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("")
    
    def log_map(self, highlighted_positions=None):
        """Log an ASCII representation of the map."""
        highlighted_positions = highlighted_positions or set()
        map_width, map_height = self.game_state_manager.get_map_dimensions()
        
        # Map terrain types to symbols
        terrain_symbols = {
            TerrainType.PLAIN: '.',
            TerrainType.FOREST: 'F',
            TerrainType.MOUNTAIN: 'M',
            TerrainType.RIVER: '~',
            TerrainType.FORT: 'O',
            TerrainType.WALL: '#'
        }
        
        # Create unit position lookup
        unit_positions = {}
        for unit in self.game_state_manager.units.values():
            if unit.disposition == DispositionEnum.ACTIVE:
                unit_positions[unit.position] = unit.id[:1]  # First letter of unit ID
        
        # Build the ASCII map
        ascii_map = []
        ascii_map.append('  ' + ''.join(f'{x % 10}' for x in range(map_width)))
        
        for y in range(map_height):
            row = f'{y % 10} '
            for x in range(map_width):
                pos = (x, y)
                if pos in unit_positions:
                    row += unit_positions[pos]
                elif pos in highlighted_positions:
                    row += '*'
                else:
                    terrain = self.game_state_manager.get_terrain_at(pos)
                    row += terrain_symbols.get(terrain, '?')
            ascii_map.append(row)
        
        self.log('\n'.join(ascii_map))
    
    def log_unit_move(self, unit_id, path):
        """Log a unit's movement path."""
        unit = self.game_state_manager.get_unit(unit_id)
        if not unit:
            return
        
        path_str = ' -> '.join(str(pos) for pos in [unit.position] + path)
        self.log(f"{unit.name} moves: {path_str}")
    
    def close(self):
        """Close the logger."""
        pass

def create_unit(unit_id, name, faction, position, movement_type, movement=5, movement_stars=0, hp=20, max_hp=20):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.position = position
    unit.movement_type = movement_type
    unit.movement = movement
    unit.movement_stars = movement_stars
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.disposition = DispositionEnum.ACTIVE
    return unit

def test_movement_mechanics():
    """Test movement mechanics."""
    # Setup game state and systems
    game_state_manager = MockGameStateManager()
    movement_system = MovementSystem()
    movement_system.initialize(game_state_manager)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../logs/mechanic_tests/movement'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file
    log_path = os.path.join(log_dir, f"movement_mechanics.txt")
    
    visual_logger = VisualScenarioLogger(game_state_manager, log_dir)
    visual_logger.set_log_file(log_path)
    
    # Log initial state
    visual_logger.log_initial_state("Movement Mechanics Test")
    
    # Set up terrain map
    # Plain, Forest, Mountain, River, Fort, Wall
    # 0 = Plain, 1 = Forest, 2 = Mountain, 3 = River, 4 = Fort, 5 = Wall
    terrain_map = [
        [0, 0, 0, 0, 0, 0, 3, 3, 0, 0],
        [0, 0, 1, 1, 0, 0, 3, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 3, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 3, 0, 1, 1],
        [5, 5, 5, 5, 4, 0, 3, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 3, 0, 2, 2],
        [0, 1, 1, 0, 0, 3, 3, 0, 2, 5],
        [0, 1, 1, 1, 0, 3, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 3, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 3, 0, 0, 0, 0]
    ]
    
    # Convert numeric terrain to TerrainType
    terrain_types = [TerrainType.PLAIN, TerrainType.FOREST, TerrainType.MOUNTAIN, 
                    TerrainType.RIVER, TerrainType.FORT, TerrainType.WALL]
    
    terrain_grid = [[terrain_types[val] for val in row] for row in terrain_map]
    game_state_manager.setup_terrain(terrain_grid)
    
    # Test 1: Infantry Movement
    visual_logger.log("\n=== TEST 1: INFANTRY MOVEMENT ===")
    infantry = create_unit("PLAYER_INFANTRY", "Infantry", FactionEnum.PLAYER, (1, 1), MovementType.INFANTRY, movement=5)
    game_state_manager.add_unit(infantry)
    
    visual_logger.log(f"Infantry unit: {infantry.name}, Position: {infantry.position}, Movement: {infantry.get_movement_range()}")
    
    # Calculate reachable tiles
    reachable_tiles = movement_system.get_reachable_tiles(infantry.id)
    visual_logger.log(f"Reachable tiles for Infantry: {reachable_tiles}")
    
    # Display map with reachable tiles
    visual_logger.log("\nMap with reachable tiles for Infantry (* = reachable):")
    visual_logger.log_map(reachable_tiles)
    
    # Move the unit
    target_pos = (4, 2)
    path = movement_system.get_path_to(infantry.id, target_pos)
    visual_logger.log(f"\nPath to {target_pos}: {path}")
    
    move_result = movement_system.move_unit(infantry.id, target_pos)
    visual_logger.log(f"Move result: {move_result}")
    
    # Display map after movement
    visual_logger.log("\nMap after Infantry movement:")
    visual_logger.log_map()
    
    # Test 2: Cavalry Movement
    visual_logger.log("\n=== TEST 2: CAVALRY MOVEMENT ===")
    cavalry = create_unit("PLAYER_CAVALRY", "Cavalry", FactionEnum.PLAYER, (8, 8), MovementType.CAVALRY, movement=7)
    game_state_manager.add_unit(cavalry)
    
    visual_logger.log(f"Cavalry unit: {cavalry.name}, Position: {cavalry.position}, Movement: {cavalry.get_movement_range()}")
    
    # Calculate reachable tiles
    reachable_tiles = movement_system.get_reachable_tiles(cavalry.id)
    visual_logger.log(f"Reachable tiles for Cavalry: {reachable_tiles}")
    
    # Display map with reachable tiles
    visual_logger.log("\nMap with reachable tiles for Cavalry (* = reachable):")
    visual_logger.log_map(reachable_tiles)
    
    # Move the unit
    target_pos = (5, 5)
    path = movement_system.get_path_to(cavalry.id, target_pos)
    visual_logger.log(f"\nPath to {target_pos}: {path}")
    
    move_result = movement_system.move_unit(cavalry.id, target_pos)
    visual_logger.log(f"Move result: {move_result}")
    
    # Display map after movement
    visual_logger.log("\nMap after Cavalry movement:")
    visual_logger.log_map()
    
    # Test 3: Flier Movement
    visual_logger.log("\n=== TEST 3: FLIER MOVEMENT ===")
    flier = create_unit("PLAYER_FLIER", "Pegasus Knight", FactionEnum.PLAYER, (0, 0), MovementType.FLIER, movement=7)
    game_state_manager.add_unit(flier)
    
    visual_logger.log(f"Flier unit: {flier.name}, Position: {flier.position}, Movement: {flier.get_movement_range()}")
    
    # Calculate reachable tiles
    reachable_tiles = movement_system.get_reachable_tiles(flier.id)
    visual_logger.log(f"Reachable tiles for Flier: {reachable_tiles}")
    
    # Display map with reachable tiles
    visual_logger.log("\nMap with reachable tiles for Flier (* = reachable):")
    visual_logger.log_map(reachable_tiles)
    
    # Move the unit across terrain that would be impassable for others
    target_pos = (5, 6)
    path = movement_system.get_path_to(flier.id, target_pos)
    visual_logger.log(f"\nPath to {target_pos}: {path}")
    
    move_result = movement_system.move_unit(flier.id, target_pos)
    visual_logger.log(f"Move result: {move_result}")
    
    # Display map after movement
    visual_logger.log("\nMap after Flier movement:")
    visual_logger.log_map()
    
    # Test 4: Armor Movement
    visual_logger.log("\n=== TEST 4: ARMOR MOVEMENT ===")
    armor = create_unit("PLAYER_ARMOR", "Armored Knight", FactionEnum.PLAYER, (4, 4), MovementType.ARMOR, movement=4)
    game_state_manager.add_unit(armor)
    
    visual_logger.log(f"Armor unit: {armor.name}, Position: {armor.position}, Movement: {armor.get_movement_range()}")
    
    # Calculate reachable tiles
    reachable_tiles = movement_system.get_reachable_tiles(armor.id)
    visual_logger.log(f"Reachable tiles for Armor: {reachable_tiles}")
    
    # Display map with reachable tiles
    visual_logger.log("\nMap with reachable tiles for Armor (* = reachable):")
    visual_logger.log_map(reachable_tiles)
    
    # Move the unit
    target_pos = (6, 5)
    path = movement_system.get_path_to(armor.id, target_pos)
    visual_logger.log(f"\nPath to {target_pos}: {path}")
    
    move_result = movement_system.move_unit(armor.id, target_pos)
    visual_logger.log(f"Move result: {move_result}")
    
    # Display map after movement
    visual_logger.log("\nMap after Armor movement:")
    visual_logger.log_map()
    
    # Test 5: Movement Stars
    visual_logger.log("\n=== TEST 5: MOVEMENT STARS ===")
    ranger = create_unit("PLAYER_RANGER", "Ranger", FactionEnum.PLAYER, (0, 7), MovementType.INFANTRY, movement=5, movement_stars=2)
    game_state_manager.add_unit(ranger)
    
    visual_logger.log(f"Ranger unit: {ranger.name}, Position: {ranger.position}, Base Movement: {ranger.movement}, Movement Stars: {ranger.movement_stars}, Total Movement: {ranger.get_movement_range()}")
    
    # Calculate reachable tiles
    reachable_tiles = movement_system.get_reachable_tiles(ranger.id)
    visual_logger.log(f"Reachable tiles for Ranger: {reachable_tiles}")
    
    # Display map with reachable tiles
    visual_logger.log("\nMap with reachable tiles for Ranger (* = reachable):")
    visual_logger.log_map(reachable_tiles)
    
    # Move the unit
    target_pos = (7, 7)
    path = movement_system.get_path_to(ranger.id, target_pos)
    visual_logger.log(f"\nPath to {target_pos}: {path}")
    
    move_result = movement_system.move_unit(ranger.id, target_pos)
    visual_logger.log(f"Move result: {move_result}")
    
    # Display map after movement
    visual_logger.log("\nMap after Ranger movement:")
    visual_logger.log_map()
    
    # Final Map
    visual_logger.log("\n=== FINAL MAP STATE ===")
    visual_logger.log("Legend: . = Plain, F = Forest, M = Mountain, ~ = River, O = Fort, # = Wall")
    visual_logger.log("Units: I = Infantry, C = Cavalry, P = Pegasus Knight, A = Armored Knight, R = Ranger")
    visual_logger.log_map()
    
    # Final summary
    visual_logger.log("\n=== FINAL UNIT POSITIONS ===")
    for unit in game_state_manager.get_all_units():
        visual_logger.log(f"{unit.name} (ID: {unit.id}): Position {unit.position}, Movement Type: {unit.movement_type.name}")
    
    visual_logger.log("\nMOVEMENT_MECHANICS_TEST_COMPLETE")
    visual_logger.close()

if __name__ == "__main__":
    test_movement_mechanics() 