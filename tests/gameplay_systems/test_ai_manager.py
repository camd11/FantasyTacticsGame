import unittest
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager, AIBehaviorType, AITargetPriority, AIProfile, AIAction


class TestAIManager(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_actionHandler = MagicMock(name="ActionHandler")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.PLAYER
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Create the AIManager instance
        self.ai_manager = AIManager()
    
    # TDD Anchor: test_ai_manager_initialization
    def test_ai_manager_initialization(self):
        """Test that AIManager initializes correctly with dependencies."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Verify dependencies were set
        self.assertEqual(self.ai_manager.gameStateManager, self.mock_gameStateManager)
        self.assertEqual(self.ai_manager.unitSystem, self.mock_unitSystem)
        self.assertEqual(self.ai_manager.mapSystem, self.mock_mapSystem)
        self.assertEqual(self.ai_manager.movementSystem, self.mock_movementSystem)
        self.assertEqual(self.ai_manager.combatSystem, self.mock_combatSystem)
        self.assertEqual(self.ai_manager.actionHandler, self.mock_actionHandler)
        self.assertEqual(self.ai_manager.dataProvider, self.mock_dataProvider)
        
        # Verify state was initialized
        self.assertIsInstance(self.ai_manager.unit_ai_profiles, dict)
        self.assertIsInstance(self.ai_manager.last_attackers, dict)
    
    def test_load_ai_profiles(self):
        """Test that _load_ai_profiles correctly loads AI profiles for units."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Create mock units
        mock_unit1 = MagicMock()
        mock_unit1.faction = FactionEnum.ENEMY
        
        mock_unit2 = MagicMock()
        mock_unit2.faction = FactionEnum.NPC
        
        mock_unit3 = MagicMock()
        mock_unit3.faction = FactionEnum.PLAYER  # Should be ignored
        
        # Configure mock behavior
        self.mock_game_state.unit_states = {
            "unit1": mock_unit1,
            "unit2": mock_unit2,
            "unit3": mock_unit3
        }
        
        # Configure AI profile data
        self.mock_dataProvider.get_unit_ai_profile.side_effect = lambda unit_id: {
            "unit1": {
                "behavior_type": "AGGRESSIVE",
                "target_priority": "WEAKEST",
                "aggression": 80
            },
            "unit2": {
                "behavior_type": "DEFENSIVE",
                "target_priority": "CLOSEST",
                "aggression": 30
            },
            "unit3": None
        }.get(unit_id)
        
        # Call the method under test
        self.ai_manager._load_ai_profiles()
        
        # Verify AI profiles were loaded
        self.assertIn("unit1", self.ai_manager.unit_ai_profiles)
        self.assertIn("unit2", self.ai_manager.unit_ai_profiles)
        self.assertNotIn("unit3", self.ai_manager.unit_ai_profiles)
        
        # Verify profile properties
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].behavior_type, AIBehaviorType.AGGRESSIVE)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].target_priority, AITargetPriority.WEAKEST)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].aggression, 80)
        
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit2"].behavior_type, AIBehaviorType.DEFENSIVE)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit2"].target_priority, AITargetPriority.CLOSEST)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit2"].aggression, 30)
    
    def test_change_unit_ai(self):
        """Test that change_unit_ai correctly updates a unit's AI profile."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Set up initial AI profile
        self.ai_manager.unit_ai_profiles = {
            "unit1": AIProfile(
                behavior_type=AIBehaviorType.AGGRESSIVE,
                target_priority=AITargetPriority.WEAKEST,
                aggression=80
            )
        }
        
        # Define new AI profile data
        new_ai_profile = {
            "behavior_type": "DEFENSIVE",
            "target_priority": "CLOSEST",
            "aggression": 30
        }
        
        # Call the method under test
        self.ai_manager.change_unit_ai("unit1", new_ai_profile)
        
        # Verify AI profile was updated
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].behavior_type, AIBehaviorType.DEFENSIVE)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].target_priority, AITargetPriority.CLOSEST)
        self.assertEqual(self.ai_manager.unit_ai_profiles["unit1"].aggression, 30)
        
        # Test with unit not in profiles
        self.ai_manager.change_unit_ai("unknown_unit", new_ai_profile)
        self.assertNotIn("unknown_unit", self.ai_manager.unit_ai_profiles)
    
    # TDD Anchor: test_process_phase_iterates_units
    def test_process_ai_turn(self):
        """Test that process_ai_turn correctly processes AI units for a faction."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Create mock units
        mock_unit1 = MagicMock()
        mock_unit1.id = "unit1"
        mock_unit1.has_acted = False
        
        mock_unit2 = MagicMock()
        mock_unit2.id = "unit2"
        mock_unit2.has_acted = True  # Already acted
        
        mock_unit3 = MagicMock()
        mock_unit3.id = "unit3"
        mock_unit3.has_acted = False
        
        # Configure mock behavior
        self.ai_manager._get_units_for_faction = MagicMock(return_value=[mock_unit1, mock_unit2, mock_unit3])
        self.ai_manager._sort_units_by_priority = MagicMock(return_value=[mock_unit1, mock_unit2, mock_unit3])
        self.ai_manager.determine_best_action = MagicMock()
        self.ai_manager._execute_ai_action = MagicMock()
        
        # Configure determine_best_action to return different actions
        self.ai_manager.determine_best_action.side_effect = lambda unit_id: {
            "unit1": AIAction("MOVE", "unit1", {"path": [(1, 1), (2, 2)]}),
            "unit3": AIAction("ATTACK", "unit3", {"target_unit_id": "player1"})
        }.get(unit_id)
        
        # Call the method under test
        result = self.ai_manager.process_ai_turn(FactionEnum.ENEMY)
        
        # Verify units were retrieved and sorted
        self.ai_manager._get_units_for_faction.assert_called_once_with(FactionEnum.ENEMY)
        self.ai_manager._sort_units_by_priority.assert_called_once()
        
        # Verify determine_best_action was called for units that haven't acted
        self.ai_manager.determine_best_action.assert_has_calls([
            call("unit1"),
            call("unit3")
        ])
        
        # Verify actions were executed - use ANY matcher for AIAction objects
        from unittest.mock import ANY
        self.ai_manager._execute_ai_action.assert_has_calls([
            call(ANY),
            call(ANY)
        ])
        
        # Verify the result
        self.assertTrue(result)
    
    # TDD Anchor: test_process_unit_turn_selects_best_action
    def test_determine_best_action(self):
        """Test that determine_best_action correctly selects the best action for a unit."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Create mock unit
        mock_unit = MagicMock()
        mock_unit.id = "unit1"
        
        # Create mock AI profile
        mock_profile = MagicMock()
        mock_profile.behavior_type = AIBehaviorType.AGGRESSIVE
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.return_value = mock_unit
        self.ai_manager.unit_ai_profiles = {"unit1": mock_profile}
        
        # Mock behavior-specific action determination methods
        self.ai_manager._determine_aggressive_action = MagicMock(return_value=AIAction("ATTACK", "unit1", {"target_unit_id": "player1"}))
        self.ai_manager._determine_defensive_action = MagicMock()
        self.ai_manager._determine_cautious_action = MagicMock()
        
        # Call the method under test
        result = self.ai_manager.determine_best_action("unit1")
        
        # Verify unit and profile were retrieved
        self.mock_gameStateManager.get_unit.assert_called_once_with("unit1")
        
        # Verify the correct behavior-specific method was called
        self.ai_manager._determine_aggressive_action.assert_called_once_with("unit1", mock_profile)
        self.ai_manager._determine_defensive_action.assert_not_called()
        self.ai_manager._determine_cautious_action.assert_not_called()
        
        # Verify the result
        self.assertEqual(result.action_type, "ATTACK")
        self.assertEqual(result.unit_id, "unit1")
        self.assertEqual(result.target_data, {"target_unit_id": "player1"})
        
        # Test with different behavior type
        mock_profile.behavior_type = AIBehaviorType.DEFENSIVE
        self.ai_manager._determine_defensive_action.return_value = AIAction("WAIT", "unit1", {})
        
        result = self.ai_manager.determine_best_action("unit1")
        
        # Verify the correct behavior-specific method was called
        self.ai_manager._determine_defensive_action.assert_called_once_with("unit1", mock_profile)
        
        # Verify the result
        self.assertEqual(result.action_type, "WAIT")
        
        # Test with unit not found
        self.mock_gameStateManager.get_unit.return_value = None
        
        result = self.ai_manager.determine_best_action("unknown_unit")
        
        # Verify the result
        self.assertIsNone(result)
        
        # Test with profile not found
        self.mock_gameStateManager.get_unit.return_value = mock_unit
        self.ai_manager.unit_ai_profiles = {}
        
        result = self.ai_manager.determine_best_action("unit1")
        
        # Verify the result
        self.assertIsNone(result)
    
    # TDD Anchor: test_find_possible_actions_considers_range_and_targets
    def test_determine_aggressive_action(self):
        """Test that _determine_aggressive_action correctly determines an aggressive action."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Create mock profile
        mock_profile = MagicMock()
        mock_profile.target_priority = AITargetPriority.CLOSEST
        mock_profile.specific_target_id = None
        mock_profile.movement_range = None
        
        # Configure mock behavior
        self.ai_manager._find_targets = MagicMock(return_value=[MagicMock(), MagicMock()])
        self.ai_manager._sort_targets = MagicMock(return_value=[MagicMock(id="player1"), MagicMock(id="player2")])
        self.ai_manager._can_attack_target = MagicMock(return_value=False)
        self.ai_manager._find_path_to_attack = MagicMock(return_value=[(1, 1), (2, 2)])
        
        # Call the method under test
        result = self.ai_manager._determine_aggressive_action("unit1", mock_profile)
        
        # Verify targets were found and sorted
        self.ai_manager._find_targets.assert_called_once_with("unit1", AITargetPriority.CLOSEST, None)
        self.ai_manager._sort_targets.assert_called_once()
        
        # Verify attack possibility was checked
        self.ai_manager._can_attack_target.assert_called_with("unit1", "player1")
        
        # Verify path to attack was found
        self.ai_manager._find_path_to_attack.assert_called_with("unit1", "player1")
        
        # Verify the result
        self.assertEqual(result.action_type, "MOVE")
        self.assertEqual(result.unit_id, "unit1")
        self.assertEqual(result.target_data, {"path": [(1, 1), (2, 2)]})
        
        # Test with no targets
        self.ai_manager._find_targets.return_value = []
        
        result = self.ai_manager._determine_aggressive_action("unit1", mock_profile)
        
        # Verify the result
        self.assertEqual(result.action_type, "WAIT")
        self.assertEqual(result.unit_id, "unit1")
        self.assertEqual(result.target_data, {})
        
        # Test with can attack target
        self.ai_manager._find_targets.return_value = [MagicMock(), MagicMock()]
        self.ai_manager._can_attack_target.return_value = True
        
        result = self.ai_manager._determine_aggressive_action("unit1", mock_profile)
        
        # Verify the result
        self.assertEqual(result.action_type, "ATTACK")
        self.assertEqual(result.unit_id, "unit1")
        self.assertEqual(result.target_data, {"target_unit_id": "player1"})
    
    def test_execute_ai_action(self):
        """Test that _execute_ai_action correctly executes an AI action."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Create mock action
        action = AIAction("MOVE", "unit1", {"path": [(1, 1), (2, 2)]})
        
        # Call the method under test
        self.ai_manager._execute_ai_action(action)
        
        # Verify action was executed
        self.mock_actionHandler.perform_action.assert_called_once()
        
        # Test with different action type
        action = AIAction("ATTACK", "unit1", {"target_unit_id": "player1"})
        
        # Reset mock
        self.mock_actionHandler.perform_action.reset_mock()
        
        # Call the method under test
        self.ai_manager._execute_ai_action(action)
        
        # Verify action was executed
        self.mock_actionHandler.perform_action.assert_called_once()
    
    def test_record_attack(self):
        """Test that record_attack correctly records an attack."""
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider
        )
        
        # Call the method under test
        self.ai_manager.record_attack("attacker1", "defender1")
        
        # Verify attack was recorded
        self.assertIn("defender1", self.ai_manager.last_attackers)
        self.assertEqual(self.ai_manager.last_attackers["defender1"], "attacker1")
        
        # Test with different attacker
        self.ai_manager.record_attack("attacker2", "defender1")
        
        # Verify attack was updated
        self.assertEqual(self.ai_manager.last_attackers["defender1"], "attacker2")


if __name__ == '__main__':
    unittest.main()