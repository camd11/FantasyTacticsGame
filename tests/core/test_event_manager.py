"""
Test for Event Manager

This test verifies that the EventManager correctly handles event triggers and outcomes
based on various conditions (turn number, area reached, unit defeated, talk).
"""

import unittest
from unittest.mock import MagicMock, patch, call
from typing import Dict, List, Tuple, Optional, Any

# Import the classes to be tested
from src.core_engine.event_system import (
    EventManager, EventDefinition, EventCondition, EventAction, ActionExecutor
)
from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum
from src.core_engine.data_provider import DataProvider


class TestEventTriggering(unittest.TestCase):
    """Test cases for event triggering in the EventManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock dependencies
        self.mock_game_state = MagicMock(spec=GameState)
        # Add set_flag method to the mock_game_state
        self.mock_game_state.set_flag = MagicMock()
        self.mock_data_provider = MagicMock(spec=DataProvider)
        self.mock_action_executor = MagicMock(spec=ActionExecutor)
        self.mock_map_system = MagicMock()
        
        # Create the EventManager with mock dependencies
        self.event_manager = EventManager()
        self.event_manager.initialize(
            self.mock_game_state,
            self.mock_data_provider,
            self.mock_action_executor,
            self.mock_map_system
        )
        
        # Sample event triggers for testing
        self.turn_trigger = EventCondition(type="TurnNumber", turn=3)
        self.area_trigger = EventCondition(
            type="Location", 
            unit_id="LEIF", 
            location=(5, 5)
        )
        self.unit_death_trigger = EventCondition(type="UnitDeath", unit_id="ENEMY1")
        self.talk_trigger = EventCondition(
            type="TalkBetweenUnits", 
            talker_id="LEIF", 
            listener_id="FINN"
        )
        
        # Sample event actions for testing
        self.spawn_action = EventAction(
            type="SpawnUnit", 
            unit_template_id="BANDIT", 
            location=(10, 10)
        )
        self.dialogue_action = EventAction(
            type="DisplayMessage", 
            message_key="REINFORCEMENT_MESSAGE"
        )
        self.set_flag_action = EventAction(
            type="SetFlag", 
            flag_id="REINFORCEMENTS_TRIGGERED"
        )
        
        # Sample events for testing
        self.turn_event = EventDefinition(
            event_id="turn_3_reinforcements",
            trigger_point="StartPlayerPhase",
            repeatable=False,
            conditions=[self.turn_trigger],
            actions=[self.spawn_action, self.dialogue_action]
        )
        
        self.area_event = EventDefinition(
            event_id="area_reached_event",
            trigger_point="UnitMoved",
            repeatable=False,
            conditions=[self.area_trigger],
            actions=[self.dialogue_action, self.set_flag_action]
        )
        
        self.death_event = EventDefinition(
            event_id="enemy_defeated_event",
            trigger_point="UnitDefeated",
            repeatable=False,
            conditions=[self.unit_death_trigger],
            actions=[self.dialogue_action]
        )
        
        self.talk_event = EventDefinition(
            event_id="talk_event",
            trigger_point="UnitAction",
            repeatable=False,
            conditions=[self.talk_trigger],
            actions=[self.dialogue_action]
        )

    def test_turn_based_trigger(self):
        """Test that events are triggered correctly based on turn number."""
        # Set up the game state for the test
        self.mock_game_state.current_turn = 3
        
        # Add the event to the event manager
        self.event_manager.chapter_events = [self.turn_event]
        
        # Mock the check_conditions and execute_event methods
        self.event_manager.check_conditions = MagicMock(return_value=True)
        self.event_manager.execute_event = MagicMock()
        
        # Mock the game_state.get_flag method to return False (event not triggered yet)
        self.mock_game_state.get_flag = MagicMock(return_value=False)
        
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.check_events("StartPlayerPhase", context)
        
        # Assertions
        self.event_manager.check_conditions.assert_called_once_with(self.turn_event, context)
        self.event_manager.execute_event.assert_called_once_with(self.turn_event, context)
        
        # Verify the event is marked as triggered
        self.mock_game_state.set_flag.assert_called_with("event_turn_3_reinforcements_triggered", True)
        
        # Test that the event is not triggered again
        self.mock_game_state.get_flag.return_value = True
        self.event_manager.check_conditions.reset_mock()
        self.event_manager.execute_event.reset_mock()
        
        self.event_manager.check_events("StartPlayerPhase", context)
        self.event_manager.check_conditions.assert_not_called()
        self.event_manager.execute_event.assert_not_called()

    def test_area_reached_trigger(self):
        """Test that events are triggered correctly when a unit reaches a specific area."""
        # Set up the game state for the test
        self.mock_game_state.get_unit = MagicMock(return_value=MagicMock())
        
        # Mock the check_unit_location function to return True
        with patch('src.core_engine.event_system.check_unit_location', return_value=True):
            # Add the event to the event manager
            self.event_manager.chapter_events = [self.area_event]
            
            # Mock the check_conditions and execute_event methods
            self.event_manager.check_conditions = MagicMock(return_value=True)
            self.event_manager.execute_event = MagicMock()
            
            # Mock the game_state.get_flag method to return False (event not triggered yet)
            self.mock_game_state.get_flag = MagicMock(return_value=False)
            
            # Call the method under test
            context = {"unit_id": "LEIF", "position": (5, 5)}
            self.event_manager.check_events("UnitMoved", context)
            
            # Assertions
            self.event_manager.check_conditions.assert_called_once_with(self.area_event, context)
            self.event_manager.execute_event.assert_called_once_with(self.area_event, context)
            
            # Verify the event is marked as triggered
            self.mock_game_state.set_flag.assert_called_with("event_area_reached_event_triggered", True)

    def test_unit_defeated_trigger(self):
        """Test that events are triggered correctly when a unit is defeated."""
        # Set up the game state for the test
        self.mock_game_state.is_unit_dead = MagicMock(return_value=True)
        
        # Add the event to the event manager
        self.event_manager.chapter_events = [self.death_event]
        
        # Mock the check_conditions and execute_event methods
        self.event_manager.check_conditions = MagicMock(return_value=True)
        self.event_manager.execute_event = MagicMock()
        
        # Mock the game_state.get_flag method to return False (event not triggered yet)
        self.mock_game_state.get_flag = MagicMock(return_value=False)
        
        # Call the method under test
        context = {"unit_id": "ENEMY1", "cause": "combat"}
        self.event_manager.check_events("UnitDefeated", context)
        
        # Assertions
        self.event_manager.check_conditions.assert_called_once_with(self.death_event, context)
        self.event_manager.execute_event.assert_called_once_with(self.death_event, context)
        
        # Verify the event is marked as triggered
        self.mock_game_state.set_flag.assert_called_with("event_enemy_defeated_event_triggered", True)

    def test_talk_trigger(self):
        """Test that events are triggered correctly when units talk to each other."""
        # Set up the game state for the test
        
        # Mock the check_talk_condition function to return True
        with patch('src.core_engine.event_system.check_talk_condition', return_value=True):
            # Add the event to the event manager
            self.event_manager.chapter_events = [self.talk_event]
            
            # Mock the check_conditions and execute_event methods
            self.event_manager.check_conditions = MagicMock(return_value=True)
            self.event_manager.execute_event = MagicMock()
            
            # Mock the game_state.get_flag method to return False (event not triggered yet)
            self.mock_game_state.get_flag = MagicMock(return_value=False)
            
            # Call the method under test
            context = {"action_type": "Talk", "talker_id": "LEIF", "listener_id": "FINN"}
            self.event_manager.check_events("UnitAction", context)
            
            # Assertions
            self.event_manager.check_conditions.assert_called_once_with(self.talk_event, context)
            self.event_manager.execute_event.assert_called_once_with(self.talk_event, context)
            
            # Verify the event is marked as triggered
            self.mock_game_state.set_flag.assert_called_with("event_talk_event_triggered", True)


class TestEventOutcomes(unittest.TestCase):
    """Test cases for event outcomes in the EventManager class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock dependencies
        self.mock_game_state = MagicMock(spec=GameState)
        self.mock_data_provider = MagicMock(spec=DataProvider)
        self.mock_action_executor = MagicMock(spec=ActionExecutor)
        self.mock_map_system = MagicMock()
        
        # Create the EventManager with mock dependencies
        self.event_manager = EventManager()
        self.event_manager.initialize(
            self.mock_game_state,
            self.mock_data_provider,
            self.mock_action_executor,
            self.mock_map_system
        )
        
        # Sample event actions for testing
        self.spawn_action = EventAction(
            type="SpawnUnit", 
            unit_template_id="BANDIT", 
            location=(10, 10)
        )
        self.dialogue_action = EventAction(
            type="DisplayMessage", 
            message_key="REINFORCEMENT_MESSAGE"
        )
        self.set_flag_action = EventAction(
            type="SetFlag", 
            flag_id="REINFORCEMENTS_TRIGGERED"
        )
        self.update_objective_action = EventAction(
            type="UpdateObjective",
            objective_id="main_objective",
            new_status="completed"
        )
        
        # Sample event for testing
        self.test_event = EventDefinition(
            event_id="test_event",
            trigger_point="StartPlayerPhase",
            repeatable=False,
            conditions=[],
            actions=[
                self.spawn_action, 
                self.dialogue_action, 
                self.set_flag_action,
                self.update_objective_action
            ]
        )

    def test_reinforcement_spawn_outcome(self):
        """Test that reinforcement units are spawned correctly."""
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.execute_event(self.test_event, context)
        
        # Assertions
        self.mock_action_executor.execute.assert_any_call(self.spawn_action, context)

    def test_dialogue_outcome(self):
        """Test that dialogue is shown correctly."""
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.execute_event(self.test_event, context)
        
        # Assertions
        self.mock_action_executor.execute.assert_any_call(self.dialogue_action, context)

    def test_flag_setting_outcome(self):
        """Test that flags are set correctly."""
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.execute_event(self.test_event, context)
        
        # Assertions
        self.mock_action_executor.execute.assert_any_call(self.set_flag_action, context)

    def test_objective_update_outcome(self):
        """Test that objectives are updated correctly."""
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.execute_event(self.test_event, context)
        
        # Assertions
        self.mock_action_executor.execute.assert_any_call(self.update_objective_action, context)

    def test_multiple_actions_executed_in_order(self):
        """Test that multiple actions are executed in the correct order."""
        # Call the method under test
        context = {"turn": 3, "phase": "Player"}
        self.event_manager.execute_event(self.test_event, context)
        
        # Assertions
        expected_calls = [
            call(self.spawn_action, context),
            call(self.dialogue_action, context),
            call(self.set_flag_action, context),
            call(self.update_objective_action, context)
        ]
        self.mock_action_executor.execute.assert_has_calls(expected_calls, any_order=False)


if __name__ == '__main__':
    unittest.main()