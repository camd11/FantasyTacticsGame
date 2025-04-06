import unittest
from unittest.mock import MagicMock, patch, call
import random

from src.gameplay_systems.combat_system import CombatSystem
from src.core_engine.game_state import StatusEffectEnum, DispositionEnum
from src.core_engine.data_provider import ItemTypeEnum, WeaponTypeEnum

# Constants for testing
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
SCROLL = ItemTypeEnum.SCROLL

# Skill constants
WRATH = "WRATH"
ADEPT = "ADEPT"
MIRACLE = "MIRACLE"
NIHIL = "NIHIL"
SOL = "SOL"
LUNA = "LUNA"
PAVISE = "PAVISE"


class TestCombatCalculator(unittest.TestCase):
    """Test cases for the combat calculation methods in CombatSystem."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_unit_system = MagicMock(name="UnitSystem")
        self.mock_map_system = MagicMock(name="MapSystem")
        self.mock_inventory_system = MagicMock(name="InventorySystem")
        
        # Create the CombatSystem instance
        self.combat_system = CombatSystem()
        self.combat_system.initialize(
            self.mock_game_state_manager,
            self.mock_data_provider,
            self.mock_unit_system,
            self.mock_map_system,
            self.mock_inventory_system
        )
        
        # Set up random seed for predictable test results
        random.seed(42)

    # --- TDD Anchors: CombatCalculator Tests ---
    
    def test_calculate_attack_speed_physical_weapon_wt_greater_than_con(self):
        """Test calculate_attack_speed when physical weapon weight > constitution."""
        # Arrange
        unit = MagicMock()
        unit.spd = 10
        unit.con = 5
        
        weapon = MagicMock()
        weapon.weight = 8
        weapon.type = "PHYSICAL"  # Not magical
        
        # Mock _is_weapon_physical to return True for this test
        self.combat_system._is_weapon_physical = MagicMock(return_value=True)
        
        # Act
        # Call the private method directly for testing
        result = self.combat_system._calculate_attack_speed(unit, weapon)
        
        # Assert
        # Expected: SPD - (WT - CON) = 10 - (8 - 5) = 7
        self.assertEqual(result, 7)
    
    def test_calculate_attack_speed_physical_weapon_wt_less_than_con(self):
        """Test calculate_attack_speed when physical weapon weight <= constitution."""
        # Arrange
        unit = MagicMock()
        unit.spd = 10
        unit.con = 8
        
        weapon = MagicMock()
        weapon.weight = 5
        weapon.type = "PHYSICAL"  # Not magical
        
        # Mock _is_weapon_physical to return True for this test
        self.combat_system._is_weapon_physical = MagicMock(return_value=True)
        
        # Act
        result = self.combat_system._calculate_attack_speed(unit, weapon)
        
        # Assert
        # Expected: SPD - 0 = 10 - 0 = 10 (no penalty when WT <= CON)
        self.assertEqual(result, 10)
    
    def test_calculate_attack_speed_magical_weapon(self):
        """Test calculate_attack_speed with magical weapon (tomes)."""
        # Arrange
        unit = MagicMock()
        unit.spd = 10
        unit.con = 8  # Should be ignored for magical weapons
        
        weapon = MagicMock()
        weapon.weight = 3
        weapon.type = "MAGICAL"
        
        # Mock _is_weapon_physical to return False for this test
        self.combat_system._is_weapon_physical = MagicMock(return_value=False)
        
        # Act
        result = self.combat_system._calculate_attack_speed(unit, weapon)
        
        # Assert
        # Expected: SPD - WT = 10 - 3 = 7 (Con doesn't offset tome weight)
        self.assertEqual(result, 7)
    
    def test_calculate_attack_speed_with_capture_penalty(self):
        """Test calculate_attack_speed with capture penalty applied."""
        # Arrange
        unit = MagicMock()
        unit.spd = 10  # This would be halved due to capture
        unit.con = 5
        
        weapon = MagicMock()
        weapon.weight = 8
        weapon.type = "PHYSICAL"
        
        # Mock _is_weapon_physical to return True for this test
        self.combat_system._is_weapon_physical = MagicMock(return_value=True)
        
        # Act
        # Pass override_spd to simulate capture penalty (SPD halved)
        result = self.combat_system._calculate_attack_speed(unit, weapon, override_spd=5)
        
        # Assert
        # Expected: (SPD/2) - (WT - CON) = 5 - (8 - 5) = 2
        self.assertEqual(result, 2)
    
    def test_calculate_hit_rate_base_calculation(self):
        """Test calculate_hit_rate with base calculation (no bonuses)."""
        # Arrange
        unit = MagicMock()
        unit.skl = 8
        unit.luk = 6
        
        weapon = MagicMock()
        weapon.hit = 80
        
        opponent = MagicMock()
        opponent.equipped_weapon = None
        
        # Mock methods to return 0 for all bonuses
        self.combat_system._get_support_bonus = MagicMock(return_value=0)
        self.combat_system._get_leadership_bonus = MagicMock(return_value=0)
        self.combat_system._get_charisma_bonus = MagicMock(return_value=0)
        self.combat_system._get_weapon_triangle_bonus = MagicMock(return_value=0)
        
        # Act
        result = self.combat_system._calculate_hit_rate(unit, weapon, opponent)
        
        # Assert
        # Expected: Weapon Hit + (2 * SKL) + LUK = 80 + (2 * 8) + 6 = 102
        self.assertEqual(result, 102)
    
    def test_calculate_hit_rate_with_weapon_triangle_advantage(self):
        """Test calculate_hit_rate with weapon triangle advantage."""
        # Arrange
        unit = MagicMock()
        unit.skl = 8
        unit.luk = 6
        
        weapon = MagicMock()
        weapon.hit = 80
        weapon.weapon_type = WeaponTypeEnum.SWORD
        
        opponent = MagicMock()
        opponent.equipped_weapon = MagicMock()
        opponent.equipped_weapon.weapon_type = WeaponTypeEnum.AXE
        
        # Mock methods for bonuses
        self.combat_system._get_support_bonus = MagicMock(return_value=0)
        self.combat_system._get_leadership_bonus = MagicMock(return_value=0)
        self.combat_system._get_charisma_bonus = MagicMock(return_value=0)
        self.combat_system._get_weapon_triangle_bonus = MagicMock(return_value=5)  # Advantage
        
        # Act
        result = self.combat_system._calculate_hit_rate(unit, weapon, opponent)
        
        # Assert
        # Expected: Weapon Hit + (2 * SKL) + LUK + WT Bonus = 80 + (2 * 8) + 6 + 5 = 107
        self.assertEqual(result, 107)
    
    def test_calculate_hit_rate_with_weapon_triangle_disadvantage(self):
        """Test calculate_hit_rate with weapon triangle disadvantage."""
        # Arrange
        unit = MagicMock()
        unit.skl = 8
        unit.luk = 6
        
        weapon = MagicMock()
        weapon.hit = 80
        weapon.weapon_type = WeaponTypeEnum.SWORD
        
        opponent = MagicMock()
        opponent.equipped_weapon = MagicMock()
        opponent.equipped_weapon.weapon_type = WeaponTypeEnum.LANCE
        
        # Mock methods for bonuses
        self.combat_system._get_support_bonus = MagicMock(return_value=0)
        self.combat_system._get_leadership_bonus = MagicMock(return_value=0)
        self.combat_system._get_charisma_bonus = MagicMock(return_value=0)
        self.combat_system._get_weapon_triangle_bonus = MagicMock(return_value=-5)  # Disadvantage
        
        # Act
        result = self.combat_system._calculate_hit_rate(unit, weapon, opponent)
        
        # Assert
        # Expected: Weapon Hit + (2 * SKL) + LUK + WT Bonus = 80 + (2 * 8) + 6 - 5 = 97
        self.assertEqual(result, 97)
    
    def test_calculate_avoid_rate_base_calculation(self):
        """Test calculate_avoid_rate with base calculation (no bonuses)."""
        # Arrange
        unit = MagicMock()
        unit.luk = 6
        unit.equipped_weapon = MagicMock()
        
        opponent = MagicMock()
        
        # Mock methods for calculations
        self.combat_system._calculate_attack_speed = MagicMock(return_value=10)  # AS = 10
        self.combat_system._get_support_bonus = MagicMock(return_value=0)
        self.combat_system._get_leadership_bonus = MagicMock(return_value=0)
        self.combat_system._get_charisma_bonus = MagicMock(return_value=0)
        self.combat_system._get_terrain_avoid_bonus = MagicMock(return_value=0)
        
        # Act
        result = self.combat_system._calculate_avoid_rate(unit, opponent)
        
        # Assert
        # Expected: (2 * AS) + LUK = (2 * 10) + 6 = 26
        self.assertEqual(result, 26)
    
    def test_calculate_avoid_rate_with_terrain_bonus_infantry(self):
        """Test calculate_avoid_rate with terrain bonus for infantry."""
        # Arrange
        unit = MagicMock()
        unit.luk = 6
        unit.equipped_weapon = MagicMock()
        unit.is_mounted = False
        unit.is_flying = False
        unit.position = (3, 4)
        
        opponent = MagicMock()
        
        # Mock methods for calculations
        self.combat_system._calculate_attack_speed = MagicMock(return_value=10)
        self.combat_system._get_support_bonus = MagicMock(return_value=0)
        self.combat_system._get_leadership_bonus = MagicMock(return_value=0)
        self.combat_system._get_charisma_bonus = MagicMock(return_value=0)
        self.combat_system._get_terrain_avoid_bonus = MagicMock(return_value=20)  # Forest gives +20 avoid
        
        # Act
        result = self.combat_system._calculate_avoid_rate(unit, opponent)
        
        # Assert
        # Expected: (2 * AS) + LUK + Terrain = (2 * 10) + 6 + 20 = 46
        self.assertEqual(result, 46)
    
    def test_calculate_battle_hit_chance_high_hit_low_avoid(self):
        """Test calculate_battle_hit_chance with high hit and low avoid (capped at 99)."""
        # Arrange
        attacker_stats = {'Hit': 120}
        defender_stats = {'Avoid': 10}
        
        # Act
        result = self.combat_system._calculate_battle_hit_chance(attacker_stats, defender_stats)
        
        # Assert
        # Expected: Hit - Avoid = 120 - 10 = 110, capped at 99
        self.assertEqual(result, 99)
    
    def test_calculate_battle_hit_chance_low_hit_high_avoid(self):
        """Test calculate_battle_hit_chance with low hit and high avoid (capped at 1)."""
        # Arrange
        attacker_stats = {'Hit': 20}
        defender_stats = {'Avoid': 40}
        
        # Act
        result = self.combat_system._calculate_battle_hit_chance(attacker_stats, defender_stats)
        
        # Assert
        # Expected: Hit - Avoid = 20 - 40 = -20, capped at 1
        self.assertEqual(result, 1)
    
    def test_calculate_battle_hit_chance_with_miracle_active(self):
        """Test calculate_battle_hit_chance with defender's Miracle skill active."""
        # Arrange
        attacker_stats = {'Hit': 85}
        defender_stats = {
            'Avoid': 25,
            'Skills': [MIRACLE],
            'current_hp': 8  # Below 10 HP threshold for Miracle
        }
        
        # Mock _unit_has_skill to return True for Miracle
        self.combat_system._unit_has_skill = MagicMock(return_value=True)
        
        # Act
        result = self.combat_system._calculate_battle_hit_chance(attacker_stats, defender_stats)
        
        # Assert
        # Expected: 1 (minimum hit chance when Miracle is active)
        self.assertEqual(result, 1)
