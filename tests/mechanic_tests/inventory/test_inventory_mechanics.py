#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script for inventory mechanics.
This test covers item pickup, usage, and transfer between units.
"""

import os
import sys
import random
import datetime
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any

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

class EquipmentSlotEnum(Enum):
    WEAPON = "WEAPON"
    ARMOR = "ARMOR"
    ACCESSORY = "ACCESSORY"

# Define simplified state classes
class ItemState:
    """Simplified item state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.type = ""
        self.effects = {}
        self.uses = 0
        self.position = None
        self.owner_id = None

class UnitState:
    """Simplified unit state for testing."""
    def __init__(self):
        self.id = ""
        self.name = ""
        self.faction = None
        self.position = (0, 0)
        self.current_hp = 0
        self.max_hp = 0
        self.base_stats = {}
        self.inventory = []
        self.status_effects = []
        self.disposition = DispositionEnum.ACTIVE
        self.equipment = {
            EquipmentSlotEnum.WEAPON: None,
            EquipmentSlotEnum.ARMOR: None,
            EquipmentSlotEnum.ACCESSORY: None
        }
    
    def get_stat(self, stat_name):
        """Get a unit's stat, including effects from items and status effects."""
        base_value = self.base_stats.get(stat_name, 0)
        # In a real implementation, would add bonuses from equipment and status effects
        return base_value

class GameStateManager:
    """Simplified game state manager for testing."""
    def __init__(self):
        self.units = {}
        self.items = {}
        self.map_grid = [[0 for _ in range(10)] for _ in range(10)]
    
class InventorySystem:
    """Simplified inventory system for testing."""
    def __init__(self):
        self.game_state_manager = None
    
    def initialize(self, game_state_manager):
        """Initialize the inventory system with a game state manager."""
        self.game_state_manager = game_state_manager
    
    def pickup_item(self, unit_id, item_id):
        """Have a unit pick up an item."""
        unit = self.game_state_manager.units.get(unit_id)
        item = self.game_state_manager.items.get(item_id)
        
        if not unit or not item:
            return False
        
        if item.position is None:
            return False  # Item is not on the ground
        
        if item.owner_id is not None:
            return False  # Item is already owned
        
        # Check if unit is at the same position as the item
        if unit.position != item.position:
            return False
        
        # Add item to unit's inventory
        unit.inventory.append(item)
        item.position = None
        item.owner_id = unit_id
        return True
    
    def use_item(self, unit_id, item_id):
        """Have a unit use an item."""
        unit = self.game_state_manager.units.get(unit_id)
        item = self.game_state_manager.items.get(item_id)
        
        if not unit or not item:
            return False
        
        # Check if unit owns the item
        if item.owner_id != unit_id:
            return False
        
        # Check if item is in unit's inventory
        if item not in unit.inventory:
            return False
        
        # Apply item effects
        if "heal" in item.effects:
            unit.current_hp = min(unit.max_hp, unit.current_hp + item.effects["heal"])
        
        # Apply stat boosts (temporary implementation)
        for stat, boost in item.effects.items():
            if stat != "heal" and stat in ["STR", "DEF", "SKL", "SPD"]:
                unit.base_stats[stat] = unit.base_stats.get(stat, 0) + boost
        
        # Use up the item
        item.uses -= 1
        if item.uses <= 0:
            unit.inventory.remove(item)
            self.game_state_manager.items.pop(item_id, None)
            return True
        
        return True
    
    def transfer_item(self, from_unit_id, to_unit_id, item_id):
        """Transfer an item between units."""
        from_unit = self.game_state_manager.units.get(from_unit_id)
        to_unit = self.game_state_manager.units.get(to_unit_id)
        item = self.game_state_manager.items.get(item_id)
        
        if not from_unit or not to_unit or not item:
            return False
        
        # Check if from_unit owns the item
        if item.owner_id != from_unit_id:
            return False
        
        # Check if item is in from_unit's inventory
        if item not in from_unit.inventory:
            return False
        
        # Check if units are adjacent
        if not self._are_units_adjacent(from_unit, to_unit):
            return False
        
        # Transfer the item
        from_unit.inventory.remove(item)
        to_unit.inventory.append(item)
        item.owner_id = to_unit_id
        return True
    
    def _are_units_adjacent(self, unit1, unit2):
        """Check if two units are adjacent."""
        x1, y1 = unit1.position
        x2, y2 = unit2.position
        return abs(x1 - x2) + abs(y1 - y2) <= 1

