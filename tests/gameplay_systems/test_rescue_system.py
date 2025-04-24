"""
Test the Rescue System module.

This module tests the rescue mechanics in the game, specifically focusing on
the Build/Constitution checks for rescue, take, and movement penalties.
"""

import unittest
from unittest.mock import MagicMock, patch, call

from src.gameplay_systems.rescue_system import RescueSystem
from src.core_engine.game_state import StatusEnum, DispositionEnum

# Constants for testing
NORMAL = StatusEnum.NORMAL
RESCUING = StatusEnum.RESCUING
RESCUED = StatusEnum.RESCUED
CAPTURED = StatusEnum.CAPTURED

PLAYER = "PLAYER"
ENEMY = "ENEMY"
NPC = "NPC"

class TestRescueSystem(unittest.TestCase):
    """Test cases for the RescueSystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_map_system = MagicMock(name="MapSystem")
        self.mock_action_system = MagicMock(name="ActionSystem")
        
        # Create the RescueSystem instance
        self.rescue_system = RescueSystem()
        self.rescue_system.initialize(
            self.mock_game_state_manager,
            self.mock_data_provider,
            self.mock_map_system,
            self.mock_action_system
        )

    # Test Rescue Conditions
    def test_can_rescue_valid_ally(self):
        """Test that a unit can rescue a valid ally."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_valid_npc(self):
        """Test that a unit can rescue a valid NPC."""
        # Arrange
        rescuer_id = "R001"
        target_id = "N001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target (NPC)
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = NPC
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_invalid_con_too_low(self):
        """Test that a unit cannot rescue a target with CON too high for the rescuer's Build/Con."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer with lower CON (5)
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 5, "bld": 5}
        mock_rescuer.position = (5, 5)
        mock_rescuer.is_mounted = False
        
        # Mock target with higher CON (12) 
        # With target.con = 12, target.con/2 = 6, which is > rescuer.con (5)
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 12, "bld": 12}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_invalid_enemy_target(self):
        """Test that a unit cannot rescue an enemy."""
        # Arrange
        rescuer_id = "R001"
        target_id = "E001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target (enemy)
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = ENEMY
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_invalid_target_already_carried(self):
        """Test that a unit cannot rescue a target that is already being carried."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target (already being rescued)
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = RESCUED
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_invalid_rescuer_already_carrying(self):
        """Test that a unit cannot rescue if they are already carrying someone."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer (already carrying)
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_invalid_self_target(self):
        """Test that a unit cannot rescue itself."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        mock_unit.status = NORMAL
        mock_unit.faction = PLAYER
        mock_unit.stats = {"con": 10}
        mock_unit.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.rescue_system.can_rescue(unit_id, unit_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(unit_id),
            call(unit_id)
        ], any_order=True)
        # Adjacency check should not be called
        self.mock_map_system.is_adjacent.assert_not_called()

    def test_can_rescue_invalid_target_is_carrier(self):
        """Test that a unit cannot rescue a unit that is carrying someone."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        
        # Mock target (carrying someone)
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = RESCUING
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)

    def test_can_rescue_dismounted_indoors_check(self):
        """Test that a dismounted unit can rescue indoors."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer (dismounted)
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.is_mounted = True
        mock_rescuer.is_dismounted = True
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Mock indoor check
        self.mock_map_system.is_indoor.return_value = True
        
        # Act
        result = self.rescue_system.can_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(target_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, mock_target.position)
        self.mock_map_system.is_indoor.assert_called_once_with(mock_rescuer.position)

    # Test Rescue Effects
    def test_initiate_rescue_success(self):
        """Test that initiate_rescue successfully rescues a unit."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Act
        result = self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertTrue(result)
        self.rescue_system.can_rescue.assert_called_once_with(rescuer_id, target_id)
        
        # Check that states were updated correctly
        self.assertEqual(mock_rescuer.status, RESCUING)
        self.assertEqual(mock_rescuer.carried_unit_id, target_id)
        self.assertEqual(mock_target.status, RESCUED)
        self.assertEqual(mock_target.carrier_unit_id, rescuer_id)

    def test_initiate_rescue_applies_rescuer_penalties_correctly(self):
        """Test that initiate_rescue applies penalties to the rescuer correctly."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Mock apply_carry_penalties
        self.rescue_system.apply_carry_penalties = MagicMock()
        
        # Act
        self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.rescue_system.apply_carry_penalties.assert_called_once_with(mock_rescuer, mock_target)

    def test_initiate_rescue_removes_target_from_map_display(self):
        """Test that initiate_rescue removes the target from the map display."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        # Check that the map system was called to update unit visibility
        self.mock_map_system.update_unit_visibility.assert_called_once_with(mock_target, False)

    def test_initiate_rescue_consumes_rescuer_action(self):
        """Test that initiate_rescue consumes the rescuer's action."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        mock_rescuer.action_taken = False
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertTrue(mock_rescuer.action_taken)

    def test_initiate_rescue_failure_if_cannot_rescue(self):
        """Test that initiate_rescue fails if can_rescue returns False."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        mock_rescuer.action_taken = False
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return False
        self.rescue_system.can_rescue = MagicMock(return_value=False)
        
        # Mock apply_carry_penalties
        self.rescue_system.apply_carry_penalties = MagicMock()
        
        # Act
        result = self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertFalse(result)
        self.rescue_system.can_rescue.assert_called_once_with(rescuer_id, target_id)
        
        # Check that states were not updated
        self.assertEqual(mock_rescuer.status, NORMAL)
        self.assertIsNone(mock_rescuer.carried_unit_id)
        self.assertEqual(mock_target.status, NORMAL)
        self.assertIsNone(mock_target.carrier_unit_id)
        
        # Check that apply_carry_penalties was not called
        self.rescue_system.apply_carry_penalties.assert_not_called()
        
        # Check that action was not consumed
        self.assertFalse(mock_rescuer.action_taken)

    # Test Drop Conditions
    def test_can_drop_valid(self):
        """Test that a unit can drop a carried unit at a valid position."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.movement_type = "INFANTRY"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Mock tile checks
        self.mock_map_system.get_unit_at.return_value = None  # No unit at drop position
        self.mock_map_system.is_passable.return_value = True  # Terrain is passable
        
        # Act
        result = self.rescue_system.can_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(carried_unit_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, drop_position)
        self.mock_map_system.get_unit_at.assert_called_once_with(drop_position)
        self.mock_map_system.is_passable.assert_called_once_with(drop_position, mock_carried.movement_type)

    def test_can_drop_invalid_not_rescuing(self):
        """Test that a unit cannot drop if they are not carrying anyone."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        
        # Mock rescuer (not carrying)
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.carried_unit_id = None
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_rescuer
        
        # Act
        result = self.rescue_system.can_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(rescuer_id)
        self.mock_map_system.is_adjacent.assert_not_called()
        self.mock_map_system.get_unit_at.assert_not_called()
        self.mock_map_system.is_passable.assert_not_called()

    def test_can_drop_invalid_position_occupied_by_unit(self):
        """Test that a unit cannot drop at a position occupied by another unit."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        occupying_unit_id = "O001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_rescuer
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Mock tile checks
        self.mock_map_system.get_unit_at.return_value = occupying_unit_id  # Position is occupied
        
        # Act
        result = self.rescue_system.can_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(rescuer_id)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, drop_position)
        self.mock_map_system.get_unit_at.assert_called_once_with(drop_position)
        self.mock_map_system.is_passable.assert_not_called()

    def test_can_drop_invalid_position_impassable_terrain_for_dropped_unit(self):
        """Test that a unit cannot drop at a position with impassable terrain for the carried unit."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.movement_type = "INFANTRY"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Mock tile checks
        self.mock_map_system.get_unit_at.return_value = None  # No unit at drop position
        self.mock_map_system.is_passable.return_value = False  # Terrain is impassable
        
        # Act
        result = self.rescue_system.can_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(rescuer_id),
            call(carried_unit_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, drop_position)
        self.mock_map_system.get_unit_at.assert_called_once_with(drop_position)
        self.mock_map_system.is_passable.assert_called_once_with(drop_position, mock_carried.movement_type)

    # Test Drop Effects
    def test_initiate_drop_success(self):
        """Test that initiate_drop successfully drops a carried unit."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        mock_rescuer.action_taken = False
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        mock_carried.position = None
        mock_carried.action_taken = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Mock remove_carry_penalties
        self.rescue_system.remove_carry_penalties = MagicMock()
        
        # Act
        result = self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertTrue(result)
        self.rescue_system.can_drop.assert_called_once_with(rescuer_id, drop_position)
        
        # Check that states were updated correctly
        self.assertEqual(mock_rescuer.status, NORMAL)
        self.assertIsNone(mock_rescuer.carried_unit_id)
        self.assertEqual(mock_carried.status, NORMAL)
        self.assertIsNone(mock_carried.carrier_unit_id)
        self.assertEqual(mock_carried.position, drop_position)
        
        # Check that remove_carry_penalties was called
        self.rescue_system.remove_carry_penalties.assert_called_once_with(mock_rescuer)
        
        # Check that actions were consumed
        self.assertTrue(mock_rescuer.action_taken)
        self.assertTrue(mock_carried.action_taken)

    def test_initiate_drop_updates_rescuer_status_to_normal(self):
        """Test that initiate_drop updates the rescuer's status to normal."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertEqual(mock_rescuer.status, NORMAL)
        self.assertIsNone(mock_rescuer.carried_unit_id)

    def test_initiate_drop_updates_dropped_unit_status_to_normal(self):
        """Test that initiate_drop updates the dropped unit's status to normal."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertEqual(mock_carried.status, NORMAL)
        self.assertIsNone(mock_carried.carrier_unit_id)

    def test_initiate_drop_removes_rescuer_penalties(self):
        """Test that initiate_drop removes penalties from the rescuer."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Mock remove_carry_penalties
        self.rescue_system.remove_carry_penalties = MagicMock()
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.rescue_system.remove_carry_penalties.assert_called_once_with(mock_rescuer)

    def test_initiate_drop_places_dropped_unit_at_correct_position(self):
        """Test that initiate_drop places the dropped unit at the correct position."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        mock_carried.position = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertEqual(mock_carried.position, drop_position)
        self.mock_map_system.update_unit_visibility.assert_called_once_with(mock_carried, True)
        self.mock_map_system.update_unit_position.assert_called_once_with(mock_carried, drop_position)

    def test_initiate_drop_sets_dropped_unit_action_taken(self):
        """Test that initiate_drop sets the dropped unit's action_taken flag."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        mock_carried.action_taken = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertTrue(mock_carried.action_taken)

    def test_initiate_drop_consumes_rescuer_action(self):
        """Test that initiate_drop consumes the rescuer's action."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        mock_rescuer.action_taken = False
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return True
        self.rescue_system.can_drop = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertTrue(mock_rescuer.action_taken)

    def test_initiate_drop_failure_if_cannot_drop(self):
        """Test that initiate_drop fails if can_drop returns False."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (6, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        mock_rescuer.action_taken = False
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_drop to return False
        self.rescue_system.can_drop = MagicMock(return_value=False)
        
        # Mock remove_carry_penalties
        self.rescue_system.remove_carry_penalties = MagicMock()
        
        # Act
        result = self.rescue_system.initiate_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertFalse(result)
        self.rescue_system.can_drop.assert_called_once_with(rescuer_id, drop_position)
        
        # Check that states were not updated
        self.assertEqual(mock_rescuer.status, RESCUING)
        self.assertEqual(mock_rescuer.carried_unit_id, carried_unit_id)
        self.assertEqual(mock_carried.status, RESCUED)
        self.assertEqual(mock_carried.carrier_unit_id, rescuer_id)
        
        # Check that remove_carry_penalties was not called
        self.rescue_system.remove_carry_penalties.assert_not_called()
        
        # Check that actions were not consumed
        self.assertFalse(mock_rescuer.action_taken)

    def test_can_drop_invalid_position_not_adjacent(self):
        """Test that a unit cannot drop at a non-adjacent position."""
        # Arrange
        rescuer_id = "R001"
        drop_position = (7, 7)  # Not adjacent to (5, 5)
        carried_unit_id = "C001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_rescuer
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = False
        
        # Act
        result = self.rescue_system.can_drop(rescuer_id, drop_position)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(rescuer_id)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_rescuer.position, drop_position)
        self.mock_map_system.get_unit_at.assert_not_called()
        self.mock_map_system.is_passable.assert_not_called()
        
        # This test doesn't need to check apply_carry_penalties or action_taken
        # as it's only testing the can_drop method which doesn't modify these

    def test_initiate_rescue_updates_rescuer_status_and_carried_id(self):
        """Test that initiate_rescue updates the rescuer's status and carried_unit_id."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertEqual(mock_rescuer.status, RESCUING)
        self.assertEqual(mock_rescuer.carried_unit_id, target_id)

    def test_initiate_rescue_updates_target_status_and_carrier_id(self):
        """Test that initiate_rescue updates the target's status and carrier_unit_id."""
        # Arrange
        rescuer_id = "R001"
        target_id = "T001"
        
        # Mock rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.faction = PLAYER
        mock_rescuer.stats = {"con": 10}
        mock_rescuer.position = (5, 5)
        mock_rescuer.carried_unit_id = None
        
        # Mock target
        mock_target = MagicMock()
        mock_target.id = target_id
        mock_target.status = NORMAL
        mock_target.faction = PLAYER
        mock_target.stats = {"con": 5}
        mock_target.position = (5, 6)
        mock_target.carrier_unit_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            rescuer_id: mock_rescuer,
            target_id: mock_target
        }.get(id)
        
        # Mock can_rescue to return True
        self.rescue_system.can_rescue = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_rescue(rescuer_id, target_id)
        
        # Assert
        self.assertEqual(mock_target.status, RESCUED)
        self.assertEqual(mock_target.carrier_unit_id, rescuer_id)

    # Test Take Conditions
    def test_can_take_valid(self):
        """Test that a unit can take a carried unit from another unit."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = NORMAL
        mock_taker.stats = {"con": 10}
        mock_taker.position = (5, 6)
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.stats = {"con": 5}
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertTrue(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(taker_id),
            call(current_rescuer_id),
            call(carried_unit_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_taker.position, mock_rescuer.position)

    def test_can_take_invalid_not_adjacent(self):
        """Test that a unit cannot take if not adjacent to the current rescuer."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.position = (7, 7)  # Not adjacent to (5, 5)
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = False
        
        # Act
        result = self.rescue_system.can_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(taker_id),
            call(current_rescuer_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_taker.position, mock_rescuer.position)

    def test_can_take_invalid_rescuer_not_carrying(self):
        """Test that a unit cannot take if the current rescuer is not carrying anyone."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.position = (5, 6)
        
        # Mock current rescuer (not carrying)
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = NORMAL
        mock_rescuer.carried_unit_id = None
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(taker_id),
            call(current_rescuer_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_taker.position, mock_rescuer.position)

    def test_can_take_invalid_taker_already_carrying(self):
        """Test that a unit cannot take if they are already carrying someone."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        taker_carried_id = "C002"
        
        # Mock taker (already carrying)
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = RESCUING
        mock_taker.carried_unit_id = taker_carried_id
        mock_taker.position = (5, 6)
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer
        }.get(id)
        
        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True
        
        # Act
        result = self.rescue_system.can_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(taker_id),
            call(current_rescuer_id)
        ], any_order=True)
        self.mock_map_system.is_adjacent.assert_called_once_with(mock_taker.position, mock_rescuer.position)

    def test_can_take_invalid_taker_con_too_low(self):
        """Test that a unit cannot take if their CON is too low for the carried unit's Build/Con."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        
        # Mock taker with low CON (5)
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = NORMAL
        mock_taker.stats = {"con": 5, "bld": 5}
        mock_taker.position = (5, 6)
        mock_taker.is_mounted = False
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        mock_rescuer.position = (5, 5)

        # Mock carried unit with high CON (12)
        # With carried.con = 12, carried.con/2 = 6, which is > taker.con (5)
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.stats = {"con": 12, "bld": 12}

        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)

        # Mock adjacency check
        self.mock_map_system.is_adjacent.return_value = True

        # Act
        result = self.rescue_system.can_take(taker_id, current_rescuer_id)

        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(taker_id),
            call(current_rescuer_id),
            call(carried_unit_id)
        ], any_order=True)

    def test_can_take_invalid_self_target(self):
        """Test that a unit cannot take from itself."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.rescue_system.can_take(unit_id, unit_id)
        
        # Assert
        self.assertFalse(result)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(unit_id),
            call(unit_id)
        ], any_order=True)
        # Adjacency check should not be called
        self.mock_map_system.is_adjacent.assert_not_called()

    # Test Take Effects
    def test_initiate_take_success(self):
        """Test that initiate_take successfully transfers a carried unit."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = NORMAL
        mock_taker.carried_unit_id = None
        mock_taker.action_taken = False
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.carrier_unit_id = current_rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_take to return True
        self.rescue_system.can_take = MagicMock(return_value=True)
        
        # Mock remove_carry_penalties and apply_carry_penalties
        self.rescue_system.remove_carry_penalties = MagicMock()
        self.rescue_system.apply_carry_penalties = MagicMock()
        
        # Act
        result = self.rescue_system.initiate_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertTrue(result)
        self.rescue_system.can_take.assert_called_once_with(taker_id, current_rescuer_id)
        
        # Check that states were updated correctly
        self.assertEqual(mock_rescuer.status, NORMAL)
        self.assertIsNone(mock_rescuer.carried_unit_id)
        self.assertEqual(mock_taker.status, RESCUING)
        self.assertEqual(mock_taker.carried_unit_id, carried_unit_id)
        self.assertEqual(mock_carried.carrier_unit_id, taker_id)
        
        # Check that penalties were removed from original rescuer and applied to taker
        self.rescue_system.remove_carry_penalties.assert_called_once_with(mock_rescuer)
        self.rescue_system.apply_carry_penalties.assert_called_once_with(mock_taker, mock_carried)
        
        # Check that action was consumed
        self.assertTrue(mock_taker.action_taken)

    # Test Carry Penalties
    def test_apply_carry_penalties_stats_halved_correctly(self):
        """Test that apply_carry_penalties halves the carrier's stats correctly."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carrier.is_mounted = False
        carrier.temp_stats = None
        carrier.is_dismounted = False
        
        carried = MagicMock()
        carried.stats = {"bld": 6, "con": 6}
        
        # Act
        self.rescue_system.apply_carry_penalties(carrier, carried)
        
        # Assert
        # Check that original stats were stored
        self.assertEqual(carrier.temp_stats["original_str"], 20)
        self.assertEqual(carrier.temp_stats["original_mag"], 16)
        self.assertEqual(carrier.temp_stats["original_skl"], 18)
        self.assertEqual(carrier.temp_stats["original_spd"], 20)
        self.assertEqual(carrier.temp_stats["original_def"], 12)
        self.assertEqual(carrier.temp_stats["original_mov"], 8)

        # Check that stats were halved (floor division)
        self.assertEqual(carrier.stats["str"], 10)
        self.assertEqual(carrier.stats["mag"], 8)
        self.assertEqual(carrier.stats["skl"], 9)
        self.assertEqual(carrier.stats["spd"], 10)
        self.assertEqual(carrier.stats["def"], 6)
        
        # Check that MOV was not halved (carried.bld = 6 <= carrier.bld/2 = 5)
        # With the new implementation, carried.bld (6) > carrier.bld/2 (5), so MOV should be halved
        self.assertEqual(carrier.stats["mov"], 4)  # 8 // 2 = 4
        
        # Test with a lighter carried unit that doesn't trigger movement penalty
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carried.stats = {"bld": 4, "con": 4}  # 4 < 10/2 = 5, so no movement penalty
        
        self.rescue_system.apply_carry_penalties(carrier, carried)
        self.assertEqual(carrier.stats["mov"], 8)  # Movement not halved
        
    def test_apply_carry_penalties_mounted(self):
        """Test applying carry penalties to a mounted unit."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carrier.is_mounted = True
        carrier.is_dismounted = False
        carrier.temp_stats = None
        
        carried = MagicMock()
        carried.stats = {"bld": 16, "con": 16}
        
        # Act
        self.rescue_system.apply_carry_penalties(carrier, carried)
        
        # Assert
        # Check that combat stats are halved
        self.assertEqual(carrier.stats["str"], 10)
        self.assertEqual(carrier.stats["mag"], 8)
        self.assertEqual(carrier.stats["skl"], 9)
        self.assertEqual(carrier.stats["spd"], 10)
        self.assertEqual(carrier.stats["def"], 6)
        
        # Verify movement is halved because carried.bld (16) > (carrier.bld+5)/2 (7.5)
        self.assertEqual(carrier.stats["mov"], 4)  # 8 // 2 = 4
        
        # Now test with a carried unit exactly at the threshold (should not trigger penalty)
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carried.stats = {"bld": 7.5, "con": 7.5}  # 7.5 == (10+5)/2 = 7.5, movement should not be halved
        
        self.rescue_system.apply_carry_penalties(carrier, carried)
        # Since the check is carried_build > half_carrier_build, when they're equal, no movement penalty
        self.assertEqual(carrier.stats["mov"], 8)  # Movement not halved
    
    def test_apply_carry_penalties_mounted_mov_check_uses_bonus(self):
        """Test that apply_carry_penalties adds +5 to effective Build/Con for mounted units when checking MOV penalty."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carrier.is_mounted = True
        carrier.is_dismounted = False
        carrier.temp_stats = None
        
        carried = MagicMock()
        # Carried unit exactly at threshold (should not trigger penalty)
        carried.stats = {"bld": 7.5, "con": 7.5}  # 7.5 == (10+5)/2 = 7.5, no movement penalty
        
        # Act
        self.rescue_system.apply_carry_penalties(carrier, carried)
        
        # Assert
        # Check that combat stats are halved
        self.assertEqual(carrier.stats["str"], 10)
        self.assertEqual(carrier.stats["mag"], 8)
        self.assertEqual(carrier.stats["skl"], 9)
        self.assertEqual(carrier.stats["spd"], 10)
        self.assertEqual(carrier.stats["def"], 6)
        
        # Verify movement is not halved because carried.bld == half_carrier_build
        # With carrier.bld = 10 and mounted bonus +5, effective Build = 15
        # Effective build / 2 = 7.5, carried.bld = 7.5
        # Since carried_build > half_carrier_build is false (they're equal), no movement penalty
        self.assertEqual(carrier.stats["mov"], 8)  # Movement not halved
        
        # Now test with a heavier carried unit that should trigger the penalty
        carrier.stats = {"str": 20, "mag": 16, "skl": 18, "spd": 20, "def": 12, "mov": 8, "bld": 10, "con": 10}
        carried.stats = {"bld": 7.6, "con": 7.6}  # 7.6 > (10+5)/2 = 7.5, so movement is halved
        
        self.rescue_system.apply_carry_penalties(carrier, carried)
        self.assertEqual(carrier.stats["mov"], 4)  # 8 // 2 = 4, Movement halved
    
    def test_remove_carry_penalties_restores_all_stats(self):
        """Test that remove_carry_penalties restores all stats to their original values."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {
            "str": 5,  # Halved from 10
            "mag": 4,  # Halved from 8
            "skl": 6,  # Halved from 12
            "spd": 4,  # Halved from 9
            "def": 3,  # Halved from 7
            "mov": 3   # Halved from 6
        }
        carrier.temp_stats = {
            "original_str": 10,
            "original_mag": 8,
            "original_skl": 12,
            "original_spd": 9,
            "original_def": 7,
            "original_mov": 6
        }
        
        # Act
        self.rescue_system.remove_carry_penalties(carrier)
        
        # Assert
        # Check that stats were restored
        self.assertEqual(carrier.stats["str"], 10)
        self.assertEqual(carrier.stats["mag"], 8)
        self.assertEqual(carrier.stats["skl"], 12)
        self.assertEqual(carrier.stats["spd"], 9)
        self.assertEqual(carrier.stats["def"], 7)
        self.assertEqual(carrier.stats["mov"], 6)
        
        # Check that temp_stats was cleared
        self.assertEqual(carrier.temp_stats, {})

    def test_remove_carry_penalties_clears_temp_stats(self):
        """Test that remove_carry_penalties clears the temporary stats storage."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {
            "str": 5,
            "mag": 4,
            "skl": 6,
            "spd": 4,
            "def": 3,
            "mov": 3
        }
        carrier.temp_stats = {
            "original_str": 10,
            "original_mag": 8,
            "original_skl": 12,
            "original_spd": 9,
            "original_def": 7,
            "original_mov": 6
        }
        
        # Act
        self.rescue_system.remove_carry_penalties(carrier)
        
        # Assert
        self.assertEqual(carrier.temp_stats, {})

    def test_remove_carry_penalties_handles_no_penalties_applied(self):
        """Test that remove_carry_penalties handles the case where no penalties were applied."""
        # Arrange
        carrier = MagicMock()
        carrier.stats = {
            "str": 10,
            "mag": 8,
            "skl": 12,
            "spd": 9,
            "def": 7,
            "mov": 6
        }
        carrier.temp_stats = {}  # Empty temp_stats
        
        # Act
        self.rescue_system.remove_carry_penalties(carrier)
        
        # Assert
        # No exception should be raised
        self.assertEqual(carrier.temp_stats, {})
        # Stats should remain unchanged
        self.assertEqual(carrier.stats["str"], 10)
        self.assertEqual(carrier.stats["mag"], 8)
        self.assertEqual(carrier.stats["skl"], 12)
        self.assertEqual(carrier.stats["spd"], 9)
        self.assertEqual(carrier.stats["def"], 7)
        self.assertEqual(carrier.stats["mov"], 6)

    def test_initiate_take_updates_statuses_correctly(self):
        """Test that initiate_take updates all unit statuses correctly."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = NORMAL
        mock_taker.carried_unit_id = None
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.status = RESCUED
        mock_carried.carrier_unit_id = current_rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_take to return True
        self.rescue_system.can_take = MagicMock(return_value=True)
        
        # Act
        self.rescue_system.initiate_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertEqual(mock_rescuer.status, NORMAL)
        self.assertEqual(mock_taker.status, RESCUING)
        self.assertEqual(mock_carried.status, RESCUED)  # Status remains RESCUED

    def test_initiate_take_failure_if_cannot_take(self):
        """Test that initiate_take fails if can_take returns False."""
        # Arrange
        taker_id = "T001"
        current_rescuer_id = "R001"
        carried_unit_id = "C001"
        
        # Mock taker
        mock_taker = MagicMock()
        mock_taker.id = taker_id
        mock_taker.status = NORMAL
        mock_taker.carried_unit_id = None
        mock_taker.action_taken = False
        
        # Mock current rescuer
        mock_rescuer = MagicMock()
        mock_rescuer.id = current_rescuer_id
        mock_rescuer.status = RESCUING
        mock_rescuer.carried_unit_id = carried_unit_id
        
        # Mock carried unit
        mock_carried = MagicMock()
        mock_carried.id = carried_unit_id
        mock_carried.carrier_unit_id = current_rescuer_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            taker_id: mock_taker,
            current_rescuer_id: mock_rescuer,
            carried_unit_id: mock_carried
        }.get(id)
        
        # Mock can_take to return False
        self.rescue_system.can_take = MagicMock(return_value=False)
        
        # Mock remove_carry_penalties and apply_carry_penalties
        self.rescue_system.remove_carry_penalties = MagicMock()
        self.rescue_system.apply_carry_penalties = MagicMock()
        
        # Act
        result = self.rescue_system.initiate_take(taker_id, current_rescuer_id)
        
        # Assert
        self.assertFalse(result)
        self.rescue_system.can_take.assert_called_once_with(taker_id, current_rescuer_id)
        
        # Check that states were not updated
        self.assertEqual(mock_rescuer.status, RESCUING)
        self.assertEqual(mock_rescuer.carried_unit_id, carried_unit_id)
        self.assertEqual(mock_taker.status, NORMAL)
        self.assertIsNone(mock_taker.carried_unit_id)
        self.assertEqual(mock_carried.carrier_unit_id, current_rescuer_id)
        
        # Check that penalties were not modified
        self.rescue_system.remove_carry_penalties.assert_not_called()
        self.rescue_system.apply_carry_penalties.assert_not_called()
        
        # Check that action was not consumed
        self.assertFalse(mock_taker.action_taken)

if __name__ == "__main__":
    unittest.main()
