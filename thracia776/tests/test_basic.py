#!/usr/bin/env python3
"""
Basic tests for the Thracia 776 recreation project.
This file contains simple tests to verify that the core components are working correctly.
"""

import os
import sys
import unittest
from typing import Dict, Any

# Add the parent directory to the path so we can import the thracia776 package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import core components
from thracia776.data.static_data_loader import StaticDataLoader
from thracia776.data.unit_manager import UnitManager
from thracia776.data.item_manager import ItemManager
from thracia776.data.map_manager import MapManager
from thracia776.data.models import Affiliation, TerrainType, MovementType, Unit, Item, MapTile

class TestBasicFunctionality(unittest.TestCase):
    """
    Test basic functionality of the core components.
    """
    
    @classmethod
    def setUpClass(cls):
        """
        Set up test data and initialize components.
        """
        # Set up data path
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_path = os.path.join(base_dir, "assets", "data")
        
        # Create test data if it doesn't exist
        if not os.path.exists(data_path) or not os.listdir(data_path):
            print("No data found. Creating test data...")
            from thracia776.main import setup_test_data
            setup_test_data(data_path)
        
        # Initialize static data loader
        cls.static_loader = StaticDataLoader(data_path=data_path)
        cls.static_loader.load_all_data()
        
        # Initialize managers
        cls.unit_manager = UnitManager(cls.static_loader)
        cls.item_manager = ItemManager(cls.static_loader)
        cls.map_manager = MapManager(cls.static_loader)
    
    def test_static_data_loader(self):
        """
        Test that the StaticDataLoader can load and retrieve data.
        """
        # Test item definitions
        iron_sword_def = self.static_loader.get_item_definition("iron_sword")
        self.assertIsNotNone(iron_sword_def, "Iron Sword definition not found")
        self.assertEqual(iron_sword_def.get("name"), "Iron Sword", "Iron Sword name mismatch")
        
        # Test class data
        lord_data = self.static_loader.get_class_data("lord")
        self.assertIsNotNone(lord_data, "Lord class data not found")
        self.assertEqual(lord_data.get("name"), "Lord", "Lord class name mismatch")
        
        # Test terrain data
        plain_data = self.static_loader.get_terrain_data("plain")
        self.assertIsNotNone(plain_data, "Plain terrain data not found")
        self.assertEqual(plain_data.get("type"), "PLAIN", "Plain terrain type mismatch")
    
    def test_unit_manager(self):
        """
        Test that the UnitManager can create and manage units.
        """
        # Create a test unit
        leif = self.unit_manager.create_unit("leif", "Leif", "lord", Affiliation.PLAYER)
        self.assertIsNotNone(leif, "Failed to create Leif unit")
        self.assertEqual(leif.name, "Leif", "Unit name mismatch")
        self.assertEqual(leif.cls_name, "lord", "Unit class mismatch")
        
        # Test retrieving the unit
        retrieved_leif = self.unit_manager.get_unit("leif")
        self.assertIsNotNone(retrieved_leif, "Failed to retrieve Leif unit")
        self.assertEqual(retrieved_leif.name, "Leif", "Retrieved unit name mismatch")
        
        # Test level up
        success, increases = self.unit_manager.level_up("leif")
        self.assertTrue(success, "Level up failed")
        self.assertEqual(leif.level, 2, "Level not increased")
        
        # Test getting units by affiliation
        player_units = self.unit_manager.get_all_units_by_affiliation(Affiliation.PLAYER)
        self.assertEqual(len(player_units), 1, "Incorrect number of player units")
        self.assertEqual(player_units[0].id, "leif", "Player unit ID mismatch")
    
    def test_item_manager(self):
        """
        Test that the ItemManager can create and manage items.
        """
        # Create a test item
        iron_sword = self.item_manager.create_item("iron_sword")
        self.assertIsNotNone(iron_sword, "Failed to create Iron Sword item")
        self.assertEqual(iron_sword.name, "Iron Sword", "Item name mismatch")
        
        # Test retrieving the item
        retrieved_sword = self.item_manager.get_item(iron_sword.instance_id)
        self.assertIsNotNone(retrieved_sword, "Failed to retrieve Iron Sword item")
        self.assertEqual(retrieved_sword.name, "Iron Sword", "Retrieved item name mismatch")
        
        # Test updating durability
        initial_uses = iron_sword.uses
        self.item_manager.update_item_durability(iron_sword.instance_id)
        self.assertEqual(iron_sword.uses, initial_uses - 1, "Durability not decreased")
        
        # Test adding to convoy
        self.item_manager.add_to_convoy(iron_sword.instance_id)
        convoy_items = self.item_manager.get_convoy_items()
        self.assertEqual(len(convoy_items), 1, "Incorrect number of convoy items")
        self.assertEqual(convoy_items[0].id, "iron_sword", "Convoy item ID mismatch")
    
    def test_map_manager(self):
        """
        Test that the MapManager can load and manage maps.
        """
        # Load a test map
        success = self.map_manager.load_map("ch1")
        self.assertTrue(success, "Failed to load map")
        
        # Test map dimensions
        width, height = self.map_manager.get_map_dimensions()
        self.assertEqual(width, 15, "Map width mismatch")
        self.assertEqual(height, 10, "Map height mismatch")
        
        # Test getting a tile
        tile = self.map_manager.get_tile(0, 0)
        self.assertIsNotNone(tile, "Failed to get tile")
        self.assertEqual(tile.terrain_type, TerrainType.PLAIN, "Tile terrain type mismatch")
        
        # Test placing a unit on the map
        leif = self.unit_manager.create_unit("leif2", "Leif", "lord", Affiliation.PLAYER)
        success = self.map_manager.set_unit_on_tile("leif2", 2, 2)
        self.assertTrue(success, "Failed to place unit on tile")
        
        # Test getting unit position
        position = self.map_manager.get_unit_position("leif2")
        self.assertEqual(position, (2, 2), "Unit position mismatch")
        
        # Test removing a unit from the map
        success = self.map_manager.remove_unit_from_map("leif2")
        self.assertTrue(success, "Failed to remove unit from map")
        position = self.map_manager.get_unit_position("leif2")
        self.assertIsNone(position, "Unit still on map after removal")

if __name__ == "__main__":
    unittest.main()