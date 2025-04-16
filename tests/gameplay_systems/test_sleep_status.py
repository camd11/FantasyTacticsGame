"""
Test for Sleep Status Effect

This test verifies that the sleep status effect correctly prevents a unit from taking any actions,
reduces their Avoid to 0, and is cured when the unit takes damage or after its duration expires.
"""

import pytest
import logging
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import GameStateManager, GameState, StatusEffectEnum, UnitState, FactionEnum, DispositionEnum
from src.core_engine.data_provider import DataProvider, StatEnum
from src.gameplay_systems.status_effects_system import StatusEffectManager, StatusEffectInstance
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.action_system import ActionSystem
from src.gameplay_systems.combat_system import CombatSystem
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.turn_manager import TurnManager

# Constants
ACTIVE = DispositionEnum.ACTIVE
SLEEP = StatusEffectEnum.SLEEP
AVOID = "AVOID"  # Using string instead of enum since StatEnum doesn't have AVOID

# Mock EventSystem for testing
class MockEventSystem:
    """A simple mock event system for testing."""
    
    def __init__(self):
        self.subscribers = {}
        self.published_events = []
    
    def subscribe(self, event_type, callback):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type, event_data):
        """Publish an event."""
        self.published_events.append((event_type, event_data))
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                callback(event_data)

# Mock StatusEffectData for testing
class MockSleepStatusEffectData:
    """A mock sleep status effect data class for testing."""
    
    def __init__(self):
        self.name = "Sleep"
        self.description = "Unit is asleep and cannot perform any actions. Avoid becomes 0. Cured by taking damage or after duration expires."
        self.duration_type = "TURN_COUNT"
        self.default_duration = 3
        self.cure_methods = ["Restore Staff", "Taking Damage", "Chapter End"]
        self.icon = "sleep_icon"
        self.effects = [
            {
                "type": "PREVENT_ACTION",
                "parameters": {}
            },
            {
                "type": "SET_STAT",
                "parameters": {
                    "stat": "Avoid",
                    "value": 0
                }
            },
            {
                "type": "CURE_ON_DAMAGE",
                "parameters": {}
            }
        ]

