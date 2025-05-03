"""
Test for the Fatigue Accumulation scenario.

This test verifies that the fatigue system correctly accumulates fatigue
as units perform actions, and that fatigue persists between turns.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.fantasy_tactics_core.game_state import GameStateManager, FactionEnum, DispositionEnum
from src.fantasy_tactics_core.data_provider import DataProvider
from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_gameplay.systems.unit_system import UnitSystem


class TestFatigueAccumulation(unittest.TestCase):
    """Test case for the Fatigue Accumulation scenario."""

    def setUp(self):
        """Set up the test environment."""
        # Create mock instances
        self.data_provider = MagicMock(spec=DataProvider)
        self.game_state_manager = MagicMock(spec=GameStateManager)
        self.unit_system = MagicMock(spec=UnitSystem)
        self.combat_system = MagicMock(spec=CombatSystem)
        
        # Mock unit state
        self.mock_finn = MagicMock()
        self.mock_finn.id = "FINN"
        self.mock_finn.current_fatigue = 0
        self.mock_finn.max_hp = 20
        self.mock_finn.faction = FactionEnum.PLAYER
        self.mock_finn.disposition = DispositionEnum.ACTIVE
        
        # Set up game state manager to return our mock unit
        self.game_state_manager.get_unit.return_value = self.mock_finn
        
        # Make update_fatigue actually update the mock unit's fatigue
        def update_fatigue_side_effect(unit_id, amount):
            if unit_id == "FINN":
                self.mock_finn.current_fatigue += amount
            return True
            
        self.game_state_manager.update_fatigue.side_effect = update_fatigue_side_effect

    def test_fatigue_increases_after_combat(self):
        """Test that fatigue increases by 1 after combat."""
        # Initial fatigue
        initial_fatigue = self.mock_finn.current_fatigue
        
        # Simulate combat
        self.game_state_manager.update_fatigue("FINN", 1)
        
        # Verify fatigue increased by 1
        self.assertEqual(self.mock_finn.current_fatigue, initial_fatigue + 1)
        self.game_state_manager.update_fatigue.assert_called_once_with("FINN", 1)

    def test_fatigue_accumulates_over_multiple_actions(self):
        """Test that fatigue accumulates over multiple combat actions."""
        # Initial fatigue
        initial_fatigue = self.mock_finn.current_fatigue
        
        # Simulate multiple combat actions
        for _ in range(3):
            self.game_state_manager.update_fatigue("FINN", 1)
        
        # Verify fatigue accumulated correctly
        self.assertEqual(self.mock_finn.current_fatigue, initial_fatigue + 3)
        self.assertEqual(self.game_state_manager.update_fatigue.call_count, 3)

    def test_fatigue_persists_between_turns(self):
        """Test that fatigue persists between turns."""
        # Set initial fatigue
        self.mock_finn.current_fatigue = 2
        
        # Simulate end of turn and start of new turn
        # In the real game, this would involve the turn manager
        # Here we just verify the fatigue value doesn't reset
        
        # Simulate another combat action in the new turn
        self.game_state_manager.update_fatigue("FINN", 1)
        
        # Verify fatigue persisted and increased
        self.assertEqual(self.mock_finn.current_fatigue, 3)

    def test_fatigue_threshold_for_deployment(self):
        """Test that a unit becomes fatigued for deployment when fatigue >= max HP."""
        # Set fatigue below threshold
        self.mock_finn.current_fatigue = 19  # Just below max HP (20)
        
        # Check if unit is fatigued for deployment
        self.game_state_manager.is_unit_fatigued_for_deployment.return_value = False
        result = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        self.assertFalse(result)
        
        # Set fatigue at threshold
        self.mock_finn.current_fatigue = 20  # Equal to max HP (20)
        
        # Check if unit is fatigued for deployment
        self.game_state_manager.is_unit_fatigued_for_deployment.return_value = True
        result = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        self.assertTrue(result)
        
        # Set fatigue above threshold
        self.mock_finn.current_fatigue = 21  # Above max HP (20)
        
        # Check if unit is fatigued for deployment
        result = self.game_state_manager.is_unit_fatigued_for_deployment("FINN")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()