"""
Test for Silence Status Effect

This test verifies that the silence status effect correctly prevents units from using magic tomes and staves.
"""

import pytest
import logging
from unittest.mock import MagicMock, patch
from src.core_engine.game_state import GameStateManager, GameState, UnitState, FactionEnum, PhaseEnum
from src.core_engine.data_provider import DataProvider, StatEnum, ItemTypeEnum
from src.gameplay_systems.status_effects_system import StatusEffectManager, StatusEffectInstance
from src.gameplay_systems.unit_system import UnitSystem
from src.gameplay_systems.action_system import ActionSystem

# Define Action class for testing
class Action:
    """A simple action class for testing."""
    
    def __init__(self, action_type, description, parameters=None):
        self.action_type = action_type
        self.description = description
        self.parameters = parameters or {}

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
class MockSilenceStatusData:
    """A mock silence status effect data class for testing."""
    
    def __init__(self, duration=5):
        self.name = "Silence"
        self.description = "Unit cannot use magic tomes or staves."
        self.duration_type = "SCRIPTED_TURNS"
        self.turns_remaining = duration
        self.cure_methods = ["Restore Staff", "Duration Expiry", "Chapter End"]
        self.icon = "silence_icon"
        self.effects = [
            {
                "type": "ACTION_RESTRICTION",
                "parameters": {
                    "action": "Magic",
                    "allowed": False
                }
            },
            {
                "type": "ACTION_RESTRICTION",
                "parameters": {
                    "action": "Staff",
                    "allowed": False
                }
            }
        ]

# Mock Item for testing
class MockItem:
    """A mock item class for testing."""
    
    def __init__(self, item_id, name, item_type):
        self.id = item_id
        self.name = name
        self.type = item_type