class MockCLIDisplay:
    """Mock display class for testing."""
    
    def render_game_state(self, game_state_manager, focused_position=None):
        """Mock method for rendering the game state."""
        return
        
    def render_map_ascii(self, game_map, unit_positions, active_unit_id=None):
        """Render the map in ASCII format for the log."""
        width, height = 10, 10  # Simplified for test
        ascii_map = []
        
        # Create a 2D grid filled with terrain characters
        grid = [['.'] * width for _ in range(height)]
        
        # Add units
        for unit_id, position in unit_positions.items():
            if position:
                x, y = position
                if 0 <= x < width and 0 <= y < height:
                    if unit_id == active_unit_id:
                        grid[y][x] = 'A'  # Active unit
                    else:
                        grid[y][x] = 'U'  # Regular unit
        
        # Convert grid to ASCII strings
        for row in grid:
            ascii_map.append(''.join(row))
        
        return '\n'.join(ascii_map)

    def render_map(self, game_state_manager, highlighted_positions=None):
        return "ASCII map representation"
    
    def render_unit_stats(self, unit):
        return f"Unit stats: {unit.name} HP: {unit.current_hp}/{unit.max_hp}"

class MockGameStateManager(GameStateManager):
    """Mock game state manager for testing inventory mechanics."""
    def __init__(self):
        super().__init__()
        self.units = {}
        self.items = {}
        self.map_grid = [[0 for _ in range(10)] for _ in range(10)]
        
    def add_unit(self, unit):
        """Add a unit to the game state."""
        self.units[unit.id] = unit
        return unit.id
        
    def get_all_units(self):
        """Return all units in the game state."""
        return list(self.units.values())
    
    def get_unit_at_position(self, position):
        """Return the unit at the given position."""
        for unit in self.units.values():
            if unit.position == position:
                return unit
        return None
    
    def add_item(self, item):
        """Add an item to the game state."""
        self.items[item.id] = item
        return item.id
    
    def get_item(self, item_id):
        """Get an item by its ID."""
        return self.items.get(item_id)
    
    def get_all_items(self):
        """Return all items in the game state."""
        return list(self.items.values())

class VisualScenarioLogger:
    """Simplified logger for tests."""
    def __init__(self, game_state_manager, cli_display, log_dir=None):
        self.game_state_manager = game_state_manager
        self.cli_display = cli_display
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
    
    def close(self):
        """Close the logger."""
        pass

def create_unit(unit_id, name, faction, position, hp=20, max_hp=20, stats=None):
    """Helper function to create a unit for testing."""
    unit = UnitState()
    unit.id = unit_id
    unit.name = name
    unit.faction = faction
    unit.position = position
    unit.current_hp = hp
    unit.max_hp = max_hp
    unit.inventory = []
    unit.disposition = DispositionEnum.ACTIVE
    unit.base_stats = stats or {"STR": 5, "DEF": 3, "SKL": 4, "SPD": 3}
    unit.status_effects = []
    unit.equipment = {
        EquipmentSlotEnum.WEAPON: None,
        EquipmentSlotEnum.ARMOR: None,
        EquipmentSlotEnum.ACCESSORY: None
    }
    return unit

def create_item(item_id, name, item_type, effects=None, uses=3):
    """Helper function to create an item for testing."""
    item = ItemState()
    item.id = item_id
    item.name = name
    item.type = item_type
    item.effects = effects or {}
    item.uses = uses
    item.position = None  # When on ground
    item.owner_id = None  # When held by a unit
    return item

