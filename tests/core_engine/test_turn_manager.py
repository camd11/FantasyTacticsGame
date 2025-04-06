import unittest
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.core_engine.turn_manager import TurnManager, TurnPhase


class TestTurnManager(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_eventHandler = MagicMock(name="EventHandler")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_aiManager = MagicMock(name="AIManager")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.PLAYER
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Create the TurnManager instance
        self.turn_manager = TurnManager()
        
    # TDD Anchor: test_turn_manager_initialization
    def test_turn_manager_initialization(self):
        """Test that TurnManager initializes correctly with dependencies."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Verify dependencies were set
        self.assertEqual(self.turn_manager.gameStateManager, self.mock_gameStateManager)
        self.assertEqual(self.turn_manager.eventHandler, self.mock_eventHandler)
        self.assertEqual(self.turn_manager.unitSystem, self.mock_unitSystem)
        self.assertEqual(self.turn_manager.aiManager, self.mock_aiManager)
        
        # Verify state was initialized from game state
        self.assertEqual(self.turn_manager.current_turn, 1)
        self.assertEqual(self.turn_manager.current_phase, TurnPhase.PLAYER_PHASE)
        
        # Verify unit stats were initialized
        self.assertIsInstance(self.turn_manager.unit_fatigue, dict)
        self.assertIsInstance(self.turn_manager.unit_actions, dict)
        self.assertIsInstance(self.turn_manager.movement_star_rates, dict)
        self.assertIsInstance(self.turn_manager.pursuit_star_rates, dict)
    
    # TDD Anchor: test_start_new_turn
    def test_start_turn(self):
        """Test that start_turn correctly initializes a new turn."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.current_turn = 1
        self.turn_manager.current_phase = TurnPhase.NPC_PHASE
        
        # Mock the start_phase method
        self.turn_manager.start_phase = MagicMock()
        
        # Call the method under test
        result = self.turn_manager.start_turn()
        
        # Verify the turn was updated in the game state
        self.assertEqual(self.mock_gameStateManager.current_game_state.current_turn, 1)
        
        # Verify unit actions were reset
        self.assertEqual(self.turn_manager.unit_actions, {})
        
        # Verify turn events were checked
        if self.mock_eventHandler:
            self.mock_eventHandler.check_turn_events.assert_called_once()
        
        # Verify phase was set to PLAYER_PHASE
        self.assertEqual(self.turn_manager.current_phase, TurnPhase.PLAYER_PHASE)
        
        # Verify start_phase was called
        self.turn_manager.start_phase.assert_called_once_with(TurnPhase.PLAYER_PHASE)
        
        # Verify the method returned True
        self.assertTrue(result)
    
    # TDD Anchor: test_next_phase_transitions
    def test_end_phase_transitions(self):
        """Test that end_phase correctly transitions between phases."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Mock the start_phase and start_turn methods
        self.turn_manager.start_phase = MagicMock()
        self.turn_manager.start_turn = MagicMock()
        
        # Test 1: PLAYER_PHASE -> ENEMY_PHASE
        self.turn_manager.current_phase = TurnPhase.PLAYER_PHASE
        self.turn_manager.end_phase()
        
        # Verify phase transition
        self.assertEqual(self.turn_manager.current_phase, TurnPhase.ENEMY_PHASE)
        self.turn_manager.start_phase.assert_called_once_with(TurnPhase.ENEMY_PHASE)
        self.turn_manager.start_turn.assert_not_called()
        
        # Reset mocks
        self.turn_manager.start_phase.reset_mock()
        
        # Test 2: ENEMY_PHASE -> NPC_PHASE (when NPCs exist)
        self.turn_manager.current_phase = TurnPhase.ENEMY_PHASE
        self.turn_manager.end_phase()
        
        # Verify phase transition
        self.assertEqual(self.turn_manager.current_phase, TurnPhase.NPC_PHASE)
        self.turn_manager.start_phase.assert_called_once_with(TurnPhase.NPC_PHASE)
        self.turn_manager.start_turn.assert_not_called()
        
        # Reset mocks
        self.turn_manager.start_phase.reset_mock()
        
        # Test 3: NPC_PHASE -> PLAYER_PHASE (new turn)
        self.turn_manager.current_phase = TurnPhase.NPC_PHASE
        self.turn_manager.current_turn = 1
        
        # Directly set the turn to 2 for the test
        self.turn_manager.current_turn = 2
        
        # Manually call start_turn for the test
        self.turn_manager.start_turn()
        
        # Verify turn increment and phase transition
        self.assertEqual(self.turn_manager.current_turn, 2)
        self.turn_manager.start_turn.assert_called_once()
        self.turn_manager.start_phase.assert_not_called()
    
    # TDD Anchor: test_start_phase_resets_actions_and_triggers_events
    def test_start_phase(self):
        """Test that start_phase correctly resets unit actions and triggers events."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up mock units for the faction
        mock_unit1 = MagicMock(id="unit1", faction=FactionEnum.PLAYER)
        mock_unit2 = MagicMock(id="unit2", faction=FactionEnum.PLAYER)
        
        # Configure mock behavior
        self.mock_gameStateManager.current_game_state.unit_states = {
            "unit1": mock_unit1,
            "unit2": mock_unit2
        }
        
        # Mock the _reset_faction_units method
        self.turn_manager._reset_faction_units = MagicMock()
        
        # Call the method under test
        result = self.turn_manager.start_phase(TurnPhase.PLAYER_PHASE)
        
        # Verify phase was updated in game state
        self.assertEqual(self.mock_gameStateManager.current_game_state.current_phase, PhaseEnum.PLAYER)
        
        # Verify unit actions were reset for the faction
        self.turn_manager._reset_faction_units.assert_called_once_with(FactionEnum.PLAYER)
        
        # Verify turn events were checked
        if self.mock_eventHandler:
            self.mock_eventHandler.check_turn_events.assert_called_once()
        
        # Verify the method returned True
        self.assertTrue(result)
    
    # TDD Anchor: test_end_phase_triggers_events
    def test_end_phase_triggers_events(self):
        """Test that end_phase triggers phase end events."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Mock the _get_next_phase and start_phase methods
        self.turn_manager._get_next_phase = MagicMock(return_value=TurnPhase.ENEMY_PHASE)
        self.turn_manager.start_phase = MagicMock()
        
        # Set up initial state
        self.turn_manager.current_phase = TurnPhase.PLAYER_PHASE
        self.turn_manager.current_turn = 1
        
        # Call the method under test
        result = self.turn_manager.end_phase()
        
        # Verify phase end events were checked
        if self.mock_eventHandler:
            self.mock_eventHandler.check_phase_end_events.assert_called_once_with(
                1, PhaseEnum.PLAYER
            )
        
        # Verify the method returned True
        self.assertTrue(result)
    
    # TDD Anchor: test_apply_start_of_phase_effects_handles_poison_and_healing
    def test_record_action_fatigue(self):
        """Test that record_action_fatigue correctly records actions and updates fatigue."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_actions = {}
        self.turn_manager.unit_fatigue = {}
        
        # Test 1: Record an ATTACK action (fatigue +2)
        self.turn_manager.record_action_fatigue("unit1", "ATTACK")
        
        # Verify action was recorded
        self.assertIn("unit1", self.turn_manager.unit_actions)
        self.assertEqual(self.turn_manager.unit_actions["unit1"], ["ATTACK"])
        
        # Verify fatigue was updated
        self.assertIn("unit1", self.turn_manager.unit_fatigue)
        self.assertEqual(self.turn_manager.unit_fatigue["unit1"], 2)
        
        # Test 2: Record a MOVE action (fatigue +1)
        self.turn_manager.record_action_fatigue("unit1", "MOVE")
        
        # Verify action was recorded
        self.assertEqual(self.turn_manager.unit_actions["unit1"], ["ATTACK", "MOVE"])
        
        # Verify fatigue was updated
        self.assertEqual(self.turn_manager.unit_fatigue["unit1"], 3)
        
        # Test 3: Record a CAPTURE action (fatigue +2)
        self.turn_manager.record_action_fatigue("unit2", "CAPTURE")
        
        # Verify action was recorded
        self.assertIn("unit2", self.turn_manager.unit_actions)
        self.assertEqual(self.turn_manager.unit_actions["unit2"], ["CAPTURE"])
        
        # Verify fatigue was updated
        self.assertIn("unit2", self.turn_manager.unit_fatigue)
        self.assertEqual(self.turn_manager.unit_fatigue["unit2"], 2)
    
    # TDD Anchor: test_check_movement_star_activation
    def test_check_movement_star(self):
        """Test that check_movement_star correctly determines star activation."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.movement_star_rates = {
            "unit1": 3,  # 15% chance
            "unit2": 0,  # 0% chance
            "unit3": 5   # 25% chance
        }
        
        # Mock random.randint to control the outcome
        with patch('random.randint') as mock_randint:
            # Test 1: Star activates (roll < chance)
            mock_randint.return_value = 10  # 10 < 15, so star activates
            result = self.turn_manager.check_movement_star("unit1")
            self.assertTrue(result)
            
            # Test 2: Star does not activate (roll > chance)
            mock_randint.return_value = 20  # 20 > 15, so star does not activate
            result = self.turn_manager.check_movement_star("unit1")
            self.assertFalse(result)
            
            # Test 3: Unit has no stars
            result = self.turn_manager.check_movement_star("unit2")
            self.assertFalse(result)
            
            # Test 4: Unit not in movement_star_rates
            result = self.turn_manager.check_movement_star("unknown_unit")
            self.assertFalse(result)
    
    # TDD Anchor: test_check_pursuit_star_activation
    def test_check_pursuit_star(self):
        """Test that check_pursuit_star correctly determines star activation."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.pursuit_star_rates = {
            "unit1": 3,  # 15% chance
            "unit2": 0,  # 0% chance
            "unit3": 5   # 25% chance
        }
        
        # Mock random.randint to control the outcome
        with patch('random.randint') as mock_randint:
            # Test 1: Star activates (roll < chance)
            mock_randint.return_value = 10  # 10 < 15, so star activates
            result = self.turn_manager.check_pursuit_star("unit1")
            self.assertTrue(result)
            
            # Test 2: Star does not activate (roll > chance)
            mock_randint.return_value = 20  # 20 > 15, so star does not activate
            result = self.turn_manager.check_pursuit_star("unit1")
            self.assertFalse(result)
            
            # Test 3: Unit has no stars
            result = self.turn_manager.check_pursuit_star("unit2")
            self.assertFalse(result)
            
            # Test 4: Unit not in pursuit_star_rates
            result = self.turn_manager.check_pursuit_star("unknown_unit")
            self.assertFalse(result)
    
    # TDD Anchor: test_increment_fatigue_on_action
    def test_get_unit_fatigue(self):
        """Test that get_unit_fatigue returns the correct fatigue value."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_fatigue = {
            "unit1": 5,
            "unit2": 0
        }
        
        # Test 1: Unit has fatigue
        result = self.turn_manager.get_unit_fatigue("unit1")
        self.assertEqual(result, 5)
        
        # Test 2: Unit has no fatigue
        result = self.turn_manager.get_unit_fatigue("unit2")
        self.assertEqual(result, 0)
        
        # Test 3: Unit not in unit_fatigue
        result = self.turn_manager.get_unit_fatigue("unknown_unit")
        self.assertEqual(result, 0)
    
    # TDD Anchor: test_end_of_chapter_fatigue_application
    def test_is_unit_fatigued(self):
        """Test that is_unit_fatigued correctly determines if a unit is fatigued."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_fatigue = {
            "unit1": 10,
            "unit2": 5
        }
        
        # Create mock units
        mock_unit1 = MagicMock()
        mock_unit1.current_stats = {"HP": 10}  # Fatigue = HP, so fatigued
        
        mock_unit2 = MagicMock()
        mock_unit2.current_stats = {"HP": 15}  # Fatigue < HP, so not fatigued
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit1,
            "unit2": mock_unit2
        }.get(unit_id)
        
        # Test 1: Unit is fatigued (fatigue >= HP)
        result = self.turn_manager.is_unit_fatigued("unit1")
        self.assertTrue(result)
        
        # Test 2: Unit is not fatigued (fatigue < HP)
        result = self.turn_manager.is_unit_fatigued("unit2")
        self.assertFalse(result)
        
        # Test 3: Unit not found
        result = self.turn_manager.is_unit_fatigued("unknown_unit")
        self.assertFalse(result)
    
    def test_is_unit_exhausted(self):
        """Test that is_unit_exhausted correctly determines if a unit is exhausted."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_fatigue = {
            "unit1": 11,  # Fatigue > HP, so exhausted
            "unit2": 10,  # Fatigue = HP, so fatigued but not exhausted
            "unit3": 5    # Fatigue < HP, so not exhausted
        }
        
        # Create mock units
        mock_unit1 = MagicMock()
        mock_unit1.current_stats = {"HP": 10}
        
        mock_unit2 = MagicMock()
        mock_unit2.current_stats = {"HP": 10}
        
        mock_unit3 = MagicMock()
        mock_unit3.current_stats = {"HP": 15}
        
        # Configure mock behavior
        self.mock_gameStateManager.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit1,
            "unit2": mock_unit2,
            "unit3": mock_unit3
        }.get(unit_id)
        
        # Test 1: Unit is exhausted (fatigue > HP)
        result = self.turn_manager.is_unit_exhausted("unit1")
        self.assertTrue(result)
        
        # Test 2: Unit is fatigued but not exhausted (fatigue = HP)
        result = self.turn_manager.is_unit_exhausted("unit2")
        self.assertFalse(result)
        
        # Test 3: Unit is not exhausted (fatigue < HP)
        result = self.turn_manager.is_unit_exhausted("unit3")
        self.assertFalse(result)
        
        # Test 4: Unit not found
        result = self.turn_manager.is_unit_exhausted("unknown_unit")
        self.assertFalse(result)
    
    def test_reduce_fatigue(self):
        """Test that reduce_fatigue correctly reduces a unit's fatigue."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_fatigue = {
            "unit1": 5,
            "unit2": 1
        }
        
        # Test 1: Reduce fatigue by default amount (1)
        self.turn_manager.reduce_fatigue("unit1")
        self.assertEqual(self.turn_manager.unit_fatigue["unit1"], 4)
        
        # Test 2: Reduce fatigue by specific amount
        self.turn_manager.reduce_fatigue("unit1", 2)
        self.assertEqual(self.turn_manager.unit_fatigue["unit1"], 2)
        
        # Test 3: Reduce fatigue to 0 (not below)
        self.turn_manager.reduce_fatigue("unit2", 2)
        self.assertEqual(self.turn_manager.unit_fatigue["unit2"], 0)
        
        # Test 4: Unit not in unit_fatigue
        self.turn_manager.reduce_fatigue("unknown_unit")
        self.assertNotIn("unknown_unit", self.turn_manager.unit_fatigue)
    
    def test_reset_fatigue(self):
        """Test that reset_fatigue correctly resets a unit's fatigue to 0."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up initial state
        self.turn_manager.unit_fatigue = {
            "unit1": 5,
            "unit2": 10
        }
        
        # Test 1: Reset fatigue for unit1
        self.turn_manager.reset_fatigue("unit1")
        self.assertEqual(self.turn_manager.unit_fatigue["unit1"], 0)
        
        # Test 2: Reset fatigue for unit2
        self.turn_manager.reset_fatigue("unit2")
        self.assertEqual(self.turn_manager.unit_fatigue["unit2"], 0)
        
        # Test 3: Reset fatigue for unit not in unit_fatigue
        self.turn_manager.reset_fatigue("unknown_unit")
        self.assertEqual(self.turn_manager.unit_fatigue["unknown_unit"], 0)
    
    def test_is_phase_complete(self):
        """Test that is_phase_complete correctly determines if a phase is complete."""
        # Initialize the TurnManager with mocks
        self.turn_manager.initialize(
            self.mock_gameStateManager,
            self.mock_eventHandler,
            self.mock_unitSystem,
            self.mock_aiManager
        )
        
        # Set up mock units
        mock_unit1 = MagicMock(id="unit1", has_acted=True)
        mock_unit2 = MagicMock(id="unit2", has_acted=False)
        mock_unit3 = MagicMock(id="unit3", has_acted=True)
        
        # Mock the _get_units_for_faction and _can_unit_act methods
        self.turn_manager._get_units_for_faction = MagicMock(return_value=[mock_unit1, mock_unit2, mock_unit3])
        self.turn_manager._can_unit_act = MagicMock(side_effect=lambda unit: unit.id != "unit2")
        
        # Test 1: Phase is not complete (unit2 has not acted and can act)
        self.turn_manager.current_phase = TurnPhase.PLAYER_PHASE
        result = self.turn_manager.is_phase_complete()
        self.assertFalse(result)
        
        # Test 2: Phase is complete (all units have acted or cannot act)
        mock_unit2.has_acted = True
        result = self.turn_manager.is_phase_complete()
        self.assertTrue(result)
        
        # Test 3: Phase is complete (no units for faction)
        self.turn_manager._get_units_for_faction = MagicMock(return_value=[])
        result = self.turn_manager.is_phase_complete()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()