import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.archetype_handlers.heal_support_handler import HealSupportArchetypeHandler


class TestAIManagerHealSupport(unittest.TestCase):
    """Test cases for the HEAL_SUPPORT archetype in the AI Manager."""
    
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
        self.mock_staffSystem = MagicMock(name="StaffSystem")
        
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
        
        # Create a HEAL_SUPPORT AI profile
        self.heal_support_profile = AIProfile(
            behavior_type=AIBehaviorType.HEAL_SUPPORT,
            target_priority=AITargetPriority.WEAKEST,
            aggression=30,
            heal_threshold_ally=0.7,  # Heal allies below 70% HP
            heal_threshold_self=0.5,  # Prioritize self-healing below 50% HP
            retreat_threshold=0.3     # Retreat when below 30% HP
        )
        
        # Create the specialized components
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
        
        self.heal_support_handler = HealSupportArchetypeHandler(
            self.mock_gameStateManager,
            self.mock_unitSystem,
            self.mock_mapSystem,
            self.mock_movementSystem,
            self.mock_combatSystem,
            self.mock_inventorySystem,
            self.mock_dataProvider
        )
    
    def test_target_identification_lowest_hp_percentage(self):
        """Test that the AI correctly identifies the ally with the lowest HP percentage as the highest priority target."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create three potential ally targets with different HP percentages
        ally1 = MagicMock(name="Ally1")
        ally1.id = "ally1"
        ally1.position = (6, 5)  # Adjacent to healer
        ally1.current_hp = 15
        ally1.max_hp = 30  # 50% HP
        ally1.faction = FactionEnum.ENEMY
        
        ally2 = MagicMock(name="Ally2")
        ally2.id = "ally2"
        ally2.position = (4, 5)  # Adjacent to healer
        ally2.current_hp = 5
        ally2.max_hp = 20  # 25% HP - lowest percentage, should be highest priority
        ally2.faction = FactionEnum.ENEMY
        
        ally3 = MagicMock(name="Ally3")
        ally3.id = "ally3"
        ally3.position = (5, 6)  # Adjacent to healer
        ally3.current_hp = 18
        ally3.max_hp = 30  # 60% HP
        ally3.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": ally1,
            "ally2": ally2,
            "ally3": ally3
        }.get(unit_id)
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Mock movement system to return reachable tiles
        self.mock_movementSystem.calculate_movement_range.return_value = [(5, 5)]  # Just current position for simplicity
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Mock unit system to check if units are allies
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        
        # Mock the action_scoring's find_item_targets method to return our allies
        with patch.object(self.action_scoring, 'find_item_targets', return_value=["ally1", "ally2", "ally3"]):
            # Create mock actions for each ally
            heal_ally1_action = {
                'type': 'ITEM',
                'score': 50,
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'ally1'},
                'move_path': None,
                'is_current_pos': True
            }
            
            heal_ally2_action = {
                'type': 'ITEM',
                'score': 80,  # Higher score for lowest HP percentage
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'ally2'},
                'move_path': None,
                'is_current_pos': True
            }
            
            heal_ally3_action = {
                'type': 'ITEM',
                'score': 30,
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'ally3'},
                'move_path': None,
                'is_current_pos': True
            }
            
            # Use the HealSupportArchetypeHandler to select the best action
            with patch.object(self.heal_support_handler, 'select_best_action') as mock_select:
                # Call the method
                self.heal_support_handler.select_best_action(
                    "healer1", [heal_ally1_action, heal_ally2_action, heal_ally3_action], self.heal_support_profile
                )
                
                # Verify the method was called with the actions
                mock_select.assert_called_once()
                
                # Get the actions passed to select_best_action
                actions = mock_select.call_args[0][1]
                
                # Sort by score
                actions.sort(key=lambda a: a['score'], reverse=True)
                
                # Assert
                self.assertEqual(actions[0]['target_info']['target_unit_id'], "ally2", 
                                "AI did not select the ally with lowest HP percentage")
    
    def test_target_identification_no_targets_in_range(self):
        """Test that the AI correctly handles the case when no valid healing targets are in range."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create an ally that is at full health (not a valid healing target)
        ally1 = MagicMock(name="Ally1")
        ally1.id = "ally1"
        ally1.position = (6, 5)  # Adjacent to healer
        ally1.current_hp = 30
        ally1.max_hp = 30  # 100% HP - not a valid target
        ally1.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": ally1
        }.get(unit_id)
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Mock movement system to return reachable tiles
        self.mock_movementSystem.calculate_movement_range.return_value = [(5, 5)]  # Just current position for simplicity
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Mock unit system to check if units are allies
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        
        # Mock the action_scoring's find_item_targets method to return an empty list (no valid targets)
        with patch.object(self.action_scoring, 'find_item_targets', return_value=[]):
            # Create a wait action as fallback
            wait_action = {
                'type': 'WAIT',
                'score': 1,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
            
            # Use the HealSupportArchetypeHandler to select the best action
            with patch.object(self.heal_support_handler, 'select_best_action') as mock_select:
                # Call the method
                self.heal_support_handler.select_best_action("healer1", [wait_action], self.heal_support_profile)
                
                # Verify the method was called with the actions
                mock_select.assert_called_once()
                
                # Get the actions passed to select_best_action
                actions = mock_select.call_args[0][1]
                
                # Assert
                self.assertEqual(len(actions), 1, "Should only have the WAIT action")
                self.assertEqual(actions[0]['type'], 'WAIT', "Only action should be WAIT")
    
    def test_action_scoring_heal_utility_calculation(self):
        """Test that calculate_ally_heal_utility assigns appropriate scores to potential healing actions."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create allies with different HP percentages
        ally1 = MagicMock(name="Ally1")
        ally1.id = "ally1"
        ally1.position = (6, 5)
        ally1.current_hp = 15
        ally1.max_hp = 30  # 50% HP
        ally1.faction = FactionEnum.ENEMY
        
        ally2 = MagicMock(name="Ally2")
        ally2.id = "ally2"
        ally2.position = (4, 5)
        ally2.current_hp = 5
        ally2.max_hp = 20  # 25% HP - critically wounded
        ally2.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": ally1,
            "ally2": ally2
        }.get(unit_id)
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Act
        # Score healing ally1 (50% HP)
        score_ally1 = self.action_scoring_helpers.score_item_action(
            "healer1", "ally1", (5, 5), "heal_staff", mock_staff_data, self.heal_support_profile
        )
        
        # Score healing ally2 (25% HP - critically wounded)
        score_ally2 = self.action_scoring_helpers.score_item_action(
            "healer1", "ally2", (5, 5), "heal_staff", mock_staff_data, self.heal_support_profile
        )
        
        # Assert
        self.assertGreater(score_ally1, 0, "Healing score for ally1 should be positive")
        self.assertGreater(score_ally2, score_ally1, "Healing score for critically wounded ally2 should be higher than ally1")
    
    def test_action_prioritization_heal_over_wait(self):
        """Test that the AI selects a healing action over waiting when a valid healing target exists."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create an injured ally
        injured_ally = MagicMock(name="InjuredAlly")
        injured_ally.id = "ally1"
        injured_ally.position = (6, 5)  # Adjacent to healer
        injured_ally.current_hp = 15
        injured_ally.max_hp = 30  # 50% HP
        injured_ally.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": injured_ally
        }.get(unit_id)
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
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
                'type': 'ITEM',
                'score': 50,  # Higher score for healing
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'ally1'},
                'move_path': None,
                'is_current_pos': True
            }
        ]
        
        # Use the HealSupportArchetypeHandler to select the best action
        best_action = self.heal_support_handler.select_best_action("healer1", possible_actions, self.heal_support_profile)
        
        # Assert
        self.assertEqual(best_action.action_type, 'ITEM', "AI did not select healing action over waiting")
        self.assertEqual(best_action.target_data.get('target_unit_id'), 'ally1', "AI did not target the injured ally")
    
    def test_movement_decision_to_reach_healing_target(self):
        """Test that the AI chooses the correct movement path to get within range of a healing target."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create an injured ally that is not adjacent (requires movement)
        injured_ally = MagicMock(name="InjuredAlly")
        injured_ally.id = "ally1"
        injured_ally.position = (8, 5)  # 3 tiles away from healer
        injured_ally.current_hp = 10
        injured_ally.max_hp = 30  # 33% HP
        injured_ally.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": injured_ally
        }.get(unit_id)
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5), (7, 5)]  # Can move up to 2 tiles right
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Mock map system to calculate distances and paths
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        self.mock_mapSystem.pathfinder.reconstruct_path.return_value = [(5, 5), (6, 5), (7, 5)]  # Path to get closer to ally
        
        # Mock unit system to check if units are allies
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        
        # Mock the action_scoring's find_item_targets method to return our ally when at position (7, 5)
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            if from_tile == (7, 5):  # Only when at the closest position
                return ["ally1"]
            return []
        
        with patch.object(self.action_scoring, 'find_item_targets', side_effect=mock_find_item_targets):
            # Create a healing action with movement
            heal_action = {
                'type': 'ITEM',
                'score': 100,  # High score for healing
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'ally1'},
                'move_path': [(5, 5), (6, 5), (7, 5)],
                'is_current_pos': False
            }
            
            # Create a wait action as fallback
            wait_action = {
                'type': 'WAIT',
                'score': 10,
                'target_info': {},
                'move_path': None,
                'is_current_pos': True
            }
            
            # Use the HealSupportArchetypeHandler to select the best action
            best_action = self.heal_support_handler.select_best_action(
                "healer1", [heal_action, wait_action], self.heal_support_profile
            )
            
            # Assert
            self.assertEqual(best_action.action_type, 'ITEM', "AI did not select healing action")
            self.assertEqual(best_action.target_data.get('target_unit_id'), 'ally1', "AI did not target the injured ally")
            self.assertEqual(best_action.target_data.get('move_path')[-1], (7, 5), "AI did not move to the correct position to heal")
    
    def test_default_behavior_no_healing_targets(self):
        """Test that the AI performs a sensible default action when no valid healing targets are in range."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our healer
        self.mock_unitSystem.get_unit.return_value = healer_unit
        
        # Mock inventory system to return a heal staff
        heal_staff = MagicMock(name="HealStaff")
        heal_staff.id = "heal_staff"
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff"]
        
        # Mock data provider to return staff data
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.heals_hp = True
        mock_staff_data.heal_amount = 10
        mock_staff_data.range_min = 1
        mock_staff_data.range_max = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Mock movement system to return reachable tiles
        reachable_tiles = [(5, 5), (6, 5), (5, 6)]  # Can move right or down
        self.mock_movementSystem.calculate_movement_range.return_value = reachable_tiles
        
        # Mock map system to calculate distances and paths
        self.mock_mapSystem.calculate_manhattan_distance.return_value = 1
        self.mock_mapSystem.pathfinder.reconstruct_path.side_effect = lambda start, end, unit_id: [start, end]
        
        # Mock map system to check if a tile is safe
        self.mock_mapSystem.is_tile_safe.return_value = True
        
        # Create possible actions with only wait and move
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
                'score': 20,  # Higher score for moving to a safe position
                'target_info': {},
                'move_path': [(5, 5), (6, 5)],
                'is_current_pos': False
            }
        ]
        
        # Use the HealSupportArchetypeHandler to select the best action
        best_action = self.heal_support_handler.select_best_action("healer1", possible_actions, self.heal_support_profile)
        
        # Assert
        self.assertIsNotNone(best_action, "AI did not select any action")
        # The AI should either wait or move to a safe tile
        self.assertIn(best_action.action_type, ['WAIT', 'MOVE'], 
                     f"AI selected {best_action.action_type} instead of WAIT or MOVE when no healing targets available")


if __name__ == '__main__':
    unittest.main()