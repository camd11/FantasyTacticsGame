import unittest
from unittest.mock import MagicMock, patch

from src.fantasy_tactics_gameplay.combat.combat_system import CombatSystem
from src.fantasy_tactics_core.game_state import StatusEffectEnum

class TestCombatSystemCanAttack(unittest.TestCase):
    """Test cases for the CombatSystem.can_attack method."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_unit_system = MagicMock(name="UnitSystem")
        self.mock_map_system = MagicMock(name="MapSystem")
        self.mock_inventory_system = MagicMock(name="InventorySystem")
        self.mock_status_effect_manager = MagicMock(name="StatusEffectManager")
        
        # Create the CombatSystem instance
        self.combat_system = CombatSystem()
        self.combat_system.initialize(
            self.mock_game_state_manager,
            self.mock_data_provider,
            self.mock_unit_system,
            self.mock_map_system,
            self.mock_inventory_system,
            self.mock_status_effect_manager
        )

    def test_can_attack_basic_scenario(self):
        """Test can_attack returns True for a valid attack scenario."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Leif"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_target = MagicMock()
        mock_target.id = "U002"
        mock_target.name = "Enemy"
        mock_target.faction = "ENEMY"
        mock_target.position = (6, 5)  # Adjacent to attacker
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.range_min = 1
        mock_weapon.range_max = 1
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=mock_weapon)
        self.mock_status_effect_manager.get_unit_status_effects = MagicMock(return_value=[])
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertTrue(result)
        self.combat_system._get_equipped_weapon_data.assert_called_once_with(mock_attacker)

    def test_can_attack_no_weapon(self):
        """Test can_attack returns False when attacker has no equipped weapon."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Leif"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = -1  # No equipped weapon
        
        mock_target = MagicMock()
        mock_target.id = "U002"
        mock_target.name = "Enemy"
        mock_target.faction = "ENEMY"
        mock_target.position = (6, 5)
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=None)
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertFalse(result)
        self.combat_system._get_equipped_weapon_data.assert_called_once_with(mock_attacker)

    def test_can_attack_same_faction(self):
        """Test can_attack returns False when target is same faction."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Leif"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_target = MagicMock()
        mock_target.id = "U003"
        mock_target.name = "Ally"
        mock_target.faction = "PLAYER"  # Same faction as attacker
        mock_target.position = (6, 5)
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.range_min = 1
        mock_weapon.range_max = 1
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=mock_weapon)
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertFalse(result)

    def test_can_attack_out_of_range(self):
        """Test can_attack returns False when target is out of weapon range."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Leif"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_target = MagicMock()
        mock_target.id = "U002"
        mock_target.name = "Enemy"
        mock_target.faction = "ENEMY"
        mock_target.position = (10, 5)  # 5 tiles away, out of range
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.range_min = 1
        mock_weapon.range_max = 2  # Max range of 2
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=mock_weapon)
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertFalse(result)

    def test_can_attack_with_status_effect(self):
        """Test can_attack returns False when attacker has a status effect preventing attacks."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Leif"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_target = MagicMock()
        mock_target.id = "U002"
        mock_target.name = "Enemy"
        mock_target.faction = "ENEMY"
        mock_target.position = (6, 5)  # Adjacent to attacker
        
        # Mock weapon data
        mock_weapon = MagicMock()
        mock_weapon.range_min = 1
        mock_weapon.range_max = 1
        
        # Mock status effect
        mock_status = MagicMock()
        mock_status.status_id = StatusEffectEnum.SLEEP
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=mock_weapon)
        self.mock_status_effect_manager.get_unit_status_effects = MagicMock(return_value=[mock_status])
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertFalse(result)
        self.mock_status_effect_manager.get_unit_status_effects.assert_called_once_with(mock_attacker.id)

    def test_can_attack_with_ranged_weapon(self):
        """Test can_attack returns True for a valid ranged attack scenario."""
        # Arrange
        mock_attacker = MagicMock()
        mock_attacker.id = "U001"
        mock_attacker.name = "Archer"
        mock_attacker.faction = "PLAYER"
        mock_attacker.position = (5, 5)
        mock_attacker.equipped_weapon_index = 0
        mock_attacker.inventory = [MagicMock()]
        
        mock_target = MagicMock()
        mock_target.id = "U002"
        mock_target.name = "Enemy"
        mock_target.faction = "ENEMY"
        mock_target.position = (7, 5)  # 2 tiles away
        
        # Mock weapon data - bow with range 2-3
        mock_weapon = MagicMock()
        mock_weapon.range_min = 2
        mock_weapon.range_max = 3
        
        # Configure mocks
        self.combat_system._get_equipped_weapon_data = MagicMock(return_value=mock_weapon)
        self.mock_status_effect_manager.get_unit_status_effects = MagicMock(return_value=[])
        
        # Act
        result = self.combat_system.can_attack(mock_attacker, mock_target)
        
        # Assert
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()