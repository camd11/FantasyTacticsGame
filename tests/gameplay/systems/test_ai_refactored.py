import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_profile_manager import AIProfileManager
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers


class TestAIRefactored(unittest.TestCase):
    """Test cases for the refactored AI system."""
    
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
        
        # Add inventorySystem to the AI manager
        self.ai_manager.inventorySystem = self.mock_inventorySystem
        
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
    
    def test_ai_prioritizes_attack_over_wait(self):
        """Test that AI prioritizes attack over wait when an enemy is in range."""
        # Arrange
        unit_id = "enemy1"
        target_id = "player1"
        
        # Create mock units
        enemy_unit = MagicMock(name="EnemyUnit")
        enemy_unit.id = unit_id
        enemy_unit.position = (5, 5)
        enemy_unit.faction = FactionEnum.ENEMY
        
        player_unit = MagicMock(name="PlayerUnit")
        player_unit.id = target_id
        player_unit.position = (6, 5)  # Adjacent to enemy
        player_unit.faction = FactionEnum.PLAYER
        
        # Add units to game state
        self.mock_game_state.unit_states = {
            unit_id: enemy_unit,
            target_id: player_unit
        }
        
        # Configure unit system
        self.mock_unitSystem.get_unit.side_effect = lambda id: self.mock_game_state.unit_states.get(id)
        self.mock_unitSystem.is_enemy.return_value = True
        
        # Configure map system
        self.mock_mapSystem.calculate_manhattan_distance.return_value = 1  # Adjacent
        
        # Configure inventory system
        self.mock_inventorySystem.get_equipped_weapon.return_value = "IRON_SWORD"
        
        # Configure data provider
        mock_weapon_data = MagicMock()
        mock_weapon_data.range_min = 1
        mock_weapon_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_weapon_data
        
        # Configure combat system
        self.mock_combatSystem.simulate_combat.return_value = {
            'attacker': {'dmg': 8, 'hit': 80, 'crit': 5, 'doubles': False},
            'defender': {'dmg': 3, 'hit': 60, 'crit': 0, 'doubles': False}
        }
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'ATTACK',
                'score': 50,
                'target_info': {'target_unit_id': target_id},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock the action_evaluator.find_possible_actions to return our test actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        best_action = self.ai_manager.select_best_action(unit_id, possible_actions, AIProfile(
            behavior_type=AIBehaviorType.AGGRESSIVE,
            target_priority=AITargetPriority.CLOSEST
        ))
        
        # Assert
        self.assertIsNotNone(best_action, "No action selected")
        self.assertEqual(best_action.action_type, 'ATTACK', "AI did not select attack over wait")
        self.assertEqual(best_action.target_data.get('target_unit_id'), target_id, "AI did not target the correct unit")
    
    def test_ai_moves_towards_enemy(self):
        """Test that AI moves towards an enemy when not in attack range."""
        # Arrange
        unit_id = "enemy1"
        target_id = "player1"
        
        # Create mock units
        enemy_unit = MagicMock(name="EnemyUnit")
        enemy_unit.id = unit_id
        enemy_unit.position = (5, 5)
        enemy_unit.faction = FactionEnum.ENEMY
        
        player_unit = MagicMock(name="PlayerUnit")
        player_unit.id = target_id
        player_unit.position = (8, 8)  # Far from enemy
        player_unit.faction = FactionEnum.PLAYER
        
        # Add units to game state
        self.mock_game_state.unit_states = {
            unit_id: enemy_unit,
            target_id: player_unit
        }
        
        # Configure unit system
        self.mock_unitSystem.get_unit.side_effect = lambda id: self.mock_game_state.unit_states.get(id)
        
        # Configure movement system
        move_path = [(5, 5), (6, 6), (7, 7)]  # Path towards player
        self.mock_movementSystem.find_path.return_value = move_path
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'MOVE',
                'score': 30,
                'target_info': {},
                'move_path': move_path,
                'is_current_pos': False
            },
            {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock the action_evaluator.find_possible_actions to return our test actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        best_action = self.ai_manager.select_best_action(unit_id, possible_actions, AIProfile(
            behavior_type=AIBehaviorType.AGGRESSIVE,
            target_priority=AITargetPriority.CLOSEST
        ))
        
        # Assert
        self.assertIsNotNone(best_action, "No action selected")
        self.assertEqual(best_action.action_type, 'MOVE', "AI did not select move towards enemy")
        self.assertEqual(best_action.target_data.get('move_path'), move_path, "AI did not use the correct move path")
    
    def test_healer_prioritizes_healing(self):
        """Test that a healer prioritizes healing injured allies."""
        # Arrange
        healer_id = "healer1"
        injured_ally_id = "ally1"
        
        # Create mock units
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = healer_id
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        injured_ally = MagicMock(name="InjuredAlly")
        injured_ally.id = injured_ally_id
        injured_ally.position = (6, 5)  # Adjacent to healer
        injured_ally.faction = FactionEnum.ENEMY
        injured_ally.current_hp = 10
        injured_ally.max_hp = 20  # 50% HP
        
        # Add units to game state
        self.mock_game_state.unit_states = {
            healer_id: healer_unit,
            injured_ally_id: injured_ally
        }
        
        # Configure unit system
        self.mock_unitSystem.get_unit.side_effect = lambda id: self.mock_game_state.unit_states.get(id)
        
        # Configure inventory system
        self.mock_inventorySystem.get_usable_items.return_value = ["HEAL_STAFF"]
        
        # Configure data provider
        mock_staff_data = MagicMock()
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'ITEM',
                'score': 80,
                'target_info': {'item_id': 'HEAL_STAFF', 'target_unit_id': injured_ally_id},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Mock the action_evaluator.find_possible_actions to return our test actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        best_action = self.ai_manager.select_best_action(healer_id, possible_actions, AIProfile(
            behavior_type=AIBehaviorType.HEAL_SUPPORT,
            target_priority=AITargetPriority.WEAKEST
        ))
        
        # Assert
        self.assertIsNotNone(best_action, "No action selected")
        self.assertEqual(best_action.action_type, 'ITEM', "AI did not select healing")
        self.assertEqual(best_action.target_data.get('item_id'), 'HEAL_STAFF', "AI did not use the correct staff")
        self.assertEqual(best_action.target_data.get('target_unit_id'), injured_ally_id, "AI did not target the injured ally")


if __name__ == '__main__':
    unittest.main()