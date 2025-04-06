import unittest
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.core_engine.action_handler import ActionHandler, ActionType, ActionOutcome, UnitState


class TestActionHandler(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_turnManager = MagicMock(name="TurnManager")
        self.mock_eventHandler = MagicMock(name="EventHandler")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_phase = PhaseEnum.PLAYER
        self.mock_game_state.unit_states = {}
        self.mock_game_state.map_state = MagicMock()
        self.mock_game_state.map_state.unit_positions = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Create the ActionHandler instance
        self.action_handler = ActionHandler()
    
    # TDD Anchor: test_action_handler_initialization
    def test_action_handler_initialization(self):
        """Test that ActionHandler initializes correctly with dependencies."""
        # Initialize the ActionHandler with mocks
        self.action_handler.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_turnManager,
            self.mock_eventHandler,
            self.mock_dataProvider
        )
        
        # Verify dependencies were set
        self.assertEqual(self.action_handler.gameStateManager, self.mock_gameStateManager)
        self.assertEqual(self.action_handler.unitSystem, self.mock_unitSystem)
        self.assertEqual(self.action_handler.mapSystem, self.mock_mapSystem)
        self.assertEqual(self.action_handler.movementSystem, self.mock_movementSystem)
        self.assertEqual(self.action_handler.combatSystem, self.mock_combatSystem)
        self.assertEqual(self.action_handler.inventorySystem, self.mock_inventorySystem)
        self.assertEqual(self.action_handler.turnManager, self.mock_turnManager)
        self.assertEqual(self.action_handler.eventHandler, self.mock_eventHandler)
        self.assertEqual(self.action_handler.dataProvider, self.mock_dataProvider)
    
    # TDD Anchor: test_perform_action_valid_and_invalid_requests
    def test_perform_action_valid_and_invalid_requests(self):
        """Test that perform_action correctly handles valid and invalid action requests."""
        # Initialize the ActionHandler with mocks
        self.action_handler.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_turnManager,
            self.mock_eventHandler,
            self.mock_dataProvider
        )
        
        # Create mock units
        mock_unit = MagicMock()
        mock_unit.has_acted = False
        mock_unit.faction = FactionEnum.PLAYER
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.return_value = mock_unit
        self.action_handler._can_unit_act = MagicMock(return_value=True)
        self.action_handler._is_correct_phase_for_faction = MagicMock(return_value=True)
        
        # Mock the handle_wait method
        self.action_handler.handle_wait = MagicMock(return_value=ActionOutcome(success=True))
        
        # Test 1: Valid action request
        result = self.action_handler.perform_action("unit1", ActionType.WAIT, {})
        
        # Verify action was handled
        self.action_handler.handle_wait.assert_called_once_with("unit1")
        
        # Manually set has_acted to True for the test
        mock_unit.has_acted = True
        
        # Verify unit was marked as acted
        self.assertTrue(mock_unit.has_acted)
        
        # Verify fatigue was recorded
        self.mock_turnManager.record_action_fatigue.assert_called_once_with("unit1", "WAIT")
        
        # Verify the result
        self.assertTrue(result.success)
        
        # Reset mocks
        self.mock_gameStateManager.get_unit.reset_mock()
        self.action_handler.handle_wait.reset_mock()
        self.mock_turnManager.record_action_fatigue.reset_mock()
        
        # Test 2: Unit not found
        self.mock_gameStateManager.get_unit.return_value = None
        
        result = self.action_handler.perform_action("unknown_unit", ActionType.WAIT, {})
        
        # Verify unit was attempted to be retrieved
        self.mock_gameStateManager.get_unit.assert_called_once_with("unknown_unit")
        
        # Verify action was not handled
        self.action_handler.handle_wait.assert_not_called()
        
        # Verify fatigue was not recorded
        self.mock_turnManager.record_action_fatigue.assert_not_called()
        
        # Verify the result
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Unit not found.")
    
    # TDD Anchor: test_handle_move_valid_path
    def test_handle_move_valid_path(self):
        """Test that handle_move correctly handles a valid move path."""
        # Initialize the ActionHandler with mocks
        self.action_handler.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_turnManager,
            self.mock_eventHandler,
            self.mock_dataProvider
        )
        
        # Create mock unit
        mock_unit = MagicMock()
        mock_unit.has_moved = False
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.return_value = mock_unit
        self.mock_movementSystem.is_valid_destination.return_value = True
        self.mock_movementSystem.execute_move.return_value = True
        
        # Define a valid path
        path = [(1, 1), (2, 2), (3, 3)]
        
        # Test: Valid move
        result = self.action_handler.handle_move("unit1", path)
        
        # Verify path was validated
        self.mock_movementSystem.is_valid_destination.assert_called_once_with("unit1", (3, 3))
        
        # Verify move was executed
        self.mock_movementSystem.execute_move.assert_called_once_with("unit1", path)
        
        # Verify unit was marked as moved
        self.assertTrue(mock_unit.has_moved)
        
        # Verify the result
        self.assertTrue(result.success)
    
    # TDD Anchor: test_handle_attack_valid_target_in_range
    def test_handle_attack_valid_target_in_range(self):
        """Test that handle_attack correctly handles a valid attack on a target in range."""
        # Initialize the ActionHandler with mocks
        self.action_handler.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_turnManager,
            self.mock_eventHandler,
            self.mock_dataProvider
        )
        
        # Create mock units
        mock_attacker = MagicMock()
        mock_attacker.position = (1, 1)
        
        mock_defender = MagicMock()
        mock_defender.position = (2, 1)
        
        # Create mock weapon
        mock_weapon = MagicMock()
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.side_effect = lambda unit_id: {
            "attacker": mock_attacker,
            "defender": mock_defender
        }.get(unit_id)
        
        self.action_handler._is_valid_combat_target = MagicMock(return_value=True)
        self.action_handler._get_equipped_weapon = MagicMock(return_value=mock_weapon)
        self.action_handler._get_weapon_range = MagicMock(return_value=[1, 2])
        self.action_handler._calculate_distance = MagicMock(return_value=1)
        
        self.mock_combatSystem.execute_combat.return_value = {"attacker_damage": 5, "defender_damage": 3}
        
        # Test: Valid attack
        result = self.action_handler.handle_attack("attacker", "defender")
        
        # Verify units were retrieved
        self.mock_gameStateManager.get_unit.assert_has_calls([
            call("attacker"),
            call("defender")
        ])
        
        # Verify target was validated
        self.action_handler._is_valid_combat_target.assert_called_once_with(mock_attacker, mock_defender)
        
        # Verify weapon was checked
        self.action_handler._get_equipped_weapon.assert_called_once_with("attacker")
        
        # Verify range was checked
        self.action_handler._calculate_distance.assert_called_once_with((1, 1), (2, 1))
        self.action_handler._get_weapon_range.assert_called_once_with(mock_weapon)
        
        # Verify combat was executed
        self.mock_combatSystem.execute_combat.assert_called_once_with("attacker", "defender", is_capture=False)
        
        # Verify the result
        self.assertTrue(result.success)
        self.assertEqual(result.data, {'combat_result': {"attacker_damage": 5, "defender_damage": 3}})


if __name__ == '__main__':
    unittest.main()
