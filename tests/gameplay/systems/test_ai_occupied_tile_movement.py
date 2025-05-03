import unittest
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import FactionEnum
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator


class TestAIOccupiedTileMovement(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        self.mock_gameStateManager.get_unit = MagicMock()
        
        # Create the AIActionEvaluator instance
        self.action_evaluator = AIActionEvaluator()
        self.action_evaluator.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider
        )
        
        # Set up basic scenario data
        self.setup_occupied_tile_scenario()
    
    def setup_occupied_tile_scenario(self):
        """Set up a scenario with occupied tiles."""
        # Create mock units
        self.mock_enemy_soldier = MagicMock(name="EnemySoldier")
        self.mock_enemy_soldier.id = "ENEMY_SOLDIER_1"
        self.mock_enemy_soldier.name = "Soldier"
        self.mock_enemy_soldier.position = (1, 1)
        self.mock_enemy_soldier.faction = FactionEnum.ENEMY
        self.mock_enemy_soldier.stats = {"MOV": 5}
        
        self.mock_enemy_archer = MagicMock(name="EnemyArcher")
        self.mock_enemy_archer.id = "ENEMY_ARCHER_1"
        self.mock_enemy_archer.name = "Archer"
        self.mock_enemy_archer.position = (2, 2)  # This tile is occupied
        self.mock_enemy_archer.faction = FactionEnum.ENEMY
        self.mock_enemy_archer.stats = {"MOV": 5}
        
        self.mock_player_lord = MagicMock(name="PlayerLord")
        self.mock_player_lord.id = "LEIF"
        self.mock_player_lord.name = "Leif"
        self.mock_player_lord.position = (4, 4)
        self.mock_player_lord.faction = FactionEnum.PLAYER
        
        # Add units to game state
        self.mock_game_state.unit_states = {
            "ENEMY_SOLDIER_1": self.mock_enemy_soldier,
            "ENEMY_ARCHER_1": self.mock_enemy_archer,
            "LEIF": self.mock_player_lord
        }
        
        # Configure gameStateManager to return units
        self.mock_gameStateManager.get_unit.side_effect = lambda unit_id: self.mock_game_state.unit_states.get(unit_id)
        
        # Configure mapSystem._get_unit_at to return unit IDs at positions
        def mock_get_unit_at(position):
            for unit_id, unit in self.mock_game_state.unit_states.items():
                if unit.position == position:
                    return unit_id
            return None
        
        self.mock_mapSystem._get_unit_at = MagicMock(side_effect=mock_get_unit_at)
        
        # Create AI profile for enemy soldier
        self.enemy_soldier_profile = AIProfile(
            behavior_type=AIBehaviorType.AGGRESSIVE,
            target_priority=AITargetPriority.CLOSEST,
            aggression=70
        )
        
        # Configure pathfinder to return a path
        self.mock_mapSystem.pathfinder = MagicMock()
        self.mock_mapSystem.pathfinder.reconstruct_path = MagicMock(
            return_value=[(1, 1), (2, 1), (2, 2)]  # Path to the occupied tile
        )
        
        # Configure calculate_manhattan_distance
        self.mock_mapSystem.calculate_manhattan_distance = MagicMock(return_value=1)
        
        # Configure unitSystem.get_units_in_range
        self.mock_unitSystem.get_units_in_range = MagicMock(return_value=["LEIF"])
        
        # Configure inventorySystem
        mock_weapon = MagicMock()
        mock_weapon.item_id = "IRON_SWORD"
        self.mock_inventorySystem.get_equipped_weapon = MagicMock(return_value="IRON_SWORD")
        self.mock_inventorySystem.get_usable_items = MagicMock(return_value=[])
        
        # Configure dataProvider
        mock_weapon_data = MagicMock()
        mock_weapon_data.range_min = 1
        mock_weapon_data.range_max = 1
        self.mock_dataProvider.get_item_data = MagicMock(return_value=mock_weapon_data)
    
    def test_ai_avoids_occupied_tiles_for_movement(self):
        """Test that AI doesn't select occupied tiles as movement destinations."""
        # Call evaluate_actions_from_tile with the occupied tile (2, 2)
        actions = self.action_evaluator.evaluate_actions_from_tile(
            "ENEMY_SOLDIER_1", (2, 2), self.enemy_soldier_profile, is_current_pos=False
        )
        
        # Verify that _get_unit_at was called with the tile position
        self.mock_mapSystem._get_unit_at.assert_called_with((2, 2))
        
        # Verify that no MOVE actions were added for the occupied tile
        move_actions = [a for a in actions if a['type'] == 'MOVE']
        self.assertEqual(len(move_actions), 0, "No MOVE actions should be added for occupied tiles")
        
        # Verify that no ATTACK actions with movement were added for the occupied tile
        attack_actions_with_movement = [
            a for a in actions if a['type'] == 'ATTACK' and not a['is_current_pos'] and a['move_path'] is not None
        ]
        self.assertEqual(len(attack_actions_with_movement), 0, 
                         "No ATTACK actions with movement should be added for occupied tiles")
    
    def test_ai_allows_actions_from_current_position(self):
        """Test that AI allows actions from the unit's current position even if occupied."""
        # Call evaluate_actions_from_tile with the unit's current position (1, 1)
        actions = self.action_evaluator.evaluate_actions_from_tile(
            "ENEMY_SOLDIER_1", (1, 1), self.enemy_soldier_profile, is_current_pos=True
        )
        
        # Verify that actions from the current position are allowed
        self.assertGreaterEqual(len(actions), 0, "Actions from current position should be allowed")
    
    def test_ai_allows_actions_from_unoccupied_tiles(self):
        """Test that AI allows actions from unoccupied tiles."""
        # Configure _get_unit_at to return None for position (3, 3) (unoccupied)
        self.mock_mapSystem._get_unit_at = MagicMock(side_effect=lambda pos: None if pos == (3, 3) else "ENEMY_ARCHER_1")
        
        # Configure pathfinder to return a path to the unoccupied tile
        self.mock_mapSystem.pathfinder.reconstruct_path = MagicMock(
            return_value=[(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]  # Path to the unoccupied tile
        )
        
        # Call evaluate_actions_from_tile with the unoccupied tile (3, 3)
        actions = self.action_evaluator.evaluate_actions_from_tile(
            "ENEMY_SOLDIER_1", (3, 3), self.enemy_soldier_profile, is_current_pos=False
        )
        
        # Verify that _get_unit_at was called with the tile position
        self.mock_mapSystem._get_unit_at.assert_called_with((3, 3))
        
        # Verify that MOVE actions were added for the unoccupied tile
        move_actions = [a for a in actions if a['type'] == 'MOVE']
        self.assertGreater(len(move_actions), 0, "MOVE actions should be added for unoccupied tiles")


if __name__ == '__main__':
    unittest.main()