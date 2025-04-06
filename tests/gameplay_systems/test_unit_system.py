import unittest
from unittest.mock import MagicMock, patch, call
import random

from src.gameplay_systems.unit_system import UnitSystem
from src.core_engine.game_state import StatusEffectEnum, DispositionEnum
from src.core_engine.data_provider import StatEnum, RankEnum, WeaponTypeEnum

# Constants for testing
STR = StatEnum.STR
MAG = StatEnum.MAG
SKL = StatEnum.SKL
SPD = StatEnum.SPD
LUK = StatEnum.LUK
DEF = StatEnum.DEF
CON = StatEnum.CON
MOV = StatEnum.MOV
HP = StatEnum.HP

SLEEP = StatusEffectEnum.SLEEP
ACTIVE = DispositionEnum.ACTIVE


class TestUnitSystem(unittest.TestCase):
    """Test cases for the UnitSystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the UnitSystem instance
        self.unit_system = UnitSystem()
        self.unit_system.initialize(self.mock_game_state_manager, self.mock_data_provider)
        
        # Mock internal methods that are used in assertions
        self.unit_system._get_class_max_rank = MagicMock(name="_get_class_max_rank")

    # TDD: Test get_unit_details retrieves all relevant info for display/logic
    def test_get_unit_details_retrieves_complete_info(self):
        """Test that get_unit_details retrieves all relevant information for a unit."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit state
        mock_unit = MagicMock()
        mock_unit.class_id = "C001"
        mock_unit.inventory = [MagicMock(), MagicMock()]
        
        # Mock class data
        mock_class_data = MagicMock()
        mock_class_data.name = "Cavalier"
        
        # Mock item data
        mock_item_data1 = MagicMock()
        mock_item_data1.name = "Iron Sword"
        mock_item_data1.max_durability = 46
        
        mock_item_data2 = MagicMock()
        mock_item_data2.name = "Iron Lance"
        mock_item_data2.max_durability = 45
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class_data.return_value = mock_class_data
        self.mock_data_provider.get_item_data.side_effect = [mock_item_data1, mock_item_data2]
        
        # Mock calculate_current_combat_stats to return a predefined set of stats
        self.unit_system.calculate_current_combat_stats = MagicMock(return_value={
            'atk': 10, 'AS': 8, 'hit': 85, 'avo': 20, 'crit': 5, 'ddg': 3, 'rng': "1", 'FCM': 1
        })
        
        # Act
        result = self.unit_system.get_unit_details(unit_id)
        
        # Assert
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_class_data.assert_called_once_with(mock_unit.class_id)
        self.assertEqual(result['state'], mock_unit)
        self.assertEqual(result['class_info'], mock_class_data)
        self.assertEqual(len(result['inventory_details']), 2)
        self.assertEqual(result['inventory_details'][0]['name'], "Iron Sword")
        self.assertEqual(result['inventory_details'][1]['name'], "Iron Lance")
        self.assertEqual(result['calculated_stats']['atk'], 10)
        self.assertEqual(result['calculated_stats']['hit'], 85)
    
    def test_get_unit_details_returns_none_for_invalid_unit(self):
        """Test that get_unit_details returns None for an invalid unit."""
        # Arrange
        unit_id = "INVALID"
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.unit_system.get_unit_details(unit_id)
        
        # Assert
        self.assertIsNone(result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_class_data.assert_not_called()

    # TDD: Test calculate_current_combat_stats reflects base stats, items, status, supports, terrain etc.
    def test_calculate_current_combat_stats_with_physical_weapon(self):
        """Test calculate_current_combat_stats correctly calculates stats with a physical weapon."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with base stats and equipped weapon
        mock_unit = MagicMock()
        mock_unit.base_stats = {
            STR: 8, MAG: 2, SKL: 7, SPD: 9, LUK: 6, DEF: 5, CON: 7, MOV: 7
        }
        mock_unit.equipped_weapon_index = 0
        mock_unit.inventory = [MagicMock()]
        mock_unit.carrying_unit_id = None
        mock_unit.is_captured = False
        mock_unit.has_status = MagicMock(return_value=False)
        mock_unit.faction = "PLAYER"
        mock_unit.position = (5, 5)
        mock_unit.pcc = 1  # Follow-up Critical Multiplier
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.weapon_type = "SWORD"
        mock_weapon.might = 5
        mock_weapon.hit = 80
        mock_weapon.crit = 0
        mock_weapon.weight = 5
        mock_weapon.range_min = 1
        mock_weapon.range_max = 1
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_weapon
        
        # Mock helper methods
        self.unit_system._is_weapon_physical = MagicMock(return_value=True)
        self.unit_system._is_weapon_magical = MagicMock(return_value=False)
        self.unit_system._is_weapon_tome = MagicMock(return_value=False)
        self.unit_system.get_total_support_bonus = MagicMock(return_value=0)
        self.unit_system.get_total_leadership_bonus = MagicMock(return_value=0)
        self.unit_system.get_total_charisma_bonus = MagicMock(return_value=0)
        self.unit_system._get_terrain_bonuses = MagicMock(return_value={'def': 0, 'avo': 0})
        self.unit_system.can_unit_benefit_from_terrain = MagicMock(return_value=True)
        
        # Act
        result = self.unit_system.calculate_current_combat_stats(unit_id)
        
        # Assert
        # Expected calculations:
        # Atk = STR + weapon might = 8 + 5 = 13
        # AS = SPD - max(0, weight - CON) = 9 - max(0, 5 - 7) = 9 - 0 = 9
        # Hit = weapon hit + SKL*2 + LUK = 80 + 7*2 + 6 = 100
        # Avo = AS*2 + LUK = 9*2 + 6 = 24
        # Crit = weapon crit + SKL = 0 + 7 = 7
        # Ddg = LUK // 2 = 6 // 2 = 3
        # Rng = "1"
        # FCM = 1
        self.assertEqual(result['atk'], 13)
        self.assertEqual(result['AS'], 9)
        self.assertEqual(result['hit'], 100)
        self.assertEqual(result['avo'], 24)
        self.assertEqual(result['crit'], 7)
        self.assertEqual(result['ddg'], 3)
        self.assertEqual(result['rng'], "1")
        self.assertEqual(result['FCM'], 1)
    
    def test_calculate_current_combat_stats_with_status_penalties(self):
        """Test calculate_current_combat_stats correctly applies status penalties."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with base stats and sleep status
        mock_unit = MagicMock()
        mock_unit.base_stats = {
            STR: 8, MAG: 2, SKL: 7, SPD: 9, LUK: 6, DEF: 5, CON: 7, MOV: 7
        }
        mock_unit.equipped_weapon_index = 0
        mock_unit.inventory = [MagicMock()]
        mock_unit.carrying_unit_id = None
        mock_unit.is_captured = False
        mock_unit.has_status = MagicMock(side_effect=lambda status: status == SLEEP)
        mock_unit.faction = "PLAYER"
        mock_unit.position = (5, 5)
        mock_unit.pcc = 1
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.weapon_type = "SWORD"
        mock_weapon.might = 5
        mock_weapon.hit = 80
        mock_weapon.crit = 0
        mock_weapon.weight = 5
        mock_weapon.range_min = 1
        mock_weapon.range_max = 1
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_weapon
        
        # Mock helper methods
        self.unit_system._is_weapon_physical = MagicMock(return_value=True)
        self.unit_system._is_weapon_magical = MagicMock(return_value=False)
        self.unit_system._is_weapon_tome = MagicMock(return_value=False)
        self.unit_system.get_total_support_bonus = MagicMock(return_value=0)
        self.unit_system.get_total_leadership_bonus = MagicMock(return_value=0)
        self.unit_system.get_total_charisma_bonus = MagicMock(return_value=0)
        self.unit_system._get_terrain_bonuses = MagicMock(return_value={'def': 0, 'avo': 0})
        self.unit_system.can_unit_benefit_from_terrain = MagicMock(return_value=True)
        
        # Act
        result = self.unit_system.calculate_current_combat_stats(unit_id)
        
        # Assert
        # Expected calculations with sleep penalties (halved STR, MAG, SKL, SPD, DEF):
        # Atk = STR/2 + weapon might = 8/2 + 5 = 4 + 5 = 9
        # AS = SPD/2 - max(0, weight - CON) = 9/2 - max(0, 5 - 7) = 4 - 0 = 4
        # Hit = weapon hit + (SKL/2)*2 + LUK = 80 + (7/2)*2 + 6 = 80 + 6 + 6 = 92
        # Avo = AS*2 + LUK = 4*2 + 6 = 14
        # Crit = weapon crit + SKL/2 = 0 + 7/2 = 3
        # Ddg = LUK // 2 = 6 // 2 = 3 (not affected by sleep)
        self.assertEqual(result['atk'], 9)
        self.assertEqual(result['AS'], 4)
        self.assertEqual(result['hit'], 92)
        self.assertEqual(result['avo'], 14)
        self.assertEqual(result['crit'], 3)
        self.assertEqual(result['ddg'], 3)

    # TDD: Test support bonus calculation considers range and stacking cap
    def test_get_total_support_bonus_with_nearby_partners(self):
        """Test get_total_support_bonus correctly calculates bonuses from nearby support partners."""
        # Arrange
        unit_id = "U001"
        stat_type = "hit"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.position = (5, 5)
        
        # Mock support partners
        mock_partner1 = MagicMock()
        mock_partner1.position = (6, 5)  # Adjacent (distance 1)
        mock_partner1.disposition = ACTIVE
        
        mock_partner2 = MagicMock()
        mock_partner2.position = (7, 7)  # Distance 4 (outside support range)
        mock_partner2.disposition = ACTIVE
        
        mock_partner3 = MagicMock()
        mock_partner3.position = (3, 5)  # Distance 2 (within support range)
        mock_partner3.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            unit_id: mock_unit,
            "P001": mock_partner1,
            "P002": mock_partner2,
            "P003": mock_partner3
        }.get(id)
        
        # Mock support partners data
        support_partners = [
            {'partner_id': 'P001', 'bonus': 10},
            {'partner_id': 'P002', 'bonus': 15},
            {'partner_id': 'P003', 'bonus': 25}
        ]
        self.mock_data_provider.get_support_partners.return_value = support_partners
        
        # Mock distance calculation
        self.unit_system._calculate_distance = MagicMock(side_effect=lambda pos1, pos2:
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))
        
        # Act
        result = self.unit_system.get_total_support_bonus(unit_id, stat_type)
        
        # Assert
        # Expected: Partner1 (10) + Partner3 (25) = 35, but capped at 30
        self.assertEqual(result, 30)
        self.mock_game_state_manager.get_unit.assert_has_calls([
            call(unit_id),
            call("P001"),
            call("P002"),
            call("P003")
        ], any_order=True)
        self.mock_data_provider.get_support_partners.assert_called_once_with(unit_id)
    
    def test_get_total_support_bonus_returns_zero_for_invalid_unit(self):
        """Test get_total_support_bonus returns zero for an invalid unit."""
        # Arrange
        unit_id = "INVALID"
        stat_type = "hit"
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.unit_system.get_total_support_bonus(unit_id, stat_type)
        
        # Assert
        self.assertEqual(result, 0)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_support_partners.assert_not_called()

    # TDD: Test leadership bonus calculation sums stars correctly
    def test_get_total_leadership_bonus_sums_stars_correctly(self):
        """Test get_total_leadership_bonus correctly sums leadership stars from active units."""
        # Arrange
        faction = "PLAYER"
        stat_type = "hit"
        
        # Mock units with leadership stars
        mock_unit1 = MagicMock()
        mock_unit1.leadership_stars = 2
        mock_unit1.disposition = ACTIVE
        
        mock_unit2 = MagicMock()
        mock_unit2.leadership_stars = 3
        mock_unit2.disposition = ACTIVE
        
        mock_unit3 = MagicMock()
        mock_unit3.leadership_stars = 1
        mock_unit3.disposition = "DEAD"  # Inactive unit
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = [
            mock_unit1, mock_unit2, mock_unit3
        ]
        
        # Act
        result = self.unit_system.get_total_leadership_bonus(faction, stat_type)
        
        # Assert
        # Expected: (2 + 3) * 3 = 15 (only active units, 3 hit/avo per star)
        self.assertEqual(result, 15)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_get_total_leadership_bonus_returns_zero_for_non_hit_avo_stats(self):
        """Test get_total_leadership_bonus returns zero for stats other than hit/avo."""
        # Arrange
        faction = "PLAYER"
        stat_type = "crit"  # Leadership doesn't affect crit
        
        # Act
        result = self.unit_system.get_total_leadership_bonus(faction, stat_type)
        
        # Assert
        self.assertEqual(result, 0)
        self.mock_game_state_manager.get_units_by_faction.assert_not_called()

    # TDD: Test terrain benefit check considers mounted/flying status
    def test_can_unit_benefit_from_terrain_for_different_unit_types(self):
        """Test can_unit_benefit_from_terrain correctly determines if a unit benefits from terrain."""
        # Arrange
        infantry_id = "I001"
        mounted_id = "M001"
        dismounted_id = "D001"
        flying_id = "F001"
        
        # Mock units
        mock_infantry = MagicMock()
        mock_infantry.class_id = "C001"
        
        mock_mounted = MagicMock()
        mock_mounted.class_id = "C002"
        
        mock_dismounted = MagicMock()
        mock_dismounted.class_id = "C002"
        
        mock_flying = MagicMock()
        mock_flying.class_id = "C003"
        
        # Mock class data
        mock_infantry_class = MagicMock()
        mock_infantry_class.movement_type = "INFANTRY"
        
        mock_mounted_class = MagicMock()
        mock_mounted_class.movement_type = "CAVALRY"
        
        mock_flying_class = MagicMock()
        mock_flying_class.movement_type = "FLYING"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            infantry_id: mock_infantry,
            mounted_id: mock_mounted,
            dismounted_id: mock_dismounted,
            flying_id: mock_flying
        }.get(id)
        
        self.mock_data_provider.get_class_data.side_effect = lambda class_id: {
            "C001": mock_infantry_class,
            "C002": mock_mounted_class,
            "C003": mock_flying_class
        }.get(class_id)
        
        # Mock mounted/dismounted checks
        self.unit_system._is_class_mounted = MagicMock(side_effect=lambda class_id:
            class_id in ["C002"])
        
        self.unit_system._is_unit_dismounted = MagicMock(side_effect=lambda unit:
            unit == mock_dismounted)
        
        # Act
        infantry_result = self.unit_system.can_unit_benefit_from_terrain(infantry_id)
        mounted_result = self.unit_system.can_unit_benefit_from_terrain(mounted_id)
        dismounted_result = self.unit_system.can_unit_benefit_from_terrain(dismounted_id)
        flying_result = self.unit_system.can_unit_benefit_from_terrain(flying_id)
        
        # Assert
        self.assertTrue(infantry_result, "Infantry units should benefit from terrain")
        self.assertFalse(mounted_result, "Mounted units should not benefit from terrain")
        self.assertTrue(dismounted_result, "Dismounted units should benefit from terrain")
        self.assertFalse(flying_result, "Flying units should not benefit from terrain")

    # TDD: Test level up applies growths correctly respecting caps
    def test_trigger_level_up_applies_growths_correctly(self):
        """Test trigger_level_up correctly applies stat growths based on RNG."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.level = 5
        mock_unit.experience = 100
        mock_unit.base_stats = {
            STR: 8, MAG: 2, SKL: 7, SPD: 9, LUK: 6, DEF: 5, CON: 7, MOV: 7, HP: 25
        }
        mock_unit.max_hp = 25
        mock_unit.current_hp = 20
        mock_unit.growth_rates = {
            STR: 40, MAG: 10, SKL: 35, SPD: 45, LUK: 30, DEF: 25, CON: 5, MOV: 5, HP: 70
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock class caps
        class_caps = {
            STR: 20, MAG: 20, SKL: 20, SPD: 20, LUK: 30, DEF: 20, CON: 15, MOV: 10, HP: 60
        }
        self.unit_system._get_class_caps = MagicMock(return_value=class_caps)
        
        # Mock random_chance to control which stats increase
        # For this test, let's say STR, SPD, LUK, and HP increase
        self.unit_system._random_chance = MagicMock(side_effect=lambda percentage:
            percentage in [40, 45, 30, 70])  # STR, SPD, LUK, HP growths
        
        # Act
        result = self.unit_system.trigger_level_up(unit_id)
        
        # Assert
        # Expected stat gains: STR+1, SPD+1, LUK+1, HP+1
        self.assertEqual(mock_unit.base_stats[STR], 9)
        self.assertEqual(mock_unit.base_stats[MAG], 2)  # No change
        self.assertEqual(mock_unit.base_stats[SKL], 7)  # No change
        self.assertEqual(mock_unit.base_stats[SPD], 10)
        self.assertEqual(mock_unit.base_stats[LUK], 7)
        self.assertEqual(mock_unit.base_stats[DEF], 5)  # No change
        self.assertEqual(mock_unit.base_stats[CON], 7)  # No change
        self.assertEqual(mock_unit.base_stats[MOV], 7)  # No change
        self.assertEqual(mock_unit.base_stats[HP], 26)
        
        # Check level and experience reset
        self.assertEqual(mock_unit.level, 6)
        self.assertEqual(mock_unit.experience, 0)
        
        # Check HP update
        self.assertEqual(mock_unit.max_hp, 26)
        self.assertEqual(mock_unit.current_hp, 21)  # Healed by the HP gain
        
        # Check returned stat gains
        self.assertEqual(result[STR], 1)
        self.assertEqual(result[SPD], 1)
        self.assertEqual(result[LUK], 1)
        self.assertEqual(result[HP], 1)
        self.assertEqual(len(result), 4)  # Only 4 stats increased
    
    def test_trigger_level_up_respects_stat_caps(self):
        """Test trigger_level_up respects class stat caps."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with stats at or near caps
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.level = 19
        mock_unit.experience = 100
        mock_unit.base_stats = {
            STR: 19, MAG: 20, SKL: 20, SPD: 20, LUK: 29, DEF: 20, CON: 15, MOV: 10, HP: 59
        }
        mock_unit.max_hp = 59
        mock_unit.current_hp = 59
        mock_unit.growth_rates = {
            STR: 40, MAG: 10, SKL: 35, SPD: 45, LUK: 30, DEF: 25, CON: 5, MOV: 5, HP: 70
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock class caps
        class_caps = {
            STR: 20, MAG: 20, SKL: 20, SPD: 20, LUK: 30, DEF: 20, CON: 15, MOV: 10, HP: 60
        }
        self.unit_system._get_class_caps = MagicMock(return_value=class_caps)
        
        # Mock random_chance to return True for all stats
        # This would normally increase all stats, but caps should prevent some
        self.unit_system._random_chance = MagicMock(return_value=True)
        
        # Act
        result = self.unit_system.trigger_level_up(unit_id)
        
        # Assert
        # Expected stat gains: STR+1, LUK+1, HP+1 (others at cap)
        self.assertEqual(mock_unit.base_stats[STR], 20)  # Increased to cap
        self.assertEqual(mock_unit.base_stats[MAG], 20)  # Already at cap
        self.assertEqual(mock_unit.base_stats[SKL], 20)  # Already at cap
        self.assertEqual(mock_unit.base_stats[SPD], 20)  # Already at cap
        self.assertEqual(mock_unit.base_stats[LUK], 30)  # Increased to cap
        self.assertEqual(mock_unit.base_stats[DEF], 20)  # Already at cap
        self.assertEqual(mock_unit.base_stats[CON], 15)  # Already at cap
        self.assertEqual(mock_unit.base_stats[MOV], 10)  # Already at cap
        self.assertEqual(mock_unit.base_stats[HP], 60)  # Increased to cap
        
        # Check returned stat gains
        self.assertEqual(result[STR], 1)
        self.assertEqual(result[LUK], 1)
        self.assertEqual(result[HP], 1)
        self.assertEqual(len(result), 3)  # Only 3 stats increased

    # TDD: Test weapon rank up occurs at correct WExp thresholds
    def test_trigger_weapon_rank_up_at_threshold(self):
        """Test trigger_weapon_rank_up correctly increases rank when WExp threshold is reached."""
        # Arrange
        unit_id = "U001"
        weapon_type = WeaponTypeEnum.SWORD
        
        # Mock unit with weapon ranks and WExp
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.class_id = "C001"
        mock_unit.weapon_ranks = {weapon_type: RankEnum.D}
        mock_unit.weapon_exp = {weapon_type: 100}  # Threshold for C rank
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock next rank info
        self.unit_system._get_next_weapon_rank_info = MagicMock(return_value=(RankEnum.C, 100))
        
        # Mock class max rank check
        self.unit_system._get_class_max_rank = MagicMock(return_value=RankEnum.A)
        self.unit_system._is_rank_higher = MagicMock(return_value=-1)  # Next rank is lower than max
        
        # Act
        result = self.unit_system.trigger_weapon_rank_up(unit_id, weapon_type)
        
        # Assert
        self.assertEqual(result, RankEnum.C)
        self.assertEqual(mock_unit.weapon_ranks[weapon_type], RankEnum.C)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.unit_system._get_next_weapon_rank_info.assert_called_once_with(RankEnum.D)
        self.unit_system._get_class_max_rank.assert_called_once_with(mock_unit.class_id, weapon_type)
        self.unit_system._is_rank_higher.assert_called_once_with(RankEnum.C, RankEnum.A)
    
    def test_trigger_weapon_rank_up_below_threshold(self):
        """Test trigger_weapon_rank_up returns None when WExp is below threshold."""
        # Arrange
        unit_id = "U001"
        weapon_type = WeaponTypeEnum.SWORD
        
        # Mock unit with weapon ranks and WExp
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.class_id = "C001"
        mock_unit.weapon_ranks = {weapon_type: RankEnum.D}
        mock_unit.weapon_exp = {weapon_type: 80}  # Below threshold for C rank
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock next rank info
        self.unit_system._get_next_weapon_rank_info = MagicMock(return_value=(RankEnum.C, 100))
        
        # Act
        result = self.unit_system.trigger_weapon_rank_up(unit_id, weapon_type)
        
        # Assert
        self.assertIsNone(result)
        self.assertEqual(mock_unit.weapon_ranks[weapon_type], RankEnum.D)  # No change
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.unit_system._get_next_weapon_rank_info.assert_called_once_with(RankEnum.D)
        # Check that _get_class_max_rank was not called
        self.assertEqual(self.unit_system._get_class_max_rank.call_count, 0)
    
    def test_trigger_weapon_rank_up_at_class_max_rank(self):
        """Test trigger_weapon_rank_up respects class max rank."""
        # Arrange
        unit_id = "U001"
        weapon_type = WeaponTypeEnum.SWORD
        
        # Mock unit with weapon ranks and WExp
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.class_id = "C001"
        mock_unit.weapon_ranks = {weapon_type: RankEnum.B}
        mock_unit.weapon_exp = {weapon_type: 200}  # Threshold for A rank
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Mock next rank info
        self.unit_system._get_next_weapon_rank_info = MagicMock(return_value=(RankEnum.A, 200))
        
        # Mock class max rank check - B is max for this class
        self.unit_system._get_class_max_rank = MagicMock(return_value=RankEnum.B)
        self.unit_system._is_rank_higher = MagicMock(return_value=1)  # Next rank is higher than max
        
        # Act
        result = self.unit_system.trigger_weapon_rank_up(unit_id, weapon_type)
        
        # Assert
        self.assertIsNone(result)
        self.assertEqual(mock_unit.weapon_ranks[weapon_type], RankEnum.B)  # No change
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.unit_system._get_next_weapon_rank_info.assert_called_once_with(RankEnum.B)
        self.unit_system._get_class_max_rank.assert_called_once_with(mock_unit.class_id, weapon_type)
        self.unit_system._is_rank_higher.assert_called_once_with(RankEnum.A, RankEnum.B)

    # TDD: Test promotion applies bonuses, resets level, updates class/ranks
    def test_trigger_promotion_applies_bonuses_and_updates_class(self):
        """Test trigger_promotion correctly applies promotion bonuses and updates class."""
        # Arrange
        unit_id = "U001"
        promotion_item_id = "MASTER_SEAL"
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.name = "Leif"
        mock_unit.class_id = "C001"  # Social Knight
        mock_unit.level = 10
        mock_unit.experience = 50
        mock_unit.base_stats = {
            STR: 8, MAG: 2, SKL: 7, SPD: 9, LUK: 6, DEF: 5, CON: 7, MOV: 7, HP: 25
        }
        mock_unit.max_hp = 25
        mock_unit.current_hp = 20
        mock_unit.weapon_ranks = {"SWORD": RankEnum.C, "LANCE": RankEnum.D}
        mock_unit.weapon_exp = {"SWORD": 50, "LANCE": 20}
        
        # Mock class data
        mock_class_data = MagicMock()
        mock_class_data.name = "Social Knight"
        mock_class_data.promotion_options = {promotion_item_id: "C002"}  # Paladin
        
        mock_promoted_class_data = MagicMock()
        mock_promoted_class_data.name = "Paladin"
        mock_promoted_class_data.base_stats = {
            STR: 5, MAG: 1, SKL: 5, SPD: 6, LUK: 0, DEF: 5, CON: 8, MOV: 8, HP: 20
        }
        mock_promoted_class_data.max_stats = {
            STR: 20, MAG: 20, SKL: 20, SPD: 20, LUK: 30, DEF: 20, CON: 15, MOV: 10, HP: 60
        }
        
        # Mock promotion gains
        mock_promotion_gains = MagicMock()
        mock_promotion_gains.stat_gains = {
            STR: 2, MAG: 0, SKL: 2, SPD: 1, LUK: 0, DEF: 2, CON: 1, MOV: 1, HP: 3
        }
        mock_promotion_gains.rank_changes = {
            "SWORD": "+1",  # C -> B
            "LANCE": "+1",  # D -> C
            "AXE": "E"      # None -> E
        }
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_class_data.side_effect = lambda class_id: {
            "C001": mock_class_data,
            "C002": mock_promoted_class_data
        }.get(class_id)
        self.mock_data_provider.get_promotion_gains.return_value = mock_promotion_gains
        
        # Mock rank increase
        self.unit_system._apply_rank_increase = MagicMock(side_effect=lambda current_rank, change: {
            (RankEnum.C, "+1"): RankEnum.B,
            (RankEnum.D, "+1"): RankEnum.C,
            (None, "E"): RankEnum.E
        }.get((current_rank, change)))
        
        # Act
        result = self.unit_system.trigger_promotion(unit_id, promotion_item_id)
        
        # Assert
        self.assertTrue(result)
        
        # Check class update
        self.assertEqual(mock_unit.class_id, "C002")
        
        # Check level and experience reset
        self.assertEqual(mock_unit.level, 1)
        self.assertEqual(mock_unit.experience, 0)
        
        # Check stat increases
        # Expected: Base + Promotion Gain, but at least new class base
        self.assertEqual(mock_unit.base_stats[STR], 10)  # 8 + 2
        self.assertEqual(mock_unit.base_stats[MAG], 2)   # 2 + 0 (no change)
        self.assertEqual(mock_unit.base_stats[SKL], 9)   # 7 + 2
        self.assertEqual(mock_unit.base_stats[SPD], 10)  # 9 + 1
        self.assertEqual(mock_unit.base_stats[LUK], 6)   # 6 + 0 (no change)
        self.assertEqual(mock_unit.base_stats[DEF], 7)   # 5 + 2
        self.assertEqual(mock_unit.base_stats[CON], 8)   # 7 + 1
        self.assertEqual(mock_unit.base_stats[MOV], 8)   # 7 + 1
        self.assertEqual(mock_unit.base_stats[HP], 28)   # 25 + 3
        
        # Check HP update
        self.assertEqual(mock_unit.max_hp, 28)
        self.assertEqual(mock_unit.current_hp, 23)  # 20 + 3 (HP gain)
        
        # Check weapon rank updates
        self.assertEqual(mock_unit.weapon_ranks["SWORD"], RankEnum.B)  # C -> B
        self.assertEqual(mock_unit.weapon_ranks["LANCE"], RankEnum.C)  # D -> C
        self.assertEqual(mock_unit.weapon_ranks["AXE"], RankEnum.E)    # None -> E
        
        # Check weapon exp for new weapon type
        self.assertEqual(mock_unit.weapon_exp["AXE"], 0)


if __name__ == '__main__':
    unittest.main()

    # TDD: Test charisma bonus calculation considers range and stacking
    def test_get_total_charisma_bonus_counts_nearby_units_with_charisma(self):
        """Test get_total_charisma_bonus correctly counts nearby units with Charisma skill."""
        # Arrange
        position = (5, 5)
        faction = "PLAYER"
        stat_type = "hit"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.position = (6, 5)  # Adjacent (distance 1)
        mock_unit1.disposition = ACTIVE
        
        mock_unit2 = MagicMock()
        mock_unit2.position = (7, 7)  # Distance 4 (outside charisma range)
        mock_unit2.disposition = ACTIVE
        
        mock_unit3 = MagicMock()
        mock_unit3.position = (3, 5)  # Distance 2 (within charisma range)
        mock_unit3.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = [
            mock_unit1, mock_unit2, mock_unit3
        ]
        
        # Mock charisma skill check
        self.unit_system._has_charisma_skill = MagicMock(side_effect=lambda unit:
            unit in [mock_unit1, mock_unit3])  # Units 1 and 3 have Charisma
        
        # Mock distance calculation
        self.unit_system._calculate_distance = MagicMock(side_effect=lambda pos1, pos2:
            abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))
        
        # Act
        result = self.unit_system.get_total_charisma_bonus(position, faction, stat_type)
        
        # Assert
        # Expected: 2 units with Charisma within range * 10 = 20
        self.assertEqual(result, 20)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_get_total_charisma_bonus_returns_zero_for_non_hit_avo_stats(self):
        """Test get_total_charisma_bonus returns zero for stats other than hit/avo."""
        # Arrange
        position = (5, 5)
        faction = "PLAYER"
        stat_type = "crit"  # Charisma doesn't affect crit
        
        # Act
        result = self.unit_system.get_total_charisma_bonus(position, faction, stat_type)
        
        # Assert
        self.assertEqual(result, 0)
        self.mock_game_state_manager.get_units_by_faction.assert_not_called()
