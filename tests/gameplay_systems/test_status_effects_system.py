import unittest
from unittest.mock import MagicMock, patch, call

from src.gameplay_systems.status_effects_system import StatusEffectManager, StatusEffectInstance
from src.core_engine.game_state import DispositionEnum
from src.core_engine.data_provider import StatEnum

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

ACTIVE = DispositionEnum.ACTIVE


class TestStatusEffectsSystem(unittest.TestCase):
    """Test cases for the Status Effects System."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_unit_system = MagicMock(name="UnitSystem")
        self.mock_event_system = MagicMock(name="EventSystem")
        
        # Create the StatusEffectManager instance
        self.status_effect_manager = StatusEffectManager()
        self.status_effect_manager.initialize(
            self.mock_game_state_manager, 
            self.mock_data_provider,
            self.mock_unit_system,
            self.mock_event_system
        )

    # TDD Anchor: test_status_effect_data_structure
    def test_status_effect_data_structure(self):
        """Test that the status effect data structure has the expected properties."""
        # Arrange
        status_name = "Poison"
        status_description = "Unit takes damage at the start of their turn."
        effects = [
            {"type": "PERIODIC_DAMAGE", "parameters": {"amount": 2}}
        ]
        duration_type = "PERMANENT_UNTIL_CURED"
        cure_methods = ["Restore Staff", "Antitoxin", "Chapter End"]
        icon = "poison_icon"
        
        # Mock the status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_name
        mock_status_data.description = status_description
        mock_status_data.effects = effects
        mock_status_data.duration_type = duration_type
        mock_status_data.cure_methods = cure_methods
        mock_status_data.icon = icon
        
        # Act
        status_instance = StatusEffectInstance(mock_status_data)
        
        # Assert
        self.assertEqual(status_instance.name, status_name)
        self.assertEqual(status_instance.description, status_description)
        self.assertEqual(status_instance.effects, effects)
        self.assertEqual(status_instance.duration_type, duration_type)
        self.assertEqual(status_instance.cure_methods, cure_methods)
        self.assertEqual(status_instance.icon, icon)
        self.assertIsNone(status_instance.turns_remaining)  # Should be None for PERMANENT_UNTIL_CURED

    # TDD Anchor: test_status_effect_duration_persistence
    def test_status_effect_duration_persistence(self):
        """Test that status effects persist and don't expire turn-to-turn unless scripted."""
        # Arrange
        unit_id = "U001"
        
        # Create a permanent status effect
        mock_permanent_status = MagicMock()
        mock_permanent_status.name = "Poison"
        mock_permanent_status.duration_type = "PERMANENT_UNTIL_CURED"
        mock_permanent_status.decrement_turn.return_value = False  # Should not expire
        
        # Create a scripted status effect
        mock_scripted_status = MagicMock()
        mock_scripted_status.name = "Paralysis"
        mock_scripted_status.duration_type = "SCRIPTED_TURNS"
        mock_scripted_status.decrement_turn.return_value = False  # Not expired yet
        
        # Create another scripted status effect that will expire
        mock_expiring_status = MagicMock()
        mock_expiring_status.name = "Paralysis"
        mock_expiring_status.duration_type = "SCRIPTED_TURNS"
        mock_expiring_status.decrement_turn.return_value = True  # Will expire
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_permanent_status, mock_scripted_status, mock_expiring_status]
        }
        
        # Act
        self.status_effect_manager.process_turn_end(unit_id)
        
        # Assert
        mock_permanent_status.decrement_turn.assert_not_called()  # Permanent statuses don't decrement
        mock_scripted_status.decrement_turn.assert_called_once()  # Scripted status should decrement
        mock_expiring_status.decrement_turn.assert_called_once()  # Expiring status should decrement
        
        # Check that the expiring status was removed
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 2)
        self.assertIn(mock_permanent_status, self.status_effect_manager.active_statuses[unit_id])
        self.assertIn(mock_scripted_status, self.status_effect_manager.active_statuses[unit_id])
        self.assertNotIn(mock_expiring_status, self.status_effect_manager.active_statuses[unit_id])
        
        # Verify event was published for the expired status
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_EXPIRED", 
            {"unit_id": unit_id, "status": mock_expiring_status.name}
        )

    # TDD Anchor: test_status_effect_cleared_on_chapter_end
    def test_status_effect_cleared_on_chapter_end(self):
        """Test that all status effects are cleared at the end of a chapter."""
        # Arrange
        unit1_id = "U001"
        unit2_id = "U002"
        
        # Create some status effects
        mock_status1 = MagicMock()
        mock_status1.name = "Poison"
        
        mock_status2 = MagicMock()
        mock_status2.name = "Sleep"
        
        mock_status3 = MagicMock()
        mock_status3.name = "Berserk"
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit1_id: [mock_status1, mock_status2],
            unit2_id: [mock_status3]
        }
        
        # Act
        self.status_effect_manager.process_chapter_end()
        
        # Assert
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)
        self.mock_event_system.publish.assert_called_once_with(
            "ALL_STATUSES_CLEARED", 
            {"reason": "Chapter End"}
        )

    # TDD Anchor: test_stat_modification_during_status
    def test_stat_modification_during_status(self):
        """Test that stats are correctly modified during relevant statuses."""
        # Arrange
        unit_id = "U001"
        base_stats = {
            STR: 10, MAG: 8, SKL: 12, SPD: 14, LUK: 7, DEF: 9, CON: 8, MOV: 6, HP: 30
        }
        
        # Mock unit with sleep status
        mock_unit = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Test with Sleep status
        self.status_effect_manager.has_status = MagicMock(side_effect=lambda unit, status:
            status == "Sleep" if unit == unit_id else False)
        
        # Act
        result = self.status_effect_manager.get_modified_stats(unit_id, base_stats)
        
        # Assert - Sleep only affects Avoid, not combat stats
        # Verify all stats remain unchanged except Avoid (which isn't in our test stats)
        self.assertEqual(result[STR], 10)  # Should not be zeroed
        self.assertEqual(result[MAG], 8)   # Should not be zeroed
        self.assertEqual(result[SKL], 12)  # Should not be zeroed
        self.assertEqual(result[SPD], 14)  # Should not be zeroed
        self.assertEqual(result[DEF], 9)   # Should not be zeroed
        self.assertEqual(result[LUK], 7)   # Should not be zeroed
        self.assertEqual(result[CON], 8)   # Should not be zeroed
        self.assertEqual(result[MOV], 6)   # Should not be zeroed
        self.assertEqual(result[HP], 30)   # Should not be zeroed

    # TDD Anchor: test_poison_application
    def test_poison_application(self):
        """Test applying poison status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Poison"
        source = "Poison Sword"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [{"type": "PERIODIC_DAMAGE", "parameters": {"amount": 2}}]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Restore Staff", "Antitoxin", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )
        
    # TDD Anchor: test_poison_damage_at_turn_start
    def test_poison_damage_at_turn_start(self):
        """Test that poison deals damage at the start of a unit's turn."""
        # Arrange
        unit_id = "U001"
        poison_damage = 2
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a poison status effect
        mock_poison_status = MagicMock()
        mock_poison_status.name = "Poison"
        mock_poison_status.get_effect_parameter.return_value = poison_damage
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_poison_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.status_effect_manager.process_turn_start_effects(unit_id)
        
        # Assert
        mock_poison_status.get_effect_parameter.assert_called_once_with(
            "PERIODIC_DAMAGE", "amount", default=1
        )
        self.mock_unit_system.apply_damage.assert_called_once_with(
            mock_unit, poison_damage, source="Poison"
        )
        self.mock_event_system.publish.assert_called_once_with(
            "POISON_DAMAGE",
            {"unit": mock_unit, "damage": poison_damage}
        )

    # TDD Anchor: test_poison_curing
    def test_poison_curing(self):
        """Test curing poison status with an antitoxin."""
        # Arrange
        unit_id = "U001"
        status_name = "Poison"
        cure_method = "Antitoxin"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a poison status effect
        mock_poison_status = MagicMock()
        mock_poison_status.name = status_name
        mock_poison_status.cure_methods = ["Restore Staff", "Antitoxin", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_poison_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)  # Should be empty after curing
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_CURED",
            {"unit": mock_unit, "status": status_name, "method": cure_method}
        )
    # TDD Anchor: test_sleep_application
    def test_sleep_application(self):
        """Test applying sleep status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Sleep"
        source = "Sleep Staff"
        
        # Mock unit (not mounted)
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        mock_unit.is_mounted.return_value = False
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"all": True}},
            {"type": "STAT_MODIFICATION", "parameters": {"zero_stats": True}},
            {"type": "AI_OVERRIDE", "parameters": {"type": "NO_ACTION_AI"}}
        ]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )
        
        # Verify unit was not dismounted (since it wasn't mounted)
        self.mock_unit_system.dismount_unit.assert_not_called()

    # TDD Anchor: test_sleep_dismount_effect
    def test_sleep_dismount_effect(self):
        """Test that mounted units are automatically dismounted when put to sleep."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Sleep"
        source = "Sleep Staff"
        
        # Mock unit (mounted)
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        mock_unit.is_mounted.return_value = True
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"all": True}},
            {"type": "STAT_MODIFICATION", "parameters": {"zero_stats": True}},
            {"type": "AI_OVERRIDE", "parameters": {"type": "NO_ACTION_AI"}}
        ]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        
        # Verify unit was dismounted
        self.mock_unit_system.dismount_unit.assert_called_once_with(mock_unit)

    # TDD Anchor: test_sleep_action_restriction
    def test_sleep_action_restriction(self):
        """Test that sleep prevents a unit from performing any actions."""
        # Arrange
        unit_id = "U001"
        action_types = ["Move", "Attack", "Item", "Trade", "Wait"]
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Test with Sleep status
        self.status_effect_manager.has_status = MagicMock(side_effect=lambda unit, status:
            status == "Sleep" if unit == unit_id else False)
        
        # Act & Assert
        for action_type in action_types:
            result = self.status_effect_manager.can_perform_action(unit_id, action_type)
            self.assertFalse(result, f"Unit with Sleep status should not be able to perform {action_type}")

    # TDD Anchor: test_sleep_curing
    def test_sleep_curing(self):
        """Test curing sleep status with a restore staff."""
        # Arrange
        unit_id = "U001"
        status_name = "Sleep"
        cure_method = "Restore Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a sleep status effect
        mock_sleep_status = MagicMock()
        mock_sleep_status.name = status_name
        mock_sleep_status.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_sleep_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)  # Should be empty after curing
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_CURED",
            {"unit": mock_unit, "status": status_name, "method": cure_method}
        )
        
    # TDD Anchor: test_silence_application
    def test_silence_application(self):
        """Test applying silence status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Silence"
        source = "Silence Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"action": "Magic", "allowed": False}},
            {"type": "ACTION_RESTRICTION", "parameters": {"action": "Staff", "allowed": False}}
        ]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )

    # TDD Anchor: test_silence_action_restriction
    def test_silence_action_restriction(self):
        """Test that silence prevents a unit from using magic or staves."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Create a silence status effect
        mock_silence_status = MagicMock()
        mock_silence_status.name = "Silence"
        mock_silence_status.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"action": "Magic", "allowed": False}},
            {"type": "ACTION_RESTRICTION", "parameters": {"action": "Staff", "allowed": False}}
        ]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_silence_status]
        }
        
        # Act & Assert
        # Should not be able to use magic or staves
        self.assertFalse(self.status_effect_manager.can_perform_action(unit_id, "Magic"))
        self.assertFalse(self.status_effect_manager.can_perform_action(unit_id, "Staff"))
        
        # Should be able to perform other actions
        self.assertTrue(self.status_effect_manager.can_perform_action(unit_id, "Move"))
        self.assertTrue(self.status_effect_manager.can_perform_action(unit_id, "Attack"))
        self.assertTrue(self.status_effect_manager.can_perform_action(unit_id, "Item"))
        self.assertTrue(self.status_effect_manager.can_perform_action(unit_id, "Trade"))
        self.assertTrue(self.status_effect_manager.can_perform_action(unit_id, "Wait"))

    # TDD Anchor: test_silence_curing
    def test_silence_curing(self):
        """Test curing silence status with a restore staff."""
        # Arrange
        unit_id = "U001"
        status_name = "Silence"
        cure_method = "Restore Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a silence status effect
        mock_silence_status = MagicMock()
        mock_silence_status.name = status_name
        mock_silence_status.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_silence_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)  # Should be empty after curing
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_CURED",
            {"unit": mock_unit, "status": status_name, "method": cure_method}
        )
        
    # TDD Anchor: test_berserk_application
    def test_berserk_application(self):
        """Test applying berserk status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Berserk"
        source = "Berserk Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "AI_OVERRIDE", "parameters": {"type": "BERSERK_AI"}}
        ]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )
        
    # TDD Anchor: test_petrify_application
    def test_petrify_application(self):
        """Test applying petrify status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Petrify"
        source = "Stone Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"all": True}},
            {"type": "STAT_MODIFICATION", "parameters": {"zero_stats": True}},
            {"type": "AI_OVERRIDE", "parameters": {"type": "NO_ACTION_AI"}}
        ]
        mock_status_data.duration_type = "PERMANENT_UNTIL_CURED"
        mock_status_data.cure_methods = ["Kia Staff", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )

    # TDD Anchor: test_petrify_action_restriction
    def test_petrify_action_restriction(self):
        """Test that petrify prevents a unit from performing any actions."""
        # Arrange
        unit_id = "U001"
        action_types = ["Move", "Attack", "Item", "Trade", "Wait"]
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Test with Petrify status
        self.status_effect_manager.has_status = MagicMock(side_effect=lambda unit, status:
            status == "Petrify" if unit == unit_id else False)
        
        # Act & Assert
        for action_type in action_types:
            result = self.status_effect_manager.can_perform_action(unit_id, action_type)
            self.assertFalse(result, f"Unit with Petrify status should not be able to perform {action_type}")

    # TDD Anchor: test_petrify_stat_modification
    def test_petrify_stat_modification(self):
        """Test that petrify zeroes certain stats for combat calculations."""
        # Arrange
        unit_id = "U001"
        base_stats = {
            STR: 10, MAG: 8, SKL: 12, SPD: 14, LUK: 7, DEF: 9, CON: 8, MOV: 6, HP: 30
        }
        
        # Mock unit with petrify status
        mock_unit = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Test with Petrify status
        self.status_effect_manager.has_status = MagicMock(side_effect=lambda unit, status:
            status == "Petrify" if unit == unit_id else False)
        
        # Act
        result = self.status_effect_manager.get_modified_stats(unit_id, base_stats)
        
        # Assert
        self.assertEqual(result[STR], 0)  # Should be zeroed
        self.assertEqual(result[MAG], 0)  # Should be zeroed
        self.assertEqual(result[SKL], 0)  # Should be zeroed
        self.assertEqual(result[SPD], 0)  # Should be zeroed
        self.assertEqual(result[DEF], 0)  # Should be zeroed
        self.assertEqual(result[LUK], 7)  # Should not be zeroed
        self.assertEqual(result[CON], 8)  # Should not be zeroed
        self.assertEqual(result[MOV], 6)  # Should not be zeroed
        self.assertEqual(result[HP], 30)  # Should not be zeroed

    # TDD Anchor: test_petrify_curing_kia_staff
    def test_petrify_curing_kia_staff(self):
        """Test curing petrify status with a Kia staff."""
        # Arrange
        unit_id = "U001"
        status_name = "Petrify"
        cure_method = "Kia Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a petrify status effect
        mock_petrify_status = MagicMock()
        mock_petrify_status.name = status_name
        mock_petrify_status.cure_methods = ["Kia Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_petrify_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)  # Should be empty after curing
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_CURED",
            {"unit": mock_unit, "status": status_name, "method": cure_method}
        )

    # TDD Anchor: test_petrify_curing_restore_staff_fails
    def test_petrify_curing_restore_staff_fails(self):
        """Test that restore staff cannot cure petrify status."""
        # Arrange
        unit_id = "U001"
        status_name = "Petrify"
        cure_method = "Restore Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a petrify status effect
        mock_petrify_status = MagicMock()
        mock_petrify_status.name = status_name
        mock_petrify_status.cure_methods = ["Kia Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_petrify_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertFalse(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)  # Status should remain
        self.mock_event_system.publish.assert_not_called()
        
    # TDD Anchor: test_paralysis_application_scripted
    def test_paralysis_application_scripted(self):
        """Test applying scripted paralysis status to a unit."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Paralysis"
        source = "Event Script"
        duration = 3  # Lasts for 3 turns
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Mock status effect data
        mock_status_data = MagicMock()
        mock_status_data.name = status_effect_name
        mock_status_data.effects = [
            {"type": "ACTION_RESTRICTION", "parameters": {"all": True}}
        ]
        mock_status_data.duration_type = "SCRIPTED_TURNS"
        mock_status_data.cure_methods = ["Restore Staff", "Duration Expiry", "Chapter End"]
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_status_effect_data.return_value = mock_status_data
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source, duration=duration)
        
        # Assert
        self.assertTrue(result)
        self.mock_data_provider.get_status_effect_data.assert_called_once_with(status_effect_name)
        self.assertIn(unit_id, self.status_effect_manager.active_statuses)
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].name, status_effect_name)
        self.assertEqual(self.status_effect_manager.active_statuses[unit_id][0].turns_remaining, duration)
        
        # Verify event was published
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_APPLIED",
            {"unit": mock_unit, "status": status_effect_name, "source": source}
        )
        
    # TDD Anchor: test_paralysis_duration_scripted
    def test_paralysis_duration_scripted(self):
        """Test that scripted paralysis expires after the specified duration."""
        # Arrange
        unit_id = "U001"
        
        # Create a scripted paralysis status effect
        mock_paralysis_status = MagicMock()
        mock_paralysis_status.name = "Paralysis"
        mock_paralysis_status.duration_type = "SCRIPTED_TURNS"
        mock_paralysis_status.turns_remaining = 1  # Will expire after one more turn
        mock_paralysis_status.decrement_turn.return_value = True  # Will expire
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_paralysis_status]
        }
        
        # Act
        self.status_effect_manager.process_turn_end(unit_id)
        
        # Assert
        mock_paralysis_status.decrement_turn.assert_called_once()
        
        # Check that the status was removed
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)
        
        # Verify event was published for the expired status
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_EXPIRED",
            {"unit_id": unit_id, "status": mock_paralysis_status.name}
        )
        
    # Additional utility tests
    
    def test_has_status_positive(self):
        """Test that has_status returns True when a unit has the specified status."""
        # Arrange
        unit_id = "U001"
        status_name = "Poison"
        
        # Create a status effect
        mock_status = MagicMock()
        mock_status.name = status_name
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_status]
        }
        
        # Act
        result = self.status_effect_manager.has_status(unit_id, status_name)
        
        # Assert
        self.assertTrue(result)
        
    def test_has_status_negative(self):
        """Test that has_status returns False when a unit doesn't have the specified status."""
        # Arrange
        unit_id = "U001"
        status_name = "Poison"
        
        # Set up the active statuses (empty)
        self.status_effect_manager.active_statuses = {}
        
        # Act
        result = self.status_effect_manager.has_status(unit_id, status_name)
        
        # Assert
        self.assertFalse(result)
        
    def test_get_active_statuses(self):
        """Test that get_active_statuses returns all active statuses for a unit."""
        # Arrange
        unit_id = "U001"
        
        # Create some status effects
        mock_status1 = MagicMock()
        mock_status1.name = "Poison"
        
        mock_status2 = MagicMock()
        mock_status2.name = "Sleep"
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_status1, mock_status2]
        }
        
        # Act
        result = self.status_effect_manager.get_active_statuses(unit_id)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn(mock_status1, result)
        self.assertIn(mock_status2, result)
        
    def test_get_active_statuses_no_statuses(self):
        """Test that get_active_statuses returns an empty list when a unit has no statuses."""
        # Arrange
        unit_id = "U001"
        
        # Set up the active statuses (empty)
        self.status_effect_manager.active_statuses = {}
        
        # Act
        result = self.status_effect_manager.get_active_statuses(unit_id)
        
        # Assert
        self.assertEqual(len(result), 0)
        
    def test_apply_status_already_active_no_stack(self):
        """Test that applying a status that's already active doesn't stack."""
        # Arrange
        unit_id = "U001"
        status_effect_name = "Poison"
        source = "Poison Sword"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create an existing poison status effect
        mock_existing_status = MagicMock()
        mock_existing_status.name = status_effect_name
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_existing_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.apply_status(unit_id, status_effect_name, source)
        
        # Assert
        self.assertFalse(result)  # Should fail since status is already active
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)  # Still only one status
        self.mock_event_system.publish.assert_not_called()  # No event should be published
        
    def test_cure_non_existent_status(self):
        """Test that curing a non-existent status returns False."""
        # Arrange
        unit_id = "U001"
        status_name = "Poison"
        cure_method = "Antitoxin"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Set up the active statuses (empty)
        self.status_effect_manager.active_statuses = {}
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertFalse(result)
        self.mock_event_system.publish.assert_not_called()