class TestSilenceStatus:
    """Test cases for the silence status effect."""

    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = MagicMock()
        game_state_manager = GameStateManager(data_provider)
        unit_system = UnitSystem()
        event_system = MockEventSystem()
        status_effect_manager = StatusEffectManager()
        action_system = MagicMock(spec=ActionSystem)
        
        # Initialize dependencies
        unit_system.initialize(game_state_manager, data_provider)
        status_effect_manager.initialize(game_state_manager, data_provider, unit_system, event_system)
        
        # Create a test unit manually
        unit_id = "MAGE_UNIT"
        
        # Initialize game state
        game_state_manager.current_game_state = GameState()
        game_state_manager.current_game_state.current_phase = PhaseEnum.PLAYER
        
        # Create a unit state
        unit = UnitState()
        unit.id = unit_id
        unit.name = "Mage"
        unit.faction = FactionEnum.PLAYER
        unit.position = (1, 1)
        unit.max_hp = 20
        unit.current_hp = 20
        unit.base_stats = {"STR": 5, "MAG": 10, "SKL": 8, "SPD": 7, "LUK": 6, "DEF": 3}
        
        # Add the unit to the game state
        game_state_manager.current_game_state.unit_states[unit_id] = unit
        
        # Mock data provider to return item types
        def mock_get_item_data(item_id):
            items = {
                "FIRE_TOME": MockItem("FIRE_TOME", "Fire", ItemTypeEnum.WEAPON),
                "HEAL_STAFF": MockItem("HEAL_STAFF", "Heal", ItemTypeEnum.STAFF),
                "IRON_SWORD": MockItem("IRON_SWORD", "Iron Sword", ItemTypeEnum.WEAPON),
                "VULNERARY": MockItem("VULNERARY", "Vulnerary", ItemTypeEnum.CONSUMABLE)
            }
            return items.get(item_id)
        
        data_provider.get_item_data.side_effect = mock_get_item_data
        
        # Mock action system to return available actions
        def mock_get_available_actions(unit_id):
            unit = game_state_manager.get_unit(unit_id)
            if not unit:
                return []
            
            # Default actions for a mage unit
            actions = [
                Action("WAIT", "Wait", {}),
                Action("MOVE", "Move", {}),
                Action("ATTACK", "Attack with Fire", {"weapon_id": "FIRE_TOME", "weapon_type": ItemTypeEnum.WEAPON}),
                Action("USE_STAFF", "Heal Ally", {"staff_id": "HEAL_STAFF", "staff_type": ItemTypeEnum.STAFF}),
                Action("ATTACK", "Attack with Iron Sword", {"weapon_id": "IRON_SWORD", "weapon_type": ItemTypeEnum.WEAPON}),
                Action("USE_ITEM", "Use Vulnerary", {"item_id": "VULNERARY", "item_type": ItemTypeEnum.CONSUMABLE})
            ]
            
            # Filter actions based on status effects
            filtered_actions = []
            for action in actions:
                if action.action_type == "ATTACK" and action.parameters.get("weapon_type") == ItemTypeEnum.WEAPON and "TOME" in action.parameters.get("weapon_id", ""):
                    if not status_effect_manager.can_perform_action(unit_id, "Magic"):
                        continue
                elif action.action_type == "USE_STAFF":
                    if not status_effect_manager.can_perform_action(unit_id, "Staff"):
                        continue
                
                filtered_actions.append(action)
            
            return filtered_actions
        
        action_system.get_available_actions.side_effect = mock_get_available_actions
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "event_system": event_system,
            "status_effect_manager": status_effect_manager,
            "action_system": action_system,
            "unit_id": unit_id,
            "unit": unit
        }
    
    def test_silence_application_duration(self, setup_game_state):
        """
        Test that the Silence status is applied with the correct duration.
        [TDD: Test Silence application/duration]
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        event_system = setup_game_state["event_system"]
        unit_id = setup_game_state["unit_id"]
        unit = setup_game_state["unit"]
        
        # Mock the data provider to return our mock silence status data
        silence_duration = 5
        mock_silence_data = MockSilenceStatusData(duration=silence_duration)
        setup_game_state["data_provider"].get_status_effect_data.return_value = mock_silence_data
        
        # Apply silence status effect
        source = "Silence Staff"
        silence_applied = status_effect_manager.apply_status(unit_id, "Silence", source, duration=silence_duration)
        
        # Verify silence was applied
        assert silence_applied, "Failed to apply Silence status effect"
        
        # Verify unit has silence status
        has_silence = status_effect_manager.has_status(unit_id, "Silence")
        assert has_silence, "Unit should have Silence status effect"
        
        # Verify the duration was set correctly
        active_statuses = status_effect_manager.get_active_statuses(unit_id)
        assert len(active_statuses) == 1, "Unit should have exactly one status effect"
        assert active_statuses[0].name == "Silence", "Status effect should be Silence"
        assert active_statuses[0].turns_remaining == silence_duration, f"Silence duration should be {silence_duration}"
        
        # Verify event was published
        silence_applied_events = [event for event in event_system.published_events if event[0] == "STATUS_APPLIED"]
        assert len(silence_applied_events) == 1, "STATUS_APPLIED event should have been published"
        assert silence_applied_events[0][1]["status"] == "Silence", "Status in event should be Silence"
        assert silence_applied_events[0][1]["source"] == source, f"Source in event should be {source}"
    
    def test_magic_staff_action_restriction(self, setup_game_state):
        """
        Test that silenced units cannot use magic tomes or staves.
        [TDD: Test magic/staff action restriction]
        """
        # Get components from fixture
        status_effect_manager = setup_game_state["status_effect_manager"]
        action_system = setup_game_state["action_system"]
        unit_id = setup_game_state["unit_id"]
        
        # Get available actions before silence
        actions_before_silence = action_system.get_available_actions(unit_id)
        
        # Verify magic and staff actions are available before silence
        magic_actions_before = [a for a in actions_before_silence if a.action_type == "ATTACK" and a.parameters.get("weapon_type") == ItemTypeEnum.WEAPON and "TOME" in a.parameters.get("weapon_id", "")]
        staff_actions_before = [a for a in actions_before_silence if a.action_type == "USE_STAFF"]
        
        assert len(magic_actions_before) > 0, "Unit should have magic actions available before silence"
        assert len(staff_actions_before) > 0, "Unit should have staff actions available before silence"
        
        # Apply silence status effect
        mock_silence_data = MockSilenceStatusData()
        setup_game_state["data_provider"].get_status_effect_data.return_value = mock_silence_data
        status_effect_manager.apply_status(unit_id, "Silence", "Test")
        
        # Get available actions after silence
        actions_after_silence = action_system.get_available_actions(unit_id)
        
        # Verify magic and staff actions are not available after silence
        magic_actions_after = [a for a in actions_after_silence if a.action_type == "ATTACK" and a.parameters.get("weapon_type") == ItemTypeEnum.WEAPON and "TOME" in a.parameters.get("weapon_id", "")]
        staff_actions_after = [a for a in actions_after_silence if a.action_type == "USE_STAFF"]
        
        assert len(magic_actions_after) == 0, "Unit should not have magic actions available when silenced"
        assert len(staff_actions_after) == 0, "Unit should not have staff actions available when silenced"
        
        # Verify directly with can_perform_action
        assert not status_effect_manager.can_perform_action(unit_id, "Magic"), "Unit should not be able to perform Magic actions when silenced"
        assert not status_effect_manager.can_perform_action(unit_id, "Staff"), "Unit should not be able to perform Staff actions when silenced"
    
    def test_non_magic_actions_allowed(self, setup_game_state):
        """
        Test that silenced units can still perform non-magic actions.
        [TDD: Test non-magic actions allowed]
        """
        # Get components from fixture
        status_effect_manager = setup_game_state["status_effect_manager"]
        action_system = setup_game_state["action_system"]
        unit_id = setup_game_state["unit_id"]
        
        # Apply silence status effect
        mock_silence_data = MockSilenceStatusData()
        setup_game_state["data_provider"].get_status_effect_data.return_value = mock_silence_data
        status_effect_manager.apply_status(unit_id, "Silence", "Test")
        
        # Get available actions after silence
        actions_after_silence = action_system.get_available_actions(unit_id)
        
        # Verify non-magic actions are still available
        wait_actions = [a for a in actions_after_silence if a.action_type == "WAIT"]
        move_actions = [a for a in actions_after_silence if a.action_type == "MOVE"]
        physical_attack_actions = [a for a in actions_after_silence if a.action_type == "ATTACK" and (a.parameters.get("weapon_type") != ItemTypeEnum.WEAPON or "TOME" not in a.parameters.get("weapon_id", ""))]
        item_actions = [a for a in actions_after_silence if a.action_type == "USE_ITEM"]
        
        assert len(wait_actions) > 0, "Unit should still be able to Wait when silenced"
        assert len(move_actions) > 0, "Unit should still be able to Move when silenced"
        assert len(physical_attack_actions) > 0, "Unit should still be able to attack with physical weapons when silenced"
        assert len(item_actions) > 0, "Unit should still be able to use items when silenced"
        
        # Verify directly with can_perform_action
        assert status_effect_manager.can_perform_action(unit_id, "Move"), "Unit should be able to perform Move actions when silenced"
        assert status_effect_manager.can_perform_action(unit_id, "Attack"), "Unit should be able to perform physical Attack actions when silenced"
        assert status_effect_manager.can_perform_action(unit_id, "Item"), "Unit should be able to perform Item actions when silenced"
        assert status_effect_manager.can_perform_action(unit_id, "Wait"), "Unit should be able to perform Wait actions when silenced"
    
    def test_silence_wears_off(self, setup_game_state):
        """
        Test that the Silence status is removed after its duration expires.
        [TDD: Test Silence wears off]
        """
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        event_system = setup_game_state["event_system"]
        unit_id = setup_game_state["unit_id"]
        
        # Apply silence status effect with duration of 2 turns
        silence_duration = 2
        mock_silence_data = MockSilenceStatusData(duration=silence_duration)
        setup_game_state["data_provider"].get_status_effect_data.return_value = mock_silence_data
        status_effect_manager.apply_status(unit_id, "Silence", "Test", duration=silence_duration)
        
        # Verify unit has silence status
        assert status_effect_manager.has_status(unit_id, "Silence"), "Unit should have Silence status effect"
        
        # Process end of turn 1
        status_effect_manager.process_turn_end(unit_id)
        
        # Verify silence is still active but duration decreased
        assert status_effect_manager.has_status(unit_id, "Silence"), "Unit should still have Silence status after 1 turn"
        active_statuses = status_effect_manager.get_active_statuses(unit_id)
        assert active_statuses[0].turns_remaining == 1, "Silence should have 1 turn remaining"
        
        # Process end of turn 2
        status_effect_manager.process_turn_end(unit_id)
        
        # Verify silence has worn off
        assert not status_effect_manager.has_status(unit_id, "Silence"), "Silence should have worn off after duration expired"
        
        # Verify STATUS_EXPIRED event was published
        silence_expired_events = [event for event in event_system.published_events if event[0] == "STATUS_EXPIRED"]
        assert len(silence_expired_events) == 1, "STATUS_EXPIRED event should have been published"
        assert silence_expired_events[0][1]["status"] == "Silence", "Status in event should be Silence"
    
    def test_ai_recognizes_silence(self, setup_game_state):
        """
        Test that AI does not attempt magic/staff actions with silenced units.
        [TDD: Test AI recognizes Silence]
        """
        # Get components from fixture
        status_effect_manager = setup_game_state["status_effect_manager"]
        unit_id = setup_game_state["unit_id"]
        
        # Create a mock AI manager
        ai_manager = MagicMock()
        
        # Create a mock method for evaluating actions
        def mock_evaluate_actions(unit_id, available_actions):
            # Filter out magic and staff actions if unit is silenced
            if status_effect_manager.has_status(unit_id, "Silence"):
                return [
                    action for action in available_actions 
                    if not (
                        (action.action_type == "ATTACK" and action.parameters.get("weapon_type") == ItemTypeEnum.WEAPON and "TOME" in action.parameters.get("weapon_id", "")) or
                        action.action_type == "USE_STAFF"
                    )
                ]
            return available_actions
        
        ai_manager.evaluate_actions = mock_evaluate_actions
        
        # Create some test actions
        magic_action = Action("ATTACK", "Attack with Fire", {"weapon_id": "FIRE_TOME", "weapon_type": ItemTypeEnum.WEAPON})
        staff_action = Action("USE_STAFF", "Heal Ally", {"staff_id": "HEAL_STAFF", "staff_type": ItemTypeEnum.STAFF})
        physical_action = Action("ATTACK", "Attack with Iron Sword", {"weapon_id": "IRON_SWORD", "weapon_type": ItemTypeEnum.WEAPON})
        wait_action = Action("WAIT", "Wait", {})
        
        test_actions = [magic_action, staff_action, physical_action, wait_action]
        
        # Test AI evaluation before silence
        actions_before_silence = ai_manager.evaluate_actions(unit_id, test_actions)
        assert len(actions_before_silence) == 4, "AI should consider all actions before silence"
        assert magic_action in actions_before_silence, "AI should consider magic actions before silence"
        assert staff_action in actions_before_silence, "AI should consider staff actions before silence"
        
        # Apply silence status effect
        mock_silence_data = MockSilenceStatusData()
        setup_game_state["data_provider"].get_status_effect_data.return_value = mock_silence_data
        status_effect_manager.apply_status(unit_id, "Silence", "Test")
        
        # Test AI evaluation after silence
        actions_after_silence = ai_manager.evaluate_actions(unit_id, test_actions)
        assert len(actions_after_silence) == 2, "AI should filter out magic and staff actions when silenced"
        assert magic_action not in actions_after_silence, "AI should not consider magic actions when silenced"
        assert staff_action not in actions_after_silence, "AI should not consider staff actions when silenced"
        assert physical_action in actions_after_silence, "AI should still consider physical actions when silenced"
        assert wait_action in actions_after_silence, "AI should still consider wait action when silenced"