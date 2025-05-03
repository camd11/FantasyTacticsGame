import unittest
from unittest.mock import MagicMock, patch, call

from src.gameplay_systems.inventory_system import InventorySystem, MAX_INVENTORY_SIZE
from src.core_engine.game_state import ItemInstance, StatusEffectEnum
from src.core_engine.data_provider import ItemTypeEnum, RankEnum, WeaponTypeEnum

# Constants for testing
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
CONSUMABLE = ItemTypeEnum.CONSUMABLE
KEY = ItemTypeEnum.KEY
SCROLL = ItemTypeEnum.SCROLL


class TestInventorySystem(unittest.TestCase):
    """Test cases for the InventorySystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the InventorySystem instance
        self.inventory_system = InventorySystem()
        self.inventory_system.initialize(self.mock_game_state_manager, self.mock_data_provider)

    # TDD: Test adding item respects inventory limit, uses correct durability
    def test_add_item_to_inventory_success(self):
        """Test adding an item to a unit's inventory successfully."""
        # Arrange
        unit_id = "U001"
        item_id = "IRON_SWORD"
        
        # Mock unit with empty inventory
        mock_unit = MagicMock()
        mock_unit.inventory = []
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.add_item_to_inventory(unit_id, item_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(item_id)
        self.assertEqual(len(mock_unit.inventory), 1)
        self.assertEqual(mock_unit.inventory[0].item_id, item_id)
        self.assertEqual(mock_unit.inventory[0].current_durability, mock_item_data.max_durability)
    
    def test_add_item_to_inventory_with_custom_durability(self):
        """Test adding an item with custom durability."""
        # Arrange
        unit_id = "U001"
        item_id = "IRON_SWORD"
        custom_durability = 30
        
        # Mock unit with empty inventory
        mock_unit = MagicMock()
        mock_unit.inventory = []
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.add_item_to_inventory(unit_id, item_id, custom_durability)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_unit.inventory[0].current_durability, custom_durability)
    
    def test_add_item_to_inventory_full_inventory(self):
        """Test adding an item to a full inventory fails."""
        # Arrange
        unit_id = "U001"
        item_id = "IRON_SWORD"
        
        # Mock unit with full inventory
        mock_unit = MagicMock()
        mock_unit.inventory = [MagicMock() for _ in range(MAX_INVENTORY_SIZE)]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.add_item_to_inventory(unit_id, item_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.assertEqual(len(mock_unit.inventory), MAX_INVENTORY_SIZE)  # Inventory unchanged
    
    def test_add_item_to_inventory_invalid_unit(self):
        """Test adding an item to an invalid unit fails."""
        # Arrange
        unit_id = "INVALID"
        item_id = "IRON_SWORD"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.inventory_system.add_item_to_inventory(unit_id, item_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_not_called()
    
    def test_add_item_to_inventory_invalid_item(self):
        """Test adding an invalid item fails."""
        # Arrange
        unit_id = "U001"
        item_id = "INVALID"
        
        # Mock unit with empty inventory
        mock_unit = MagicMock()
        mock_unit.inventory = []
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = None
        
        # Act
        result = self.inventory_system.add_item_to_inventory(unit_id, item_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(item_id)
        self.assertEqual(len(mock_unit.inventory), 0)  # Inventory unchanged

    # TDD: Test removing item handles valid/invalid index, returns correct item
    def test_remove_item_from_inventory_success(self):
        """Test removing an item from a unit's inventory successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 1
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = -1  # No equipped weapon
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.remove_item_from_inventory(unit_id, item_index)
        
        # Assert
        self.assertEqual(result, mock_item2)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.assertEqual(len(mock_unit.inventory), 1)
        self.assertEqual(mock_unit.inventory[0], mock_item1)
    
    def test_remove_item_from_inventory_equipped_item(self):
        """Test removing an equipped item unequips it."""
        # Arrange
        unit_id = "U001"
        item_index = 1
        
        # Mock unit with inventory and equipped weapon
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = 1  # Second item equipped
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.remove_item_from_inventory(unit_id, item_index)
        
        # Assert
        self.assertEqual(result, mock_item2)
        self.assertEqual(mock_unit.equipped_weapon_index, -1)  # Should be unequipped
    
    def test_remove_item_from_inventory_adjust_equipped_index(self):
        """Test removing an item before the equipped one adjusts the equipped index."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory and equipped weapon
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = 1  # Second item equipped
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.remove_item_from_inventory(unit_id, item_index)
        
        # Assert
        self.assertEqual(result, mock_item1)
        self.assertEqual(mock_unit.equipped_weapon_index, 0)  # Should be adjusted
    
    def test_remove_item_from_inventory_invalid_index(self):
        """Test removing an item with an invalid index fails."""
        # Arrange
        unit_id = "U001"
        item_index = 5  # Out of bounds
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_unit.inventory = [mock_item1]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.remove_item_from_inventory(unit_id, item_index)
        
        # Assert
        self.assertIsNone(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)

    # TDD: Test equipping valid weapon updates index, unequips previous
    def test_equip_item_success(self):
        """Test equipping an item successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 1
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "IRON_LANCE"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = 0  # First item equipped
        mock_unit.weapon_ranks = {WeaponTypeEnum.LANCE: RankEnum.D}
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Lance"
        mock_item_data.type = WEAPON
        mock_item_data.weapon_type = WeaponTypeEnum.LANCE
        mock_item_data.required_rank = RankEnum.E
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _is_rank_higher to return False (unit rank is sufficient)
        self.inventory_system._is_rank_higher = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system.equip_item(unit_id, item_index)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item2.item_id)
        self.assertEqual(mock_unit.equipped_weapon_index, item_index)
    
    # TDD: Test equipping invalid item fails
    def test_equip_item_non_weapon(self):
        """Test equipping a non-weapon item fails."""
        # Arrange
        unit_id = "U001"
        item_index = 1
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "VULNERARY"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = -1  # No equipped weapon
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Vulnerary"
        mock_item_data.type = CONSUMABLE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.equip_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item2.item_id)
        self.assertEqual(mock_unit.equipped_weapon_index, -1)  # Unchanged
    
    # TDD: Test equipping weapon with unmet rank requirement fails
    def test_equip_item_insufficient_rank(self):
        """Test equipping a weapon with insufficient rank fails."""
        # Arrange
        unit_id = "U001"
        item_index = 1
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_item2 = MagicMock()
        mock_item2.item_id = "SILVER_LANCE"
        mock_unit.inventory = [mock_item1, mock_item2]
        mock_unit.equipped_weapon_index = -1  # No equipped weapon
        mock_unit.weapon_ranks = {WeaponTypeEnum.LANCE: RankEnum.D}
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Silver Lance"
        mock_item_data.type = WEAPON
        mock_item_data.weapon_type = WeaponTypeEnum.LANCE
        mock_item_data.required_rank = RankEnum.A
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _is_rank_higher to return True (required rank is higher than unit rank)
        self.inventory_system._is_rank_higher = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.equip_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item2.item_id)
        self.inventory_system._is_rank_higher.assert_called_once()
        self.assertEqual(mock_unit.equipped_weapon_index, -1)  # Unchanged

    # TDD: Test unequipping sets index to -1
    def test_unequip_item_success(self):
        """Test unequipping an item successfully."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with equipped weapon
        mock_unit = MagicMock()
        mock_unit.equipped_weapon_index = 1
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.unequip_item(unit_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.assertEqual(mock_unit.equipped_weapon_index, -1)
    
    def test_unequip_item_invalid_unit(self):
        """Test unequipping an item from an invalid unit fails."""
        # Arrange
        unit_id = "INVALID"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.inventory_system.unequip_item(unit_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)

    # TDD: Test decrement durability reduces count correctly
    def test_decrement_item_durability_success(self):
        """Test decrementing item durability successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "IRON_SWORD"
        mock_item.current_durability = 10
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item.item_id)
        self.assertEqual(mock_item.current_durability, 9)
    
    def test_decrement_item_durability_custom_amount(self):
        """Test decrementing item durability by a custom amount."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        amount = 3
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "IRON_SWORD"
        mock_item.current_durability = 10
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index, amount)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_item.current_durability, 7)
    
    def test_decrement_item_durability_indestructible_item(self):
        """Test decrementing durability of an indestructible item."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "LEGENDARY_SWORD"
        mock_item.current_durability = 0  # Indestructible items often have 0 durability
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Legendary Sword"
        mock_item_data.max_durability = 0  # Indicates indestructible
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(mock_item.current_durability, 0)  # Unchanged

    # TDD: Test decrement durability handles breaking repairable items (becomes BROKEN_*)
    def test_decrement_item_durability_breaks_repairable_item(self):
        """Test decrementing durability breaks a repairable item."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "IRON_SWORD"
        mock_item.current_durability = 1  # Will break
        mock_unit.inventory = [mock_item]
        mock_unit.equipped_weapon_index = -1  # Not equipped
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        mock_item_data.type = WEAPON
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _get_broken_item_id to return a broken version
        self.inventory_system._get_broken_item_id = MagicMock(return_value="BROKEN_IRON_SWORD")
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)  # Returns False when item breaks
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        # The implementation gets the item data for the original item, not the broken one
        self.mock_data_provider.get_item_data.assert_called_once_with("IRON_SWORD")
        # The implementation calls _get_broken_item_id with the original item ID
        self.inventory_system._get_broken_item_id.assert_called_once_with("IRON_SWORD")
        self.assertEqual(mock_item.item_id, "BROKEN_IRON_SWORD")
        self.assertEqual(mock_item.current_durability, 0)

    # TDD: Test decrement durability removes non-repairable items at 0
    def test_decrement_item_durability_removes_non_repairable_item(self):
        """Test decrementing durability removes a non-repairable item."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "VULNERARY"
        mock_item.current_durability = 1  # Will break
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Vulnerary"
        mock_item_data.max_durability = 3
        mock_item_data.type = CONSUMABLE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _get_broken_item_id to return None (non-repairable)
        self.inventory_system._get_broken_item_id = MagicMock(return_value=None)
        
        # Mock remove_item_from_inventory
        self.inventory_system.remove_item_from_inventory = MagicMock(return_value=mock_item)
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)  # Returns False when item is removed
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item.item_id)
        self.inventory_system._get_broken_item_id.assert_called_once_with(mock_item.item_id)
        self.inventory_system.remove_item_from_inventory.assert_called_once_with(unit_id, item_index)

    # TDD: Test decrement durability unequips item if equipped weapon breaks
    def test_decrement_item_durability_unequips_broken_weapon(self):
        """Test decrementing durability unequips a weapon when it breaks."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory and equipped weapon
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "IRON_SWORD"
        mock_item.current_durability = 1  # Will break
        mock_unit.inventory = [mock_item]
        mock_unit.equipped_weapon_index = 0  # Equipped
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Iron Sword"
        mock_item_data.max_durability = 46
        mock_item_data.type = WEAPON
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _get_broken_item_id to return None (non-repairable for simplicity)
        self.inventory_system._get_broken_item_id = MagicMock(return_value=None)
        
        # Mock remove_item_from_inventory to simulate removal and unequipping
        def mock_remove(unit_id, index):
            mock_unit.equipped_weapon_index = -1
            return mock_item
        
        self.inventory_system.remove_item_from_inventory = MagicMock(side_effect=mock_remove)
        
        # Act
        result = self.inventory_system.decrement_item_durability(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)  # Returns False when item is removed
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.inventory_system.remove_item_from_inventory.assert_called_once_with(unit_id, item_index)
        self.assertEqual(mock_unit.equipped_weapon_index, -1)  # Should be unequipped

    # TDD: Test repair restores correct item ID and full durability
    def test_repair_item_success(self):
        """Test repairing a broken item successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "BROKEN_IRON_SWORD"
        mock_item.current_durability = 0
        mock_unit.inventory = [mock_item]
        
        # Mock original item data
        mock_original_item_data = MagicMock()
        mock_original_item_data.name = "Iron Sword"
        mock_original_item_data.max_durability = 46
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_original_item_data
        
        # Mock _get_original_item_id_from_broken to return the original item ID
        self.inventory_system._get_original_item_id_from_broken = MagicMock(return_value="IRON_SWORD")
        
        # Act
        result = self.inventory_system.repair_item(unit_id, item_index)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with("IRON_SWORD")
        # The implementation gets the original item ID from the broken one
        self.inventory_system._get_original_item_id_from_broken.assert_called_once_with("BROKEN_IRON_SWORD")
        self.assertEqual(mock_item.item_id, "IRON_SWORD")
        self.assertEqual(mock_item.current_durability, 46)
    
    # TDD: Test repair fails on non-broken/non-repairable items
    def test_repair_item_not_broken(self):
        """Test repairing a non-broken item fails."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "IRON_SWORD"  # Not broken
        mock_item.current_durability = 10
        mock_unit.inventory = [mock_item]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock _get_original_item_id_from_broken to return None (not a broken item)
        self.inventory_system._get_original_item_id_from_broken = MagicMock(return_value=None)
        
        # Act
        result = self.inventory_system.repair_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.inventory_system._get_original_item_id_from_broken.assert_called_once_with(mock_item.item_id)
        self.mock_data_provider.get_item_data.assert_not_called()
        self.assertEqual(mock_item.item_id, "IRON_SWORD")  # Unchanged
        self.assertEqual(mock_item.current_durability, 10)  # Unchanged
    
    def test_equip_item_invalid_index(self):
        """Test equipping an item with an invalid index fails."""
        # Arrange
        unit_id = "U001"
        item_index = 5  # Out of bounds
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item1 = MagicMock()
        mock_item1.item_id = "IRON_SWORD"
        mock_unit.inventory = [mock_item1]
        mock_unit.equipped_weapon_index = -1  # No equipped weapon
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system.equip_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.assertEqual(mock_unit.equipped_weapon_index, -1)  # Unchanged
        self.assertEqual(len(mock_unit.inventory), 1)  # Inventory unchanged
    
    def test_remove_item_from_inventory_invalid_unit(self):
        """Test removing an item from an invalid unit fails."""
        # Arrange
        unit_id = "INVALID"
        item_index = 0
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.inventory_system.remove_item_from_inventory(unit_id, item_index)
        
        # Assert
        self.assertIsNone(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
