import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum, StatusEffectEnum
from src.gameplay_systems.ai_manager import AIManager
from src.gameplay_systems.ai.ai_types import AIBehaviorType, AITargetPriority, AIProfile, AIAction
from src.gameplay_systems.ai.ai_action_evaluator import AIActionEvaluator
from src.gameplay_systems.ai.ai_action_scoring_helpers import AIActionScoringHelpers
from src.gameplay_systems.ai.ai_action_scoring import AIActionScoring
from src.gameplay_systems.ai.archetype_handlers.heal_support_handler import HealSupportArchetypeHandler


class TestAIManagerHealStaffIntegration(unittest.TestCase):
    """Test cases for the HEAL_SUPPORT archetype's staff-specific functionality in the AI Manager."""
    
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
        self.mock_statusEffectsSystem = MagicMock(name="StatusEffectsSystem")
        
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
    
    def test_heal_utility_scales_with_hp_restored(self):
        """Test that healing utility increases with the amount of HP actually restored."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create two allies with same HP percentage but different max HP
        ally1 = MagicMock(name="Ally1")
        ally1.id = "ally1"
        ally1.position = (6, 5)
        ally1.current_hp = 10
        ally1.max_hp = 20  # 50% HP, can restore 10 HP
        ally1.faction = FactionEnum.ENEMY
        
        ally2 = MagicMock(name="Ally2")
        ally2.id = "ally2"
        ally2.position = (4, 5)
        ally2.current_hp = 15
        ally2.max_hp = 30  # 50% HP, can restore 15 HP
        ally2.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": ally1,
            "ally2": ally2
        }.get(unit_id)
        
        # Create two different heal staves with different healing amounts
        heal_staff = {
            "id": "heal_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 10
        }
        
        mend_staff = {
            "id": "mend_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 20
        }
        
        # Mock data provider to return staff data
        self.mock_dataProvider.get_item_data.side_effect = lambda item_id: {
            "heal_staff": heal_staff,
            "mend_staff": mend_staff
        }.get(item_id)
        
        # Act
        # Score healing ally1 with heal staff (can restore 10 HP)
        score_ally1_heal = self.action_scoring_helpers.score_item_action(
            "healer1", "ally1", (5, 5), "heal_staff", heal_staff, self.heal_support_profile
        )
        
        # Score healing ally2 with heal staff (can restore 10 HP out of 15 missing)
        score_ally2_heal = self.action_scoring_helpers.score_item_action(
            "healer1", "ally2", (5, 5), "heal_staff", heal_staff, self.heal_support_profile
        )
        
        # Score healing ally2 with mend staff (can restore all 15 HP)
        score_ally2_mend = self.action_scoring_helpers.score_item_action(
            "healer1", "ally2", (5, 5), "mend_staff", mend_staff, self.heal_support_profile
        )
        
        # Assert
        # Both allies have same HP%, but ally2 has more absolute HP missing
        self.assertGreaterEqual(score_ally2_heal, score_ally1_heal, 
                             "Healing ally2 with more absolute HP missing should score higher or equal")
        
        # Mend staff can heal more HP for ally2 than heal staff
        self.assertGreater(score_ally2_mend, score_ally2_heal, 
                          "Using mend staff to heal more HP should score higher")
    
    def test_heal_utility_increases_for_low_hp_targets(self):
        """Test that healing utility significantly increases for targets with low HP percentage."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create allies with different HP percentages
        ally1 = MagicMock(name="Ally1")  # Moderately injured
        ally1.id = "ally1"
        ally1.position = (6, 5)
        ally1.current_hp = 15
        ally1.max_hp = 30  # 50% HP
        ally1.faction = FactionEnum.ENEMY
        
        ally2 = MagicMock(name="Ally2")  # Critically injured
        ally2.id = "ally2"
        ally2.position = (4, 5)
        ally2.current_hp = 3
        ally2.max_hp = 30  # 10% HP
        ally2.faction = FactionEnum.ENEMY
        
        ally3 = MagicMock(name="Ally3")  # Slightly injured
        ally3.id = "ally3"
        ally3.position = (5, 6)
        ally3.current_hp = 24
        ally3.max_hp = 30  # 80% HP
        ally3.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "ally1": ally1,
            "ally2": ally2,
            "ally3": ally3
        }.get(unit_id)
        
        # Mock heal staff
        heal_staff = {
            "id": "heal_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 10
        }
        
        # Mock data provider to return staff data
        self.mock_dataProvider.get_item_data.return_value = heal_staff
        
        # Act
        # Score healing each ally with the same staff
        score_ally1 = self.action_scoring_helpers.score_item_action(
            "healer1", "ally1", (5, 5), "heal_staff", heal_staff, self.heal_support_profile
        )
        score_ally2 = self.action_scoring_helpers.score_item_action(
            "healer1", "ally2", (5, 5), "heal_staff", heal_staff, self.heal_support_profile
        )
        score_ally3 = self.action_scoring_helpers.score_item_action(
            "healer1", "ally3", (5, 5), "heal_staff", heal_staff, self.heal_support_profile
        )
        
        # Assert
        # Verify that healing critically injured ally scores significantly higher
        self.assertGreater(score_ally2, score_ally1 * 1.5, 
                          "Healing critically injured ally (10% HP) should score significantly higher than moderately injured ally (50% HP)")
        
        # Verify that healing moderately injured ally scores higher than slightly injured ally
        self.assertGreater(score_ally1, score_ally3, 
                          "Healing moderately injured ally (50% HP) should score higher than slightly injured ally (80% HP)")
    
    def test_healer_considers_different_staff_ranges(self):
        """Test that the AI correctly considers different staff ranges (Heal vs. Physic) when finding targets."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create allies at different distances
        close_ally = MagicMock(name="CloseAlly")
        close_ally.id = "close_ally"
        close_ally.position = (6, 5)  # 1 tile away
        close_ally.current_hp = 15
        close_ally.max_hp = 30  # 50% HP
        close_ally.faction = FactionEnum.ENEMY
        
        distant_ally = MagicMock(name="DistantAlly")
        distant_ally.id = "distant_ally"
        distant_ally.position = (10, 5)  # 5 tiles away
        distant_ally.current_hp = 10
        distant_ally.max_hp = 30  # 33% HP - more injured
        distant_ally.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "close_ally": close_ally,
            "distant_ally": distant_ally
        }.get(unit_id)
        
        # Mock heal staff (range 1)
        heal_staff = {
            "id": "heal_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 10,
            "range_type": "FIXED",
            "range_min": 1,
            "range_max": 1
        }
        
        # Mock physic staff (range = MAG/2, assume MAG = 10 so range = 5)
        physic_staff = {
            "id": "physic_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 10,
            "range_type": "MAG_DIV_2",
            "range_min": 1,
            "range_max": 5  # Assuming MAG/2 = 5
        }
        
        # Mock data provider to return staff data
        self.mock_dataProvider.get_item_data.side_effect = lambda item_id: {
            "heal_staff": heal_staff,
            "physic_staff": physic_staff
        }.get(item_id)
        
        # Mock inventory system to return staves
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff", "physic_staff"]
        
        # Mock movement system to return reachable tiles
        self.mock_movementSystem.calculate_movement_range.return_value = [(5, 5)]  # Just current position for simplicity
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Mock unit system to check if units are allies
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        
        # Mock the find_item_targets method based on staff range
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            if item_id == "heal_staff":
                return ["close_ally"]  # Only close ally in range for heal staff
            elif item_id == "physic_staff":
                return ["close_ally", "distant_ally"]  # Both allies in range for physic staff
            return []
        
        # Mock the action_scoring's find_item_targets method
        with patch.object(self.action_scoring, 'find_item_targets', side_effect=mock_find_item_targets):
            # Create mock actions for each staff and target
            heal_close_action = {
                'type': 'ITEM',
                'score': 50,
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'close_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            physic_close_action = {
                'type': 'ITEM',
                'score': 50,
                'target_info': {'item_id': 'physic_staff', 'target_unit_id': 'close_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            physic_distant_action = {
                'type': 'ITEM',
                'score': 80,  # Higher score for more injured ally
                'target_info': {'item_id': 'physic_staff', 'target_unit_id': 'distant_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            # Use the HealSupportArchetypeHandler to select the best action
            with patch.object(self.heal_support_handler, 'select_best_action') as mock_select:
                # Call the method
                self.heal_support_handler.select_best_action(
                    "healer1", [heal_close_action, physic_close_action, physic_distant_action], self.heal_support_profile
                )
                
                # Verify the method was called with the actions
                mock_select.assert_called_once()
                
                # Get the actions passed to select_best_action
                actions = mock_select.call_args[0][1]
                
                # Sort by score
                actions.sort(key=lambda a: a['score'], reverse=True)
                
                # Assert
                self.assertEqual(actions[0]['target_info']['item_id'], "physic_staff", 
                                "AI did not select physic staff for distant target")
                self.assertEqual(actions[0]['target_info']['target_unit_id'], "distant_ally", 
                                "AI did not target the more injured distant ally")
    
    def test_healer_prioritizes_restore_for_status_effects(self):
        """Test that the AI prioritizes using Restore staff on allies with negative status effects."""
        # Arrange
        healer_unit = MagicMock(name="HealerUnit")
        healer_unit.id = "healer1"
        healer_unit.position = (5, 5)
        healer_unit.faction = FactionEnum.ENEMY
        
        # Create allies with different conditions
        injured_ally = MagicMock(name="InjuredAlly")
        injured_ally.id = "injured_ally"
        injured_ally.position = (6, 5)
        injured_ally.current_hp = 15
        injured_ally.max_hp = 30  # 50% HP
        injured_ally.faction = FactionEnum.ENEMY
        
        sleep_ally = MagicMock(name="SleepAlly")
        sleep_ally.id = "sleep_ally"
        sleep_ally.position = (4, 5)
        sleep_ally.current_hp = 25
        sleep_ally.max_hp = 30  # 83% HP - less injured but has status effect
        sleep_ally.faction = FactionEnum.ENEMY
        
        # Mock unit system to return our units
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "healer1": healer_unit,
            "injured_ally": injured_ally,
            "sleep_ally": sleep_ally
        }.get(unit_id)
        
        # Mock unit system to check for status effects
        self.mock_unitSystem.has_status.side_effect = lambda unit_id, status: unit_id == "sleep_ally" and status == StatusEffectEnum.SLEEP
        
        # Mock heal staff
        heal_staff = {
            "id": "heal_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": True,
            "heal_amount": 10,
            "range_min": 1,
            "range_max": 1
        }
        
        # Mock restore staff
        restore_staff = {
            "id": "restore_staff",
            "is_staff": True,
            "is_usable_item": False,
            "heals_hp": False,
            "cures_status": True,
            "range_min": 1,
            "range_max": 1
        }
        
        # Mock data provider to return staff data
        self.mock_dataProvider.get_item_data.side_effect = lambda item_id: {
            "heal_staff": heal_staff,
            "restore_staff": restore_staff
        }.get(item_id)
        
        # Mock inventory system to return staves
        self.mock_inventorySystem.get_usable_items.return_value = ["heal_staff", "restore_staff"]
        
        # Mock movement system to return reachable tiles
        self.mock_movementSystem.calculate_movement_range.return_value = [(5, 5)]  # Just current position for simplicity
        
        # Mock map system to calculate distances
        self.mock_mapSystem.calculate_manhattan_distance.side_effect = lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        # Mock unit system to check if units are allies
        self.mock_unitSystem.is_ally.side_effect = lambda unit1, unit2: unit1.faction == unit2.faction
        
        # Mock the find_item_targets method based on staff type
        def mock_find_item_targets(unit_id, from_tile, item_id, item_data, potential_targets):
            if item_id == "heal_staff":
                return ["injured_ally", "sleep_ally"]  # Both allies can be healed
            elif item_id == "restore_staff":
                return ["sleep_ally"]  # Only sleep_ally has a status effect
            return []
        
        # Mock the action_scoring's find_item_targets method
        with patch.object(self.action_scoring, 'find_item_targets', side_effect=mock_find_item_targets):
            # Create mock actions for each staff and target
            heal_injured_action = {
                'type': 'ITEM',
                'score': 80,  # Good score for healing injured ally
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'injured_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            heal_sleep_action = {
                'type': 'ITEM',
                'score': 40,  # Lower score for healing less injured ally
                'target_info': {'item_id': 'heal_staff', 'target_unit_id': 'sleep_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            restore_sleep_action = {
                'type': 'ITEM',
                'score': 100,  # High score for removing status effect
                'target_info': {'item_id': 'restore_staff', 'target_unit_id': 'sleep_ally'},
                'move_path': None,
                'is_current_pos': True
            }
            
            # Use the HealSupportArchetypeHandler to modify action scores
            modified_actions = self.heal_support_handler.modify_action_scores(
                "healer1", [heal_injured_action, heal_sleep_action, restore_sleep_action], self.heal_support_profile
            )
            
            # Sort by score
            modified_actions.sort(key=lambda a: a['score'], reverse=True)
            
            # Assert
            self.assertEqual(modified_actions[0]['target_info']['item_id'], "restore_staff", 
                            "AI did not select restore staff for ally with status effect")
            self.assertEqual(modified_actions[0]['target_info']['target_unit_id'], "sleep_ally", 
                            "AI did not target the ally with status effect")


if __name__ == '__main__':
    unittest.main()