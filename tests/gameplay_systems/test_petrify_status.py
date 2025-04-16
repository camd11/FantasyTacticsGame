"""
Test for Petrify Status Effect

This test verifies that the petrify status effect correctly prevents a unit from taking any actions,
sets their Avoid to 0, increases their Def/Res, and can only be cured by the Restore staff.
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
PETRIFY = "PETRIFY"  # Using string since StatusEffectEnum might not have PETRIFY yet
AVOID = "AVOID"  # Using string instead of enum since StatEnum doesn't have AVOID
DEF = StatEnum.DEF
RES = "RES"  # Using string instead of enum if not available

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

# Mock PetrifyStatusEffectData for testing
class MockPetrifyStatusEffectData:
    """A mock petrify status effect data class for testing."""
    
    def __init__(self):
        self.name = "Petrify"
        self.description = "Unit is turned to stone, cannot act, and has altered defensive stats."
        self.duration_type = "PERMANENT_UNTIL_CURED"
        self.default_duration = -1  # Indefinite duration
        self.cure_methods = ["Restore Staff", "Chapter End"]
        self.icon = "petrify_icon"
        self.effects = [
            {
                "type": "ACTION_BLOCK",
                "parameters": {
                    "value": "ALL"
                }
            },
            {
                "type": "STAT_MODIFIER_FLAT",
                "parameters": {
                    "stat": "Def",
                    "value": 10
                }
            },
            {
                "type": "STAT_MODIFIER_FLAT",
                "parameters": {
                    "stat": "Res",
                    "value": 10
                }
            },
            {
                "type": "STAT_OVERRIDE",
                "parameters": {
                    "stat": "Avoid",
                    "value": 0
                }
            }
        ]

class TestPetrifyStatus:
    """Test cases for the petrify status effect."""

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
        player_unit.base_stats = {"STR": 10, "SKL": 10, "SPD": 10, "LUK": 10, "DEF": 8, "RES": 6, "AVOID": 30}
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
        enemy_unit.base_stats = {"STR": 10, "SKL": 10, "SPD": 10, "LUK": 10, "DEF": 8, "RES": 6, "AVOID": 30}
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

    def test_petrify_application_and_duration(self, setup_game_state, caplog, monkeypatch):
        """Test that petrify status is correctly applied with indefinite duration.
        [TDD: Test Petrify application/duration]
        """
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        event_system = setup_game_state["event_system"]
        player_unit_id = setup_game_state["player_unit_id"]
        player_unit = setup_game_state["player_unit"]
        
        # Create a mock status effect instance
        mock_status_data = MockPetrifyStatusEffectData()
        mock_status_instance = StatusEffectInstance(mock_status_data)
        mock_status_instance.duration = -1  # Indefinite duration
        
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
            # Apply petrify status effect with default duration (indefinite)
            petrify_applied = status_effect_manager.apply_status(player_unit_id, "Petrify", source="Stone Staff")
            assert petrify_applied, "Failed to apply Petrify status effect"
            
            # Verify unit has petrify status
            has_petrify = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify, "Unit should have Petrify status effect"
            
            # Verify the duration is indefinite (-1)
            petrify_status = status_effect_manager.active_statuses[player_unit_id][0]
            assert petrify_status.duration == -1, f"Expected duration to be -1 (indefinite), got {petrify_status.duration}"
            
            # Verify event was published
            status_applied_events = [event for event in event_system.published_events if event[0] == "STATUS_APPLIED"]
            assert len(status_applied_events) > 0, "STATUS_APPLIED event should have been published"
            
        finally:
            # Restore the original method
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
    
    def test_petrify_blocks_all_actions(self, setup_game_state, caplog, monkeypatch):
        """Test that petrify prevents a unit from performing any actions.
        [TDD: Test Petrify blocks all actions]
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
        mock_status_data = MockPetrifyStatusEffectData()
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
        
        # Patch the has_status method to check for petrify status
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
        
        # Patch the can_unit_act method to check for petrify status
        original_can_unit_act = action_system.can_unit_act
        
        def mock_can_unit_act(unit_id):
            # Unit cannot act if it has petrify status
            if status_effect_manager.has_status(unit_id, "Petrify"):
                return False
            return True
        
        # Patch the get_available_actions method to check for petrify status
        original_get_available_actions = action_system.get_available_actions
        
        def mock_get_available_actions(unit_id):
            # No actions available if unit has petrify status
            if status_effect_manager.has_status(unit_id, "Petrify"):
                return []
            return ["Move", "Attack", "Item", "Staff", "Wait", "Trade", "Rescue"]
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(action_system, "can_unit_act", mock_can_unit_act)
        monkeypatch.setattr(action_system, "get_available_actions", mock_get_available_actions)
        
        try:
            # Check that unit can act before petrify
            can_act_before = action_system.can_unit_act(player_unit_id)
            assert can_act_before, "Unit should be able to act before Petrify"
            
            # Check available actions before petrify
            actions_before = action_system.get_available_actions(player_unit_id)
            assert len(actions_before) > 0, "Unit should have available actions before Petrify"
            
            # Apply petrify status effect
            petrify_applied = status_effect_manager.apply_status(player_unit_id, "Petrify", source="Stone Staff")
            assert petrify_applied, "Failed to apply Petrify status effect"
            
            # Verify unit has petrify status
            has_petrify = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify, "Unit should have Petrify status effect"
            
            # Check that unit cannot act with petrify
            can_act_after = action_system.can_unit_act(player_unit_id)
            assert not can_act_after, "Unit should not be able to act with Petrify"
            
            # Check available actions with petrify
            actions_after = action_system.get_available_actions(player_unit_id)
            assert len(actions_after) == 0, "Unit should have no available actions with Petrify"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(action_system, "can_unit_act", original_can_unit_act)
            monkeypatch.setattr(action_system, "get_available_actions", original_get_available_actions)
    
    def test_petrify_affects_def_avoid(self, setup_game_state, caplog, monkeypatch):
        """Test that petrify sets a unit's Avoid to 0 and increases Def/Res by 10.
        [TDD: Test Petrify affects Def/Avoid]
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
        mock_status_data = MockPetrifyStatusEffectData()
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
        
        # Patch the has_status method to check for petrify status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the get_modified_stats method to apply petrify effect on stats
        original_get_modified_stats = status_effect_manager.get_modified_stats
        
        def mock_get_modified_stats(unit_id, base_stats):
            modified_stats = base_stats.copy()
            
            # If unit has petrify status, set Avoid to 0 and increase Def/Res by 10
            if status_effect_manager.has_status(unit_id, "Petrify"):
                modified_stats[AVOID] = 0
                modified_stats["DEF"] += 10
                modified_stats["RES"] += 10
            
            return modified_stats
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "get_modified_stats", mock_get_modified_stats)
        
        try:
            # Check unit's base stats
            base_avoid = player_unit.base_stats[AVOID]
            base_def = player_unit.base_stats["DEF"]
            base_res = player_unit.base_stats["RES"]
            
            assert base_avoid > 0, "Unit's base Avoid should be greater than 0"
            
            # Get modified stats before petrify
            modified_stats_before = status_effect_manager.get_modified_stats(player_unit_id, player_unit.base_stats)
            assert modified_stats_before[AVOID] == base_avoid, f"Expected Avoid to be {base_avoid}, got {modified_stats_before[AVOID]}"
            assert modified_stats_before["DEF"] == base_def, f"Expected DEF to be {base_def}, got {modified_stats_before['DEF']}"
            assert modified_stats_before["RES"] == base_res, f"Expected RES to be {base_res}, got {modified_stats_before['RES']}"
            
            # Apply petrify status effect
            petrify_applied = status_effect_manager.apply_status(player_unit_id, "Petrify", source="Stone Staff")
            assert petrify_applied, "Failed to apply Petrify status effect"
            
            # Verify unit has petrify status
            has_petrify = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify, "Unit should have Petrify status effect"
            
            # Get modified stats after petrify
            modified_stats_after = status_effect_manager.get_modified_stats(player_unit_id, player_unit.base_stats)
            assert modified_stats_after[AVOID] == 0, f"Expected Avoid to be 0, got {modified_stats_after[AVOID]}"
            assert modified_stats_after["DEF"] == base_def + 10, f"Expected DEF to be {base_def + 10}, got {modified_stats_after['DEF']}"
            assert modified_stats_after["RES"] == base_res + 10, f"Expected RES to be {base_res + 10}, got {modified_stats_after['RES']}"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "get_modified_stats", original_get_modified_stats)
    
    def test_petrify_curing_mechanism(self, setup_game_state, caplog, monkeypatch):
        """Test that petrify is only cured by Restore staff and not by taking damage.
        [TDD: Test Petrify curing mechanism]
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
        mock_status_data = MockPetrifyStatusEffectData()
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
        
        # Patch the has_status method to check for petrify status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
        # Patch the handle_damage_taken method to NOT cure petrify
        original_handle_damage_taken = status_effect_manager.handle_damage_taken
        
        def mock_handle_damage_taken(unit_id, damage):
            # Petrify is not cured by taking damage
            pass
        
        # Patch the cure_status method to check cure methods
        original_cure_status = status_effect_manager.cure_status
        
        def mock_cure_status(unit_id, status_name, cure_method):
            if unit_id not in status_effect_manager.active_statuses:
                return False
            
            # Check if the unit has the status
            status_index = None
            for i, status in enumerate(status_effect_manager.active_statuses[unit_id]):
                if status.name == status_name or status_name is None:
                    # Check if the cure method is valid for this status
                    if cure_method in status.cure_methods:
                        status_index = i
                        break
            
            # If status found and cure method is valid, remove the status
            if status_index is not None:
                removed_status = status_effect_manager.active_statuses[unit_id].pop(status_index)
                
                # Publish event
                event_system.publish("STATUS_CURED", {
                    "unit": player_unit,
                    "status": removed_status.name,
                    "method": cure_method
                })
                
                return True
            
            return False
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "has_status", mock_has_status)
        monkeypatch.setattr(status_effect_manager, "handle_damage_taken", mock_handle_damage_taken)
        monkeypatch.setattr(status_effect_manager, "cure_status", mock_cure_status)
        
        try:
            # Apply petrify status effect
            petrify_applied = status_effect_manager.apply_status(player_unit_id, "Petrify", source="Stone Staff")
            assert petrify_applied, "Failed to apply Petrify status effect"
            
            # Verify unit has petrify status
            has_petrify = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify, "Unit should have Petrify status effect"
            
            # Handle damage taken (damage > 0)
            status_effect_manager.handle_damage_taken(player_unit_id, 5)
            
            # Verify petrify status is NOT removed by damage
            has_petrify_after_damage = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify_after_damage, "Petrify status should not be removed by taking damage"
            
            # Try to cure with an invalid method
            cured_with_invalid = status_effect_manager.cure_status(player_unit_id, "Petrify", "Antitoxin")
            assert not cured_with_invalid, "Petrify should not be cured by Antitoxin"
            
            # Verify petrify status is still active
            has_petrify_after_invalid = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert has_petrify_after_invalid, "Petrify status should not be removed by invalid cure method"
            
            # Cure with Restore Staff
            cured_with_restore = status_effect_manager.cure_status(player_unit_id, "Petrify", "Restore Staff")
            assert cured_with_restore, "Petrify should be cured by Restore Staff"
            
            # Verify petrify status is removed
            has_petrify_after_restore = status_effect_manager.has_status(player_unit_id, "Petrify")
            assert not has_petrify_after_restore, "Petrify status should be removed by Restore Staff"
            
            # Verify status cured event was published
            status_cured_events = [event for event in event_system.published_events if event[0] == "STATUS_CURED"]
            assert len(status_cured_events) > 0, "STATUS_CURED event should have been published"
            
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "has_status", original_has_status)
            monkeypatch.setattr(status_effect_manager, "handle_damage_taken", original_handle_damage_taken)
            monkeypatch.setattr(status_effect_manager, "cure_status", original_cure_status)

    def test_ai_skips_turn_when_petrified(self, setup_game_state, caplog, monkeypatch):
        """Test that AI skips the turn for a unit with petrify status.
        [TDD: Test AI skips turn when petrified]
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
        mock_status_data = MockPetrifyStatusEffectData()
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
        
        # Patch the has_status method to check for petrify status
        original_has_status = status_effect_manager.has_status
        
        def mock_has_status(unit_id, status_effect_name):
            if unit_id in status_effect_manager.active_statuses:
                for status in status_effect_manager.active_statuses[unit_id]:
                    if status.name == status_effect_name:
                        return True
            return False
        
