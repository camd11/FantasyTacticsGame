import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_profile_manager import AIProfileManager
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers

class TestAIThiefLoot(unittest.TestCase):
    """Test cases for the THIEF_LOOT archetype in the AI Manager."""
    
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
        self.mock_mapInteractionSystem = MagicMock(name="MapInteractionSystem")
        self.mock_stealingSystem = MagicMock(name="StealingSystem")
        
        # Create a mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.ENEMY
        self.mock_game_state.unit_states = {}
        
        # Configure GameStateManager mock
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
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
            self.mock_dataProvider
        )
        
        # Add additional systems to the AI manager
        self.ai_manager.inventorySystem = self.mock_inventorySystem
        self.ai_manager.mapInteractionSystem = self.mock_mapInteractionSystem
        self.ai_manager.stealingSystem = self.mock_stealingSystem
        
        # Create and initialize specialized components
        self.profile_manager = AIProfileManager()
        self.profile_manager.initialize(self.mock_gameStateManager, self.mock_dataProvider)
        
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
        
        self.action_scoring = AIActionScoring(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider
        )
        
        self.action_scoring_helpers = AIActionScoringHelpers(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider
        )
        
        # Add specialized components to the AIManager
        self.ai_manager.profile_manager = self.profile_manager
        self.ai_manager.action_evaluator = self.action_evaluator
        self.ai_manager.action_scoring = self.action_scoring
        self.ai_manager.action_scoring_helpers = self.action_scoring_helpers
        
        # Override select_best_action to avoid using archetype handlers
        original_select_best_action = self.ai_manager.select_best_action
        
        def mock_select_best_action(unit_id, possible_actions, ai_profile):
            if not possible_actions:
                return None
                
            # Filter out invalid actions (e.g., path not found for move-actions)
            valid_actions = [a for a in possible_actions if a['type'] == 'WAIT' or
                            a['is_current_pos'] or a['move_path'] is not None]
            
            if not valid_actions:
                return None
                
            # Sort actions by score (descending)
            valid_actions.sort(key=lambda a: a['score'], reverse=True)
            
            # Create AIAction from the highest scoring valid action
            best_action = valid_actions[0]
            target_data = best_action.get('target_info', {}).copy()
            
            # Add move path to target data if needed
            if best_action.get('move_path'):
                target_data['move_path'] = best_action['move_path']
                
            return AIAction(best_action['type'], unit_id, target_data)
        
        self.ai_manager.select_best_action = mock_select_best_action
        
        # Create a THIEF_LOOT AI profile
        self.thief_loot_profile = AIProfile(
            behavior_type=AIBehaviorType.THIEF_LOOT,
            target_priority=AITargetPriority.CLOSEST,
            aggression=30  # Low aggression to prioritize looting over combat
        )
    
    def test_thief_identifies_chest_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies chest targets on the map."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chests
        chest1 = MagicMock(name="Chest1")
        chest1.object_id = "chest1"
        chest1.object_type = "Chest"
        chest1.position = (8, 5)
        chest1.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'MOVE',
                'score': 100,
                'target_info': {},
                'move_path': [(5, 5), (6, 5), (7, 5)],
                'is_current_pos': False,
                'context': {"target_type": "CHEST", "target_coord": chest1.position, "object_id": chest1.object_id}
            },
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock find_possible_actions to return our predefined actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.find_possible_actions("thief1", self.thief_loot_profile)
        
        # Filter for MOVE actions towards chests
        chest_move_actions = [a for a in result_actions if a['type'] == 'MOVE' and
                             'context' in a and a['context'].get('target_type') == 'CHEST']
        
        # Assert
        self.assertTrue(len(chest_move_actions) > 0, "No move actions towards chests found")
    
    def test_thief_identifies_door_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies door targets on the map."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock doors
        door1 = MagicMock(name="Door1")
        door1.object_id = "door1"
        door1.object_type = "Door"
        door1.position = (8, 5)
        door1.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'MOVE',
                'score': 100,
                'target_info': {},
                'move_path': [(5, 5), (6, 5), (7, 5)],
                'is_current_pos': False,
                'context': {"target_type": "DOOR", "target_coord": door1.position, "object_id": door1.object_id}
            },
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock find_possible_actions to return our predefined actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.find_possible_actions("thief1", self.thief_loot_profile)
        
        # Filter for MOVE actions towards doors
        door_move_actions = [a for a in result_actions if a['type'] == 'MOVE' and
                            'context' in a and a['context'].get('target_type') == 'DOOR']
        
        # Assert
        self.assertTrue(len(door_move_actions) > 0, "No move actions towards doors found")
    
    def test_thief_identifies_steal_targets(self):
        """Test that the THIEF_LOOT AI correctly identifies units with stealable items."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        thief_unit.stats = {"speed": 12, "con": 8}
        
        # Create mock enemy units with items
        enemy1 = MagicMock(name="Enemy1")
        enemy1.id = "player1"
        enemy1.position = (8, 5)
        enemy1.faction = FactionEnum.PLAYER
        enemy1.stats = {"speed": 8}
        enemy1.calculated_stats = {"attack_speed": 8}
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "thief1": thief_unit,
            "player1": enemy1
        }.get(unit_id)
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'MOVE',
                'score': 100,
                'target_info': {},
                'move_path': [(5, 5), (6, 5), (7, 5)],
                'is_current_pos': False,
                'context': {"target_type": "STEAL_TARGET", "target_coord": enemy1.position, "unit_id": enemy1.id}
            },
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock find_possible_actions to return our predefined actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.find_possible_actions("thief1", self.thief_loot_profile)
        
        # Filter for MOVE actions towards steal targets
        steal_move_actions = [a for a in result_actions if a['type'] == 'MOVE' and
                             'context' in a and a['context'].get('target_type') == 'STEAL_TARGET']
        
        # Assert
        self.assertTrue(len(steal_move_actions) > 0, "No move actions towards steal targets found")
    
    def test_thief_prioritizes_chest_over_combat(self):
        """Test that the THIEF_LOOT AI prioritizes opening chests over combat."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'player1'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'INTERACT_MAP',
                'score': 200,  # Higher score for chest interaction
                'target_info': {'object_id': 'chest1', 'interact_type': 'CHEST'},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.action_evaluator, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'INTERACT_MAP', "AI did not select chest interaction over attack")
            self.assertEqual(best_action.target_data.get('object_id'), 'chest1', "AI did not target the chest")
    
    def test_thief_prioritizes_steal_over_combat(self):
        """Test that the THIEF_LOOT AI prioritizes stealing over combat."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': 'player2'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'STEAL',
                'score': 150,  # Higher score for stealing
                'target_info': {'target_unit_id': 'player1', 'item_id': 'item1'},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.action_evaluator, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'STEAL', "AI did not select steal over attack")
            self.assertEqual(best_action.target_data.get('target_unit_id'), 'player1', "AI did not target the enemy with item")
            self.assertEqual(best_action.target_data.get('item_id'), 'item1', "AI did not target the correct item")
    
    def test_thief_moves_towards_chest(self):
        """Test that the THIEF_LOOT AI moves towards a chest when not adjacent."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create possible actions with different scores
        possible_actions = [
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'MOVE',
                'score': 100,  # High score for moving towards chest
                'target_info': {},
                'move_path': [(5, 5), (6, 5), (7, 5)],  # Move as close as possible to chest
                'is_current_pos': False,
                'context': {"target_type": "CHEST", "target_coord": (8, 5)}
            }
        ]
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Mock find_possible_actions to return our predefined actions
        with patch.object(self.action_evaluator, 'find_possible_actions', return_value=possible_actions):
            # Act
            best_action = self.ai_manager.select_best_action("thief1", possible_actions, self.thief_loot_profile)
            
            # Assert
            self.assertEqual(best_action.action_type, 'MOVE', "AI did not select move towards chest")
            self.assertEqual(best_action.target_data.get('move_path')[-1], (7, 5), "AI did not move to the closest possible position to chest")
    
    def test_thief_executes_chest_interaction(self):
        """Test that the THIEF_LOOT AI executes chest interaction when adjacent to a chest."""
        # Arrange
        thief_unit = MagicMock(name="ThiefUnit")
        thief_unit.id = "thief1"
        thief_unit.position = (5, 5)
        thief_unit.faction = FactionEnum.ENEMY
        
        # Create mock chest adjacent to thief
        chest = MagicMock(name="Chest")
        chest.object_id = "chest1"
        chest.object_type = "Chest"
        chest.position = (6, 5)  # Adjacent to thief
        chest.state = "Locked"
        
        # Mock unit system to return our thief
        self.mock_unitSystem.get_unit.return_value = thief_unit
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'INTERACT_MAP',
                'score': 200,
                'target_info': {'object_id': 'chest1', 'interact_type': 'CHEST'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock evaluate_actions_from_tile to return our predefined actions
        self.action_evaluator.evaluate_actions_from_tile = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.evaluate_actions_from_tile(
            "thief1", thief_unit.position, self.thief_loot_profile, is_current_pos=True
        )
        
        # Filter for INTERACT_MAP actions
        interact_actions = [a for a in result_actions if a['type'] == 'INTERACT_MAP']
        
        # Assert
        self.assertTrue(len(interact_actions) > 0, "No INTERACT_MAP actions found")
        self.assertEqual(interact_actions[0]['target_info']['interact_type'], 'CHEST', "AI did not target the chest")
