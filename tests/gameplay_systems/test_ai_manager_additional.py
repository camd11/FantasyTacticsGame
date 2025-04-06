import unittest
from unittest.mock import MagicMock, patch, call, ANY

from src.core_engine.game_state import GameStateManager, FactionEnum, PhaseEnum
from src.gameplay_systems.ai_manager import AIManager, AIBehaviorType, AITargetPriority, AIProfile, AIAction


class TestAIManagerAdditional(unittest.TestCase):
    """Additional tests for AIManager to cover remaining TDD anchors."""
    
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
        self.mock_game_state.current_phase = PhaseEnum.PLAYER
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
        
        # Add inventorySystem to the AI manager (it's used in the implementation but not in the initialize method)
        self.ai_manager.inventorySystem = self.mock_inventorySystem
    
    # TDD Anchor: Test generation includes Capture actions if profile allows and target is valid
    def test_generation_includes_capture_actions(self):
        """Test that evaluate_actions_from_tile includes Capture actions if profile allows and target is valid."""
        # Create mock unit, target, and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.faction = FactionEnum.ENEMY
        
        mock_target = MagicMock()
        mock_target.position = (6, 5)
        mock_target.faction = FactionEnum.PLAYER
        
        mock_profile = MagicMock()
        mock_profile.can_capture = True
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "player1": mock_target
        }.get(unit_id)
        
        self.mock_unitSystem.get_units_in_range.return_value = ["player1"]
        self.mock_unitSystem.is_enemy.return_value = True
        self.mock_unitSystem.can_capture.return_value = True
        
        self.mock_mapSystem.calculate_distance.return_value = 1
        
        # Configure inventory system
        mock_weapon = MagicMock()
        self.mock_inventorySystem.get_equipped_weapon.return_value = mock_weapon
        
        # Configure data provider
        mock_weapon_data = MagicMock()
        mock_weapon_data.min_range = 1
        mock_weapon_data.max_range = 1
        self.mock_dataProvider.get_item_data.return_value = mock_weapon_data
        
        # Configure score_capture_action
        self.ai_manager.score_capture_action = MagicMock(return_value=70)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify capture action was included
        capture_actions = [a for a in actions if a['type'] == 'CAPTURE']
        self.assertEqual(len(capture_actions), 1)
        
        # Verify capture action properties
        capture_action = capture_actions[0]
        self.assertEqual(capture_action['type'], 'CAPTURE')
        self.assertEqual(capture_action['score'], 70)
        self.assertEqual(capture_action['target_info'], {'target_unit_id': 'player1'})
        self.assertEqual(capture_action['move_path'], None)
        self.assertEqual(capture_action['is_current_pos'], True)
        
        # Test with capture not allowed in profile
        mock_profile.can_capture = False
        
        # Reset mocks
        self.mock_unitSystem.get_unit.reset_mock()
        self.mock_unitSystem.get_units_in_range.reset_mock()
        
        # Configure mock behavior again
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "player1": mock_target
        }.get(unit_id)
        self.mock_unitSystem.get_units_in_range.return_value = ["player1"]
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify no capture action was included
        capture_actions = [a for a in actions if a['type'] == 'CAPTURE']
        self.assertEqual(len(capture_actions), 0)
    
    # TDD Anchor: Test generation includes Heal actions if profile allows and target is valid
    def test_generation_includes_heal_actions(self):
        """Test that evaluate_actions_from_tile includes Heal actions if profile allows and target is valid."""
        # Create mock unit, ally, and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.faction = FactionEnum.ENEMY
        mock_unit.current_hp = 20
        mock_unit.max_hp = 20
        
        mock_ally = MagicMock()
        mock_ally.position = (6, 5)
        mock_ally.faction = FactionEnum.ENEMY
        mock_ally.current_hp = 10
        mock_ally.max_hp = 20
        
        mock_profile = MagicMock()
        mock_profile.heal_threshold_ally = 0.6  # 60% HP threshold
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "ally1": mock_ally
        }.get(unit_id)
        
        self.mock_unitSystem.get_units_in_range.return_value = ["ally1"]
        self.mock_unitSystem.is_enemy.return_value = False  # Not an enemy (ally)
        
        self.mock_mapSystem.calculate_distance.return_value = 1
        
        # Configure inventory system
        mock_staff = MagicMock()
        self.mock_inventorySystem.get_usable_staves.return_value = [mock_staff]
        
        # Configure data provider
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.is_healing_staff = MagicMock(return_value=True)
        mock_staff_data.min_range = 1
        mock_staff_data.max_range = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Configure find_heal_targets_for_staff
        self.ai_manager.find_heal_targets_for_staff = MagicMock(return_value=["ally1"])
        
        # Configure score_item_action
        self.ai_manager.score_item_action = MagicMock(return_value=60)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify staff action was included
        staff_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('item_id') == mock_staff]
        self.assertEqual(len(staff_actions), 1)
        
        # Verify staff action properties
        staff_action = staff_actions[0]
        self.assertEqual(staff_action['type'], 'ITEM')
        self.assertEqual(staff_action['score'], 60)
        self.assertEqual(staff_action['target_info'], {'item_id': mock_staff, 'target_unit_id': 'ally1'})
        self.assertEqual(staff_action['move_path'], None)
        self.assertEqual(staff_action['is_current_pos'], True)
        
        # Test with ally HP above threshold
        mock_ally.current_hp = 15  # 75% HP, above threshold
        
        # Reset mocks
        self.mock_unitSystem.get_unit.reset_mock()
        self.ai_manager.find_heal_targets_for_staff.reset_mock()
        
        # Configure mock behavior again
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "ally1": mock_ally
        }.get(unit_id)
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify find_heal_targets_for_staff was called
        self.ai_manager.find_heal_targets_for_staff.assert_called_once()
    
    # TDD Anchor: Test generation includes Escape actions if profile allows and on escape map
    def test_generation_includes_escape_actions(self):
        """Test that evaluate_actions_from_tile includes Escape actions if profile allows and on escape map."""
        # Create mock unit and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        
        mock_profile = MagicMock()
        mock_profile.behavior_type = AIBehaviorType.FLEE
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.return_value = mock_unit
        
        # Configure map system to indicate escape is possible
        self.mock_mapSystem.is_escape_point.return_value = True
        
        # Configure score_escape_action
        self.ai_manager.score_escape_action = MagicMock(return_value=80)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify escape action was included
        escape_actions = [a for a in actions if a['type'] == 'ESCAPE']
        self.assertEqual(len(escape_actions), 1)
        
        # Verify escape action properties
        escape_action = escape_actions[0]
        self.assertEqual(escape_action['type'], 'ESCAPE')
        self.assertEqual(escape_action['score'], 80)
        self.assertEqual(escape_action['target_info'], {})
        self.assertEqual(escape_action['move_path'], None)
        self.assertEqual(escape_action['is_current_pos'], True)
        
        # Test with non-escape point
        self.mock_mapSystem.is_escape_point.return_value = False
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify no escape action was included
        escape_actions = [a for a in actions if a['type'] == 'ESCAPE']
        self.assertEqual(len(escape_actions), 0)
    
    # TDD Anchor: Test self-heal action generation checks HP threshold
    def test_self_heal_action_generation_checks_hp_threshold(self):
        """Test that evaluate_actions_from_tile checks HP threshold for self-heal actions."""
        # Create mock unit and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.current_hp = 10
        mock_unit.max_hp = 20
        
        mock_profile = MagicMock()
        mock_profile.heal_threshold_self = 0.6  # 60% HP threshold
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.return_value = mock_unit
        self.mock_unitSystem.get_units_in_range.return_value = []
        
        # Configure inventory system
        mock_item = MagicMock()
        self.mock_inventorySystem.get_usable_items.return_value = [mock_item]
        
        # Configure data provider
        mock_item_data = MagicMock()
        mock_item_data.is_staff = False
        mock_item_data.is_usable_item = True
        mock_item_data.is_healing_item = MagicMock(return_value=True)
        mock_item_data.heal_amount = 10
        self.mock_dataProvider.get_item_data.return_value = mock_item_data
        
        # Configure score_item_action
        self.ai_manager.score_item_action = MagicMock(return_value=40)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify item action was included
        item_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('item_id') == mock_item]
        self.assertEqual(len(item_actions), 1)
        
        # Verify item action properties
        item_action = item_actions[0]
        self.assertEqual(item_action['type'], 'ITEM')
        self.assertEqual(item_action['score'], 40)
        self.assertEqual(item_action['target_info'], {'item_id': mock_item, 'target_unit_id': 'unit1'})
        self.assertEqual(item_action['move_path'], None)
        self.assertEqual(item_action['is_current_pos'], True)
        
        # Test with HP above threshold
        mock_unit.current_hp = 15  # 75% HP, above threshold
        
        # Reset mocks
        self.mock_unitSystem.get_unit.reset_mock()
        
        # Configure mock behavior again
        self.mock_unitSystem.get_unit.return_value = mock_unit
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify no self-heal item action was included
        item_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('target_unit_id') == 'unit1']
        self.assertEqual(len(item_actions), 0)
    
    # TDD Anchor: Test ally heal action generation checks range and HP threshold
    def test_ally_heal_action_generation_checks_range_and_hp_threshold(self):
        """Test that evaluate_actions_from_tile checks range and HP threshold for ally heal actions."""
        # Create mock unit, ally, and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.faction = FactionEnum.ENEMY
        
        mock_ally = MagicMock()
        mock_ally.position = (6, 5)
        mock_ally.faction = FactionEnum.ENEMY
        mock_ally.current_hp = 10
        mock_ally.max_hp = 20
        
        mock_profile = MagicMock()
        mock_profile.heal_threshold_ally = 0.6  # 60% HP threshold
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "ally1": mock_ally
        }.get(unit_id)
        
        self.mock_unitSystem.get_units_in_range.return_value = ["ally1"]
        self.mock_unitSystem.is_enemy.return_value = False  # Not an enemy (ally)
        
        self.mock_mapSystem.calculate_distance.return_value = 1
        
        # Configure inventory system
        mock_staff = MagicMock()
        self.mock_inventorySystem.get_usable_staves.return_value = [mock_staff]
        
        # Configure data provider
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.is_healing_staff = MagicMock(return_value=True)
        mock_staff_data.min_range = 1
        mock_staff_data.max_range = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Configure find_heal_targets_for_staff
        self.ai_manager.find_heal_targets_for_staff = MagicMock(return_value=["ally1"])
        
        # Configure score_item_action
        self.ai_manager.score_item_action = MagicMock(return_value=60)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify staff action was included
        staff_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('item_id') == mock_staff]
        self.assertEqual(len(staff_actions), 1)
        
        # Test with ally out of range
        self.mock_mapSystem.calculate_distance.return_value = 3  # Out of range
        
        # Reset mocks
        self.mock_unitSystem.get_unit.reset_mock()
        self.ai_manager.find_heal_targets_for_staff.reset_mock()
        
        # Configure mock behavior again
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "ally1": mock_ally
        }.get(unit_id)
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify no staff action was included for the ally
        staff_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('target_unit_id') == 'ally1']
        self.assertEqual(len(staff_actions), 0)
    
    # TDD Anchor: Test status staff action generation finds valid enemy targets
    def test_status_staff_action_generation_finds_valid_enemy_targets(self):
        """Test that evaluate_actions_from_tile finds valid enemy targets for status staves."""
        # Create mock unit, enemy, and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.faction = FactionEnum.ENEMY
        
        mock_enemy = MagicMock()
        mock_enemy.position = (6, 5)
        mock_enemy.faction = FactionEnum.PLAYER
        
        mock_profile = MagicMock()
        mock_profile.use_status_staves = True
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "player1": mock_enemy
        }.get(unit_id)
        
        self.mock_unitSystem.get_units_in_range.return_value = ["player1"]
        self.mock_unitSystem.is_enemy.return_value = True  # Is an enemy
        self.mock_unitSystem.has_status.return_value = False  # No status effect yet
        
        self.mock_mapSystem.calculate_distance.return_value = 1
        
        # Configure inventory system
        mock_staff = MagicMock()
        self.mock_inventorySystem.get_usable_staves.return_value = [mock_staff]
        
        # Configure data provider
        mock_staff_data = MagicMock()
        mock_staff_data.is_staff = True
        mock_staff_data.is_usable_item = False
        mock_staff_data.is_healing_staff = MagicMock(return_value=False)
        mock_staff_data.is_status_staff = MagicMock(return_value=True)
        mock_staff_data.inflicts_status = True
        mock_staff_data.status_effect = "SLEEP"
        mock_staff_data.min_range = 1
        mock_staff_data.max_range = 1
        self.mock_dataProvider.get_item_data.return_value = mock_staff_data
        
        # Configure find_status_targets_for_staff
        self.ai_manager.find_status_targets_for_staff = MagicMock(return_value=["player1"])
        
        # Configure score_item_action
        self.ai_manager.score_item_action = MagicMock(return_value=70)
        
        # Call the method under test
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify staff action was included
        staff_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('item_id') == mock_staff]
        self.assertEqual(len(staff_actions), 1)
        
        # Verify staff action properties
        staff_action = staff_actions[0]
        self.assertEqual(staff_action['type'], 'ITEM')
        self.assertEqual(staff_action['score'], 70)
        self.assertEqual(staff_action['target_info'], {'item_id': mock_staff, 'target_unit_id': 'player1'})
        self.assertEqual(staff_action['move_path'], None)
        self.assertEqual(staff_action['is_current_pos'], True)
        
        # Test with status staves disabled in profile
        mock_profile.use_status_staves = False
        
        # Reset mocks
        self.mock_unitSystem.get_unit.reset_mock()
        self.ai_manager.find_status_targets_for_staff.reset_mock()
        
        # Configure mock behavior again
        self.mock_unitSystem.get_unit.side_effect = lambda unit_id: {
            "unit1": mock_unit,
            "player1": mock_enemy
        }.get(unit_id)
        
        # Call the method under test again
        actions = self.ai_manager.evaluate_actions_from_tile("unit1", (5, 5), mock_profile, is_current_pos=True)
        
        # Verify no status staff action was included
        staff_actions = [a for a in actions if a['type'] == 'ITEM' and a['target_info'].get('target_unit_id') == 'player1']
        self.assertEqual(len(staff_actions), 0)
    
    # TDD Anchor: Test move utility increases when moving towards objective/target
    def test_move_utility_increases_when_moving_towards_objective(self):
        """Test that calculate_move_utility increases when moving towards objective/target."""
        # Create mock unit, target, and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        
        mock_profile = MagicMock()
        mock_profile.behavior_type = AIBehaviorType.AGGRESSIVE
        
        # Create mock action
        mock_action = {
            'type': 'MOVE',
            'target_info': {},
            'move_path': [(5, 5), (6, 5), (7, 5)],  # Moving right
            'is_current_pos': False
        }
        
        # Configure mock behavior for aggressive AI (moving towards enemy)
        self.mock_unitSystem.get_unit.return_value = mock_unit
        
        # Configure _find_nearest_enemy to return a position to the right
        self.ai_manager._find_nearest_enemy = MagicMock(return_value=(10, 5))
        
        # Call the method under test
        utility = self.ai_manager.calculate_move_utility(mock_action, "unit1", mock_profile)
        
        # Verify _find_nearest_enemy was called
        self.ai_manager._find_nearest_enemy.assert_called_once_with("unit1")
        
        # Verify utility is positive (moving towards target)
        self.assertGreater(utility, 0)
        
        # Test moving away from target
        mock_action['move_path'] = [(5, 5), (4, 5), (3, 5)]  # Moving left, away from target
        
        # Reset mocks
        self.ai_manager._find_nearest_enemy.reset_mock()
        
        # Call the method under test again
        utility_away = self.ai_manager.calculate_move_utility(mock_action, "unit1", mock_profile)
        
        # Verify utility is lower when moving away
        self.assertLess(utility_away, utility)
    
    # TDD Anchor: Test Retreat AI prioritizes moving away from threats when HP is low
    def test_retreat_ai_prioritizes_moving_away_from_threats_when_hp_is_low(self):
        """Test that Retreat AI prioritizes moving away from threats when HP is low."""
        # Create mock unit and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        mock_unit.current_hp = 5
        mock_unit.max_hp = 20
        
        mock_profile = MagicMock()
        mock_profile.behavior_type = AIBehaviorType.CAUTIOUS
        mock_profile.retreat_threshold = 0.3  # 30% HP threshold
        
        # Configure mock behavior
        self.mock_unitSystem.get_unit.return_value = mock_unit
        
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
                'score': 20,
                'target_info': {},
                'move_path': [(5, 5), (4, 5), (3, 5)],  # Moving away from threats
                'is_current_pos': False
            },
            {
                'type': 'ATTACK',
                'score': 30,
                'target_info': {'target_unit_id': 'player1'},
                'move_path': [(5, 5), (6, 5)],  # Moving towards threats
                'is_current_pos': False
            }
        ]
        
        # Configure _find_threats_to_position to return threats near the attack position
        self.ai_manager._find_threats_to_position = MagicMock()
        self.ai_manager._find_threats_to_position.side_effect = lambda pos: ["player1", "player2"] if pos[0] > 5 else []
        
        # Configure _is_threatened to return True
        self.ai_manager._is_threatened = MagicMock(return_value=True)
        
        # Call the method under test
        best_action = self.ai_manager.select_best_action("unit1", possible_actions, mock_profile)
        
        # Verify the Retreat AI selected the move away action despite lower score
        self.assertEqual(best_action.action_type, 'MOVE')
        self.assertEqual(best_action.target_data, {'move_path': [(5, 5), (4, 5), (3, 5)]})
        
        # Test with HP above retreat threshold
        mock_unit.current_hp = 10  # 50% HP, above retreat threshold
        
        # Call the method under test again
        best_action = self.ai_manager.select_best_action("unit1", possible_actions, mock_profile)
        
        # Verify the AI selected the highest scoring action when HP is above retreat threshold
        self.assertEqual(best_action.action_type, 'ATTACK')
    
    # TDD Anchor: Test Heal Support AI prioritizes healing allies over attacking
    def test_heal_support_ai_prioritizes_healing_allies_over_attacking(self):
        """Test that Heal Support AI prioritizes healing allies over attacking."""
        # Create mock unit and AI profile
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        
        mock_profile = MagicMock()
        mock_profile.behavior_type = AIBehaviorType.HEALER
        
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
                'type': 'ITEM',  # Heal action
                'score': 40,
                'target_info': {'item_id': 'staff1', 'target_unit_id': 'ally1'},
                'move_path': [(5, 5), (6, 5)],
                'is_current_pos': False
            },
            {
                'type': 'ATTACK',
                'score': 50,  # Higher score than heal
                'target_info': {'target_unit_id': 'player1'},
                'move_path': [(5, 5), (4, 5)],
                'is_current_pos': False
            }
        ]
        
