import unittest
from unittest.mock import MagicMock, patch, call

from src.gameplay_systems.inventory_system import InventorySystem, MAX_INVENTORY_SIZE
from src.core_engine.game_state import ItemInstance, StatusEffectEnum, ObjectStateEnum, TerrainTypeEnum
from src.core_engine.data_provider import ItemTypeEnum, RankEnum, WeaponTypeEnum

# Constants for testing
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
CONSUMABLE = ItemTypeEnum.CONSUMABLE
KEY = ItemTypeEnum.KEY
SCROLL = ItemTypeEnum.SCROLL


class TestInventorySystemTrading(unittest.TestCase):
    """Test cases for the trading functionality in InventorySystem."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the InventorySystem instance
        self.inventory_system = InventorySystem()
        self.inventory_system.initialize(self.mock_game_state_manager, self.mock_data_provider)

    def test_initiate_trade_success(self):
        """Test initiating a trade between two adjacent allied units."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [MagicMock(), MagicMock()]
        mock_unit1.faction = "PLAYER"
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [MagicMock()]
        mock_unit2.faction = "PLAYER"
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        self.inventory_system._are_units_adjacent = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.initiate_trade(unit1_id, unit2_id)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['unit1_inventory'], mock_unit1.inventory)
        self.assertEqual(result['unit2_inventory'], mock_unit2.inventory)
        self.assertIsNone(result['captive_inventory'])
        self.inventory_system._are_units_adjacent.assert_called_once_with(unit1_id, unit2_id)

    def test_initiate_trade_with_captive(self):
        """Test initiating a trade with a captured unit."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [MagicMock(), MagicMock()]
        mock_unit1.faction = "PLAYER"
        mock_unit1.carrying_unit_id = unit2_id
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [MagicMock()]
        mock_unit2.faction = "ENEMY"
        mock_unit2.is_captured = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        self.inventory_system._are_units_adjacent = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.initiate_trade(unit1_id, unit2_id)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['unit1_inventory'], mock_unit1.inventory)
        self.assertEqual(result['unit2_inventory'], [])  # Empty for UI clarity
        self.assertEqual(result['captive_inventory'], mock_unit2.inventory)
        self.inventory_system._are_units_adjacent.assert_called_once_with(unit1_id, unit2_id)

    def test_initiate_trade_not_adjacent(self):
        """Test initiating a trade between non-adjacent units fails."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit2 = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        self.inventory_system._are_units_adjacent = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system.initiate_trade(unit1_id, unit2_id)
        
        # Assert
        self.assertIsNone(result)
        self.inventory_system._are_units_adjacent.assert_called_once_with(unit1_id, unit2_id)

    def test_initiate_trade_invalid_target(self):
        """Test initiating a trade with an invalid target (not ally or captive) fails."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.faction = "PLAYER"
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.faction = "ENEMY"
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        self.inventory_system._are_units_adjacent = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.initiate_trade(unit1_id, unit2_id)
        
        # Assert
        self.assertIsNone(result)
        self.inventory_system._are_units_adjacent.assert_called_once_with(unit1_id, unit2_id)

    def test_execute_trade_simple_transfer(self):
        """Test executing a simple trade between two units."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Create mock items
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [mock_item1]
        mock_unit1.equipped_weapon_index = -1
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [mock_item2]
        mock_unit2.equipped_weapon_index = -1
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        
        # Define transfers: move item1 from unit1 to unit2 at index 1
        item_transfers = [(unit1_id, 0, unit2_id, 1)]
        
        # Act
        result = self.inventory_system.execute_trade(unit1_id, unit2_id, item_transfers)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(mock_unit1.inventory), 0)  # Unit1 gave away their only item
        self.assertEqual(len(mock_unit2.inventory), 2)  # Unit2 now has 2 items
        self.assertEqual(mock_unit2.inventory[0], mock_item2)  # Original item still at index 0
        self.assertEqual(mock_unit2.inventory[1], mock_item1)  # New item at index 1

    def test_execute_trade_swap_items(self):
        """Test executing a trade that swaps items between two units."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Create mock items
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [mock_item1]
        mock_unit1.equipped_weapon_index = 0  # Item1 is equipped
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [mock_item2]
        mock_unit2.equipped_weapon_index = 0  # Item2 is equipped
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        
        # Define transfers: swap items between units
        item_transfers = [
            (unit1_id, 0, unit2_id, 0),  # Move item1 from unit1 to unit2
            (unit2_id, 0, unit1_id, 0)   # Move item2 from unit2 to unit1
        ]
        
        # Act
        result = self.inventory_system.execute_trade(unit1_id, unit2_id, item_transfers)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(mock_unit1.inventory), 1)
        self.assertEqual(len(mock_unit2.inventory), 1)
        self.assertEqual(mock_unit1.inventory[0], mock_item2)  # Unit1 now has item2
        self.assertEqual(mock_unit2.inventory[0], mock_item1)  # Unit2 now has item1
        self.assertEqual(mock_unit1.equipped_weapon_index, 0)  # Unit1 still has index 0 equipped
        self.assertEqual(mock_unit2.equipped_weapon_index, 0)  # Unit2 still has index 0 equipped

    def test_execute_trade_with_captive(self):
        """Test executing a trade with a captured unit."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        captive_id = "CAPTIVE"
        
        # Create mock items
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        mock_item3 = MagicMock()
        mock_item3.item_id = "VULNERARY"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [mock_item1]
        mock_unit1.equipped_weapon_index = -1
        mock_unit1.carrying_unit_id = unit2_id
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [mock_item2, mock_item3]
        mock_unit2.equipped_weapon_index = -1
        mock_unit2.is_captured = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        
        # Define transfers: take item2 from captive to unit1
        item_transfers = [(captive_id, 0, unit1_id, 1)]
        
        # Act
        result = self.inventory_system.execute_trade(unit1_id, unit2_id, item_transfers)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(mock_unit1.inventory), 2)  # Unit1 now has 2 items
        self.assertEqual(len(mock_unit2.inventory), 1)  # Captive now has 1 item
        self.assertEqual(mock_unit1.inventory[0], mock_item1)  # Original item still at index 0
        self.assertEqual(mock_unit1.inventory[1], mock_item2)  # Captive's item now at index 1
        self.assertEqual(mock_unit2.inventory[0], mock_item3)  # Captive still has their second item

    def test_execute_trade_invalid_transfer(self):
        """Test executing a trade with invalid transfers fails."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [MagicMock()]
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [MagicMock()]
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        
        # Define invalid transfers: invalid source index
        item_transfers = [(unit1_id, 5, unit2_id, 0)]  # Index 5 doesn't exist
        
        # Act
        result = self.inventory_system.execute_trade(unit1_id, unit2_id, item_transfers)
        
        # Assert
        self.assertFalse(result)
        self.assertEqual(len(mock_unit1.inventory), 1)  # Inventories unchanged
        self.assertEqual(len(mock_unit2.inventory), 1)

    def test_execute_trade_inventory_limit(self):
        """Test executing a trade that would exceed inventory limit fails."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.inventory = [MagicMock() for _ in range(2)]
        mock_unit1.carrying_unit_id = None
        
        mock_unit2 = MagicMock()
        mock_unit2.inventory = [MagicMock() for _ in range(MAX_INVENTORY_SIZE)]  # Already at max
        mock_unit2.is_captured = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit1 if id == unit1_id else mock_unit2
        
        # Define transfers that would exceed limit
        item_transfers = [
            (unit1_id, 0, unit2_id, MAX_INVENTORY_SIZE),  # This would make unit2 have MAX_INVENTORY_SIZE + 1 items
            (unit1_id, 1, unit2_id, MAX_INVENTORY_SIZE + 1)
        ]
        
        # Act
        result = self.inventory_system.execute_trade(unit1_id, unit2_id, item_transfers)
        
        # Assert
        self.assertFalse(result)
        self.assertEqual(len(mock_unit1.inventory), 2)  # Inventories unchanged
        self.assertEqual(len(mock_unit2.inventory), MAX_INVENTORY_SIZE)