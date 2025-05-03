import unittest
from unittest.mock import MagicMock, patch, call
import logging

# Import the actual Enum and EngineCore
from src.core_engine.game_state import PhaseEnum, FactionEnum, StatusEffectEnum
from src.core_engine.turn_manager import TurnPhase
from src.core_engine.engine import EngineCore

class TestEnginePhaseExecution(unittest.TestCase):
    """
    Tests for the EngineCore class focusing on phase execution.
    These tests verify that the correct units are processed during each phase's execution.
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
        self.engine._sort_units_for_ai = MagicMock(name="_sort_units_for_ai")
        self.engine._can_unit_act = MagicMock(name="_can_unit_act", return_value=True)
        
        # Set up common test data
        self.player_unit1 = MagicMock(name="PlayerUnit1", id="P1", faction=FactionEnum.PLAYER, has_acted=False, has_moved=False)
        self.player_unit2 = MagicMock(name="PlayerUnit2", id="P2", faction=FactionEnum.PLAYER, has_acted=False, has_moved=False)
        self.enemy_unit1 = MagicMock(name="EnemyUnit1", id="E1", faction=FactionEnum.ENEMY, has_acted=False, has_moved=False)
        self.enemy_unit2 = MagicMock(name="EnemyUnit2", id="E2", faction=FactionEnum.ENEMY, has_acted=False, has_moved=False)
        self.npc_unit1 = MagicMock(name="NPCUnit1", id="N1", faction=FactionEnum.NPC, has_acted=False, has_moved=False)
        self.npc_unit2 = MagicMock(name="NPCUnit2", id="N2", faction=FactionEnum.NPC, has_acted=False, has_moved=False)

    def test_execute_phase_processes_correct_units_in_player_phase(self):
        """
        Test that during PLAYER_PHASE execution, only player units are processed.
        This test uses AI vs AI mode to simplify testing.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.PLAYER
        self.mock_turn_manager.get_current_turn.return_value = 1
        
        # Set up AI vs AI mode
        self.engine.ai_vs_ai = True
        
        # Configure active faction units (player units)
        self.engine.active_faction_units = [self.player_unit1, self.player_unit2]
        
        # Configure _sort_units_for_ai to return the units in order
        self.engine._sort_units_for_ai.return_value = [self.player_unit1, self.player_unit2]
        
        # Configure AI manager to return actions for units
        player_action1 = {"type": "MOVE", "target_pos": (1, 1)}
        player_action2 = {"type": "ATTACK", "target_id": "E1"}
        self.mock_ai_manager.determine_action.side_effect = [player_action1, player_action2]
        
        # Configure action handler to process actions successfully
        self.mock_action_handler.process_action.return_value = True
        
        # Call the method under test
        self.engine.execute_phase()
        
        # Assertions
        self.engine._sort_units_for_ai.assert_called_once_with([self.player_unit1, self.player_unit2])
        
        # Verify that AI determined actions for player units
        self.mock_ai_manager.determine_action.assert_has_calls([
            call(self.player_unit1, self.mock_gs_manager),
            call(self.player_unit2, self.mock_gs_manager)
        ])
        
        # Verify that actions were processed for player units
        self.mock_action_handler.process_action.assert_has_calls([
            call(self.player_unit1.id, player_action1),
            call(self.player_unit2.id, player_action2)
        ])
        
        # Verify that game end conditions were checked after each unit's action
        self.assertEqual(self.engine.check_game_end_conditions.call_count, 2)

    def test_execute_phase_processes_correct_units_in_enemy_phase(self):
        """
        Test that during ENEMY_PHASE execution, only enemy units are processed.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.ENEMY
        self.mock_turn_manager.get_current_turn.return_value = 1
        
        # Configure active faction units (enemy units)
        self.engine.active_faction_units = [self.enemy_unit1, self.enemy_unit2]
        
        # Configure _sort_units_for_ai to return the units in order
        self.engine._sort_units_for_ai.return_value = [self.enemy_unit1, self.enemy_unit2]
        
        # Configure AI manager to return actions for units
        enemy_action1 = {"type": "MOVE", "target_pos": (3, 3)}
        enemy_action2 = {"type": "ATTACK", "target_id": "P1"}
        self.mock_ai_manager.determine_action.side_effect = [enemy_action1, enemy_action2]
        
        # Configure action handler to process actions successfully
        self.mock_action_handler.process_action.return_value = True
        
        # Call the method under test
        self.engine.execute_phase()
        
        # Assertions
        self.engine._sort_units_for_ai.assert_called_once_with([self.enemy_unit1, self.enemy_unit2])
        
        # Verify that AI determined actions for enemy units
        self.mock_ai_manager.determine_action.assert_has_calls([
            call(self.enemy_unit1, self.mock_gs_manager),
            call(self.enemy_unit2, self.mock_gs_manager)
        ])
        
        # Verify that actions were processed for enemy units
        self.mock_action_handler.process_action.assert_has_calls([
            call(self.enemy_unit1.id, enemy_action1),
            call(self.enemy_unit2.id, enemy_action2)
        ])
        
        # Verify that game end conditions were checked after each unit's action
        self.assertEqual(self.engine.check_game_end_conditions.call_count, 2)

    def test_execute_phase_processes_correct_units_in_npc_phase(self):
        """
        Test that during NPC_PHASE execution, only NPC units are processed.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.NPC
        self.mock_turn_manager.get_current_turn.return_value = 1
        
        # Configure active faction units (NPC units)
        self.engine.active_faction_units = [self.npc_unit1, self.npc_unit2]
        
        # Configure _sort_units_for_ai to return the units in order
        self.engine._sort_units_for_ai.return_value = [self.npc_unit1, self.npc_unit2]
        
        # Configure AI manager to return actions for units
        npc_action1 = {"type": "MOVE", "target_pos": (5, 5)}
        npc_action2 = {"type": "WAIT"}
        self.mock_ai_manager.determine_action.side_effect = [npc_action1, npc_action2]
        
        # Configure action handler to process actions successfully
        self.mock_action_handler.process_action.return_value = True
        
        # Call the method under test
        self.engine.execute_phase()
        
        # Assertions
        self.engine._sort_units_for_ai.assert_called_once_with([self.npc_unit1, self.npc_unit2])
        
        # Verify that AI determined actions for NPC units
        self.mock_ai_manager.determine_action.assert_has_calls([
            call(self.npc_unit1, self.mock_gs_manager),
            call(self.npc_unit2, self.mock_gs_manager)
        ])
        
        # Verify that actions were processed for NPC units
        self.mock_action_handler.process_action.assert_has_calls([
            call(self.npc_unit1.id, npc_action1)
        ])
        # The second unit's action is WAIT, which doesn't call process_action
        
        # Verify that game end conditions were checked after each unit's action
        self.assertEqual(self.engine.check_game_end_conditions.call_count, 2)

    def test_execute_phase_does_not_process_wrong_faction_units(self):
        """
        Test that during phase execution, units from other factions are not processed.
        This test verifies that enemy units are not processed during PLAYER_PHASE.
        """
        # Setup
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.PLAYER
        self.mock_turn_manager.get_current_turn.return_value = 1
        
        # Set up AI vs AI mode
        self.engine.ai_vs_ai = True
        
        # Configure active faction units (player units only)
        self.engine.active_faction_units = [self.player_unit1]
        
        # Configure _sort_units_for_ai to return the player units
        self.engine._sort_units_for_ai.return_value = [self.player_unit1]
        
        # Configure AI manager to return an action for the player unit
        player_action = {"type": "MOVE", "target_pos": (1, 1)}
        self.mock_ai_manager.determine_action.return_value = player_action
        
        # Configure action handler to process actions successfully
        self.mock_action_handler.process_action.return_value = True
        
        # Call the method under test
        self.engine.execute_phase()
        
        # Assertions
        # Verify that _sort_units_for_ai was called only with player units
        self.engine._sort_units_for_ai.assert_called_once_with([self.player_unit1])
        
        # Verify that AI determined actions only for player units
        self.mock_ai_manager.determine_action.assert_called_once_with(self.player_unit1, self.mock_gs_manager)
        
        # Verify that actions were processed only for player units
        self.mock_action_handler.process_action.assert_called_once_with(self.player_unit1.id, player_action)
        
        # Verify that enemy units were not processed at all
        for enemy_unit in [self.enemy_unit1, self.enemy_unit2]:
            self.assertNotIn(call(enemy_unit, self.mock_gs_manager), self.mock_ai_manager.determine_action.call_args_list)
            self.assertNotIn(call(enemy_unit.id, any), self.mock_action_handler.process_action.call_args_list)

    def test_process_ai_actions_for_enemy_units_handles_phase_correctly(self):
        """
        Test that _process_ai_actions_for_enemy_units correctly processes units based on the phase.
        This tests the internal method that handles AI actions for enemy and NPC phases.
        """
        # Setup for ENEMY_PHASE
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.ENEMY
        
        # Configure active faction units (enemy units)
        self.engine.active_faction_units = [self.enemy_unit1, self.enemy_unit2]
        
        # Configure _sort_units_for_ai to return the units in order
        self.engine._sort_units_for_ai.return_value = [self.enemy_unit1, self.enemy_unit2]
        
        # Configure AI manager to return actions for units
        enemy_action1 = {"type": "MOVE", "target_pos": (3, 3)}
        enemy_action2 = {"type": "ATTACK", "target_id": "P1"}
        self.mock_ai_manager.determine_action.side_effect = [enemy_action1, enemy_action2]
        
        # Configure action handler to process actions successfully
        self.mock_action_handler.process_action.return_value = True
        
        # Call the method under test
        self.engine._process_ai_actions_for_enemy_units(PhaseEnum.ENEMY)
        
        # Assertions
        self.engine._sort_units_for_ai.assert_called_once_with([self.enemy_unit1, self.enemy_unit2])
        
        # Verify that AI determined actions for enemy units
        self.mock_ai_manager.determine_action.assert_has_calls([
            call(self.enemy_unit1, self.mock_gs_manager),
            call(self.enemy_unit2, self.mock_gs_manager)
        ])
        
        # Verify that actions were processed for enemy units
        self.mock_action_handler.process_action.assert_has_calls([
            call(self.enemy_unit1.id, enemy_action1),
            call(self.enemy_unit2.id, enemy_action2)
        ])
        
        # Reset mocks for NPC phase test
        self.engine._sort_units_for_ai.reset_mock()
        self.mock_ai_manager.determine_action.reset_mock()
        self.mock_action_handler.process_action.reset_mock()
        
        # Setup for NPC_PHASE
        self.mock_turn_manager.get_current_phase.return_value = PhaseEnum.NPC
        
        # Configure active faction units (NPC units)
        self.engine.active_faction_units = [self.npc_unit1, self.npc_unit2]
        
        # Configure _sort_units_for_ai to return the units in order
        self.engine._sort_units_for_ai.return_value = [self.npc_unit1, self.npc_unit2]
        
        # Configure AI manager to return actions for units
        npc_action1 = {"type": "MOVE", "target_pos": (5, 5)}
        npc_action2 = {"type": "ATTACK", "target_id": "E1"}
        self.mock_ai_manager.determine_action.side_effect = [npc_action1, npc_action2]
        
        # Call the method under test
        self.engine._process_ai_actions_for_enemy_units(PhaseEnum.NPC)
        
        # Assertions
        self.engine._sort_units_for_ai.assert_called_once_with([self.npc_unit1, self.npc_unit2])
        
        # Verify that AI determined actions for NPC units
        self.mock_ai_manager.determine_action.assert_has_calls([
            call(self.npc_unit1, self.mock_gs_manager),
            call(self.npc_unit2, self.mock_gs_manager)
        ])
        
        # Verify that actions were processed for NPC units
        self.mock_action_handler.process_action.assert_has_calls([
            call(self.npc_unit1.id, npc_action1),
            call(self.npc_unit2.id, npc_action2)
        ])

if __name__ == '__main__':
    unittest.main()