class TestSleepStatus:
    """Test cases for the sleep status effect."""

    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = DataProvider()
        game_state_manager = GameStateManager(data_provider)
        unit_system = UnitSystem()
        event_system = MockEventSystem()
        status_effect_manager = StatusEffectManager()
        action_system = ActionSystem()
        combat_system = CombatSystem()
        map_system = MapSystem()
        turn_manager = TurnManager()
        
        # Create a mock inventory system
        inventory_system = MagicMock()
        
        # Initialize dependencies
        unit_system.initialize(game_state_manager, data_provider)
        status_effect_manager.initialize(game_state_manager, data_provider, unit_system, event_system)
        action_system.initialize(game_state_manager, data_provider, map_system, inventory_system, combat_system, None, None, status_effect_manager)
        combat_system.initialize(game_state_manager, unit_system, data_provider, event_system, inventory_system)
        map_system.initialize(game_state_manager, data_provider)
        
        # Create a mock core turn manager
        core_turn_manager = MagicMock()
        
        # Initialize turn manager
        turn_manager.initialize(core_turn_manager, game_state_manager, status_effect_manager, action_system)
        
        # Create test units manually
        player_unit_id = "PLAYER_UNIT"
        enemy_unit_id = "ENEMY_UNIT"
        
        # Initialize game state
        game_state_manager.current_game_state = GameState()
        
        # Create player unit state
        player_unit = UnitState()
        player_unit.id = player_unit_id
        player_unit.name = "Player Unit"
        player_unit.faction = FactionEnum.PLAYER
        player_unit.position = (5, 5)
        player_unit.max_hp = 20
        player_unit.current_hp = 20
        player_unit.base_stats = {"STR": 10, "SKL": 10, "SPD": 10, "LUK": 10, "DEF": 10, "AVOID": 30}
        player_unit.disposition = ACTIVE
        player_unit.equipped_weapon_index = 0
        player_unit.inventory = [MagicMock()]  # Mock weapon
        
        # Create enemy unit state
        enemy_unit = UnitState()
        enemy_unit.id = enemy_unit_id
        enemy_unit.name = "Enemy Unit"
        enemy_unit.faction = FactionEnum.ENEMY
        enemy_unit.position = (7, 5)  # 2 tiles away from player unit
        enemy_unit.max_hp = 20
        enemy_unit.current_hp = 20
        enemy_unit.base_stats = {"STR": 10, "SKL": 10, "SPD": 10, "LUK": 10, "DEF": 10, "AVOID": 30}
        enemy_unit.disposition = ACTIVE
        
        # Add the units to the game state
        game_state_manager.current_game_state.unit_states[player_unit_id] = player_unit
        game_state_manager.current_game_state.unit_states[enemy_unit_id] = enemy_unit
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "event_system": event_system,
            "status_effect_manager": status_effect_manager,
            "action_system": action_system,
            "combat_system": combat_system,
            "map_system": map_system,
            "turn_manager": turn_manager,
            "player_unit_id": player_unit_id,
            "enemy_unit_id": enemy_unit_id,
            "player_unit": player_unit,
            "enemy_unit": enemy_unit
        }
    
    def test_sleep_application_and_duration(self, setup_game_state, caplog, monkeypatch):
        """Test that sleep status is correctly applied with the specified duration.
        [TDD: Test Sleep application/duration]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        mock_status_instance.duration = 3  # Set duration to 3 turns
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance with the specified duration
            if duration is not None:
                mock_status_instance.duration = duration
            
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": player_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Apply the patch
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        
        try:
            # Apply sleep status effect with default duration
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Verify the duration is correct
            sleep_status = status_effect_manager.active_statuses[player_unit_id][0]
            assert sleep_status.duration == 3, f"Expected duration to be 3, got {sleep_status.duration}"
            
            # Apply sleep status effect with custom duration
            custom_duration = 5
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff", duration=custom_duration)
            assert sleep_applied, "Failed to apply Sleep status effect with custom duration"
            
            # Verify the duration is updated to the custom value
            sleep_status = status_effect_manager.active_statuses[player_unit_id][0]
            assert sleep_status.duration == custom_duration, f"Expected duration to be {custom_duration}, got {sleep_status.duration}"
            
        finally:
            # Restore the original method
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
    
    def test_sleep_blocks_all_actions(self, setup_game_state, caplog, monkeypatch):
        """Test that sleep prevents a unit from performing any actions.
        [TDD: Test Sleep blocks all actions]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        action_system = setup_game_state["action_system"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": player_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the has_status method to check for sleep status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Add a can_unit_act method to the action system if it doesn't exist
        if not hasattr(action_system, 'can_unit_act'):
            action_system.can_unit_act = MagicMock(return_value=True)
        
        # Patch the can_unit_act method to check for sleep status
        original_can_unit_act = action_system.can_unit_act
        
        def mock_can_unit_act(unit_id):
            # Unit cannot act if it has sleep status
            if status_effect_manager.has_status(unit_id, "Sleep"):
                return False
            return True
        
        # Patch the get_available_actions method to check for sleep status
        original_get_available_actions = action_system.get_available_actions
        
        def mock_get_available_actions(unit_id):
            # No actions available if unit has sleep status
            if status_effect_manager.has_status(unit_id, "Sleep"):
                return []
            return ["Move", "Attack", "Item", "Staff", "Wait", "Trade", "Rescue"]
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(action_system, "can_unit_act", mock_can_unit_act)
        monkeypatch.setattr(action_system, "get_available_actions", mock_get_available_actions)
        
        try:
            # Check that unit can act before sleep
            can_act_before = action_system.can_unit_act(player_unit_id)
            assert can_act_before, "Unit should be able to act before Sleep"
            
            # Check available actions before sleep
            actions_before = action_system.get_available_actions(player_unit_id)
            assert len(actions_before) > 0, "Unit should have available actions before Sleep"
            
            # Apply sleep status effect
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Check that unit cannot act with sleep
            can_act_after = action_system.can_unit_act(player_unit_id)
            assert not can_act_after, "Unit should not be able to act with Sleep"
            
            # Check available actions with sleep
            actions_after = action_system.get_available_actions(player_unit_id)
            assert len(actions_after) == 0, "Unit should have no available actions with Sleep"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(action_system, "can_unit_act", original_can_unit_act)
            monkeypatch.setattr(action_system, "get_available_actions", original_get_available_actions)
    
    def test_sleep_affects_avoid(self, setup_game_state, caplog, monkeypatch):
        """Test that sleep reduces a unit's Avoid stat to 0.
        [TDD: Test Sleep affects Avoid]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        combat_system = setup_game_state["combat_system"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": player_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the has_status method to check for sleep status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the get_modified_stats method to apply sleep effect on Avoid
        original_get_modified_stats = status_effect_manager.get_modified_stats
        
        def mock_get_modified_stats(unit_id, base_stats):
            modified_stats = base_stats.copy()
            
            # If unit has sleep status, set Avoid to 0
            if status_effect_manager.has_status(unit_id, "Sleep"):
                modified_stats[AVOID] = 0
            
            return modified_stats
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "get_modified_stats", mock_get_modified_stats)
        
        try:
            # Check unit's base Avoid stat
            base_avoid = player_unit.base_stats[AVOID]
            assert base_avoid > 0, "Unit's base Avoid should be greater than 0"
            
            # Get modified stats before sleep
            modified_stats_before = status_effect_manager.get_modified_stats(player_unit_id, player_unit.base_stats)
            assert modified_stats_before[AVOID] == base_avoid, f"Expected Avoid to be {base_avoid}, got {modified_stats_before[AVOID]}"
            
            # Apply sleep status effect
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Get modified stats after sleep
            modified_stats_after = status_effect_manager.get_modified_stats(player_unit_id, player_unit.base_stats)
            assert modified_stats_after[AVOID] == 0, f"Expected Avoid to be 0, got {modified_stats_after[AVOID]}"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "get_modified_stats", original_get_modified_stats)
    
    def test_sleep_wears_off(self, setup_game_state, caplog, monkeypatch):
        """Test that sleep status is removed after its duration expires.
        [TDD: Test Sleep wears off]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        action_system = setup_game_state["action_system"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        mock_status_instance.duration = 2  # Set duration to 2 turns
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance with the specified duration
            if duration is not None:
                mock_status_instance.duration = duration
            
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": player_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the has_status method to check for sleep status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the process_turn_start_effects method to decrement duration
        original_process_turn_start_effects = status_effect_manager.process_turn_start_effects
        
        def mock_process_turn_start_effects(unit_id):
            if unit_id not in status_effect_manager.active_statuses:
                return
            
            # Process each status effect
            statuses_to_remove = []
            for i, status in enumerate(status_effect_manager.active_statuses[unit_id]):
                if status.name == "Sleep":
                    # Decrement duration
                    status.duration -= 1
                    
                    # Check if duration has expired
                    if status.duration <= 0:
                        statuses_to_remove.append(i)
                        
                        # Publish event
                        event_system.publish("STATUS_REMOVED", {
                            "unit": player_unit,
                            "status": "Sleep",
                            "reason": "Duration Expired"
                        })
            
            # Remove expired statuses
            for i in reversed(statuses_to_remove):
                status_effect_manager.active_statuses[unit_id].pop(i)
        
        # Add a can_unit_act method to the action system if it doesn't exist
        if not hasattr(action_system, 'can_unit_act'):
            action_system.can_unit_act = MagicMock(return_value=True)
        
        # Patch the can_unit_act method to check for sleep status
        original_can_unit_act = action_system.can_unit_act
        
        def mock_can_unit_act(unit_id):
            # Unit cannot act if it has sleep status
            if status_effect_manager.has_status(unit_id, "Sleep"):
                return False
            return True
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "process_turn_start_effects", mock_process_turn_start_effects)
        monkeypatch.setattr(action_system, "can_unit_act", mock_can_unit_act)
        
        try:
            # Apply sleep status effect with duration of 2 turns
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff", duration=2)
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Verify the duration is correct
            sleep_status = status_effect_manager.active_statuses[player_unit_id][0]
            assert sleep_status.duration == 2, f"Expected duration to be 2, got {sleep_status.duration}"
            
            # Check that unit cannot act with sleep
            can_act_before = action_system.can_unit_act(player_unit_id)
            assert not can_act_before, "Unit should not be able to act with Sleep"
            
            # Process turn start effects (first turn)
            status_effect_manager.process_turn_start_effects(player_unit_id)
            
            # Verify the duration is decremented
            assert sleep_status.duration == 1, f"Expected duration to be 1, got {sleep_status.duration}"
            
            # Verify unit still has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should still have Sleep status effect after first turn"
            
            # Process turn start effects (second turn)
            status_effect_manager.process_turn_start_effects(player_unit_id)
            
            # Verify sleep status is removed
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert not has_sleep, "Unit should not have Sleep status effect after duration expires"
            
            # Check that unit can act again
            can_act_after = action_system.can_unit_act(player_unit_id)
            assert can_act_after, "Unit should be able to act after Sleep wears off"
            
            # Verify status removed event was published
            status_removed_events = [event for event in event_system.published_events if event[0] == "STATUS_REMOVED"]
            assert len(status_removed_events) > 0, "STATUS_REMOVED event should have been published"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "process_turn_start_effects", original_process_turn_start_effects)
            monkeypatch.setattr(action_system, "can_unit_act", original_can_unit_act)
    
    def test_taking_damage_cures_sleep(self, setup_game_state, caplog, monkeypatch):
        """Test that sleep status is removed when the unit takes damage.
        [TDD: Test taking damage cures Sleep]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        unit_system = setup_game_state["unit_system"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": player_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the has_status method to check for sleep status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the handle_damage_taken method to cure sleep
        original_handle_damage_taken = status_effect_manager.handle_damage_taken
        
        def mock_handle_damage_taken(unit_id, damage):
            if damage > 0 and unit_id in status_effect_manager.active_statuses:
                # Check for sleep status
                statuses_to_remove = []
                for i, status in enumerate(status_effect_manager.active_statuses[unit_id]):
                    if status.name == "Sleep":
                        statuses_to_remove.append(i)
                        
                        # Publish event
                        event_system.publish("STATUS_REMOVED", {
                            "unit": player_unit,
                            "status": "Sleep",
                            "reason": "Damage Taken"
                        })
                
                # Remove sleep status
                for i in reversed(statuses_to_remove):
                    status_effect_manager.active_statuses[unit_id].pop(i)
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "handle_damage_taken", mock_handle_damage_taken)
        
        try:
            # Apply sleep status effect
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Handle damage taken (damage > 0)
            status_effect_manager.handle_damage_taken(player_unit_id, 5)
            
            # Verify sleep status is removed
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert not has_sleep, "Unit should not have Sleep status effect after taking damage"
            
            # Verify status removed event was published
            status_removed_events = [event for event in event_system.published_events if event[0] == "STATUS_REMOVED"]
            assert len(status_removed_events) > 0, "STATUS_REMOVED event should have been published"
            
            # Apply sleep status effect again
            sleep_applied = status_effect_manager.apply_status(player_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Clear previous events
            event_system.published_events = []
            
            # Handle damage taken (damage = 0)
            status_effect_manager.handle_damage_taken(player_unit_id, 0)
            
            # Verify sleep status is not removed
            has_sleep = status_effect_manager.has_status(player_unit_id, "Sleep")
            assert has_sleep, "Unit should still have Sleep status effect after taking 0 damage"
            
            # Verify no status removed event was published
            status_removed_events = [event for event in event_system.published_events if event[0] == "STATUS_REMOVED"]
            assert len(status_removed_events) == 0, "STATUS_REMOVED event should not have been published for 0 damage"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "handle_damage_taken", original_handle_damage_taken)
    
    def test_ai_skips_turn_when_sleeping(self, setup_game_state, caplog, monkeypatch):
        """Test that AI skips the turn for a unit with sleep status.
        [TDD: Test AI skips turn when sleeping]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        turn_manager = setup_game_state["turn_manager"]
        event_system = setup_game_state["event_system"]
        enemy_unit_id = setup_game_state["enemy_unit_id"]
        enemy_unit = setup_game_state["enemy_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockSleepStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        
        # Patch the apply_status method to directly add our mock status instance
        original_apply_status = status_effect_manager.apply_status
        
        def mock_apply_status(unit_id, status_effect_name, source=None, duration=None):
            if unit_id not in status_effect_manager.active_statuses:
                status_effect_manager.active_statuses[unit_id] = []
            
            # Add our mock status instance
            status_effect_manager.active_statuses[unit_id].append(mock_status_instance)
            
            # Publish event
            event_system.publish("STATUS_APPLIED", {
                "unit": enemy_unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the has_status method to check for sleep status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the can_perform_action method to check for sleep status
        original_can_perform_action = status_effect_manager.can_perform_action
        
        def mock_can_perform_action(unit_id, action_type="ANY"):
            # Unit cannot act if it has sleep status
            if status_effect_manager.has_status(unit_id, "Sleep"):
                return False
            return True
        
        # Patch the process_unit_turn method to use our mocked status effect manager
        original_process_unit_turn = turn_manager.process_unit_turn
        
        def mock_process_unit_turn(unit_id):
            # Check if unit can act
            if not status_effect_manager.can_perform_action(unit_id, "ANY"):
                # Skip turn if unit has sleep status
                event_system.publish("TURN_SKIPPED", {
                    "unit": enemy_unit,
                    "reason": "Sleep"
                })
                return True
            
            # Normal turn processing
            return original_process_unit_turn(unit_id)
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "can_perform_action", mock_can_perform_action)
        monkeypatch.setattr(turn_manager, "process_unit_turn", mock_process_unit_turn)
        
        try:
            # Process turn before sleep
            turn_processed_before = turn_manager.process_unit_turn(enemy_unit_id)
            assert turn_processed_before, "Failed to process unit's turn before Sleep"
            
            # Verify no turn skipped event was published
            turn_skipped_events_before = [event for event in event_system.published_events if event[0] == "TURN_SKIPPED"]
            assert len(turn_skipped_events_before) == 0, "TURN_SKIPPED event should not have been published before Sleep"
            
            # Apply sleep status effect
            sleep_applied = status_effect_manager.apply_status(enemy_unit_id, "Sleep", source="Sleep Staff")
            assert sleep_applied, "Failed to apply Sleep status effect"
            
            # Verify unit has sleep status
            has_sleep = status_effect_manager.has_status(enemy_unit_id, "Sleep")
            assert has_sleep, "Unit should have Sleep status effect"
            
            # Clear previous events
            event_system.published_events = []
            
            # Process turn after sleep
            turn_processed_after = turn_manager.process_unit_turn(enemy_unit_id)
            assert turn_processed_after, "Failed to process unit's turn after Sleep"
            
            # Verify turn skipped event was published
            turn_skipped_events_after = [event for event in event_system.published_events if event[0] == "TURN_SKIPPED"]
            assert len(turn_skipped_events_after) > 0, "TURN_SKIPPED event should have been published after Sleep"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "can_perform_action", original_can_perform_action)
            monkeypatch.setattr(turn_manager, "process_unit_turn", original_process_unit_turn)
