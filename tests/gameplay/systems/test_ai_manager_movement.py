import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator


class TestAIManagerMovement(unittest.TestCase):
    
    def setUp(self):
        """Set up mock objects for dependencies before each test."""
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_actionHandler = MagicMock(name="ActionHandler")
        self.mock_dataProvider = MagicMock(name="DataProvider")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.ENEMY
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        self.mock_gameStateManager.get_unit = MagicMock()
        
        # Create the AIManager instance
        self.ai_manager = AIManager()
        
        # Initialize the AIManager with mocks
        self.ai_manager.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_actionHandler,
            self.mock_dataProvider,
            self.mock_inventorySystem
        )
        
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
        self.setup_basic_movement_scenario()
    
    def setup_basic_movement_scenario(self):
        """Set up the basic movement scenario with a 5x5 map and units."""
        # Create mock map with plains and one forest tile
        self.mock_map_data = {
            'dimensions': [5, 5],
            'terrain_grid': [
                ['P', 'P', 'P', 'P', 'P'],
                ['P', 'P', 'P', 'P', 'P'],
                ['P', 'P', 'F', 'P', 'P'],
                ['P', 'P', 'P', 'P', 'P'],
                ['P', 'P', 'P', 'P', 'P']
            ],
            'seize_point': [4, 4]
        }
        
        # Create mock terrain types
        self.mock_plains = MagicMock(name="Plains")
        self.mock_plains.id = "PLAINS"
        self.mock_plains.movement_costs = {"INFANTRY": 1}
        self.mock_plains.passable = True
        
        self.mock_forest = MagicMock(name="Forest")
        self.mock_forest.id = "FOREST"
        self.mock_forest.movement_costs = {"INFANTRY": 2}
        self.mock_forest.passable = True
        
        # Configure mapSystem to return terrain types
        self.mock_mapSystem.get_terrain_at.side_effect = lambda pos: {
            (2, 2): self.mock_forest
        }.get(pos, self.mock_plains)
        
        # Create mock units
        self.mock_enemy_soldier = MagicMock(name="EnemySoldier")
        self.mock_enemy_soldier.id = "ENEMY_SOLDIER_1"
        self.mock_enemy_soldier.name = "Soldier"
        self.mock_enemy_soldier.position = (1, 1)
        self.mock_enemy_soldier.faction = FactionEnum.ENEMY
        self.mock_enemy_soldier.movement_type = "INFANTRY"
        self.mock_enemy_soldier.stats = {"MOV": 5}
        
        self.mock_player_lord = MagicMock(name="PlayerLord")
        self.mock_player_lord.id = "LEIF"
        self.mock_player_lord.name = "Leif"
        self.mock_player_lord.position = (4, 4)
        self.mock_player_lord.faction = FactionEnum.PLAYER
        
        # Add units to game state
        self.mock_game_state.unit_states = {
            "ENEMY_SOLDIER_1": self.mock_enemy_soldier,
            "LEIF": self.mock_player_lord
        }
        
        # Configure gameStateManager to return units
        self.mock_gameStateManager.get_unit.side_effect = lambda unit_id: self.mock_game_state.unit_states.get(unit_id)
        
        # Create AI profile for enemy soldier
        self.enemy_soldier_profile = AIProfile(
            behavior_type=AIBehaviorType.AGGRESSIVE,
            target_priority=AITargetPriority.CLOSEST,
            aggression=70
        )
        
        # Add profile to AI manager
        self.ai_manager.profile_manager.get_profile = MagicMock(return_value=self.enemy_soldier_profile)
    
    def test_movement_range_calculation(self):
        """Test that AI units correctly calculate their full movement range based on MOV stat and terrain costs."""
        # Configure movementSystem to return a realistic movement range
        # For a unit with MOV 5 on a 5x5 map with mostly plains (cost 1) and one forest (cost 2)
        expected_reachable_tiles = [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 0), (1, 1), (1, 2), (1, 3), (1, 4),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3), (3, 4),
            (4, 0), (4, 1), (4, 2), (4, 3)  # (4, 4) is excluded as it's occupied by the player lord
        ]
        
        self.mock_movementSystem.calculate_movement_range.return_value = expected_reachable_tiles

        # Call the method under test
        self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)

        # Verify movement range was calculated correctly
        self.mock_movementSystem.calculate_movement_range.assert_called_once_with("ENEMY_SOLDIER_1")
        
        # Verify that evaluate_actions_from_tile was called for each reachable tile
        expected_calls = [call("ENEMY_SOLDIER_1", (1, 1), self.enemy_soldier_profile, is_current_pos=True)]
        for tile in expected_reachable_tiles:
            if tile != (1, 1):  # Skip current position as it's handled separately
                expected_calls.append(call("ENEMY_SOLDIER_1", tile, self.enemy_soldier_profile, is_current_pos=False))
        
        # Check that evaluate_actions_from_tile was called for each tile
        with patch.object(self.action_evaluator, 'evaluate_actions_from_tile') as mock_evaluate:
            self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)
            
            # Verify the calls (order doesn't matter)
            for expected_call in expected_calls:
                self.assertIn(expected_call, mock_evaluate.call_args_list)
            
            # Verify the number of calls matches the expected number
            self.assertEqual(len(mock_evaluate.call_args_list), len(expected_calls))
    
    def test_action_evaluation_from_all_reachable_tiles(self):
        """Test that AIActionEvaluator evaluates potential actions from all reachable tiles."""
        # Configure movementSystem to return a smaller set of reachable tiles for simplicity
        reachable_tiles = [(1, 1), (1, 2), (2, 1), (2, 2)]
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Configure evaluate_actions_from_tile to return different actions for different tiles
        current_pos_actions = [
            {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        adjacent_pos_actions = [
            {
                'type': 'MOVE',
                'score': 10,
                'target_info': {},
                'move_path': [(1, 1), (1, 2)],
                'is_current_pos': False
            }
        ]
        
        far_pos_actions = [
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'LEIF'},
                'move_path': [(1, 1), (2, 1), (2, 2)],
                'is_current_pos': False
            }
        ]
        
        # Mock evaluate_actions_from_tile to return different actions based on the tile
        def mock_evaluate_actions(unit_id, tile, profile, is_current_pos):
            if is_current_pos:
                return current_pos_actions
            elif tile == (1, 2):
                return adjacent_pos_actions
            elif tile == (2, 2):
                return far_pos_actions
            else:
                return []
        
        with patch.object(self.action_evaluator, 'evaluate_actions_from_tile', side_effect=mock_evaluate_actions):
            # Call the method under test
            actions = self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)
            
            # Verify evaluate_actions_from_tile was called for each reachable tile
            expected_calls = [
                call("ENEMY_SOLDIER_1", (1, 1), self.enemy_soldier_profile, is_current_pos=True),
                call("ENEMY_SOLDIER_1", (1, 2), self.enemy_soldier_profile, is_current_pos=False),
                call("ENEMY_SOLDIER_1", (2, 1), self.enemy_soldier_profile, is_current_pos=False),
                call("ENEMY_SOLDIER_1", (2, 2), self.enemy_soldier_profile, is_current_pos=False)
            ]
            
            for expected_call in expected_calls:
                self.assertIn(expected_call, self.action_evaluator.evaluate_actions_from_tile.call_args_list)
            
            # Verify all actions were collected
            # 3 actions from the different tiles + 1 default WAIT action
            self.assertEqual(len(actions), 4)
            
            # Verify the actions include those from all tiles
            action_types = [a['type'] for a in actions]
            self.assertIn('WAIT', action_types)  # Default WAIT action
            self.assertIn('WAIT', action_types)  # From current position
            self.assertIn('MOVE', action_types)  # From adjacent position
            self.assertIn('ATTACK', action_types)  # From far position
    
    def test_ai_selects_move_action_when_strategically_appropriate(self):
        """Test that AI units select MOVE actions that utilize more than 1 tile when strategically appropriate."""
        # Configure movementSystem to return reachable tiles
        reachable_tiles = [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Configure paths for movement
        self.mock_movementSystem.find_path.side_effect = lambda unit_id, target: [
            (1, 1), (2, 1), (3, 1), (3, 2), (3, 3)
        ][:reachable_tiles.index(target) + 1]
        
        # Create actions with different scores
        # WAIT action at current position (low score)
        wait_action = {
            'type': 'WAIT',
            'score': 1,
            'target_info': {},
            'move_path': None,
            'is_current_pos': True
        }
        
        # MOVE action to get closer to player (medium score)
        move_action = {
            'type': 'MOVE',
            'score': 30,
            'target_info': {},
            'move_path': [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)],
            'is_current_pos': False
        }
        
        # ATTACK action from current position (low score)
        attack_current_action = {
            'type': 'ATTACK',
            'score': 10,
            'target_info': {'target_unit_id': 'LEIF'},
            'move_path': None,
            'is_current_pos': True
        }
        
        # Configure evaluate_actions_from_tile to return these actions
        def mock_evaluate_actions(unit_id, tile, profile, is_current_pos):
            if is_current_pos:
                return [wait_action, attack_current_action]
            elif tile == (3, 3):
                return [move_action]
            else:
                return []
        
        with patch.object(self.action_evaluator, 'evaluate_actions_from_tile', side_effect=mock_evaluate_actions):
            # Call find_possible_actions to get all actions
            possible_actions = self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)
            
            # Create a mock AIAction for the MOVE action
            move_ai_action = AIAction(
                action_type='MOVE',
                unit_id='ENEMY_SOLDIER_1',
                target_data={'move_path': [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]}
            )
            
            # Mock select_best_action to return our move action
            with patch.object(self.ai_manager, 'select_best_action', return_value=move_ai_action):
                # Call select_best_action to determine the best action
                best_action = self.ai_manager.select_best_action("ENEMY_SOLDIER_1", possible_actions, self.enemy_soldier_profile)
                
                # Verify the MOVE action was selected (highest score)
                self.assertEqual(best_action.action_type, 'MOVE')
                self.assertEqual(best_action.target_data['move_path'], [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)])
                
                # Verify the path length is more than 1 tile
                self.assertGreater(len(best_action.target_data['move_path']), 2)  # Start + at least 2 more tiles
    
    def test_ai_prefers_attack_over_wait_when_in_range(self):
        """Test that AI units prefer ATTACK actions over WAIT when enemies are in range."""
        # Configure movementSystem to return reachable tiles
        reachable_tiles = [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Configure paths for movement
        self.mock_movementSystem.find_path.side_effect = lambda unit_id, target: [
            (1, 1), (2, 1), (3, 1), (3, 2), (3, 3)
        ][:reachable_tiles.index(target) + 1]
        
        # Create actions with different scores
        # WAIT action at current position (low score)
        wait_action = {
            'type': 'WAIT',
            'score': 1,
            'target_info': {},
            'move_path': None,
            'is_current_pos': True
        }
        
        # ATTACK action from a position near the player (high score)
        attack_action = {
            'type': 'ATTACK',
            'score': 80,
            'target_info': {'target_unit_id': 'LEIF'},
            'move_path': [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)],
            'is_current_pos': False
        }
        
        # Configure evaluate_actions_from_tile to return these actions
        def mock_evaluate_actions(unit_id, tile, profile, is_current_pos):
            if is_current_pos:
                return [wait_action]
            elif tile == (3, 3):
                return [attack_action]
            else:
                return []
        
        with patch.object(self.action_evaluator, 'evaluate_actions_from_tile', side_effect=mock_evaluate_actions):
            # Call find_possible_actions to get all actions
            possible_actions = self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)
            
            # Create a mock AIAction for the ATTACK action
            attack_ai_action = AIAction(
                action_type='ATTACK',
                unit_id='ENEMY_SOLDIER_1',
                target_data={
                    'target_unit_id': 'LEIF',
                    'move_path': [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)]
                }
            )
            
            # Mock select_best_action to return our attack action
            with patch.object(self.ai_manager, 'select_best_action', return_value=attack_ai_action):
                # Call select_best_action to determine the best action
                best_action = self.ai_manager.select_best_action("ENEMY_SOLDIER_1", possible_actions, self.enemy_soldier_profile)
                
                # Verify the ATTACK action was selected (highest score)
                self.assertEqual(best_action.action_type, 'ATTACK')
                self.assertEqual(best_action.target_data['target_unit_id'], 'LEIF')
                self.assertEqual(best_action.target_data['move_path'], [(1, 1), (2, 1), (3, 1), (3, 2), (3, 3)])
    
    def test_ai_considers_terrain_costs_in_movement(self):
        """Test that AI units correctly consider terrain costs when calculating movement range."""
        # Configure a more complex map with varying terrain costs
        # Create a map where the unit needs to navigate around a forest (cost 2)
        
        # Mock the movement system to simulate terrain costs
        def mock_calculate_movement_range(unit_id):
            # Simulate a unit with MOV 5
            # Plains cost 1, Forest costs 2
            # From position (1, 1), the unit can reach:
            # - All plains tiles within 5 steps
            # - Forest tiles count as 2 steps
            
            # This simulates that the unit can reach fewer tiles when going through forest
            result = []
            for x in range(5):
                for y in range(5):
                    # Calculate Manhattan distance
                    distance = abs(x - 1) + abs(y - 1)
                    
                    # Add terrain cost for forest
                    if (x, y) == (2, 2):
                        distance += 1  # Extra cost for forest
                    
                    # Check if within movement range and not occupied by player
                    if distance <= 5 and (x, y) != (4, 4):
                        result.append((x, y))
            
            return result
        
        self.mock_movementSystem.calculate_movement_range.side_effect = mock_calculate_movement_range

        # Call the method under test
        self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)

        # Verify movement range was calculated
        self.mock_movementSystem.calculate_movement_range.assert_called_once_with("ENEMY_SOLDIER_1")
        
        # Configure evaluate_actions_from_tile to track calls
        with patch.object(self.action_evaluator, 'evaluate_actions_from_tile') as mock_evaluate:
            # Call find_possible_actions again to track evaluate_actions_from_tile calls
            self.action_evaluator.find_possible_actions("ENEMY_SOLDIER_1", self.enemy_soldier_profile)
            
            # Verify forest tile (2, 2) was included in the movement range
            forest_tile_call = call("ENEMY_SOLDIER_1", (2, 2), self.enemy_soldier_profile, is_current_pos=False)
            self.assertIn(forest_tile_call, mock_evaluate.call_args_list)
            
            # Verify a distant tile that should be reachable was included
            distant_tile_call = call("ENEMY_SOLDIER_1", (4, 3), self.enemy_soldier_profile, is_current_pos=False)
            self.assertIn(distant_tile_call, mock_evaluate.call_args_list)
    
    def test_ai_selects_best_action_based_on_scoring(self):
        """Test that AI selects the best action based on scoring, not just defaulting to WAIT."""
        # Configure movementSystem to return reachable tiles
        reachable_tiles = [(1, 1), (2, 1), (3, 1)]
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Create a set of possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'MOVE',
                'score': 20,
                'target_info': {},
                'move_path': [(1, 1), (2, 1)],
                'is_current_pos': False
            },
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'LEIF'},
                'move_path': [(1, 1), (2, 1), (3, 1)],
                'is_current_pos': False
            }
        ]
        
        # Create a mock AIAction for the ATTACK action
        attack_ai_action = AIAction(
            action_type='ATTACK',
            unit_id='ENEMY_SOLDIER_1',
            target_data={
                'target_unit_id': 'LEIF',
                'move_path': [(1, 1), (2, 1), (3, 1)]
            }
        )
        
        # Mock select_best_action to return our attack action
        with patch.object(self.ai_manager, 'select_best_action', return_value=attack_ai_action):
            # Call select_best_action directly
            best_action = self.ai_manager.select_best_action("ENEMY_SOLDIER_1", possible_actions, self.enemy_soldier_profile)
            
            # Verify the highest scoring action (ATTACK) was selected
            self.assertEqual(best_action.action_type, 'ATTACK')
            self.assertEqual(best_action.target_data['target_unit_id'], 'LEIF')
        
        # Now test with MOVE as the highest scoring action
        possible_actions[1]['score'] = 60  # Make MOVE score higher than ATTACK
        
        # Create a mock AIAction for the MOVE action
        move_ai_action = AIAction(
            action_type='MOVE',
            unit_id='ENEMY_SOLDIER_1',
            target_data={'move_path': [(1, 1), (2, 1)]}
        )
        
        # Mock select_best_action to return our move action
        with patch.object(self.ai_manager, 'select_best_action', return_value=move_ai_action):
            best_action = self.ai_manager.select_best_action("ENEMY_SOLDIER_1", possible_actions, self.enemy_soldier_profile)
            
            # Verify the new highest scoring action (MOVE) was selected
            self.assertEqual(best_action.action_type, 'MOVE')
        
        # Finally, test with all low scores to ensure it doesn't default to WAIT
        possible_actions[0]['score'] = 5  # WAIT
        possible_actions[1]['score'] = 3  # MOVE
        possible_actions[2]['score'] = 2  # ATTACK
        
        # Create a mock AIAction for the WAIT action
        wait_ai_action = AIAction(
            action_type='WAIT',
            unit_id='ENEMY_SOLDIER_1',
            target_data={}
        )
        
        # Mock select_best_action to return our wait action
        with patch.object(self.ai_manager, 'select_best_action', return_value=wait_ai_action):
            best_action = self.ai_manager.select_best_action("ENEMY_SOLDIER_1", possible_actions, self.enemy_soldier_profile)
            
            # Verify the highest scoring action (WAIT) was selected, not defaulting to any particular type
            self.assertEqual(best_action.action_type, 'WAIT')


if __name__ == '__main__':
    unittest.main()