if __name__ == '__main__':
    unittest.main()
        
    def test_cure_all_statuses(self):
        """Test curing all statuses with a restore staff."""
        # Arrange
        unit_id = "U001"
        cure_method = "Restore Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create some status effects
        mock_poison_status = MagicMock()
        mock_poison_status.name = "Poison"
        mock_poison_status.cure_methods = ["Restore Staff", "Antitoxin", "Chapter End"]
        
        mock_sleep_status = MagicMock()
        mock_sleep_status.name = "Sleep"
        mock_sleep_status.cure_methods = ["Restore Staff", "Chapter End"]
        
        mock_petrify_status = MagicMock()
        mock_petrify_status.name = "Petrify"
        mock_petrify_status.cure_methods = ["Kia Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_poison_status, mock_sleep_status, mock_petrify_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, None, cure_method)  # None means cure all applicable
        
        # Assert
        self.assertTrue(result)
        # Should have cured Poison and Sleep, but not Petrify
        self.assertEqual(len(self.status_effect_manager.active_statuses[unit_id]), 1)
        self.assertIn(mock_petrify_status, self.status_effect_manager.active_statuses[unit_id])
        
        # Verify events were published for the cured statuses
        self.assertEqual(self.mock_event_system.publish.call_count, 2)
        self.mock_event_system.publish.assert_any_call(
            "STATUS_CURED",
            {"unit": mock_unit, "status": "Poison", "method": cure_method}
        )
        self.mock_event_system.publish.assert_any_call(
            "STATUS_CURED",
            {"unit": mock_unit, "status": "Sleep", "method": cure_method}
        )
        
    def test_process_turn_start_no_effect_for_sleep(self):
        """Test that sleep status has no effect at turn start."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a sleep status effect
        mock_sleep_status = MagicMock()
        mock_sleep_status.name = "Sleep"
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_sleep_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.status_effect_manager.process_turn_start_effects(unit_id)
        
        # Assert
        # No damage should be applied for sleep
        self.mock_unit_system.apply_damage.assert_not_called()
        self.mock_event_system.publish.assert_not_called()

    # TDD Anchor: test_berserk_ai_override
    def test_berserk_ai_override(self):
        """Test that berserk status overrides the unit's AI."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Create a berserk status effect
        mock_berserk_status = MagicMock()
        mock_berserk_status.name = "Berserk"
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_berserk_status]
        }
        
        # Act
        result = self.status_effect_manager.get_ai_override(unit_id)
        
        # Assert
        self.assertEqual(result, "BERSERK_AI")

    # TDD Anchor: test_berserk_curing
    def test_berserk_curing(self):
        """Test curing berserk status with a restore staff."""
        # Arrange
        unit_id = "U001"
        status_name = "Berserk"
        cure_method = "Restore Staff"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        
        # Create a berserk status effect
        mock_berserk_status = MagicMock()
        mock_berserk_status.name = status_name
        mock_berserk_status.cure_methods = ["Restore Staff", "Chapter End"]
        
        # Set up the active statuses
        self.status_effect_manager.active_statuses = {
            unit_id: [mock_berserk_status]
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.status_effect_manager.cure_status(unit_id, status_name, cure_method)
        
        # Assert
        self.assertTrue(result)
        self.assertEqual(len(self.status_effect_manager.active_statuses), 0)  # Should be empty after curing
        self.mock_event_system.publish.assert_called_once_with(
            "STATUS_CURED",
            {"unit": mock_unit, "status": status_name, "method": cure_method}
        )
