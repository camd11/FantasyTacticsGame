import unittest
from unittest.mock import MagicMock, patch, call
import logging

# Import the actual Enum and EngineCore
from src.core_engine.game_state import PhaseEnum, FactionEnum, StatusEffectEnum
from src.core_engine.turn_manager import TurnPhase
from src.core_engine.engine import EngineCore

class TestEnginePhaseConversion(unittest.TestCase):
    """
    Tests for the EngineCore class focusing on phase conversion and faction processing.
    These tests verify that the TurnPhase to PhaseEnum conversion works correctly and
    that the correct faction units are processed during each phase.
    """

    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gs_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_turn_manager = MagicMock(name="TurnManager")
        self.mock_action_handler = MagicMock(name="ActionHandler")
        self.mock_event_handler = MagicMock(name="EventHandler")
        self.mock_ai_manager = MagicMock(name="AIManager")
        self.mock_combat_system = MagicMock(name="CombatSystem")
        self.mock_map_system = MagicMock(name="MapSystem")
        self.mock_movement_system = MagicMock(name="MovementSystem")
        self.mock_input_handler = MagicMock(name="InputHandler")
        self.mock_unit_system = MagicMock(name="UnitSystem")

        # Instantiate the EngineCore with mocks
        self.engine = EngineCore(
            game_state_manager=self.mock_gs_manager,
            data_provider=self.mock_data_provider,
            turn_manager=self.mock_turn_manager,
            action_handler=self.mock_action_handler,
            event_handler=self.mock_event_handler,
            ai_manager=self.mock_ai_manager,
            combat_system=self.mock_combat_system,
            map_system=self.mock_map_system,
            movement_system=self.mock_movement_system,
            unit_system=self.mock_unit_system,
            input_handler=self.mock_input_handler
        )
        
        # Mock helper methods called by the methods under test
        self.engine._apply_start_of_phase_unit_effects = MagicMock(name="_apply_start_of_phase_unit_effects")
        self.engine.check_game_end_conditions = MagicMock(name="check_game_end_conditions")

    def test_player_phase_processes_only_player_units(self):
        """
        Test that during PLAYER_PHASE, only player units are processed.
        This verifies that TurnPhase.PLAYER_PHASE is correctly converted to PhaseEnum.PLAYER
        and that the correct faction units are retrieved.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = TurnPhase.PLAYER_PHASE
        self.mock_turn_manager._convert_to_phase_enum = MagicMock(return_value=PhaseEnum.PLAYER)
        
        # Create mock units for different factions
        player_unit1 = MagicMock(name="PlayerUnit1", id="P1", faction=FactionEnum.PLAYER, has_acted=True, has_moved=True)
        player_unit2 = MagicMock(name="PlayerUnit2", id="P2", faction=FactionEnum.PLAYER, has_acted=True, has_moved=True)
        enemy_unit = MagicMock(name="EnemyUnit", id="E1", faction=FactionEnum.ENEMY, has_acted=False, has_moved=False)
        npc_unit = MagicMock(name="NPCUnit", id="N1", faction=FactionEnum.NPC, has_acted=False, has_moved=False)
        
        # Configure mock behavior
        self.mock_gs_manager.get_units_by_faction.return_value = [player_unit1, player_unit2]
        self.mock_gs_manager.is_unit_fatigued_for_deployment.return_value = False
        
        # Call the method under test
        self.engine.start_phase()
        
        # Assertions
        self.mock_turn_manager._convert_to_phase_enum.assert_called_once_with(TurnPhase.PLAYER_PHASE)
        self.mock_gs_manager.get_units_by_faction.assert_called_once_with(FactionEnum.PLAYER)
        
        # Verify that only player units had their action states reset
        self.assertFalse(player_unit1.has_acted)
        self.assertFalse(player_unit1.has_moved)
        self.assertFalse(player_unit2.has_acted)
        self.assertFalse(player_unit2.has_moved)
        
        # Verify that enemy and NPC units were not processed (their action states remain unchanged)
        self.assertEqual(enemy_unit.has_acted, False)
        self.assertEqual(enemy_unit.has_moved, False)
        self.assertEqual(npc_unit.has_acted, False)
        self.assertEqual(npc_unit.has_moved, False)
        
        # Verify that start-of-phase effects were applied to player units
        self.engine._apply_start_of_phase_unit_effects.assert_has_calls([
            call(player_unit1),
            call(player_unit2)
        ], any_order=True)
        self.assertEqual(self.engine._apply_start_of_phase_unit_effects.call_count, 2)

    def test_enemy_phase_processes_only_enemy_units(self):
        """
        Test that during ENEMY_PHASE, only enemy units are processed.
        This verifies that TurnPhase.ENEMY_PHASE is correctly converted to PhaseEnum.ENEMY
        and that the correct faction units are retrieved.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = TurnPhase.ENEMY_PHASE
        self.mock_turn_manager._convert_to_phase_enum = MagicMock(return_value=PhaseEnum.ENEMY)
        
        # Create mock units for different factions
        player_unit = MagicMock(name="PlayerUnit", id="P1", faction=FactionEnum.PLAYER, has_acted=False, has_moved=False)
        enemy_unit1 = MagicMock(name="EnemyUnit1", id="E1", faction=FactionEnum.ENEMY, has_acted=True, has_moved=True)
        enemy_unit2 = MagicMock(name="EnemyUnit2", id="E2", faction=FactionEnum.ENEMY, has_acted=True, has_moved=True)
        npc_unit = MagicMock(name="NPCUnit", id="N1", faction=FactionEnum.NPC, has_acted=False, has_moved=False)
        
        # Configure mock behavior
        self.mock_gs_manager.get_units_by_faction.return_value = [enemy_unit1, enemy_unit2]
        self.mock_gs_manager.is_unit_fatigued_for_deployment.return_value = False
        
        # Call the method under test
        self.engine.start_phase()
        
        # Assertions
        self.mock_turn_manager._convert_to_phase_enum.assert_called_once_with(TurnPhase.ENEMY_PHASE)
        self.mock_gs_manager.get_units_by_faction.assert_called_once_with(FactionEnum.ENEMY)
        
        # Verify that only enemy units had their action states reset
        self.assertFalse(enemy_unit1.has_acted)
        self.assertFalse(enemy_unit1.has_moved)
        self.assertFalse(enemy_unit2.has_acted)
        self.assertFalse(enemy_unit2.has_moved)
        
        # Verify that player and NPC units were not processed (their action states remain unchanged)
        self.assertEqual(player_unit.has_acted, False)
        self.assertEqual(player_unit.has_moved, False)
        self.assertEqual(npc_unit.has_acted, False)
        self.assertEqual(npc_unit.has_moved, False)
        
        # Verify that start-of-phase effects were applied to enemy units
        self.engine._apply_start_of_phase_unit_effects.assert_has_calls([
            call(enemy_unit1),
            call(enemy_unit2)
        ], any_order=True)
        self.assertEqual(self.engine._apply_start_of_phase_unit_effects.call_count, 2)

    def test_npc_phase_processes_only_npc_units(self):
        """
        Test that during NPC_PHASE, only NPC units are processed.
        This verifies that TurnPhase.NPC_PHASE is correctly converted to PhaseEnum.NPC
        and that the correct faction units are retrieved.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = TurnPhase.NPC_PHASE
        self.mock_turn_manager._convert_to_phase_enum = MagicMock(return_value=PhaseEnum.NPC)
        
        # Create mock units for different factions
        player_unit = MagicMock(name="PlayerUnit", id="P1", faction=FactionEnum.PLAYER, has_acted=False, has_moved=False)
        enemy_unit = MagicMock(name="EnemyUnit", id="E1", faction=FactionEnum.ENEMY, has_acted=False, has_moved=False)
        npc_unit1 = MagicMock(name="NPCUnit1", id="N1", faction=FactionEnum.NPC, has_acted=True, has_moved=True)
        npc_unit2 = MagicMock(name="NPCUnit2", id="N2", faction=FactionEnum.NPC, has_acted=True, has_moved=True)
        
        # Configure mock behavior
        self.mock_gs_manager.get_units_by_faction.return_value = [npc_unit1, npc_unit2]
        self.mock_gs_manager.is_unit_fatigued_for_deployment.return_value = False
        
        # Call the method under test
        self.engine.start_phase()
        
        # Assertions
        self.mock_turn_manager._convert_to_phase_enum.assert_called_once_with(TurnPhase.NPC_PHASE)
        self.mock_gs_manager.get_units_by_faction.assert_called_once_with(FactionEnum.NPC)
        
        # Verify that only NPC units had their action states reset
        self.assertFalse(npc_unit1.has_acted)
        self.assertFalse(npc_unit1.has_moved)
        self.assertFalse(npc_unit2.has_acted)
        self.assertFalse(npc_unit2.has_moved)
        
        # Verify that player and enemy units were not processed (their action states remain unchanged)
        self.assertEqual(player_unit.has_acted, False)
        self.assertEqual(player_unit.has_moved, False)
        self.assertEqual(enemy_unit.has_acted, False)
        self.assertEqual(enemy_unit.has_moved, False)
        
        # Verify that start-of-phase effects were applied to NPC units
        self.engine._apply_start_of_phase_unit_effects.assert_has_calls([
            call(npc_unit1),
            call(npc_unit2)
        ], any_order=True)
        self.assertEqual(self.engine._apply_start_of_phase_unit_effects.call_count, 2)

    def test_no_unknown_phase_warning_during_normal_transitions(self):
        """
        Test that the "Unknown phase" warning is not triggered during normal phase transitions.
        This verifies that the phase conversion is working correctly.
        """
        # Setup - capture log messages
        with patch('logging.warning') as mock_warning:
            # Test all three normal phases
            for turn_phase, phase_enum, faction_enum in [
                (TurnPhase.PLAYER_PHASE, PhaseEnum.PLAYER, FactionEnum.PLAYER),
                (TurnPhase.ENEMY_PHASE, PhaseEnum.ENEMY, FactionEnum.ENEMY),
                (TurnPhase.NPC_PHASE, PhaseEnum.NPC, FactionEnum.NPC)
            ]:
                # Reset mocks
                mock_warning.reset_mock()
                self.mock_turn_manager.get_current_phase.return_value = turn_phase
                self.mock_turn_manager._convert_to_phase_enum = MagicMock(return_value=phase_enum)
                self.mock_gs_manager.get_units_by_faction.return_value = []
                
                # Call the method under test
                self.engine.start_phase()
                
                # Verify that the warning was not called with "Unknown phase"
                for call_args in mock_warning.call_args_list:
                    args, _ = call_args
                    self.assertFalse(
                        any("Unknown phase" in str(arg) for arg in args),
                        f"'Unknown phase' warning was triggered for {turn_phase.name}"
                    )

    def test_get_faction_for_phase_correctly_identifies_active_faction(self):
        """
        Test that _get_faction_for_phase correctly identifies the active faction based on the phase.
        This verifies that the phase to faction mapping is correct.
        """
        # Test all three normal phases
        self.assertEqual(self.engine._get_faction_for_phase(PhaseEnum.PLAYER), FactionEnum.PLAYER)
        self.assertEqual(self.engine._get_faction_for_phase(PhaseEnum.ENEMY), FactionEnum.ENEMY)
        self.assertEqual(self.engine._get_faction_for_phase(PhaseEnum.NPC), FactionEnum.NPC)
        
        # Test with an unknown phase (should default to PLAYER)
        with patch('logging.warning') as mock_warning:
            result = self.engine._get_faction_for_phase(PhaseEnum.EVENT)
            self.assertEqual(result, FactionEnum.PLAYER)
            mock_warning.assert_called_once()
            args, _ = mock_warning.call_args
            self.assertIn("Unknown phase", str(args))

if __name__ == '__main__':
    unittest.main()