def test_inventory_mechanics():
    """Test inventory mechanics including pickup, use, and transfer."""
    # Setup game state and systems
    game_state_manager = MockGameStateManager()
    inventory_system = InventorySystem()
    inventory_system.initialize(game_state_manager)
    
    # Create log directory if it doesn't exist
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../logs/mechanic_tests/inventory'))
    os.makedirs(log_dir, exist_ok=True)
    
    # Create a log file with a timestamp
    log_path = os.path.join(log_dir, f"inventory_mechanics.txt")
    
    cli_display = MockCLIDisplay()
    visual_logger = VisualScenarioLogger(game_state_manager, cli_display, log_dir)
    visual_logger.set_log_file(log_path)
    
    # Create test units with positions matching item positions for easy pickup
    # Position them adjacent to each other for easy transfer later
    commander = create_unit("PLAYER_COMMANDER", "Commander", FactionEnum.PLAYER, (3, 4), hp=25, max_hp=25)
    knight = create_unit("PLAYER_KNIGHT", "Knight", FactionEnum.PLAYER, (4, 4), hp=30, max_hp=30)
    
    # Create test items at the same positions as units
    healing_potion = create_item("HEALING_POTION", "Healing Potion", "CONSUMABLE", {"heal": 10}, uses=2)
    strength_potion = create_item("STRENGTH_POTION", "Strength Potion", "CONSUMABLE", {"STR": 3}, uses=1)
    iron_sword = create_item("IRON_SWORD", "Iron Sword", "WEAPON", {"ATK": 5}, uses=30)
    
    # Add units and items to game state
    game_state_manager.add_unit(commander)
    game_state_manager.add_unit(knight)
    
    # Place items on the map at unit positions
    healing_potion.position = (3, 4)  # Same as commander
    strength_potion.position = (4, 4)  # Same as knight
    iron_sword.position = (4, 4)      # Also at knight's position
    
    game_state_manager.add_item(healing_potion)
    game_state_manager.add_item(strength_potion)
    game_state_manager.add_item(iron_sword)
    
    # Log initial state
    visual_logger.log_initial_state("Inventory Mechanics Test")
    visual_logger.log(f"Map contains {len(game_state_manager.get_all_units())} units and {len(game_state_manager.get_all_items())} items.")
    visual_logger.log(f"Items on ground: Healing Potion at {healing_potion.position}, Strength Potion at {strength_potion.position}, Iron Sword at {iron_sword.position}")
    visual_logger.log(f"Units: Commander at {commander.position}, Knight at {knight.position}")
    
    # Test 1: Pickup items
    visual_logger.log("\n=== TEST 1: ITEM PICKUP ===")
    
    # Commander picks up healing potion
    pickup_result = inventory_system.pickup_item(commander.id, healing_potion.id)
    visual_logger.log(f"Commander attempts to pick up Healing Potion. Result: {pickup_result}")
    visual_logger.log(f"Commander's inventory: {[item.name for item in commander.inventory]}")
    visual_logger.log(f"Healing Potion position: {healing_potion.position}, owner: {healing_potion.owner_id}")
    
    # Knight picks up strength potion
    pickup_result = inventory_system.pickup_item(knight.id, strength_potion.id)
    visual_logger.log(f"Knight attempts to pick up Strength Potion. Result: {pickup_result}")
    visual_logger.log(f"Knight's inventory: {[item.name for item in knight.inventory]}")
    
    # Knight picks up iron sword
    pickup_result = inventory_system.pickup_item(knight.id, iron_sword.id)
    visual_logger.log(f"Knight attempts to pick up Iron Sword. Result: {pickup_result}")
    visual_logger.log(f"Knight's inventory: {[item.name for item in knight.inventory]}")
    
    # Test 2: Use items
    visual_logger.log("\n=== TEST 2: ITEM USAGE ===")
    
    # Commander uses healing potion
    commander.current_hp = 15  # Reduce HP for testing
    visual_logger.log(f"Commander's HP before using potion: {commander.current_hp}/{commander.max_hp}")
    
    use_result = inventory_system.use_item(commander.id, healing_potion.id)
    visual_logger.log(f"Commander uses Healing Potion. Result: {use_result}")
    visual_logger.log(f"Commander's HP after using potion: {commander.current_hp}/{commander.max_hp}")
    visual_logger.log(f"Healing Potion uses remaining: {healing_potion.uses}")
    
    # Knight uses strength potion
    visual_logger.log(f"Knight's STR before using potion: {knight.base_stats['STR']}")
    
    use_result = inventory_system.use_item(knight.id, strength_potion.id)
    visual_logger.log(f"Knight uses Strength Potion. Result: {use_result}")
    visual_logger.log(f"Knight's STR after using potion: {knight.get_stat('STR')}")
    visual_logger.log(f"Knight's inventory after using potion: {[item.name for item in knight.inventory]}")
    
    # Test 3: Transfer items
    visual_logger.log("\n=== TEST 3: ITEM TRANSFER ===")
    visual_logger.log(f"Commander position: {commander.position}, Knight position: {knight.position}")
    visual_logger.log(f"Are units adjacent? {inventory_system._are_units_adjacent(commander, knight)}")
    
    # Knight transfers iron sword to commander
    transfer_result = inventory_system.transfer_item(knight.id, commander.id, iron_sword.id)
    visual_logger.log(f"Knight transfers Iron Sword to Commander. Result: {transfer_result}")
    visual_logger.log(f"Commander's inventory: {[item.name for item in commander.inventory]}")
    visual_logger.log(f"Knight's inventory: {[item.name for item in knight.inventory]}")
    
    # Commander uses healing potion again (should be used up)
    use_result = inventory_system.use_item(commander.id, healing_potion.id)
    visual_logger.log(f"Commander uses Healing Potion again. Result: {use_result}")
    visual_logger.log(f"Commander's inventory after using potion: {[item.name for item in commander.inventory]}")
    
    # Log final state
    visual_logger.log("\n=== FINAL STATE ===")
    for unit in game_state_manager.get_all_units():
        visual_logger.log(f"{unit.name} (ID: {unit.id}): HP {unit.current_hp}/{unit.max_hp}, Position {unit.position}")
        visual_logger.log(f"  Inventory: {[item.name for item in unit.inventory]}")
    
    visual_logger.log("INVENTORY_MECHANICS_TEST_COMPLETE")
    visual_logger.close()

if __name__ == "__main__":
    test_inventory_mechanics() 