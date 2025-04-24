import unittest
from unittest.mock import MagicMock, patch, call

# Import the DismountingSystem (will be implemented later)
from src.gameplay_systems.dismounting_system import DismountingSystem

# Import necessary enums and classes
from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider, StatEnum, WeaponTypeEnum

# Constants for testing
STR = StatEnum.STR
MAG = StatEnum.MAG
SKL = StatEnum.SKL
SPD = StatEnum.SPD
LUK = StatEnum.LUK
DEF = StatEnum.DEF
CON = StatEnum.CON
MOV = StatEnum.MOV
HP = StatEnum.HP

# Movement types
INFANTRY = "INFANTRY"
CAVALRY = "CAVALRY"
FLYING = "FLYING"

# Weapon types
SWORD = WeaponTypeEnum.SWORD
LANCE = WeaponTypeEnum.LANCE
AXE = WeaponTypeEnum.AXE
BOW = WeaponTypeEnum.BOW


class TestDismountingSystem(unittest.TestCase):
    """Test cases for the DismountingSystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_unit_system = MagicMock(name="UnitSystem")
        self.mock_map_system = MagicMock(name="MapSystem")
        
        # Create the DismountingSystem instance
        self.dismounting_system = DismountingSystem()
        self.dismounting_system.initialize(
            self.mock_game_state_manager,
            self.mock_data_provider,
            self.mock_unit_system,
            self.mock_map_system
        )

    # TDD_ANCHOR: test_can_dismount_eligibility
    def test_can_dismount_eligibility(self):
        """Test that can_dismount correctly determines if a unit is eligible to dismount."""
        # Arrange
        mounted_unit_id = "M001"
        dismounted_unit_id = "D001"
        non_mountable_unit_id = "N001"
        indoor_unit_id = "I001"
        
        # Mock units
        mock_mounted_unit = MagicMock()
        mock_mounted_unit.is_mounted = True
        mock_mounted_unit.mounted_class_id = "C001"
        mock_mounted_unit.position = (5, 5)
        
        mock_dismounted_unit = MagicMock()
        mock_dismounted_unit.is_mounted = False
        
        mock_non_mountable_unit = MagicMock()
        mock_non_mountable_unit.is_mounted = True
        mock_non_mountable_unit.mounted_class_id = "C002"
        mock_non_mountable_unit.position = (6, 6)
        
        mock_indoor_unit = MagicMock()
        mock_indoor_unit.is_mounted = True
        mock_indoor_unit.mounted_class_id = "C001"
        mock_indoor_unit.position = (7, 7)
        
        # Mock class data
        mock_mountable_class = MagicMock()
        mock_mountable_class.can_mount = True
        
        mock_non_mountable_class = MagicMock()
        mock_non_mountable_class.can_mount = False
        
        # Mock tiles
        mock_outdoor_tile = MagicMock()
        mock_indoor_tile = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.side_effect = lambda id: {
            mounted_unit_id: mock_mounted_unit,
            dismounted_unit_id: mock_dismounted_unit,
            non_mountable_unit_id: mock_non_mountable_unit,
            indoor_unit_id: mock_indoor_unit
        }.get(id)
        
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mountable_class,
            "C002": mock_non_mountable_class
        }.get(class_id)
        
        self.mock_map_system.get_tile.side_effect = lambda pos: {
            (5, 5): mock_outdoor_tile,
            (6, 6): mock_outdoor_tile,
            (7, 7): mock_indoor_tile
        }.get(pos)
        
        self.mock_map_system.is_tile_indoors.side_effect = lambda tile: tile == mock_indoor_tile
        
        # Act
        mounted_result = self.dismounting_system.can_dismount(mounted_unit_id)
        dismounted_result = self.dismounting_system.can_dismount(dismounted_unit_id)
        non_mountable_result = self.dismounting_system.can_dismount(non_mountable_unit_id)
        indoor_result = self.dismounting_system.can_dismount(indoor_unit_id)
        
        # Assert
        self.assertTrue(mounted_result, "Mounted unit with can_mount class should be eligible to dismount")
        self.assertFalse(dismounted_result, "Already dismounted unit should not be eligible to dismount")
        self.assertFalse(non_mountable_result, "Unit with non-mountable class should not be eligible to dismount")
        self.assertFalse(indoor_result, "Unit on indoor tile should not be eligible to dismount (already forced)")

    # TDD_ANCHOR: test_can_mount_eligibility
    def test_can_mount_eligibility(self):
        """Test that can_mount correctly determines if a unit is eligible to mount."""
        # Arrange
        dismounted_unit_id = "D001"
        mounted_unit_id = "M001"
        non_mountable_unit_id = "N001"
        indoor_unit_id = "I001"
        
        # Mock units
        mock_dismounted_unit = MagicMock()
        mock_dismounted_unit.is_mounted = False
        mock_dismounted_unit.mounted_class_id = "C001"
        mock_dismounted_unit.position = (5, 5)
        
        mock_mounted_unit = MagicMock()
        mock_mounted_unit.is_mounted = True
        
        mock_non_mountable_unit = MagicMock()
        mock_non_mountable_unit.is_mounted = False
        mock_non_mountable_unit.mounted_class_id = "C002"
        mock_non_mountable_unit.position = (6, 6)
        
        mock_indoor_unit = MagicMock()
        mock_indoor_unit.is_mounted = False
        mock_indoor_unit.mounted_class_id = "C001"
        mock_indoor_unit.position = (7, 7)
        
        # Mock class data
        mock_mountable_class = MagicMock()
        mock_mountable_class.can_mount = True
        
        mock_non_mountable_class = MagicMock()
        mock_non_mountable_class.can_mount = False
        
        # Mock tiles
        mock_outdoor_tile = MagicMock()
        mock_indoor_tile = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.side_effect = lambda id: {
            dismounted_unit_id: mock_dismounted_unit,
            mounted_unit_id: mock_mounted_unit,
            non_mountable_unit_id: mock_non_mountable_unit,
            indoor_unit_id: mock_indoor_unit
        }.get(id)
        
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mountable_class,
            "C002": mock_non_mountable_class
        }.get(class_id)
        
        self.mock_map_system.get_tile.side_effect = lambda pos: {
            (5, 5): mock_outdoor_tile,
            (6, 6): mock_outdoor_tile,
            (7, 7): mock_indoor_tile
        }.get(pos)
        
        self.mock_map_system.is_tile_indoors.side_effect = lambda tile: tile == mock_indoor_tile
        
        # Act
        dismounted_result = self.dismounting_system.can_mount(dismounted_unit_id)
        mounted_result = self.dismounting_system.can_mount(mounted_unit_id)
        non_mountable_result = self.dismounting_system.can_mount(non_mountable_unit_id)
        indoor_result = self.dismounting_system.can_mount(indoor_unit_id)
        
        # Assert
        self.assertTrue(dismounted_result, "Dismounted unit with can_mount class should be eligible to mount")
        self.assertFalse(mounted_result, "Already mounted unit should not be eligible to mount")
        self.assertFalse(non_mountable_result, "Unit with non-mountable class should not be eligible to mount")
        self.assertFalse(indoor_result, "Unit on indoor tile should not be eligible to mount")
    # TDD_ANCHOR: test_execute_dismount_state_changes
    def test_execute_dismount_state_changes(self):
        """Test that execute_dismount correctly applies all state changes."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = True
        mock_unit.mounted_class_id = "C001"
        mock_unit.current_stats = {MOV: 8}
        mock_unit.current_movement_type = CAVALRY
        
        # Mock classes
        mock_mounted_class = MagicMock()
        mock_mounted_class.dismount_class_id = "C002"
        mock_mounted_class.dismount_stat_modifiers = None
        
        mock_dismounted_class = MagicMock()
        mock_dismounted_class.mov = 5
        mock_dismounted_class.movement_type = INFANTRY
        mock_dismounted_class.usable_weapon_types_dismounted = [SWORD]
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_dismount to return True
        self.dismounting_system.can_dismount = MagicMock(return_value=True)
        
        # Act
        result = self.dismounting_system.execute_dismount(unit_id)
        
        # Assert
        self.assertTrue(result.success, "execute_dismount should return success")
        self.assertEqual(mock_unit.is_mounted, False, "Unit should be marked as dismounted")
        self.assertEqual(mock_unit.current_movement_type, INFANTRY, "Movement type should change to Infantry")
        
        # Verify method calls
        self.dismounting_system.can_dismount.assert_called_once_with(unit_id)
        self.mock_unit_system.set_unit_action_taken.assert_called_once_with(unit_id)
        self.mock_game_state_manager.notify_visual_update.assert_called_once_with(unit_id, "dismounted")
        
        # Test MOV stat update separately
        def test_dismount_mov_stat_update(self):
            """Test that dismounting correctly updates the MOV stat."""
            # Arrange
            unit_id = "U001"
            
            # Mock unit
            mock_unit = MagicMock()
            mock_unit.is_mounted = True
            mock_unit.mounted_class_id = "C001"
            mock_unit.current_stats = MagicMock()
            mock_unit.current_movement_type = CAVALRY
            
            # Mock classes
            mock_mounted_class = MagicMock()
            mock_mounted_class.dismount_class_id = "C002"
            mock_mounted_class.dismount_stat_modifiers = None
            
            mock_dismounted_class = MagicMock()
            mock_dismounted_class.mov = 5
            mock_dismounted_class.movement_type = INFANTRY
            mock_dismounted_class.usable_weapon_types_dismounted = [SWORD]
            
            # Configure mocks
            self.mock_unit_system.get_unit.return_value = mock_unit
            self.mock_data_provider.get_class.side_effect = lambda class_id: {
                "C001": mock_mounted_class,
                "C002": mock_dismounted_class
            }.get(class_id)
            
            # Mock can_dismount to return True
            self.dismounting_system.can_dismount = MagicMock(return_value=True)
            
            # Act
            self.dismounting_system.execute_dismount(unit_id)
            
            # Assert
            mock_unit.current_stats.__setitem__.assert_called_with("MOV", 5)
        self.mock_unit_system.get_unit.assert_called_with(unit_id)
        self.mock_data_provider.get_class.assert_has_calls([
            call("C001"),  # Get mounted class
            call("C002")   # Get dismounted class
        ])
        self.mock_unit_system.set_unit_action_taken.assert_called_once_with(unit_id)
        self.mock_game_state_manager.notify_visual_update.assert_called_once_with(unit_id, "dismounted")

    # TDD_ANCHOR: test_dismount_stat_adjustment
    def test_dismount_stat_adjustment(self):
        """Test that dismounting correctly adjusts unit stats."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = True
        mock_unit.mounted_class_id = "C001"
        mock_unit.current_stats = {
            STR: 10, MAG: 5, SKL: 8, SPD: 9,
            LUK: 7, DEF: 6, CON: 8, MOV: 8
        }
        
        # Case 1: Using specific dismount modifiers
        mock_mounted_class_with_modifiers = MagicMock()
        mock_mounted_class_with_modifiers.dismount_class_id = "C002"
        mock_mounted_class_with_modifiers.dismount_stat_modifiers = {
            STR: -1, SPD: -2, DEF: -1, MOV: -3
        }
        
        mock_dismounted_class = MagicMock()
        mock_dismounted_class.mov = 5
        mock_dismounted_class.movement_type = INFANTRY
        mock_dismounted_class.usable_weapon_types_dismounted = [SWORD]
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class_with_modifiers,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_dismount to return True
        self.dismounting_system.can_dismount = MagicMock(return_value=True)
        
        # Act
        result = self.dismounting_system.execute_dismount(unit_id)
        
        # Assert
        self.assertTrue(result.success)
        self.assertEqual(mock_unit.current_stats[STR], 9, "STR should be reduced by 1")
        self.assertEqual(mock_unit.current_stats[MAG], 5, "MAG should remain unchanged")
        self.assertEqual(mock_unit.current_stats[SKL], 8, "SKL should remain unchanged")
        self.assertEqual(mock_unit.current_stats[SPD], 7, "SPD should be reduced by 2")
        self.assertEqual(mock_unit.current_stats[LUK], 7, "LUK should remain unchanged")
        self.assertEqual(mock_unit.current_stats[DEF], 5, "DEF should be reduced by 1")
        self.assertEqual(mock_unit.current_stats[CON], 8, "CON should remain unchanged")
        self.assertEqual(mock_unit.current_stats[MOV], 5, "MOV should be set to dismounted class value")

    # TDD_ANCHOR: test_dismount_movement_type_change
    def test_dismount_movement_type_change(self):
        """Test that dismounting correctly changes the unit's movement type."""
        # Arrange
        cavalry_unit_id = "C001"
        flying_unit_id = "F001"
        
        # Mock units
        mock_cavalry_unit = MagicMock()
        mock_cavalry_unit.is_mounted = True
        mock_cavalry_unit.mounted_class_id = "MC001"
        mock_cavalry_unit.current_movement_type = CAVALRY
        
        mock_flying_unit = MagicMock()
        mock_flying_unit.is_mounted = True
        mock_flying_unit.mounted_class_id = "MF001"
        mock_flying_unit.current_movement_type = FLYING
        
        # Mock classes
        mock_mounted_cavalry_class = MagicMock()
        mock_mounted_cavalry_class.dismount_class_id = "DC001"
        mock_mounted_cavalry_class.dismount_stat_modifiers = None
        
        mock_dismounted_cavalry_class = MagicMock()
        mock_dismounted_cavalry_class.mov = 5
        mock_dismounted_cavalry_class.movement_type = INFANTRY
        mock_dismounted_cavalry_class.usable_weapon_types_dismounted = [SWORD]
        
        mock_mounted_flying_class = MagicMock()
        mock_mounted_flying_class.dismount_class_id = "DF001"
        mock_mounted_flying_class.dismount_stat_modifiers = None
        
        mock_dismounted_flying_class = MagicMock()
        mock_dismounted_flying_class.mov = 5
        mock_dismounted_flying_class.movement_type = INFANTRY
        mock_dismounted_flying_class.usable_weapon_types_dismounted = [LANCE]
        
        # Configure mocks for cavalry unit
        self.mock_unit_system.get_unit.side_effect = lambda id: {
            cavalry_unit_id: mock_cavalry_unit,
            flying_unit_id: mock_flying_unit
        }.get(id)
        
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "MC001": mock_mounted_cavalry_class,
            "DC001": mock_dismounted_cavalry_class,
            "MF001": mock_mounted_flying_class,
            "DF001": mock_dismounted_flying_class
        }.get(class_id)
        
        # Mock can_dismount to return True
        self.dismounting_system.can_dismount = MagicMock(return_value=True)
        
        # Act
        cavalry_result = self.dismounting_system.execute_dismount(cavalry_unit_id)
        flying_result = self.dismounting_system.execute_dismount(flying_unit_id)
        
        # Assert
        self.assertTrue(cavalry_result.success)
        self.assertEqual(mock_cavalry_unit.current_movement_type, INFANTRY,
                         "Cavalry unit should change to Infantry movement type")
        
        self.assertTrue(flying_result.success)
        self.assertEqual(mock_flying_unit.current_movement_type, INFANTRY,
                         "Flying unit should change to Infantry movement type")
                         
    # TDD_ANCHOR: test_dismount_weapon_restriction
    def test_dismount_weapon_restriction(self):
        """Test that dismounting correctly applies weapon restrictions."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = True
        mock_unit.mounted_class_id = "C001"
        mock_unit.id = unit_id
        
        # Mock classes
        mock_mounted_class = MagicMock()
        mock_mounted_class.dismount_class_id = "C002"
        mock_mounted_class.dismount_stat_modifiers = None
        mock_mounted_class.usable_weapon_types_mounted = [SWORD, LANCE]
        
        mock_dismounted_class = MagicMock()
        mock_dismounted_class.mov = 5
        mock_dismounted_class.movement_type = INFANTRY
        mock_dismounted_class.usable_weapon_types_dismounted = [SWORD]
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_dismount to return True
        self.dismounting_system.can_dismount = MagicMock(return_value=True)
        
        # Mock handle_weapon_restriction method
        self.dismounting_system.handle_weapon_restriction = MagicMock()
        
        # Act
        result = self.dismounting_system.execute_dismount(unit_id)
        
        # Assert
        self.assertTrue(result.success)
        # Verify handle_weapon_restriction was called with the correct parameters
        self.dismounting_system.handle_weapon_restriction.assert_called_once_with(
            mock_unit, mock_dismounted_class.usable_weapon_types_dismounted
        )

    # TDD_ANCHOR: test_execute_mount_state_changes
    def test_execute_mount_state_changes(self):
        """Test that execute_mount correctly applies all state changes."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = False
        mock_unit.mounted_class_id = "C001"
        mock_unit.current_stats = {MOV: 5}
        mock_unit.current_movement_type = INFANTRY
        mock_unit.id = unit_id
        
        # Mock classes
        mock_mounted_class = MagicMock()
        mock_mounted_class.dismount_class_id = "C002"
        mock_mounted_class.mov = 8
        mock_mounted_class.movement_type = CAVALRY
        mock_mounted_class.dismount_stat_modifiers = None
        
        mock_dismounted_class = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_mount to return True
        self.dismounting_system.can_mount = MagicMock(return_value=True)
        
        # Act
        result = self.dismounting_system.execute_mount(unit_id)
        
        # Assert
        self.assertTrue(result.success, "execute_mount should return success")
        self.assertEqual(mock_unit.is_mounted, True, "Unit should be marked as mounted")
        self.assertEqual(mock_unit.current_movement_type, CAVALRY, "Movement type should change to Cavalry")
        
        # Verify method calls
        self.dismounting_system.can_mount.assert_called_once_with(unit_id)
        self.mock_unit_system.set_unit_action_taken.assert_called_once_with(unit_id)
        self.mock_game_state_manager.notify_visual_update.assert_called_once_with(unit_id, "mounted")
        
        # Test MOV stat update separately
        def test_mount_mov_stat_update(self):
            """Test that mounting correctly updates the MOV stat."""
            # Arrange
            unit_id = "U001"
            
            # Mock unit
            mock_unit = MagicMock()
            mock_unit.is_mounted = False
            mock_unit.mounted_class_id = "C001"
            mock_unit.current_stats = MagicMock()
            mock_unit.current_movement_type = INFANTRY
            
            # Mock classes
            mock_mounted_class = MagicMock()
            mock_mounted_class.dismount_class_id = "C002"
            mock_mounted_class.mov = 8
            mock_mounted_class.movement_type = CAVALRY
            
            mock_dismounted_class = MagicMock()
            
            # Configure mocks
            self.mock_unit_system.get_unit.return_value = mock_unit
            self.mock_data_provider.get_class.side_effect = lambda class_id: {
                "C001": mock_mounted_class,
                "C002": mock_dismounted_class
            }.get(class_id)
            
            # Mock can_mount to return True
            self.dismounting_system.can_mount = MagicMock(return_value=True)
            
            # Act
            self.dismounting_system.execute_mount(unit_id)
            
            # Assert
            mock_unit.current_stats.__setitem__.assert_called_with("MOV", 8)
        self.mock_unit_system.get_unit.assert_called_with(unit_id)
        self.mock_data_provider.get_class.assert_has_calls([
            call("C001"),  # Get mounted class
            call("C002")   # Get dismounted class
        ])
        self.mock_unit_system.set_unit_action_taken.assert_called_once_with(unit_id)
        self.mock_game_state_manager.notify_visual_update.assert_called_once_with(unit_id, "mounted")

    # TDD_ANCHOR: test_mount_stat_reversion
    def test_mount_stat_reversion(self):
        """Test that mounting correctly reverts unit stats."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = False
        mock_unit.mounted_class_id = "C001"
        mock_unit.current_stats = {
            STR: 9, MAG: 5, SKL: 8, SPD: 7,
            LUK: 7, DEF: 5, CON: 8, MOV: 5
        }
        
        # Case 1: Using specific dismount modifiers (which should be reversed)
        mock_mounted_class = MagicMock()
        mock_mounted_class.dismount_class_id = "C002"
        mock_mounted_class.mov = 8
        mock_mounted_class.movement_type = CAVALRY
        mock_mounted_class.dismount_stat_modifiers = {
            STR: -1, SPD: -2, DEF: -1, MOV: -3
        }
        
        mock_dismounted_class = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_mount to return True
        self.dismounting_system.can_mount = MagicMock(return_value=True)
        
        # Act
        result = self.dismounting_system.execute_mount(unit_id)
        
        # Assert
        self.assertTrue(result.success)
        self.assertEqual(mock_unit.current_stats[STR], 10, "STR should be increased by 1")
        self.assertEqual(mock_unit.current_stats[MAG], 5, "MAG should remain unchanged")
        self.assertEqual(mock_unit.current_stats[SKL], 8, "SKL should remain unchanged")
        self.assertEqual(mock_unit.current_stats[SPD], 9, "SPD should be increased by 2")
        self.assertEqual(mock_unit.current_stats[LUK], 7, "LUK should remain unchanged")
        self.assertEqual(mock_unit.current_stats[DEF], 6, "DEF should be increased by 1")
        self.assertEqual(mock_unit.current_stats[CON], 8, "CON should remain unchanged")
        self.assertEqual(mock_unit.current_stats[MOV], 8, "MOV should be set to mounted class value")

    # TDD_ANCHOR: test_mount_movement_type_reversion
    def test_mount_movement_type_reversion(self):
        """Test that mounting correctly reverts the unit's movement type."""
        # Arrange
        cavalry_unit_id = "C001"
        flying_unit_id = "F001"
        
        # Mock units
        mock_cavalry_unit = MagicMock()
        mock_cavalry_unit.is_mounted = False
        mock_cavalry_unit.mounted_class_id = "MC001"
        mock_cavalry_unit.current_movement_type = INFANTRY
        
        mock_flying_unit = MagicMock()
        mock_flying_unit.is_mounted = False
        mock_flying_unit.mounted_class_id = "MF001"
        mock_flying_unit.current_movement_type = INFANTRY
        
        # Mock classes
        mock_mounted_cavalry_class = MagicMock()
        mock_mounted_cavalry_class.dismount_class_id = "DC001"
        mock_mounted_cavalry_class.dismount_stat_modifiers = None
        mock_mounted_cavalry_class.movement_type = CAVALRY
        mock_mounted_cavalry_class.mov = 8
        
        mock_dismounted_cavalry_class = MagicMock()
        
        mock_mounted_flying_class = MagicMock()
        mock_mounted_flying_class.dismount_class_id = "DF001"
        mock_mounted_flying_class.dismount_stat_modifiers = None
        mock_mounted_flying_class.movement_type = FLYING
        mock_mounted_flying_class.mov = 7
        
        mock_dismounted_flying_class = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.side_effect = lambda id: {
            cavalry_unit_id: mock_cavalry_unit,
            flying_unit_id: mock_flying_unit
        }.get(id)
        
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "MC001": mock_mounted_cavalry_class,
            "DC001": mock_dismounted_cavalry_class,
            "MF001": mock_mounted_flying_class,
            "DF001": mock_dismounted_flying_class
        }.get(class_id)
        
        # Mock can_mount to return True
        self.dismounting_system.can_mount = MagicMock(return_value=True)
        
        # Act
        cavalry_result = self.dismounting_system.execute_mount(cavalry_unit_id)
        flying_result = self.dismounting_system.execute_mount(flying_unit_id)
        
        # Assert
        self.assertTrue(cavalry_result.success)
        self.assertEqual(mock_cavalry_unit.current_movement_type, CAVALRY,
                         "Cavalry unit should revert to Cavalry movement type")
        
        self.assertTrue(flying_result.success)
        self.assertEqual(mock_flying_unit.current_movement_type, FLYING,
                         "Flying unit should revert to Flying movement type")

    # TDD_ANCHOR: test_mount_weapon_access_restored
    def test_mount_weapon_access_restored(self):
        """Test that mounting correctly restores weapon access."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.is_mounted = False
        mock_unit.mounted_class_id = "C001"
        mock_unit.id = unit_id
        
        # Mock classes
        mock_mounted_class = MagicMock()
        mock_mounted_class.dismount_class_id = "C002"
        mock_mounted_class.mov = 8
        mock_mounted_class.movement_type = CAVALRY
        
        mock_dismounted_class = MagicMock()
        
        # Configure mocks
        self.mock_unit_system.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mounted_class,
            "C002": mock_dismounted_class
        }.get(class_id)
        
        # Mock can_mount to return True
        self.dismounting_system.can_mount = MagicMock(return_value=True)
        
        # Act
        result = self.dismounting_system.execute_mount(unit_id)
        
        # Assert
        self.assertTrue(result.success)
        # Weapon access is restored implicitly by changing the mounted state
        # No explicit method call is needed for this in the current design

    # TDD_ANCHOR: test_auto_dismount_indoor_map
    def test_auto_dismount_indoor_map(self):
        """Test automatic dismounting when loading an indoor map."""
        # Arrange
        map_id = "INDOOR_MAP"
        
        # Mock map data
        mock_map_data = MagicMock()
        mock_map_data.is_indoor = True
        
        # Mock units
        mock_mounted_unit1 = MagicMock()
        mock_mounted_unit1.is_mounted = True
        mock_mounted_unit1.mounted_class_id = "C001"
        mock_mounted_unit1.id = "U001"
        
        mock_mounted_unit2 = MagicMock()
        mock_mounted_unit2.is_mounted = True
        mock_mounted_unit2.mounted_class_id = "C002"
        mock_mounted_unit2.id = "U002"
        
        mock_dismounted_unit = MagicMock()
        mock_dismounted_unit.is_mounted = False
        mock_dismounted_unit.id = "U003"
        
        # Mock classes
        mock_mountable_class = MagicMock()
        mock_mountable_class.can_mount = True
        
        mock_non_mountable_class = MagicMock()
        mock_non_mountable_class.can_mount = False
        
        # Configure mocks
        self.mock_data_provider.get_map.return_value = mock_map_data
        self.mock_unit_system.get_all_player_units.return_value = [
            mock_mounted_unit1, mock_mounted_unit2, mock_dismounted_unit
        ]
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mountable_class,
            "C002": mock_non_mountable_class
        }.get(class_id)
        
        # Mock apply_dismount_state method
        self.dismounting_system.apply_dismount_state = MagicMock()
        
        # Act
        self.dismounting_system.handle_automatic_dismount_on_map_load(map_id)
        
        # Assert
        # Should call apply_dismount_state for mounted units with can_mount class
        self.dismounting_system.apply_dismount_state.assert_has_calls([
            call(mock_mounted_unit1.id, False)  # False indicates no action cost
        ])
        self.assertEqual(self.dismounting_system.apply_dismount_state.call_count, 1)
        
        # Verify method calls
        self.mock_data_provider.get_map.assert_called_once_with(map_id)
        self.mock_unit_system.get_all_player_units.assert_called_once()
        self.mock_data_provider.get_class.assert_has_calls([
            call(mock_mounted_unit1.mounted_class_id),
            call(mock_mounted_unit2.mounted_class_id)
        ])

    # TDD_ANCHOR: test_weapon_auto_unequip_on_dismount
    def test_weapon_auto_unequip_on_dismount(self):
        """Test that restricted weapons are automatically unequipped when dismounting."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with equipped lance (which will be restricted when dismounted)
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock equipped item (lance)
        mock_equipped_item = MagicMock()
        mock_equipped_item.id = "I001"
        
        # Mock item data
        mock_item_data = MagicMock()
        mock_item_data.type = LANCE
        
        # Configure mocks
        self.mock_unit_system.get_equipped_item.return_value = mock_equipped_item
        self.mock_data_provider.get_item.return_value = mock_item_data
        
        # Allowed weapon types when dismounted (only sword)
        allowed_weapon_types = [SWORD]
        
        # Act
        self.dismounting_system.handle_weapon_restriction(mock_unit, allowed_weapon_types)
        
        # Assert
        # Should unequip the lance since it's not in allowed_weapon_types
        self.mock_unit_system.unequip_item.assert_called_once_with(unit_id)
        self.mock_unit_system.get_equipped_item.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item.assert_called_once_with(mock_equipped_item.id)

    # TDD_ANCHOR: test_weapon_auto_equip_valid_on_dismount
    def test_weapon_auto_equip_valid_on_dismount(self):
        """Test that a valid weapon is automatically equipped when dismounting."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with equipped lance (which will be restricted when dismounted)
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock equipped item (lance)
        mock_equipped_item = MagicMock()
        mock_equipped_item.id = "I001"
        
        # Mock inventory items
        mock_sword_item = MagicMock()
        mock_sword_item.id = "I002"
        
        mock_axe_item = MagicMock()
        mock_axe_item.id = "I003"
        
        mock_unit.inventory = [mock_sword_item, mock_axe_item]
        
        # Mock item data
        mock_lance_data = MagicMock()
        mock_lance_data.type = LANCE
        
        mock_sword_data = MagicMock()
        mock_sword_data.type = SWORD
        
        mock_axe_data = MagicMock()
        mock_axe_data.type = AXE
        
        # Configure mocks
        self.mock_unit_system.get_equipped_item.return_value = mock_equipped_item
        self.mock_data_provider.get_item.side_effect = lambda item_id: {
            "I001": mock_lance_data,
            "I002": mock_sword_data,
            "I003": mock_axe_data
        }.get(item_id)
        
        # Allowed weapon types when dismounted (only sword)
        allowed_weapon_types = [SWORD]
        
        # Act
        self.dismounting_system.handle_weapon_restriction(mock_unit, allowed_weapon_types)
        
        # Assert
        # Should unequip the lance and equip the sword
        self.mock_unit_system.unequip_item.assert_called_once_with(unit_id)
        # We now expect equip_item to be called with the unit ID and the index of the sword item in the inventory
        # Since the mock_unit.inventory = [mock_sword_item, mock_axe_item], the index of mock_sword_item is 0
        self.mock_unit_system.equip_item.assert_called_once_with(unit_id, 0)
        
        # Verify get_item was called for all items
        self.mock_data_provider.get_item.assert_has_calls([
            call(mock_equipped_item.id),
            call(mock_sword_item.id),
            call(mock_axe_item.id)
        ])


if __name__ == '__main__':
    unittest.main()

    # TDD_ANCHOR: test_auto_mount_prep_screen_outdoor
    def test_auto_mount_prep_screen_outdoor(self):
        """Test automatic mounting when loading the prep screen for an outdoor map."""
        # Arrange
        map_id = "OUTDOOR_MAP"
        
        # Mock map data
        mock_map_data = MagicMock()
        mock_map_data.is_indoor = False
        
        # Mock units
        mock_dismounted_unit1 = MagicMock()
        mock_dismounted_unit1.is_mounted = False
        mock_dismounted_unit1.mounted_class_id = "C001"
        mock_dismounted_unit1.id = "U001"
        
        mock_dismounted_unit2 = MagicMock()
        mock_dismounted_unit2.is_mounted = False
        mock_dismounted_unit2.mounted_class_id = "C002"
        mock_dismounted_unit2.id = "U002"
        
        mock_mounted_unit = MagicMock()
        mock_mounted_unit.is_mounted = True
        mock_mounted_unit.id = "U003"
        
        # Mock classes
        mock_mountable_class = MagicMock()
        mock_mountable_class.can_mount = True
        
        mock_non_mountable_class = MagicMock()
        mock_non_mountable_class.can_mount = False
        
        # Configure mocks
        self.mock_data_provider.get_map.return_value = mock_map_data
        self.mock_unit_system.get_all_player_units_in_roster.return_value = [
            mock_dismounted_unit1, mock_dismounted_unit2, mock_mounted_unit
        ]
        self.mock_data_provider.get_class.side_effect = lambda class_id: {
            "C001": mock_mountable_class,
            "C002": mock_non_mountable_class
        }.get(class_id)
        
        # Mock apply_mount_state method
        self.dismounting_system.apply_mount_state = MagicMock()
        
        # Act
        self.dismounting_system.handle_automatic_mount_on_prep_load(map_id)
        
        # Assert
        # Should call apply_mount_state for dismounted units with can_mount class
        self.dismounting_system.apply_mount_state.assert_has_calls([
            call(mock_dismounted_unit1.id)
        ])
        self.assertEqual(self.dismounting_system.apply_mount_state.call_count, 1)
        
        # Verify method calls
        self.mock_data_provider.get_map.assert_called_once_with(map_id)
        self.mock_unit_system.get_all_player_units_in_roster.assert_called_once()
        self.mock_data_provider.get_class.assert_has_calls([
            call(mock_dismounted_unit1.mounted_class_id),
            call(mock_dismounted_unit2.mounted_class_id)
        ])
