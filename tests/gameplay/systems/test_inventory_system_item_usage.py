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


class TestInventorySystemItemUsage(unittest.TestCase):
    """Test cases for the item usage functionality in InventorySystem."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the InventorySystem instance
        self.inventory_system = InventorySystem()
        self.inventory_system.initialize(self.mock_game_state_manager, self.mock_data_provider)
        
        # Mock methods that are being asserted with assert_not_called
        self.original_decrement_item_durability = self.inventory_system.decrement_item_durability
        self.inventory_system.decrement_item_durability = MagicMock(name="decrement_item_durability")
        self.inventory_system.decrement_item_durability.side_effect = self.original_decrement_item_durability
        
        # Mock _open_lock for tests that assert it's not called
        self.original_open_lock = self.inventory_system._open_lock
        self.inventory_system._open_lock = MagicMock(name="_open_lock")
        self.inventory_system._open_lock.side_effect = self.original_open_lock

    def test_use_consumable_item_success(self):
        """Test using a consumable item successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "VULNERARY"
        mock_item.current_durability = 3
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Vulnerary"
        mock_item_data.type = CONSUMABLE
        mock_item_data.effects = [{'type': 'HEAL', 'amount': 20}]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _apply_item_effect to return True
        self.inventory_system._apply_item_effect = MagicMock(return_value=True)
        
        # Mock decrement_item_durability to simulate item usage
        self.inventory_system.decrement_item_durability = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item.item_id)
        self.inventory_system._apply_item_effect.assert_called_once_with(unit_id, mock_item_data.effects, None)
        self.inventory_system.decrement_item_durability.assert_called_once_with(unit_id, item_index)
        self.mock_game_state_manager.set_unit_acted.assert_called_once_with(unit_id)

    def test_use_consumable_item_on_target(self):
        """Test using a consumable item on another unit."""
        # Arrange
        unit_id = "U001"
        target_id = "U002"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "VULNERARY"
        mock_item.current_durability = 3
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Vulnerary"
        mock_item_data.type = CONSUMABLE
        mock_item_data.effects = [{'type': 'HEAL', 'amount': 20}]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _apply_item_effect to return True
        self.inventory_system._apply_item_effect = MagicMock(return_value=True)
        
        # Mock decrement_item_durability to simulate item usage
        self.inventory_system.decrement_item_durability = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index, target_id)
        
        # Assert
        self.assertTrue(result)
        self.inventory_system._apply_item_effect.assert_called_once_with(unit_id, mock_item_data.effects, target_id)

    def test_use_consumable_item_effect_failed(self):
        """Test using a consumable item where the effect fails to apply."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "VULNERARY"
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Vulnerary"
        mock_item_data.type = CONSUMABLE
        mock_item_data.effects = [{'type': 'HEAL', 'amount': 20}]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _apply_item_effect to return False (effect failed)
        self.inventory_system._apply_item_effect = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.inventory_system._apply_item_effect.assert_called_once_with(unit_id, mock_item_data.effects, None)
        self.inventory_system.decrement_item_durability.assert_not_called()
        self.mock_game_state_manager.set_unit_acted.assert_not_called()

    def test_use_key_item_success(self):
        """Test using a key item successfully."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        target_tile = (5, 5)
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "DOOR_KEY"
        mock_item.current_durability = 1
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Door Key"
        mock_item_data.type = KEY
        mock_item_data.key_type = "DOOR"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _is_tile_lock to return True
        self.inventory_system._is_tile_lock = MagicMock(return_value=True)
        
        # Mock _open_lock to return True
        self.inventory_system._open_lock = MagicMock(return_value=True)
        
        # Mock decrement_item_durability to simulate item usage
        self.inventory_system.decrement_item_durability = MagicMock(return_value=True)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index, target_tile=target_tile)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_called_once_with(mock_item.item_id)
        self.inventory_system._is_tile_lock.assert_called_once_with(target_tile)
        self.inventory_system._open_lock.assert_called_once_with(target_tile, "DOOR")
        self.inventory_system.decrement_item_durability.assert_called_once_with(unit_id, item_index)
        self.mock_game_state_manager.set_unit_acted.assert_called_once_with(unit_id)

    def test_use_key_item_no_lock(self):
        """Test using a key item on a tile with no lock fails."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        target_tile = (5, 5)
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "DOOR_KEY"
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Door Key"
        mock_item_data.type = KEY
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _is_tile_lock to return False (no lock)
        self.inventory_system._is_tile_lock = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index, target_tile=target_tile)
        
        # Assert
        self.assertFalse(result)
        self.inventory_system._is_tile_lock.assert_called_once_with(target_tile)
        self.inventory_system._open_lock.assert_not_called()
        self.inventory_system.decrement_item_durability.assert_not_called()
        self.mock_game_state_manager.set_unit_acted.assert_not_called()

    def test_use_key_item_lock_failed(self):
        """Test using a key item where opening the lock fails."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        target_tile = (5, 5)
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "DOOR_KEY"
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Door Key"
        mock_item_data.type = KEY
        mock_item_data.key_type = "DOOR"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Mock _is_tile_lock to return True
        self.inventory_system._is_tile_lock = MagicMock(return_value=True)
        
        # Mock _open_lock to return False (failed to open)
        self.inventory_system._open_lock = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index, target_tile=target_tile)
        
        # Assert
        self.assertFalse(result)
        self.inventory_system._is_tile_lock.assert_called_once_with(target_tile)
        self.inventory_system._open_lock.assert_called_once_with(target_tile, "DOOR")
        self.inventory_system.decrement_item_durability.assert_not_called()
        self.mock_game_state_manager.set_unit_acted.assert_not_called()

    def test_use_scroll_item_fails(self):
        """Test using a scroll item fails (scrolls are passive)."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "HEZUL_SCROLL"
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Hezul Scroll"
        mock_item_data.type = SCROLL
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.set_unit_acted.assert_not_called()

    def test_use_staff_item_fails(self):
        """Test using a staff item fails (staves are used through combat system)."""
        # Arrange
        unit_id = "U001"
        item_index = 0
        
        # Mock unit with inventory
        mock_unit = MagicMock()
        mock_item = MagicMock()
        mock_item.item_id = "HEAL_STAFF"
        mock_unit.inventory = [mock_item]
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.name = "Heal Staff"
        mock_item_data.type = STAFF
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        
        # Act
        result = self.inventory_system.use_item(unit_id, item_index)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.set_unit_acted.assert_not_called()

    def test_apply_item_effect_heal(self):
        """Test applying a healing effect from an item."""
        # Arrange
        unit_id = "U001"
        effects = [{'type': 'HEAL', 'amount': 20}]
        
        # Mock unit
        mock_unit = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system._apply_item_effect(unit_id, effects)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.apply_healing.assert_called_once_with(unit_id, 20)

    def test_apply_item_effect_stat_boost(self):
        """Test applying a stat boost effect from an item."""
        # Arrange
        unit_id = "U001"
        effects = [{'type': 'STAT_BOOST', 'stat': 'STR', 'amount': 2}]
        
        # Mock unit
        mock_unit = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system._apply_item_effect(unit_id, effects)
        
        # Assert
        self.assertTrue(result)
        # Note: In the current implementation, stat boosts are not fully implemented
        # and just return True. In a complete implementation, we would check for
        # a call to a method like apply_stat_boost.

    def test_apply_item_effect_cure_status(self):
        """Test applying a status cure effect from an item."""
        # Arrange
        unit_id = "U001"
        effects = [{'type': 'CURE_STATUS', 'status': 'POISON'}]
        
        # Mock unit with poison status
        mock_unit = MagicMock()
        mock_unit.has_status.return_value = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system._apply_item_effect(unit_id, effects)
        
        # Assert
        self.assertTrue(result)
        mock_unit.has_status.assert_called_once_with(StatusEffectEnum.POISON)
        self.mock_game_state_manager.remove_status_effect.assert_called_once_with(unit_id, StatusEffectEnum.POISON)

    def test_apply_item_effect_cure_status_not_afflicted(self):
        """Test applying a status cure effect when the unit doesn't have that status."""
        # Arrange
        unit_id = "U001"
        effects = [{'type': 'CURE_STATUS', 'status': 'POISON'}]
        
        # Mock unit without poison status
        mock_unit = MagicMock()
        mock_unit.has_status.return_value = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.inventory_system._apply_item_effect(unit_id, effects)
        
        # Assert
        self.assertFalse(result)  # Should fail since unit doesn't have the status
        mock_unit.has_status.assert_called_once_with(StatusEffectEnum.POISON)
        self.mock_game_state_manager.remove_status_effect.assert_not_called()

    def test_is_tile_lock_door(self):
        """Test checking if a tile contains a door lock."""
        # Arrange
        position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.DOOR
        
        # Act
        result = self.inventory_system._is_tile_lock(position)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)

    def test_is_tile_lock_chest(self):
        """Test checking if a tile contains a chest lock."""
        # Arrange
        position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN
        self.mock_game_state_manager.current_game_state.map_state.object_states = {position: ObjectStateEnum.NORMAL}
        
        # Act
        result = self.inventory_system._is_tile_lock(position)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)

    def test_is_tile_lock_no_lock(self):
        """Test checking if a tile with no lock returns False."""
        # Arrange
        position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN
        self.mock_game_state_manager.current_game_state.map_state.object_states = {}
        
        # Act
        result = self.inventory_system._is_tile_lock(position)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)

    def test_open_lock_door(self):
        """Test opening a door lock."""
        # Arrange
        position = (5, 5)
        key_type = "DOOR"
        
        # Configure mocks
        self.inventory_system._is_tile_lock = MagicMock(return_value=True)
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.DOOR
        self.mock_game_state_manager.current_game_state.map_state.object_states = {}
        
        # Act
        result = self.inventory_system._open_lock(position, key_type)
        
        # Assert
        self.assertTrue(result)
        self.inventory_system._is_tile_lock.assert_called_once_with(position)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)
        self.assertEqual(self.mock_game_state_manager.current_game_state.map_state.object_states[position], 
                         ObjectStateEnum.OPENED)

    def test_open_lock_chest(self):
        """Test opening a chest lock."""
        # Arrange
        position = (5, 5)
        key_type = "CHEST"
        
        # Configure mocks
        self.inventory_system._is_tile_lock = MagicMock(return_value=True)
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN
        self.mock_game_state_manager.current_game_state.map_state.object_states = {position: ObjectStateEnum.NORMAL}
        
        # Act
        result = self.inventory_system._open_lock(position, key_type)
        
        # Assert
        self.assertTrue(result)
        self.inventory_system._is_tile_lock.assert_called_once_with(position)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)
        self.assertEqual(self.mock_game_state_manager.current_game_state.map_state.object_states[position], 
                         ObjectStateEnum.LOOTED)

    def test_open_lock_no_lock(self):
        """Test opening a tile with no lock fails."""
        # Arrange
        position = (5, 5)
        key_type = "DOOR"
        
        # Configure mocks
        self.inventory_system._is_tile_lock = MagicMock(return_value=False)
        
        # Act
        result = self.inventory_system._open_lock(position, key_type)
        
        # Assert
        self.assertFalse(result)
        self.inventory_system._is_tile_lock.assert_called_once_with(position)
        self.mock_game_state_manager.get_terrain_type.assert_not_called()