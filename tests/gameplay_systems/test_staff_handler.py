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


class TestStaffHandler(unittest.TestCase):
    """Test cases for the staff usage mechanics in CombatSystem."""

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

    # --- TDD Anchors: StaffHandler Tests ---
    
    def test_resolve_staff_use_heal_success(self):
        """Test resolve_staff_use with a successful healing staff."""
        # Arrange
        staff_user = MagicMock()
        staff_user.id = "U001"
        staff_user.name = "Cleric"
        
        target_unit = MagicMock()
        target_unit.id = "U002"
        target_unit.name = "Injured Unit"
        target_unit.current_hp = 10
        target_unit.max_hp = 20
        
        staff_item = MagicMock()
        staff_item.name = "Heal"
        staff_item.type = STAFF
        staff_item.base_hit = 100  # Always hits
        staff_item.weapon_type = WeaponTypeEnum.STAFF
        staff_item.required_rank = "E"
        staff_item.effects = [{'type': 'HEAL', 'amount': 10}]
        staff_item.uses = 30
        
        # Mock methods
        self.combat_system._calculate_staff_hit_chance = MagicMock(return_value=100)  # Always hits
        
        # Mock random.randint to ensure hit
        with patch('random.randint', return_value=50):  # Will hit with 100% chance
            # Act
            result = self.combat_system._resolve_staff_use(staff_user, target_unit, staff_item)
        
        # Assert
        self.assertEqual(result, "Success")
        
        # Verify healing was applied
        self.mock_game_state_manager.apply_healing.assert_called_once_with(target_unit.id, 10)
        
        # Verify staff durability was decremented
        staff_item.uses -= 1
        self.assertEqual(staff_item.uses, 29)
        
        # Verify fatigue was updated (E rank = 1 fatigue)
        self.mock_game_state_manager.update_fatigue.assert_called_once_with(staff_user.id, 1)
    
    def test_resolve_staff_use_sleep_success(self):
        """Test resolve_staff_use with a successful sleep staff."""
        # Arrange
        staff_user = MagicMock()
        staff_user.id = "U001"
        staff_user.name = "Dark Mage"
        
        target_unit = MagicMock()
        target_unit.id = "U002"
        target_unit.name = "Enemy"
        
        staff_item = MagicMock()
        staff_item.name = "Sleep"
        staff_item.type = STAFF
        staff_item.base_hit = 60  # 60% base hit
        staff_item.weapon_type = WeaponTypeEnum.STAFF
        staff_item.required_rank = "C"
        staff_item.effects = [{'type': 'STATUS', 'status': 'SLEEP', 'duration': 3}]
        staff_item.uses = 5
        
        # Mock methods
        self.combat_system._calculate_staff_hit_chance = MagicMock(return_value=80)  # 80% hit chance
        
        # Mock random.randint to ensure hit
        with patch('random.randint', return_value=50):  # Will hit with 80% chance
            # Act
            result = self.combat_system._resolve_staff_use(staff_user, target_unit, staff_item)
        
        # Assert
        self.assertEqual(result, "Success")
        
        # Verify status effect was applied
        self.mock_game_state_manager.add_status_effect.assert_called_once_with(
            target_unit.id, StatusEffectEnum.SLEEP, 3
        )
        
        # Verify staff durability was decremented
        staff_item.uses -= 1
        self.assertEqual(staff_item.uses, 4)
        
        # Verify fatigue was updated (C rank = 3 fatigue)
        self.mock_game_state_manager.update_fatigue.assert_called_once_with(staff_user.id, 3)
    
    def test_resolve_staff_use_sleep_miss(self):
        """Test resolve_staff_use with a missed sleep staff."""
        # Arrange
        staff_user = MagicMock()
        staff_user.id = "U001"
        staff_user.name = "Dark Mage"
        
        target_unit = MagicMock()
        target_unit.id = "U002"
        target_unit.name = "Enemy"
        
        staff_item = MagicMock()
        staff_item.name = "Sleep"
        staff_item.type = STAFF
        staff_item.base_hit = 60  # 60% base hit
        staff_item.weapon_type = WeaponTypeEnum.STAFF
        staff_item.required_rank = "C"
        staff_item.effects = [{'type': 'STATUS', 'status': 'SLEEP', 'duration': 3}]
        staff_item.uses = 5
        
        # Mock methods
        self.combat_system._calculate_staff_hit_chance = MagicMock(return_value=80)  # 80% hit chance
        
        # Mock random.randint to ensure miss
        with patch('random.randint', return_value=90):  # Will miss with 80% chance
            # Act
            result = self.combat_system._resolve_staff_use(staff_user, target_unit, staff_item)
        
        # Assert
        self.assertEqual(result, "Miss")
        
        # Verify status effect was NOT applied
        self.mock_game_state_manager.add_status_effect.assert_not_called()
        
        # Verify staff durability was still decremented
        staff_item.uses -= 1
        self.assertEqual(staff_item.uses, 4)
        
        # Verify fatigue was still updated (C rank = 3 fatigue)
        self.mock_game_state_manager.update_fatigue.assert_called_once_with(staff_user.id, 3)
    
    def test_resolve_staff_use_restore_curing_status(self):
        """Test resolve_staff_use with a restore staff curing status effects."""
        # Arrange
        staff_user = MagicMock()
        staff_user.id = "U001"
        staff_user.name = "Cleric"
        
        target_unit = MagicMock()
        target_unit.id = "U002"
        target_unit.name = "Silenced Unit"
        target_unit.status_effects = [StatusEffectEnum.SILENCE]
        
        staff_item = MagicMock()
        staff_item.name = "Restore"
        staff_item.type = STAFF
        staff_item.base_hit = 100  # Always hits
        staff_item.weapon_type = WeaponTypeEnum.STAFF
        staff_item.required_rank = "C"
        staff_item.effects = [{'type': 'RESTORE'}]
        staff_item.uses = 10
        
        # Mock methods
        self.combat_system._calculate_staff_hit_chance = MagicMock(return_value=100)  # Always hits
        
        # Mock random.randint to ensure hit
        with patch('random.randint', return_value=50):  # Will hit with 100% chance
            # Act
            result = self.combat_system._resolve_staff_use(staff_user, target_unit, staff_item)
        
        # Assert
        self.assertEqual(result, "Success")
        
        # Verify status effects were cleared
        self.mock_game_state_manager.clear_status_effects.assert_called_once_with(target_unit.id)
        
        # Verify staff durability was decremented
        staff_item.uses -= 1
        self.assertEqual(staff_item.uses, 9)
        
        # Verify fatigue was updated (C rank = 3 fatigue)
        self.mock_game_state_manager.update_fatigue.assert_called_once_with(staff_user.id, 3)
    
    def test_resolve_staff_use_repair_restoring_durability(self):
        """Test resolve_staff_use with a repair staff restoring weapon durability."""
        # Arrange
        staff_user = MagicMock()
        staff_user.id = "U001"
        staff_user.name = "Hammerne User"
        
        target_unit = MagicMock()
        target_unit.id = "U002"
        target_unit.name = "Weapon User"
        target_unit.equipped_weapon_index = 0
        
        target_weapon = MagicMock()
        target_weapon.current_durability = 10
        target_weapon.max_durability = 45
        target_unit.inventory = [target_weapon]
        
        staff_item = MagicMock()
        staff_item.name = "Hammerne"
        staff_item.type = STAFF
        staff_item.base_hit = 100  # Always hits
        staff_item.weapon_type = WeaponTypeEnum.STAFF
        staff_item.required_rank = "A"
        staff_item.effects = [{'type': 'REPAIR'}]
        staff_item.uses = 3
        
        # Mock methods
        self.combat_system._calculate_staff_hit_chance = MagicMock(return_value=100)  # Always hits
        
        # Mock random.randint to ensure hit
        with patch('random.randint', return_value=50):  # Will hit with 100% chance
            # Act
            result = self.combat_system._resolve_staff_use(staff_user, target_unit, staff_item)
        
        # Assert
        self.assertEqual(result, "Success")
        
        # Verify weapon durability was restored
        self.mock_inventory_system.repair_item.assert_called_once_with(
            target_unit.id, target_unit.equipped_weapon_index
        )
        
        # Verify staff durability was decremented
        staff_item.uses -= 1
        self.assertEqual(staff_item.uses, 2)
        
        # Verify fatigue was updated (A rank = 5 fatigue)
        self.mock_game_state_manager.update_fatigue.assert_called_once_with(staff_user.id, 5)
    
    def test_calculate_staff_hit_chance(self):
        """Test calculate_staff_hit_chance with base calculation."""
        # Arrange
        staff_user = MagicMock()
        staff_user.skl = 8
        
        staff_item = MagicMock()
        staff_item.base_hit = 60
        
        # Act
        result = self.combat_system._calculate_staff_hit_chance(staff_user, staff_item)
        
        # Assert
        # Expected: Base Hit + (4 * SKL) = 60 + (4 * 8) = 60 + 32 = 92
        self.assertEqual(result, 92)
    
    def test_calculate_staff_hit_chance_high_skill(self):
        """Test calculate_staff_hit_chance with high skill (capped at 99)."""
        # Arrange
        staff_user = MagicMock()
        staff_user.skl = 15  # Very high skill
        
        staff_item = MagicMock()
        staff_item.base_hit = 60
        
        # Act
        result = self.combat_system._calculate_staff_hit_chance(staff_user, staff_item)
        
        # Assert
        # Expected: Base Hit + (4 * SKL) = 60 + (4 * 15) = 60 + 60 = 120, capped at 99
        self.assertEqual(result, 99)
    
    def test_get_staff_fatigue_cost(self):
        """Test get_staff_fatigue_cost returns correct fatigue cost based on staff rank."""
        # Arrange
        staff_data_e = MagicMock()
        staff_data_e.required_rank = "E"
        
        staff_data_d = MagicMock()
        staff_data_d.required_rank = "D"
        
        staff_data_c = MagicMock()
        staff_data_c.required_rank = "C"
        
        staff_data_b = MagicMock()
        staff_data_b.required_rank = "B"
        
        staff_data_a = MagicMock()
        staff_data_a.required_rank = "A"
        
        # Act
        result_e = self.combat_system._get_staff_fatigue_cost(staff_data_e)
        result_d = self.combat_system._get_staff_fatigue_cost(staff_data_d)
        result_c = self.combat_system._get_staff_fatigue_cost(staff_data_c)
        result_b = self.combat_system._get_staff_fatigue_cost(staff_data_b)
        result_a = self.combat_system._get_staff_fatigue_cost(staff_data_a)
        
        # Assert
        self.assertEqual(result_e, 1)  # E rank = 1 fatigue
        self.assertEqual(result_d, 2)  # D rank = 2 fatigue
        self.assertEqual(result_c, 3)  # C rank = 3 fatigue
        self.assertEqual(result_b, 4)  # B rank = 4 fatigue
        self.assertEqual(result_a, 5)  # A rank = 5 fatigue