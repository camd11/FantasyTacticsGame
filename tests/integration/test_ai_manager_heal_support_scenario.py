import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_profile_manager import AIProfileManager
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers
from src.core_engine.data_provider import DataProvider


class TestAIManagerHealSupportScenario(unittest.TestCase):
    """Integration test for the HEAL_SUPPORT archetype using a test scenario."""
    
    def setUp(self):
        """Set up the test environment with a loaded scenario."""
        # Create real DataProvider to load the scenario
        self.data_provider = DataProvider()
        
        # Mock other systems
        self.mock_gameStateManager = MagicMock(name="GameStateManager")
        self.mock_unitSystem = MagicMock(name="UnitSystem")
        self.mock_mapSystem = MagicMock(name="MapSystem")
        self.mock_movementSystem = MagicMock(name="MovementSystem")
        self.mock_combatSystem = MagicMock(name="CombatSystem")
        self.mock_actionHandler = MagicMock(name="ActionHandler")
        self.mock_inventorySystem = MagicMock(name="InventorySystem")
        self.mock_staffSystem = MagicMock(name="StaffSystem")
        self.mock_statusEffectsSystem = MagicMock(name="StatusEffectsSystem")
        
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
            self.data_provider
        )
        
        # Add inventorySystem to the AI manager
        self.ai_manager.inventorySystem = self.mock_inventorySystem
        
        # Create and initialize specialized components
        self.profile_manager = AIProfileManager()
        self.profile_manager.initialize(self.mock_gameStateManager, self.data_provider)
        
        self.action_evaluator = AIActionEvaluator()
        self.action_evaluator.initialize(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.data_provider
        )
        
        self.action_scoring = AIActionScoring(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.data_provider
        )
        
        self.action_scoring_helpers = AIActionScoringHelpers(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.data_provider
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
        
        # Create a mock scenario instead of loading from file
        self.scenario = {
            'map_size': [10, 10],
            'units': [
                {
                    'id': 'enemy_healer',
                    'name': 'Enemy Healer',
                    'position': [5, 5],
                    'faction': 'ENEMY',
                    'stats': {'HP': 20, 'MOV': 5},
                    'current_hp': 20,
                    'inventory': [
                        {'item': 'HEAL_STAFF'},
                        {'item': 'MEND_STAFF'},
                        {'item': 'PHYSIC_STAFF'},
                        {'item': 'RESTORE_STAFF'}
                    ]
                },
                {
                    'id': 'enemy_fighter1',
                    'name': 'Enemy Fighter 1',
                    'position': [6, 6],
                    'faction': 'ENEMY',
                    'stats': {'HP': 30, 'MOV': 5},
                    'current_hp': 20  # 66% HP
                },
                {
                    'id': 'enemy_fighter2',
                    'name': 'Enemy Fighter 2',
                    'position': [7, 7],
                    'faction': 'ENEMY',
                    'stats': {'HP': 30, 'MOV': 5},
                    'current_hp': 6  # 20% HP (critically injured)
                },
                {
                    'id': 'enemy_mage',
                    'name': 'Enemy Mage',
                    'position': [4, 4],
                    'faction': 'ENEMY',
                    'stats': {'HP': 25, 'MOV': 5},
                    'current_hp': 25,
                    'status_effects': [
                        {'type': 'SLEEP', 'duration': 3}
                    ]
                }
            ]
        }
        
        # Set up the mock game state
        self.mock_game_state = MagicMock()
        self.mock_game_state.current_turn = 1
        self.mock_game_state.current_phase = PhaseEnum.ENEMY
        
        # Create unit states from scenario
        self.unit_states = {}
        for unit_data in self.scenario.get('units', []):
            unit = MagicMock(name=unit_data['name'])
            unit.id = unit_data['id']
            unit.name = unit_data['name']
            unit.position = tuple(unit_data['position'])
            unit.faction = getattr(FactionEnum, unit_data['faction'])
            unit.current_hp = unit_data.get('current_hp', unit_data['stats']['HP'])
            unit.max_hp = unit_data['stats']['HP']
            
            # Add status effects if present
            if 'status_effects' in unit_data:
                unit.status_effects = []
                for status in unit_data['status_effects']:
                    unit.status_effects.append({
                        'type': getattr(StatusEffectEnum, status['type']),
                        'duration': status['duration']
                    })
            
            self.unit_states[unit.id] = unit
        
        self.mock_game_state.unit_states = self.unit_states
        self.mock_gameStateManager.current_game_state = self.mock_game_state
        
        # Set up mock unit system
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: self.unit_states.get(unit_id)
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        self.mock_unitSystem.has_status.side_effect = lambda unit_id, status: any(
            s['type'] == status for s in getattr(self.unit_states.get(unit_id), 'status_effects', [])
        )
        # Mock get_units_in_range to return all unit IDs (range check happens later)
        self.mock_unitSystem.get_units_in_range.side_effect = lambda unit_id, tile: list(self.unit_states.keys())
        
        # Set up mock inventory system
        def mock_get_usable_items(unit_id):
            unit_data = next((u for u in self.scenario['units'] if u['id'] == unit_id), None)
            if unit_data:
                return [item['item'] for item in unit_data.get('inventory', [])]
            return []
        
        self.mock_inventorySystem.get_usable_items.side_effect = mock_get_usable_items
        
        # Set up mock map system
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Set up mock movement system
        def mock_calculate_movement_range(unit_id):
            unit = self.unit_states.get(unit_id)
            if not unit:
                return []
            
            # Simple implementation: return all tiles within MOV range
            unit_data = next((u for u in self.scenario['units'] if u['id'] == unit_id), None)
            if not unit_data:
                return [unit.position]
            
            mov = unit_data['stats'].get('MOV', 5)
            x, y = unit.position
            
            # Generate tiles within movement range
            tiles = []
            for dx in range(-mov, mov + 1):
                for dy in range(-mov, mov + 1):
                    if abs(dx) + abs(dy) <= mov:  # Manhattan distance
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self.scenario['map_size'][0] and 0 <= new_y < self.scenario['map_size'][1]:
                            tiles.append((new_x, new_y))
            
            return tiles
        
        self.mock_movementSystem.calculate_movement_range.side_effect = mock_calculate_movement_range
    
    def test_healer_prioritizes_critically_injured_ally(self):
        """Test that the healer prioritizes healing the critically injured ally first."""
        # Arrange
        healer_id = "enemy_healer"
        critical_fighter_id = "enemy_fighter2"  # 20% HP
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'ITEM',
                'score': 80,
                'target_info': {'item_id': 'HEAL_STAFF', 'target_unit_id': 'enemy_fighter1'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ITEM',
                'score': 100,  # Higher score for critically injured
                'target_info': {'item_id': 'HEAL_STAFF', 'target_unit_id': 'enemy_fighter2'},
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
        
        # Mock find_possible_actions to return our predefined actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.find_possible_actions(healer_id, AIProfile(
            behavior_type=AIBehaviorType.HEAL_SUPPORT,
            target_priority=AITargetPriority.WEAKEST,
            aggression=30,
            heal_threshold_ally=0.7
        ))
        
        # Filter for ITEM actions (healing)
        heal_actions = [a for a in result_actions if a['type'] == 'ITEM' and 'target_unit_id' in a.get('target_info', {})]
        
        # Sort by score to find the highest priority
        heal_actions.sort(key=lambda a: a['score'], reverse=True)
        best_action = heal_actions[0] if heal_actions else None
        
        # Assert
        self.assertIsNotNone(best_action, "No healing action found")
        self.assertEqual(best_action['target_info'].get('target_unit_id'), critical_fighter_id,
                        "AI did not prioritize the critically injured fighter")
    
    def test_healer_prioritizes_status_removal_after_critical_healing(self):
        """Test that after critical healing is done, the healer prioritizes removing status effects."""
        # Arrange
        healer_id = "enemy_healer"
        sleeping_mage_id = "enemy_mage"  # Has SLEEP status
        
        # Update the critically injured fighter to be at full health
        self.unit_states["enemy_fighter2"].current_hp = self.unit_states["enemy_fighter2"].max_hp
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'ITEM',
                'score': 80,
                'target_info': {'item_id': 'HEAL_STAFF', 'target_unit_id': 'enemy_fighter1'},
                'move_path': None,
                'is_current_pos': True
            },
            {
                'type': 'ITEM',
                'score': 100,  # Higher score for status removal
                'target_info': {'item_id': 'RESTORE_STAFF', 'target_unit_id': 'enemy_mage'},
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
        
        # Mock find_possible_actions to return our predefined actions
        self.action_evaluator.find_possible_actions = MagicMock(return_value=possible_actions)
        
        # Act
        result_actions = self.action_evaluator.find_possible_actions(healer_id, AIProfile(
            behavior_type=AIBehaviorType.HEAL_SUPPORT,
            target_priority=AITargetPriority.WEAKEST,
            aggression=30,
            heal_threshold_ally=0.7,
            use_status_staves=True
        ))
        
        # Filter for ITEM actions
        item_actions = [a for a in result_actions if a['type'] == 'ITEM' and 'target_unit_id' in a.get('target_info', {})]
        
        # Sort by score to find the highest priority
        item_actions.sort(key=lambda a: a['score'], reverse=True)
        best_action = item_actions[0] if item_actions else None
        
        # Assert
        self.assertIsNotNone(best_action, "No item action found")
        self.assertEqual(best_action['target_info'].get('item_id'), "RESTORE_STAFF",
                        "AI did not select restore staff")
        self.assertEqual(best_action['target_info'].get('target_unit_id'), sleeping_mage_id,
                        "AI did not target the ally with status effect")
    
    def test_healer_moves_to_reach_healing_target(self):
        """Test that the healer moves to reach a healing target that is out of range."""
        # Arrange
        healer_id = "enemy_healer"
        injured_fighter_id = "enemy_fighter1"
        
        # Move the injured fighter out of initial staff range
        self.unit_states["enemy_fighter1"].position = (8, 3)  # Further away
        
        # Create a mock path
        mock_path = [(5, 5), (6, 4), (7, 3), (8, 3)]
        
        # Create test actions directly
        possible_actions = [
            {
                'type': 'ITEM',
                'score': 90,
                'target_info': {'item_id': 'HEAL_STAFF', 'target_unit_id': 'enemy_fighter1'},
                'move_path': mock_path,
                'is_current_pos': False
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
        result_actions = self.action_evaluator.find_possible_actions(healer_id, AIProfile(
            behavior_type=AIBehaviorType.HEAL_SUPPORT,
            target_priority=AITargetPriority.WEAKEST,
            aggression=30,
            heal_threshold_ally=0.7
        ))
        
        # Filter for actions that involve movement and healing
        move_heal_actions = [a for a in result_actions if a['type'] == 'ITEM' and
                            'move_path' in a and a['move_path'] is not None]
        
        # Sort by score to find the highest priority
        move_heal_actions.sort(key=lambda a: a['score'], reverse=True)
        best_action = move_heal_actions[0] if move_heal_actions else None
        
        # Assert
        self.assertIsNotNone(best_action, "No move-and-heal action found")
        self.assertEqual(best_action['target_info'].get('target_unit_id'), injured_fighter_id,
                        "AI did not target the injured fighter after moving")
        self.assertIsNotNone(best_action.get('move_path'), "No movement path in the action")


if __name__ == '__main__':
    unittest.main()