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


class TestCaptureHandler(unittest.TestCase):
    """Test cases for the capture mechanics in CombatSystem."""

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

    # --- TDD Anchors: CaptureHandler Tests ---
    
    def test_check_capture_conditions_attacker_con_greater_than_target(self):
        """Test check_capture_conditions when attacker's Con > target's Con."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 10
        attacker.is_mounted = False
        
        target = MagicMock()
        target.con = 8
        target.is_mounted = False
        target.is_capture_immune = False
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertTrue(result)
    
    def test_check_capture_conditions_attacker_mounted(self):
        """Test check_capture_conditions when attacker is mounted."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 8
        attacker.is_mounted = True
        
        target = MagicMock()
        target.con = 10  # Even though target Con > attacker Con, mounted attacker can capture
        target.is_mounted = False
        target.is_capture_immune = False
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertTrue(result)
    
    def test_check_capture_conditions_attacker_con_less_than_target_not_mounted(self):
        """Test check_capture_conditions when attacker's Con <= target's Con and not mounted."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 8
        attacker.is_mounted = False
        
        target = MagicMock()
        target.con = 10
        target.is_mounted = False
        target.is_capture_immune = False
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertFalse(result)
    
    def test_check_capture_conditions_target_mounted(self):
        """Test check_capture_conditions when target is mounted (should fail)."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 12
        attacker.is_mounted = True
        
        target = MagicMock()
        target.con = 8
        target.is_mounted = True  # Mounted units cannot be captured
        target.is_capture_immune = False
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertFalse(result)
    
    def test_check_capture_conditions_target_con_too_high(self):
        """Test check_capture_conditions when target's Con >= 20 (should fail)."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 25
        attacker.is_mounted = True
        
        target = MagicMock()
        target.con = 20  # Con >= 20 cannot be captured
        target.is_mounted = False
        target.is_capture_immune = False
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertFalse(result)
    
    def test_check_capture_conditions_target_immune(self):
        """Test check_capture_conditions when target is immune to capture (should fail)."""
        # Arrange
        attacker = MagicMock()
        attacker.con = 12
        attacker.is_mounted = True
        
        target = MagicMock()
        target.con = 8
        target.is_mounted = False
        target.is_capture_immune = True  # Immune to capture (e.g., boss)
        
        # Act
        result = self.combat_system._check_capture_conditions(attacker, target)
        
        # Assert
        self.assertFalse(result)
    
    def test_process_capture_success(self):
        """Test process_capture_success correctly sets unit states and inventory access."""
        # Arrange
        attacker = MagicMock()
        attacker.id = "U001"
        attacker.name = "Leif"
        
        captured_unit = MagicMock()
        captured_unit.id = "U002"
        captured_unit.name = "Enemy"
        captured_unit.inventory = MagicMock()
        
        combat_log = MagicMock()
        
        # Act
        self.combat_system._process_capture_success(attacker, captured_unit, combat_log)
        
        # Assert
        # Verify attacker is set to carrying state
        self.assertEqual(attacker.carrying_unit_id, captured_unit.id)
        
        # Verify captured unit is marked as captured
        self.assertTrue(captured_unit.is_captured)
        
        # Verify captured unit's inventory is made accessible
        captured_unit.inventory.set_accessible.assert_called_once_with(True)
        
        # Verify combat log is updated
        combat_log.set_capture_success.assert_called_once()
    
    def test_release_captive(self):
        """Test release_captive correctly releases a captive and updates states."""
        # Arrange
        carrier_unit = MagicMock()
        carrier_unit.state = "Carrying"
        
        captive = MagicMock()
        carrier_unit.carried_unit = captive
        
        # Act
        result = self.combat_system._release_captive(carrier_unit)
        
        # Assert
        self.assertTrue(result)
        
        # Verify captive is removed from map
        captive.remove_from_map.assert_called_once()
        
        # Verify carrier state is reset
        self.assertEqual(carrier_unit.state, "Idle")
    
    def test_release_captive_not_carrying(self):
        """Test release_captive when unit is not carrying anyone (should fail)."""
        # Arrange
        carrier_unit = MagicMock()
        carrier_unit.state = "Idle"  # Not carrying
        
        # Act
        result = self.combat_system._release_captive(carrier_unit)
        
        # Assert
        self.assertFalse(result)