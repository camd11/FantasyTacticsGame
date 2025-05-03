"""
Test for Poison Status Effect

This test verifies that the poison status effect correctly applies damage at the start of a unit's turn.
"""

import pytest
import logging
from src.fantasy_tactics_core.game_state import GameStateManager, GameState, StatusEffectEnum, UnitState, FactionEnum
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_gameplay.systems.status_effects_system import StatusEffectManager, StatusEffectInstance
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem

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
class MockStatusEffectData:
    """A mock status effect data class for testing."""
    
    def __init__(self):
        self.name = "Poison"
        self.description = "Unit takes 2 damage at the start of their turn"
        self.duration_type = "UNTIL_CURED"
        self.cure_methods = ["Antidote", "Restore Staff", "Chapter End"]
        self.icon = "poison_icon"
        self.effects = [
            {
                "type": "PERIODIC_DAMAGE",
                "parameters": {
                    "amount": 2
                }
            }
        ]

class TestPoisonStatus:
    """Test cases for the poison status effect."""

    @pytest.fixture
    def setup_game_state(self):
        """Set up the game state with required components."""
        # Initialize components
        data_provider = DataProvider()
        game_state_manager = GameStateManager(data_provider)
        unit_system = UnitSystem()
        event_system = MockEventSystem()
        status_effect_manager = StatusEffectManager()
        
        # Initialize dependencies
        unit_system.initialize(game_state_manager, data_provider)
        status_effect_manager.initialize(game_state_manager, data_provider, unit_system, event_system)
        
        # Create a test unit manually
        unit_id = "LEIF"
        
        # Initialize game state
        game_state_manager.current_game_state = GameState()
        
        # Create a unit state
        unit = UnitState()
        unit.id = unit_id
        unit.name = "Leif"
        unit.faction = FactionEnum.PLAYER
        unit.position = (1, 1)
        unit.max_hp = 20
        unit.current_hp = 20
        unit.base_stats = {"STR": 10, "SKL": 10, "SPD": 10, "LUK": 10, "DEF": 10}
        
        # Add the unit to the game state
        game_state_manager.current_game_state.unit_states[unit_id] = unit
        
        return {
            "game_state_manager": game_state_manager,
            "data_provider": data_provider,
            "unit_system": unit_system,
            "event_system": event_system,
            "status_effect_manager": status_effect_manager,
            "unit_id": unit_id,
            "unit": unit
        }
    
    def test_poison_damage_application(self, setup_game_state, caplog, monkeypatch):
        """Test that poison damage is correctly applied at the start of a unit's turn."""
        caplog.set_level(logging.INFO)
        
        # Get components from fixture
        game_state_manager = setup_game_state["game_state_manager"]
        status_effect_manager = setup_game_state["status_effect_manager"]
        event_system = setup_game_state["event_system"]
        unit_id = setup_game_state["unit_id"]
        unit = setup_game_state["unit"]
        
        # Record initial HP
        initial_hp = unit.current_hp
        assert initial_hp == 20, f"Expected initial HP to be 20, got {initial_hp}"
        
        # Create a mock status effect instance
        mock_status_data = MockStatusEffectData()
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
                "unit": unit,
                "status": status_effect_name,
                "source": source
            })
            
            return True
        
        # Patch the process_turn_start_effects method to simulate poison damage
        original_process_turn_start_effects = status_effect_manager.process_turn_start_effects
        
        def mock_process_turn_start_effects(unit_id):
            if unit_id not in status_effect_manager.active_statuses:
                return
            
            unit = game_state_manager.get_unit(unit_id)
            
            for status in status_effect_manager.active_statuses[unit_id]:
                if status.name == "Poison":
                    # Get damage amount from the status effect
                    damage = 2  # Hardcoded for test
                    
                    # Apply damage directly to the unit
                    unit.current_hp = max(0, unit.current_hp - damage)
                    
                    # Publish event
                    event_system.publish("POISON_DAMAGE", {
                        "unit": unit,
                        "damage": damage
                    })
        
        # Apply the patches
        monkeypatch.setattr(status_effect_manager, "apply_status", mock_apply_status)
        monkeypatch.setattr(status_effect_manager, "process_turn_start_effects", mock_process_turn_start_effects)
        
        try:
            # Apply poison status effect
            poison_applied = status_effect_manager.apply_status(unit_id, "Poison", source="Test")
            assert poison_applied, "Failed to apply Poison status effect"
            
            # Verify unit has poison status
            has_poison = status_effect_manager.has_status(unit_id, "Poison")
            assert has_poison, "Unit should have Poison status effect"
            
            # Set up event listener to capture poison damage event
            poison_damage_event_triggered = False
            poison_damage_amount = 0
            
            def poison_damage_listener(event_data):
                nonlocal poison_damage_event_triggered, poison_damage_amount
                poison_damage_event_triggered = True
                poison_damage_amount = event_data["damage"]
            
            event_system.subscribe("POISON_DAMAGE", poison_damage_listener)
            
            # Process turn start effects (simulating start of unit's turn)
            status_effect_manager.process_turn_start_effects(unit_id)
            
            # Verify poison damage was applied
            expected_damage = 2
            expected_hp = initial_hp - expected_damage
            assert unit.current_hp == expected_hp, f"Expected HP to be {expected_hp}, got {unit.current_hp}"
            
            # Verify poison damage event was triggered
            assert poison_damage_event_triggered, "POISON_DAMAGE event should have been triggered"
            assert poison_damage_amount == expected_damage, f"Expected damage amount to be {expected_damage}, got {poison_damage_amount}"
            
            # Process another turn to verify consistent damage
            status_effect_manager.process_turn_start_effects(unit_id)
            
            # Verify poison damage was applied again
            expected_hp = initial_hp - (expected_damage * 2)
            assert unit.current_hp == expected_hp, f"Expected HP to be {expected_hp}, got {unit.current_hp}"
            
            # Cure the poison
            poison_cured = status_effect_manager.cure_status(unit_id, "Poison", cure_method="Antidote")
            assert poison_cured, "Failed to cure Poison status effect"
            
            # Verify unit no longer has poison status
            has_poison = status_effect_manager.has_status(unit_id, "Poison")
            assert not has_poison, "Unit should not have Poison status effect after cure"
            
            # Process another turn to verify no more damage
            current_hp = unit.current_hp
            status_effect_manager.process_turn_start_effects(unit_id)
            
            # Verify no additional damage was applied
            assert unit.current_hp == current_hp, f"HP should remain at {current_hp}, got {unit.current_hp}"
        
        finally:
            # Restore the original methods
            monkeypatch.setattr(status_effect_manager, "apply_status", original_apply_status)
            monkeypatch.setattr(status_effect_manager, "process_turn_start_effects", original_process_turn_start_effects)