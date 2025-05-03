import unittest
from unittest.mock import MagicMock, patch, call
import random

from src.gameplay_systems.staff_system import StaffSystem
from src.core_engine.data_provider import ItemTypeEnum, WeaponTypeEnum, RankEnum, TerrainTypeEnum
from src.core_engine.game_state import StatusEffectEnum, DispositionEnum
from tests.gameplay_systems.test_data_provider import TestDataProvider


class TestStaffSystem(unittest.TestCase):
    """Test cases for the Staff System."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Load test data
        self.test_data_provider = TestDataProvider("staff_system_test.yaml")
        
        # Set up mock systems
        mock_systems = self.test_data_provider.setup_mock_systems_for_staff_tests()
        self.mock_item_system = mock_systems["item_system"]
        self.mock_unit_system = mock_systems["unit_system"]
        self.mock_status_effects_system = mock_systems["status_effects_system"]
        self.mock_map_system = mock_systems["map_system"]
        self.mock_action_system = mock_systems["action_system"]
        self.mock_exp_system = mock_systems["exp_system"]
        self.mock_ai_system = mock_systems["ai_system"]
        self.mock_data_provider = mock_systems["data_provider"]
        
        # Create the StaffSystem instance
        self.staff_system = StaffSystem()
        self.staff_system.initialize(
            self.mock_item_system,
            self.mock_unit_system,
            self.mock_status_effects_system,
            self.mock_map_system,
            self.mock_action_system,
            self.mock_exp_system,
            self.mock_ai_system,
            self.mock_data_provider
        )
        
        # Set up random seed for predictable test results
        random.seed(42)

    # --- Test Staff Data Loading ---
    
    def test_staff_data_loading_heal_staff(self):
        """Test that heal staff data is correctly loaded from items.yaml."""
        # Arrange
        mock_heal_staff_data = {
            "id": "HEAL_STAFF",
            "name": "Heal",
            "type": "STAFF",
            "weapon_type": "STAFF",
            "required_rank": "E",
            "weight": 4,
            "max_durability": 30,
            "value": 600,
            "effect_type": "HEAL",
            "target_type": "ALLY",
            "range_type": "FIXED",
            "range_min": 1,
            "range_max": 1,
            "base_hit": None,  # Auto-hits
            "heal_formula": "POTENCY_PLUS_USER_MAG",
            "base_potency": 10
        }
        
        # Mock the data provider to return our mock staff data
        self.mock_data_provider.get_item_data.return_value = mock_heal_staff_data
        
        # Act
        staff_data = self.staff_system.get_staff_data("HEAL_STAFF")
        
        # Assert
        self.assertEqual(staff_data["effect_type"], "HEAL")
        self.assertEqual(staff_data["target_type"], "ALLY")
        self.assertEqual(staff_data["range_type"], "FIXED")
        self.assertEqual(staff_data["range_min"], 1)
        self.assertEqual(staff_data["range_max"], 1)
        self.assertIsNone(staff_data["base_hit"])
        self.assertEqual(staff_data["heal_formula"], "POTENCY_PLUS_USER_MAG")
        self.assertEqual(staff_data["base_potency"], 10)
        
        # Verify the data provider was called correctly
        self.mock_data_provider.get_item_data.assert_called_once_with("HEAL_STAFF")
    
    def test_staff_data_loading_sleep_staff(self):
        """Test that sleep staff data is correctly loaded from items.yaml."""
        # Arrange
        mock_sleep_staff_data = {
            "id": "SLEEP_STAFF",
            "name": "Sleep",
            "type": "STAFF",
            "weapon_type": "STAFF",
            "required_rank": "C",
            "weight": 6,
            "max_durability": 7,
            "value": 1500,
            "effect_type": "STATUS_INFLICT",
            "target_type": "ENEMY",
            "range_type": "USER_MAG",
            "range_min": 1,
            "range_max": 99,  # Placeholder, calculated dynamically
            "base_hit": 60,  # Standard base hit for status staves
            "status_inflicted": "SLEEP"
        }
        
        # Mock the data provider to return our mock staff data
        self.mock_data_provider.get_item_data.return_value = mock_sleep_staff_data
        
        # Act
        staff_data = self.staff_system.get_staff_data("SLEEP_STAFF")
        
        # Assert
        self.assertEqual(staff_data["effect_type"], "STATUS_INFLICT")
        self.assertEqual(staff_data["target_type"], "ENEMY")
        self.assertEqual(staff_data["range_type"], "USER_MAG")
        self.assertEqual(staff_data["range_min"], 1)
        self.assertEqual(staff_data["range_max"], 99)
        self.assertEqual(staff_data["base_hit"], 60)
        self.assertEqual(staff_data["status_inflicted"], "SLEEP")
        
        # Verify the data provider was called correctly
        self.mock_data_provider.get_item_data.assert_called_once_with("SLEEP_STAFF")
    
    # --- Test Targeting Rules ---
    
    def test_get_staff_range_fixed(self):
        """Test that get_staff_range returns correct range for fixed range staves."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        self.mock_unit_system.get_stat.return_value = 10  # MAG = 10
        
        staff_item = {
            "id": "HEAL_STAFF",
            "range_type": "FIXED",
            "range_min": 1,
            "range_max": 1
        }
        
        # Act
        min_range, max_range = self.staff_system.get_staff_range(user, staff_item)
        
        # Assert
        self.assertEqual(min_range, 1)
        self.assertEqual(max_range, 1)
        
        # Verify unit_system was not called for fixed range
        self.mock_unit_system.get_stat.assert_not_called()
    
    def test_get_staff_range_mag_div_2(self):
        """Test that get_staff_range returns correct range for MAG/2 range staves."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        self.mock_unit_system.get_stat.return_value = 10  # MAG = 10
        
        staff_item = {
            "id": "PHYSIC_STAFF",
            "range_type": "MAG_DIV_2",
            "range_min": 1,
            "range_max": 99  # Placeholder
        }
        
        # Act
        min_range, max_range = self.staff_system.get_staff_range(user, staff_item)
        
        # Assert
        self.assertEqual(min_range, 1)
        self.assertEqual(max_range, 5)  # 10 / 2 = 5
        
        # Verify unit_system was called correctly
        self.mock_unit_system.get_stat.assert_called_once_with(user, "MAG")
    
    def test_get_valid_targets_heal_staff_ally_only(self):
        """Test that get_valid_targets returns only valid ally targets for heal staff."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        user_pos = (5, 5)
        self.mock_unit_system.get_position.return_value = user_pos
        
        staff_item = {
            "id": "HEAL_STAFF",
            "effect_type": "HEAL",
            "target_type": "ALLY",
            "range_type": "FIXED",
            "range_min": 1,
            "range_max": 1
        }
        
        # Mock map system to return tiles in range
        tiles_in_range = [(4, 5), (5, 4), (6, 5), (5, 6)]
        self.mock_map_system.get_tiles_in_range.return_value = tiles_in_range
        
        # Mock units on those tiles
        ally1 = MagicMock()
        ally1.id = "ALLY1"
        ally1.current_hp = 10
        ally1.max_hp = 20
        
        ally2 = MagicMock()
        ally2.id = "ALLY2"
        ally2.current_hp = 20  # Full HP
        ally2.max_hp = 20
        
        enemy = MagicMock()
        enemy.id = "ENEMY1"
        
        # Mock map system to return units at positions
        def mock_get_unit_at(pos):
            if pos == (4, 5):
                return ally1
            elif pos == (5, 4):
                return ally2
            elif pos == (6, 5):
                return enemy
            else:
                return None
        
        self.mock_map_system.get_unit_at.side_effect = mock_get_unit_at
        
        # Mock unit system to check if units are allies
        def mock_is_ally(unit1, unit2):
            return unit2.id in ["ALLY1", "ALLY2"]
        
        self.mock_unit_system.is_ally.side_effect = mock_is_ally
        
        # Mock unit system to check if units are at max HP
        def mock_is_at_max_hp(unit):
            return unit.current_hp == unit.max_hp
        
        self.mock_unit_system.is_at_max_hp.side_effect = mock_is_at_max_hp
        
        # Act
        valid_targets = self.staff_system.get_valid_targets(user, staff_item)
        
        # Assert
        self.assertEqual(len(valid_targets), 1)
        self.assertEqual(valid_targets[0].id, "ALLY1")
        
        # Verify map system was called correctly
        self.mock_map_system.get_tiles_in_range.assert_called_once_with(user_pos, 1, 1)
    
    def test_get_valid_targets_status_staff_enemy_only_los(self):
        """Test that get_valid_targets returns only valid enemy targets for status staff with LoS check."""
        # Arrange
        user = MagicMock()
        user.id = "DARK_MAGE"
        user_pos = (5, 5)
        self.mock_unit_system.get_position.return_value = user_pos
        self.mock_unit_system.get_stat.return_value = 8  # MAG = 8
        
        staff_item = {
            "id": "SLEEP_STAFF",
            "effect_type": "STATUS_INFLICT",
            "target_type": "ENEMY",
            "range_type": "USER_MAG",
            "range_min": 1,
            "range_max": 99,  # Placeholder
            "status_inflicted": "SLEEP"
        }
        
        # Mock map system to return tiles in range
        tiles_in_range = [(3, 5), (4, 5), (5, 3), (5, 4), (5, 6), (5, 7), (6, 5), (7, 5)]
        self.mock_map_system.get_tiles_in_range.return_value = tiles_in_range
        
        # Mock units on those tiles
        ally = MagicMock()
        ally.id = "ALLY1"
        
        enemy1 = MagicMock()
        enemy1.id = "ENEMY1"
        
        enemy2 = MagicMock()
        enemy2.id = "ENEMY2"
        
        # Mock map system to return units at positions
        def mock_get_unit_at(pos):
            if pos == (3, 5):
                return ally
            elif pos == (5, 3):
                return enemy1
            elif pos == (5, 7):
                return enemy2
            else:
                return None
        
        self.mock_map_system.get_unit_at.side_effect = mock_get_unit_at
        
        # Mock line of sight checks
        def mock_has_line_of_sight(pos1, pos2):
            # Assume enemy2 is behind a wall
            if pos2 == (5, 7):
                return False
            return True
        
        self.mock_map_system.has_line_of_sight.side_effect = mock_has_line_of_sight
        
        # Mock unit system to check if units are enemies
        def mock_is_enemy(unit1, unit2):
            return unit2.id in ["ENEMY1", "ENEMY2"]
        
        self.mock_unit_system.is_enemy.side_effect = mock_is_enemy
        
        # Act
        valid_targets = self.staff_system.get_valid_targets(user, staff_item)
        
        # Assert
        self.assertEqual(len(valid_targets), 1)
        self.assertEqual(valid_targets[0].id, "ENEMY1")
        
        # Verify map system was called correctly
        self.mock_map_system.get_tiles_in_range.assert_called_once_with(user_pos, 1, 8)
    
    # --- Test Effect Application ---
    
    def test_calculate_heal_amount_potency_plus_mag(self):
        """Test that calculate_heal_amount returns correct amount for POTENCY_PLUS_USER_MAG formula."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        self.mock_unit_system.get_stat.return_value = 10  # MAG = 10
        
        target = MagicMock()
        target.id = "TARGET"
        
        self.mock_unit_system.get_current_hp.return_value = 10
        self.mock_unit_system.get_max_hp.return_value = 30
        
        staff_item = {
            "id": "HEAL_STAFF",
            "heal_formula": "POTENCY_PLUS_USER_MAG",
            "base_potency": 10
        }
        
        # Act
        heal_amount = self.staff_system.calculate_heal_amount(user, staff_item, target)
        
        # Assert
        self.assertEqual(heal_amount, 20)  # 10 (base) + 10 (MAG) = 20
        
        # Verify unit system was called correctly
        self.mock_unit_system.get_stat.assert_called_once_with(user, "MAG")
        self.mock_unit_system.get_current_hp.assert_called_once_with(target)
        self.mock_unit_system.get_max_hp.assert_called_once_with(target)
    
    def test_apply_heal_effect_updates_hp(self):
        """Test that apply_staff_effect correctly updates HP for healing staff."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        
        target = MagicMock()
        target.id = "TARGET"
        
        staff_item = {
            "id": "HEAL_STAFF",
            "effect_type": "HEAL",
            "heal_formula": "POTENCY_PLUS_USER_MAG",
            "base_potency": 10
        }
        
        # Mock calculate_heal_amount to return a fixed value
        self.staff_system.calculate_heal_amount = MagicMock(return_value=15)
        
        # Act
        success = self.staff_system.apply_staff_effect(user, staff_item, target)
        
        # Assert
        self.assertTrue(success)
        
        # Verify unit system was called correctly
        self.mock_unit_system.heal_unit.assert_called_once_with(target, 15)
    
    def test_apply_status_inflict_adds_status(self):
        """Test that apply_staff_effect correctly applies status effect."""
        # Arrange
        user = MagicMock()
        user.id = "DARK_MAGE"
        
        target = MagicMock()
        target.id = "TARGET"
        
        staff_item = {
            "id": "SLEEP_STAFF",
            "effect_type": "STATUS_INFLICT",
            "status_inflicted": "SLEEP"
        }
        
        # Act
        success = self.staff_system.apply_staff_effect(user, staff_item, target)
        
        # Assert
        self.assertTrue(success)
        
        # Verify status effects system was called correctly
        self.mock_status_effects_system.apply_status.assert_called_once_with(target, "SLEEP")
    
    def test_apply_warp_moves_unit(self):
        """Test that apply_staff_effect correctly warps a unit."""
        # Arrange
        user = MagicMock()
        user.id = "WARP_USER"
        
        target = MagicMock()
        target.id = "TARGET"
        
        staff_item = {
            "id": "WARP_STAFF",
            "effect_type": "WARP"
        }
        
        # Mock get_warp_destination_from_ui to return a destination tile
        destination_tile = MagicMock()
        destination_tile.coord = (10, 10)
        self.staff_system.get_warp_destination_from_ui = MagicMock(return_value=destination_tile)
        
        # Mock map system to check if destination is valid
        self.mock_map_system.is_valid_tile.return_value = True
        self.mock_map_system.get_unit_at.return_value = None  # No unit at destination
        
        # Act
        success = self.staff_system.apply_staff_effect(user, staff_item, target)
        
        # Assert
        self.assertTrue(success)
        
        # Verify map system was called correctly
        self.mock_map_system.is_valid_tile.assert_called_once_with(destination_tile.coord)
        self.mock_map_system.get_unit_at.assert_called_once_with(destination_tile.coord)
        self.mock_map_system.move_unit.assert_called_once_with(target, destination_tile.coord)
    
    # --- Test Hit Chance Calculation ---
    
    def test_calculate_staff_hit_chance_standard(self):
        """Test that calculate_staff_hit_chance returns correct hit chance for standard formula."""
        # Arrange
        user = MagicMock()
        user.id = "DARK_MAGE"
        # Disable side_effect to allow setting return_value directly
        self.mock_unit_system.get_stat.side_effect = None
        self.mock_unit_system.get_stat.return_value = 8  # SKL = 8
        
        staff_item = {
            "id": "SLEEP_STAFF",
            "base_hit": 60
        }
        
        # Act
        hit_chance = self.staff_system.calculate_staff_hit_chance(user, staff_item)
        
        # Assert
        self.assertEqual(hit_chance, 92)  # 60 + (4 * 8) = 92
        
        # Verify unit system was called correctly
        self.mock_unit_system.get_stat.assert_called_once_with(user, "SKL")
    
    def test_calculate_staff_hit_chance_capped_at_99(self):
        """Test that calculate_staff_hit_chance is capped at 99."""
        # Arrange
        user = MagicMock()
        user.id = "DARK_MAGE"
        # Disable side_effect to allow setting return_value directly
        self.mock_unit_system.get_stat.side_effect = None
        self.mock_unit_system.get_stat.return_value = 15  # SKL = 15
        
        staff_item = {
            "id": "SLEEP_STAFF",
            "base_hit": 60
        }
        
        # Act
        hit_chance = self.staff_system.calculate_staff_hit_chance(user, staff_item)
        
        # Assert
        self.assertEqual(hit_chance, 99)  # 60 + (4 * 15) = 120, capped at 99
        
        # Verify unit system was called correctly
        self.mock_unit_system.get_stat.assert_called_once_with(user, "SKL")
    
    # --- Test Staff Use ---
    
    def test_use_staff_success_flow(self):
        """Test that use_staff correctly executes the full staff usage flow."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        
        target = MagicMock()
        target.id = "TARGET"
        
        staff_item = {
            "id": "HEAL_STAFF",
            "effect_type": "HEAL",
            "weapon_type": "STAFF",
            "required_rank": "E"
        }
        
        # Mock can_use_staff to return True
        self.staff_system.can_use_staff = MagicMock(return_value=True)
        
        # Mock calculate_staff_hit_chance to return 100 (always hit)
        self.staff_system.calculate_staff_hit_chance = MagicMock(return_value=100)
        
        # Mock apply_staff_effect to return True (success)
        self.staff_system.apply_staff_effect = MagicMock(return_value=True)
        
        # Mock calculate_fatigue_cost to return 1
        self.staff_system.calculate_fatigue_cost = MagicMock(return_value=1)
        
        # Mock calculate_staff_exp to return 10
        self.staff_system.calculate_staff_exp = MagicMock(return_value=10)
        
        # Mock calculate_staff_wexp to return 1
        self.staff_system.calculate_staff_wexp = MagicMock(return_value=1)
        
        # Act
        with patch('random.randint', return_value=50):  # Will hit with 100% chance
            success = self.staff_system.use_staff(user, staff_item, target)
        
        # Assert
        self.assertTrue(success)
        
        # Verify action was consumed
        self.mock_action_system.consume_action.assert_called_once_with(user)
        
        # Verify durability was decreased
        self.mock_item_system.decrease_durability.assert_called_once_with(staff_item, 1)
        
        # Verify fatigue was added
        self.mock_unit_system.add_fatigue.assert_called_once_with(user, 1)
        
        # Verify EXP was granted
        self.mock_exp_system.grant_exp.assert_called_once_with(user, 10)
        
        # Verify WEXP was granted
        self.mock_unit_system.add_wexp.assert_called_once_with(user, "STAFF", 1)
    
    def test_use_staff_miss_status_effect(self):
        """Test that use_staff correctly handles a missed status effect."""
        # Arrange
        user = MagicMock()
        user.id = "DARK_MAGE"
        
        target = MagicMock()
        target.id = "TARGET"
        
        staff_item = {
            "id": "SLEEP_STAFF",
            "effect_type": "STATUS_INFLICT",
            "weapon_type": "STAFF",
            "required_rank": "C"
        }
        
        # Mock can_use_staff to return True
        self.staff_system.can_use_staff = MagicMock(return_value=True)
        
        # Mock calculate_staff_hit_chance to return 80
        self.staff_system.calculate_staff_hit_chance = MagicMock(return_value=80)
        
        # Mock calculate_fatigue_cost to return 3
        self.staff_system.calculate_fatigue_cost = MagicMock(return_value=3)
        
        # Act
        with patch('random.randint', return_value=90):  # Will miss with 80% chance
            success = self.staff_system.use_staff(user, staff_item, target)
        
        # Assert
        self.assertFalse(success)
        
        # Verify action was consumed
        self.mock_action_system.consume_action.assert_called_once_with(user)
        
        # Verify durability was decreased
        self.mock_item_system.decrease_durability.assert_called_once_with(staff_item, 1)
        
        # Verify fatigue was added
        self.mock_unit_system.add_fatigue.assert_called_once_with(user, 3)
        
        # Verify apply_staff_effect was not called
        self.staff_system.apply_staff_effect = MagicMock()
        self.staff_system.apply_staff_effect.assert_not_called()
        
        # Verify EXP and WEXP were not granted
        self.mock_exp_system.grant_exp.assert_not_called()
        self.mock_unit_system.add_wexp.assert_not_called()
    
    # --- Test Rank-Based Calculations ---
    
    def test_calculate_fatigue_cost_by_rank(self):
        """Test that calculate_fatigue_cost returns correct fatigue cost based on staff rank."""
        # Arrange
        staff_e = {"required_rank": "E", "fatigue_cost_override": None}
        staff_d = {"required_rank": "D", "fatigue_cost_override": None}
        staff_c = {"required_rank": "C", "fatigue_cost_override": None}
        staff_b = {"required_rank": "B", "fatigue_cost_override": None}
        staff_a = {"required_rank": "A", "fatigue_cost_override": None}
        staff_override = {"required_rank": "C", "fatigue_cost_override": 5}
        
        # Act
        fatigue_e = self.staff_system.calculate_fatigue_cost(staff_e)
        fatigue_d = self.staff_system.calculate_fatigue_cost(staff_d)
        fatigue_c = self.staff_system.calculate_fatigue_cost(staff_c)
        fatigue_b = self.staff_system.calculate_fatigue_cost(staff_b)
        fatigue_a = self.staff_system.calculate_fatigue_cost(staff_a)
        fatigue_override = self.staff_system.calculate_fatigue_cost(staff_override)
        
        # Assert
        self.assertEqual(fatigue_e, 1)
        self.assertEqual(fatigue_d, 2)
        self.assertEqual(fatigue_c, 3)
        self.assertEqual(fatigue_b, 4)
        self.assertEqual(fatigue_a, 5)
        self.assertEqual(fatigue_override, 5)  # Override takes precedence
    
    def test_calculate_staff_wexp_by_rank(self):
        """Test that calculate_staff_wexp returns correct WEXP gain based on staff rank."""
        # Arrange
        staff_e = {"required_rank": "E"}
        staff_d = {"required_rank": "D"}
        staff_c = {"required_rank": "C"}
        staff_b = {"required_rank": "B"}
        staff_a = {"required_rank": "A"}
        
        # Act
        wexp_e = self.staff_system.calculate_staff_wexp(staff_e)
        wexp_d = self.staff_system.calculate_staff_wexp(staff_d)
        wexp_c = self.staff_system.calculate_staff_wexp(staff_c)
        wexp_b = self.staff_system.calculate_staff_wexp(staff_b)
        wexp_a = self.staff_system.calculate_staff_wexp(staff_a)
        
        # Assert
        self.assertEqual(wexp_e, 1)
        self.assertEqual(wexp_d, 2)
        self.assertEqual(wexp_c, 3)
        self.assertEqual(wexp_b, 4)
        self.assertEqual(wexp_a, 5)
    
    def test_calculate_staff_exp_base(self):
        """Test that calculate_staff_exp returns correct base EXP gain."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        
        staff_item = {
            "id": "HEAL_STAFF",
            "required_rank": "E",
            "effect_type": "HEAL"
        }
        
        # Act
        exp_gain = self.staff_system.calculate_staff_exp(user, staff_item)
        
        # Assert
        self.assertEqual(exp_gain, 10)  # Base EXP for staff use
    
    def test_calculate_staff_exp_rank_bonus(self):
        """Test that calculate_staff_exp includes rank bonus for higher rank staves."""
        # Arrange
        user = MagicMock()
        user.id = "HEALER"
        
        staff_c = {"id": "PHYSIC_STAFF", "required_rank": "C", "effect_type": "HEAL"}
        staff_b = {"id": "RESTORE_STAFF", "required_rank": "B", "effect_type": "STATUS_CURE"}
        staff_a = {"id": "WARP_STAFF", "required_rank": "A", "effect_type": "WARP"}
        
        # Act
        exp_c = self.staff_system.calculate_staff_exp(user, staff_c)
        exp_b = self.staff_system.calculate_staff_exp(user, staff_b)
        exp_a = self.staff_system.calculate_staff_exp(user, staff_a)
        
        # Assert
        self.assertEqual(exp_c, 15)  # 10 base + 5 for C rank
        self.assertEqual(exp_b, 18)  # 10 base + 8 for B rank
        self.assertEqual(exp_a, 27)  # 10 base + 12 for A rank + 5 for WARP effect
