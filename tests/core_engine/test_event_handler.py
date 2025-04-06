import unittest
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.core_engine.event_handler import EventHandler, EventTrigger, ConditionType, EventActionType, EventData, EventCondition, EventAction


class TestEventHandler(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_turnManager = MagicMock(name="TurnManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        self.mock_uiManager = MagicMock(name="UIManager")
        self.mock_aiManager = MagicMock(name="AIManager")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.PLAYER
        self.mock_game_state.event_flags = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Create the EventHandler instance
        self.event_handler = EventHandler()
    
    # TDD Anchor: test_event_handler_initialization_and_load
    def test_event_handler_initialization(self):
        """Test that EventHandler initializes correctly with dependencies."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Verify dependencies were set
        self.assertEqual(self.event_handler.gameStateManager, self.mock_gameStateManager)
        self.assertEqual(self.event_handler.turnManager, self.mock_turnManager)
        self.assertEqual(self.event_handler.unitSystem, self.mock_unitSystem)
        self.assertEqual(self.event_handler.mapSystem, self.mock_mapSystem)
        self.assertEqual(self.event_handler.inventorySystem, self.mock_inventorySystem)
        self.assertEqual(self.event_handler.dataProvider, self.mock_dataProvider)
        self.assertEqual(self.event_handler.uiManager, self.mock_uiManager)
        self.assertEqual(self.event_handler.aiManager, self.mock_aiManager)
        
        # Verify state was initialized
        self.assertIsInstance(self.event_handler.chapterEvents, list)
        self.assertIsInstance(self.event_handler.activeEventFlags, set)
    
    def test_load_chapter_events(self):
        """Test that load_chapter_events correctly loads events from the DataProvider."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Create mock event data
        mock_event_data = [
            {
                "id": "event1",
                "trigger": "TURN_START",
                "trigger_params": {"turn": 1},
                "conditions": [],
                "actions": [{"type": "SHOW_DIALOGUE", "params": {"dialogue_id": "intro"}}],
                "priority": 0,
                "is_repeatable": False
            }
        ]
        
        # Configure mock behavior
        self.mock_dataProvider.get_event_scripts.return_value = mock_event_data
        self.event_handler._convert_raw_events = MagicMock(return_value=[MagicMock()])
        
        # Call the method under test
        self.event_handler.load_chapter_events("chapter1")
        
        # Verify event data was retrieved
        self.mock_dataProvider.get_event_scripts.assert_called_once_with("chapter1", None)
        
        # Verify events were converted
        self.event_handler._convert_raw_events.assert_called_once_with(mock_event_data)
        
        # Verify events were stored
        self.assertEqual(len(self.event_handler.chapterEvents), 1)
    
    # TDD Anchor: test_check_turn_events_trigger_correctly
    def test_check_turn_events(self):
        """Test that check_turn_events correctly identifies and executes turn events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the find_and_execute_events method
        self.event_handler.find_and_execute_events = MagicMock()
        
        # Call the method under test
        self.event_handler.check_turn_events(1, PhaseEnum.PLAYER)
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_called_once_with(
            EventTrigger.TURN_START,
            {'turn': 1, 'phase': PhaseEnum.PLAYER}
        )
    
    # TDD Anchor: test_check_location_events_trigger_on_move
    def test_check_location_events(self):
        """Test that check_location_events correctly identifies and executes location events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the find_and_execute_events method
        self.event_handler.find_and_execute_events = MagicMock()
        
        # Call the method under test
        self.event_handler.check_location_events("unit1", (5, 5))
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_has_calls([
            call(EventTrigger.LOCATION_ENTER, {'unit_id': 'unit1', 'position': (5, 5)}),
            call(EventTrigger.LOCATION_STAND, {'unit_id': 'unit1', 'position': (5, 5)})
        ])
    
    # TDD Anchor: test_check_action_events_trigger_talk_visit_seize
    def test_check_action_event(self):
        """Test that check_action_event correctly identifies and executes action events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the find_and_execute_events method
        self.event_handler.find_and_execute_events = MagicMock()
        
        # Test 1: TALK action
        self.event_handler.check_action_event("TALK", "unit1", {"target_unit_id": "unit2"})
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_called_once_with(
            EventTrigger.ACTION_TALK,
            {'unit_id': 'unit1', 'target_unit_id': 'unit2'}
        )
        
        # Reset mock
        self.event_handler.find_and_execute_events.reset_mock()
        
        # Test 2: VISIT action
        self.event_handler.check_action_event("VISIT", "unit1", {"target_tile": (5, 5)})
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_called_once_with(
            EventTrigger.ACTION_VISIT,
            {'unit_id': 'unit1', 'target_tile': (5, 5)}
        )
        
        # Reset mock
        self.event_handler.find_and_execute_events.reset_mock()
        
        # Test 3: SEIZE action
        self.event_handler.check_action_event("SEIZE", "unit1", {"target_tile": (5, 5)})
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_called_once_with(
            EventTrigger.ACTION_SEIZE,
            {'unit_id': 'unit1', 'target_tile': (5, 5)}
        )
    
    # TDD Anchor: test_check_death_event_triggers
    def test_check_death_event(self):
        """Test that check_death_event correctly identifies and executes death events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the find_and_execute_events method
        self.event_handler.find_and_execute_events = MagicMock()
        
        # Call the method under test
        self.event_handler.check_death_event("unit1")
        
        # Verify find_and_execute_events was called with the correct parameters
        self.event_handler.find_and_execute_events.assert_called_once_with(
            EventTrigger.UNIT_DEATH,
            {'unit_id': 'unit1'}
        )
    
    # TDD Anchor: test_find_and_execute_events_filters_correctly
    def test_find_and_execute_events(self):
        """Test that find_and_execute_events correctly filters and executes events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Create mock events
        mock_event1 = MagicMock()
        mock_event1.has_triggered = False
        mock_event1.is_repeatable = False
        mock_event1.trigger = EventTrigger.TURN_START
        mock_event1.priority = 1
        
        mock_event2 = MagicMock()
        mock_event2.has_triggered = False
        mock_event2.is_repeatable = False
        mock_event2.trigger = EventTrigger.TURN_START
        mock_event2.priority = 0
        
        mock_event3 = MagicMock()
        mock_event3.has_triggered = True  # Already triggered
        mock_event3.is_repeatable = False
        mock_event3.trigger = EventTrigger.TURN_START
        
        mock_event4 = MagicMock()
        mock_event4.has_triggered = True  # Already triggered but repeatable
        mock_event4.is_repeatable = True
        mock_event4.trigger = EventTrigger.TURN_START
        mock_event4.priority = 2
        
        # Set up chapter events
        self.event_handler.chapterEvents = [mock_event1, mock_event2, mock_event3, mock_event4]
        
        # Mock the check methods
        self.event_handler.check_trigger_details = MagicMock(return_value=True)
        self.event_handler.check_event_conditions = MagicMock(return_value=True)
        self.event_handler.execute_event = MagicMock()
        
        # Call the method under test
        self.event_handler.find_and_execute_events(EventTrigger.TURN_START, {'turn': 1})
        
        # Verify events were checked
        self.event_handler.check_trigger_details.assert_has_calls([
            call(mock_event1, {'turn': 1}),
            call(mock_event2, {'turn': 1}),
            call(mock_event4, {'turn': 1})
        ])
        
        # Verify conditions were checked
        self.event_handler.check_event_conditions.assert_has_calls([
            call(mock_event1.conditions, {'turn': 1}),
            call(mock_event2.conditions, {'turn': 1}),
            call(mock_event4.conditions, {'turn': 1})
        ])
        
        # Verify events were executed in priority order
        self.event_handler.execute_event.assert_has_calls([
            call(mock_event4, {'turn': 1}),
            call(mock_event1, {'turn': 1}),
            call(mock_event2, {'turn': 1})
        ])
        
        # Verify events were marked as triggered
        self.assertTrue(mock_event1.has_triggered)
        self.assertTrue(mock_event2.has_triggered)
        self.assertTrue(mock_event4.has_triggered)
    
    # TDD Anchor: test_check_trigger_details_match_context
    def test_check_trigger_details(self):
        """Test that check_trigger_details correctly matches trigger details to context."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the _is_location_match method
        self.event_handler._is_location_match = MagicMock()
        self.event_handler._is_lord = MagicMock()
        
        # Test 1: TURN_START trigger
        event = MagicMock()
        event.trigger = EventTrigger.TURN_START
        event.trigger_params = {'turn': 1}
        
        result = self.event_handler.check_trigger_details(event, {'turn': 1})
        self.assertTrue(result)
        
        result = self.event_handler.check_trigger_details(event, {'turn': 2})
        self.assertFalse(result)
        
        # Test 2: LOCATION_ENTER trigger
        event.trigger = EventTrigger.LOCATION_ENTER
        event.trigger_params = {'location': (5, 5), 'unit_id': 'unit1'}
        self.event_handler._is_location_match.return_value = True
        
        result = self.event_handler.check_trigger_details(event, {'position': (5, 5), 'unit_id': 'unit1'})
        self.assertTrue(result)
        
        result = self.event_handler.check_trigger_details(event, {'position': (5, 5), 'unit_id': 'unit2'})
        self.assertFalse(result)
        
        # Test 3: ACTION_TALK trigger
        event.trigger = EventTrigger.ACTION_TALK
        event.trigger_params = {'talker_id': 'unit1', 'listener_id': 'unit2'}
        
        result = self.event_handler.check_trigger_details(event, {'unit_id': 'unit1', 'target_unit_id': 'unit2'})
        self.assertTrue(result)
        
        result = self.event_handler.check_trigger_details(event, {'unit_id': 'unit2', 'target_unit_id': 'unit1'})
        self.assertTrue(result)
        
        result = self.event_handler.check_trigger_details(event, {'unit_id': 'unit1', 'target_unit_id': 'unit3'})
        self.assertFalse(result)
    
    # TDD Anchor: test_check_event_conditions_evaluates_correctly
    def test_check_event_conditions(self):
        """Test that check_event_conditions correctly evaluates event conditions."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock helper methods
        self.event_handler._is_unit_alive = MagicMock()
        self.event_handler._is_unit_in_region = MagicMock()
        self.event_handler._unit_has_item = MagicMock()
        
        # Create conditions
        condition1 = EventCondition(ConditionType.UNIT_ALIVE, {'unit_id': 'unit1'})
        condition2 = EventCondition(ConditionType.FLAG_SET, {'flag_name': 'flag1'})
        condition3 = EventCondition(ConditionType.FLAG_NOT_SET, {'flag_name': 'flag2'})
        
        # Test 1: All conditions pass
        self.event_handler._is_unit_alive.return_value = True
        self.event_handler.activeEventFlags = {'flag1'}
        
        result = self.event_handler.check_event_conditions([condition1, condition2, condition3], {})
        self.assertTrue(result)
        
        # Test 2: UNIT_ALIVE condition fails
        self.event_handler._is_unit_alive.return_value = False
        
        result = self.event_handler.check_event_conditions([condition1, condition2, condition3], {})
        self.assertFalse(result)
        
        # Test 3: FLAG_SET condition fails
        self.event_handler._is_unit_alive.return_value = True
        self.event_handler.activeEventFlags = {}
        
        result = self.event_handler.check_event_conditions([condition1, condition2, condition3], {})
        self.assertFalse(result)
        
        # Test 4: FLAG_NOT_SET condition fails
        self.event_handler.activeEventFlags = {'flag1', 'flag2'}
        
        result = self.event_handler.check_event_conditions([condition1, condition2, condition3], {})
        self.assertFalse(result)
    
    # TDD Anchor: test_execute_event_performs_actions
    def test_execute_event(self):
        """Test that execute_event correctly performs all actions in an event."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Mock the execute_event_action method
        self.event_handler.execute_event_action = MagicMock()
        
        # Create mock event
        action1 = MagicMock()
        action2 = MagicMock()
        
        event = MagicMock()
        event.id = "event1"
        event.actions = [action1, action2]
        
        # Call the method under test
        self.event_handler.execute_event(event, {'turn': 1})
        
        # Verify actions were executed
        self.event_handler.execute_event_action.assert_has_calls([
            call(action1, {'turn': 1}),
            call(action2, {'turn': 1})
        ])
    
    # TDD Anchor: test_execute_event_action_handles_all_types
    def test_execute_event_action(self):
        """Test that execute_event_action correctly handles different action types."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Test 1: SHOW_DIALOGUE action
        action = EventAction(EventActionType.SHOW_DIALOGUE, {
            'dialogue_id': 'dialogue1',
            'speaker_unit_id': 'unit1'
        })
        
        self.event_handler.execute_event_action(action, {})
        
        # Verify dialogue was shown
        self.mock_uiManager.show_dialogue.assert_called_once_with('dialogue1', 'unit1')
        
        # Test 2: SPAWN_UNIT action
        action = EventAction(EventActionType.SPAWN_UNIT, {
            'unit_data': {'id': 'unit1'},
            'location': (5, 5),
            'ai_override': 'aggressive'
        })
        
        self.event_handler.execute_event_action(action, {})
        
        # Verify unit was spawned
        self.mock_unitSystem.spawn_unit.assert_called_once_with(
            {'id': 'unit1'},
            (5, 5),
            'aggressive'
        )
        
        # Test 3: SET_FLAG action
        action = EventAction(EventActionType.SET_FLAG, {
            'flag_name': 'flag1'
        })
        
        self.event_handler.execute_event_action(action, {})
        
        # Verify flag was set
        self.assertIn('flag1', self.event_handler.activeEventFlags)
        self.assertEqual(self.mock_gameStateManager.current_game_state.event_flags['flag1'], True)
    
    # TDD Anchor: test_has_talk_event_finds_existing
    def test_has_talk_event(self):
        """Test that has_talk_event correctly identifies talk events between units."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Create mock events
        event1 = MagicMock()
        event1.trigger = EventTrigger.ACTION_TALK
        event1.trigger_params = {'talker_id': 'unit1', 'listener_id': 'unit2'}
        
        event2 = MagicMock()
        event2.trigger = EventTrigger.ACTION_TALK
        event2.trigger_params = {'talker_id': 'unit3', 'listener_id': 'unit4'}
        
        # Set up chapter events
        self.event_handler.chapterEvents = [event1, event2]
        
        # Test 1: Talk event exists (direct order)
        result = self.event_handler.has_talk_event('unit1', 'unit2')
        self.assertTrue(result)
        
        # Test 2: Talk event exists (reverse order)
        result = self.event_handler.has_talk_event('unit2', 'unit1')
        self.assertTrue(result)
        
        # Test 3: Talk event does not exist
        result = self.event_handler.has_talk_event('unit1', 'unit3')
        self.assertFalse(result)
    
    # TDD Anchor: test_trigger_talk_event_executes
    def test_trigger_talk_event(self):
        """Test that trigger_talk_event correctly executes talk events."""
        # Initialize the EventHandler with mocks
        self.event_handler.initialize(
            self.mock_gameStateManager,
            self.mock_turnManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider,
            self.mock_uiManager,
            self.mock_aiManager
        )
        
        # Create mock events
        event = MagicMock()
        event.trigger = EventTrigger.ACTION_TALK
        event.trigger_params = {'talker_id': 'unit1', 'listener_id': 'unit2'}
        event.conditions = []
        
        # Set up chapter events
        self.event_handler.chapterEvents = [event]
        
        # Mock the check_event_conditions and execute_event methods
        self.event_handler.check_event_conditions = MagicMock(return_value=True)
        self.event_handler.execute_event = MagicMock()
        
        # Test: Trigger talk event
        result = self.event_handler.trigger_talk_event('unit1', 'unit2')
        
        # Verify conditions were checked
        self.event_handler.check_event_conditions.assert_called_once_with(
            event.conditions,
            {'unit_id': 'unit1', 'target_unit_id': 'unit2'}
        )
        
        # Verify event was executed
        self.event_handler.execute_event.assert_called_once_with(
            event,
            {'unit_id': 'unit1', 'target_unit_id': 'unit2'}
        )
        
        # Verify event was marked as triggered
        self.assertTrue(event.has_triggered)
        
        # Verify the result
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()