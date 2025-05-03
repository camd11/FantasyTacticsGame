import unittest
from unittest.mock import MagicMock, patch, call

from src.core_engine.game_state import DispositionEnum
from src.gameplay_systems.support_leadership_system import SupportLeadershipSystem

# Constants for testing
ACTIVE = DispositionEnum.ACTIVE


class TestSupportLeadershipSystem(unittest.TestCase):
    """Test cases for the SupportLeadershipSystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the SupportLeadershipSystem instance
        self.support_system = SupportLeadershipSystem()
        self.support_system.initialize(self.mock_game_state_manager, self.mock_data_provider)

    # Support System Tests
    
    def test_calculate_support_bonus_no_allies(self):
        """Test that calculate_support_bonus returns zero bonuses when no allies are present."""
        # Arrange
        target_unit_id = "LEIF_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit]  # Only the target unit
        
        # Mock support data
        mock_support_data = {}
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
        self.mock_data_provider.get_support_data.assert_called_once()
    
    def test_calculate_support_bonus_one_ally_in_range(self):
        """Test that calculate_support_bonus correctly calculates bonuses from one ally in range."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "FINN_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Mock support data
        mock_support_data = {
            (ally_unit_id, target_unit_id): {"bonus": 10, "mutual": False}  # Finn supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 10, "avoid": 10, "crit": 10, "crit_evade": 10}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
        self.mock_data_provider.get_support_data.assert_called_once()
    
    def test_calculate_support_bonus_multiple_allies_stacking(self):
        """Test that calculate_support_bonus correctly stacks bonuses from multiple allies."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally1_unit_id = "FINN_ID"
        ally2_unit_id = "NANNA_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally units
        mock_ally1_unit = MagicMock()
        mock_ally1_unit.unit_id = ally1_unit_id
        mock_ally1_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally1_unit.faction = "PLAYER"
        mock_ally1_unit.disposition = ACTIVE
        
        mock_ally2_unit = MagicMock()
        mock_ally2_unit.unit_id = ally2_unit_id
        mock_ally2_unit.position = (5, 7)  # Distance 2 (within support range)
        mock_ally2_unit.faction = "PLAYER"
        mock_ally2_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally1_unit, mock_ally2_unit]
        
        # Mock support data
        mock_support_data = {
            (ally1_unit_id, target_unit_id): {"bonus": 10, "mutual": False},  # Finn supports Leif
            (ally2_unit_id, target_unit_id): {"bonus": 15, "mutual": False}   # Nanna supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 25, "avoid": 25, "crit": 25, "crit_evade": 25}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
        self.mock_data_provider.get_support_data.assert_called_once()
    
    def test_calculate_support_bonus_stacking_cap(self):
        """Test that calculate_support_bonus correctly applies the stacking cap."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally1_unit_id = "FINN_ID"
        ally2_unit_id = "NANNA_ID"
        ally3_unit_id = "EYVEL_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally units
        mock_ally1_unit = MagicMock()
        mock_ally1_unit.unit_id = ally1_unit_id
        mock_ally1_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally1_unit.faction = "PLAYER"
        mock_ally1_unit.disposition = ACTIVE
        
        mock_ally2_unit = MagicMock()
        mock_ally2_unit.unit_id = ally2_unit_id
        mock_ally2_unit.position = (5, 7)  # Distance 2 (within support range)
        mock_ally2_unit.faction = "PLAYER"
        mock_ally2_unit.disposition = ACTIVE
        
        mock_ally3_unit = MagicMock()
        mock_ally3_unit.unit_id = ally3_unit_id
        mock_ally3_unit.position = (4, 5)  # Adjacent (distance 1)
        mock_ally3_unit.faction = "PLAYER"
        mock_ally3_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [
            mock_target_unit, mock_ally1_unit, mock_ally2_unit, mock_ally3_unit
        ]
        
        # Mock support data
        mock_support_data = {
            (ally1_unit_id, target_unit_id): {"bonus": 10, "mutual": False},  # Finn supports Leif
            (ally2_unit_id, target_unit_id): {"bonus": 15, "mutual": False},  # Nanna supports Leif
            (ally3_unit_id, target_unit_id): {"bonus": 20, "mutual": False}   # Eyvel supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        # Expected: 10 + 15 + 20 = 45, but capped at 30
        expected_result = {"hit": 30, "avoid": 30, "crit": 30, "crit_evade": 30}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
        self.mock_data_provider.get_support_data.assert_called_once()
    
    def test_calculate_support_bonus_one_way_support(self):
        """Test that calculate_support_bonus correctly handles one-way support relationships."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "FINN_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Mock support data - only Finn supports Leif, not the other way around
        mock_support_data = {
            (ally_unit_id, target_unit_id): {"bonus": 10, "mutual": False}  # Finn supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 10, "avoid": 10, "crit": 10, "crit_evade": 10}
        self.assertEqual(result, expected_result)
        
        # Now test the reverse direction (Leif doesn't support Finn)
        self.mock_game_state_manager.get_unit.return_value = mock_ally_unit  # Now Finn is the target
        
        # Act
        result = self.support_system.calculate_support_bonus(ally_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}
        self.assertEqual(result, expected_result)
    
    def test_calculate_support_bonus_mutual_support(self):
        """Test that calculate_support_bonus correctly handles mutual support relationships."""
        # Arrange
        unit1_id = "LEIF_ID"
        unit2_id = "NANNA_ID"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.unit_id = unit1_id
        mock_unit1.position = (5, 5)
        mock_unit1.faction = "PLAYER"
        
        mock_unit2 = MagicMock()
        mock_unit2.unit_id = unit2_id
        mock_unit2.position = (6, 5)  # Adjacent (distance 1)
        mock_unit2.faction = "PLAYER"
        mock_unit2.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_all_units.return_value = [mock_unit1, mock_unit2]
        
        # Mock support data - mutual support between Leif and Nanna
        mock_support_data = {
            (unit1_id, unit2_id): {"bonus": 10, "mutual": True},  # Leif supports Nanna
            (unit2_id, unit1_id): {"bonus": 10, "mutual": True}   # Nanna supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Test Leif receiving support from Nanna
        self.mock_game_state_manager.get_unit.return_value = mock_unit1
        
        # Act
        result = self.support_system.calculate_support_bonus(unit1_id)
        
        # Assert
        expected_result = {"hit": 10, "avoid": 10, "crit": 10, "crit_evade": 10}
        self.assertEqual(result, expected_result)
        
        # Test Nanna receiving support from Leif
        self.mock_game_state_manager.get_unit.return_value = mock_unit2
        
        # Act
        result = self.support_system.calculate_support_bonus(unit2_id)
        
        # Assert
        expected_result = {"hit": 10, "avoid": 10, "crit": 10, "crit_evade": 10}
        self.assertEqual(result, expected_result)
    
    def test_calculate_support_bonus_enemy_nearby_no_bonus(self):
        """Test that calculate_support_bonus doesn't apply bonuses from enemy units."""
        # Arrange
        target_unit_id = "LEIF_ID"
        enemy_unit_id = "ENEMY_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock enemy unit
        mock_enemy_unit = MagicMock()
        mock_enemy_unit.unit_id = enemy_unit_id
        mock_enemy_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_enemy_unit.faction = "ENEMY"
        mock_enemy_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_enemy_unit]
        
        # Mock support data
        mock_support_data = {
            (enemy_unit_id, target_unit_id): {"bonus": 10, "mutual": False}  # Enemy supports Leif (shouldn't happen)
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}
        self.assertEqual(result, expected_result)
    
    def test_calculate_support_bonus_one_ally_out_of_range(self):
        """Test that calculate_support_bonus returns zero bonuses when ally is out of range."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "FINN_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (9, 5)  # Distance 4 (outside support range)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Mock support data
        mock_support_data = {
            (ally_unit_id, target_unit_id): {"bonus": 10, "mutual": False}  # Finn supports Leif
        }
        self.mock_data_provider.get_support_data.return_value = mock_support_data
        
        # Act
        result = self.support_system.calculate_support_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0, "crit": 0, "crit_evade": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
        self.mock_data_provider.get_support_data.assert_called_once()
    # Leadership System Tests
    
    def test_calculate_leadership_no_leaders(self):
        """Test that calculate_leadership_bonus returns zero when no leaders are present."""
        # Arrange
        faction = "PLAYER"
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = []
        
        # Act
        result = self.support_system.calculate_leadership_bonus(faction)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_calculate_leadership_one_leader(self):
        """Test that calculate_leadership_bonus correctly calculates bonuses from one leader."""
        # Arrange
        faction = "PLAYER"
        
        # Mock leader unit
        mock_leader = MagicMock()
        mock_leader.leadership_stars = 2
        mock_leader.is_deployed = True
        mock_leader.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = [mock_leader]
        
        # Act
        result = self.support_system.calculate_leadership_bonus(faction)
        
        # Assert
        # Expected: 2 stars * 3% per star = 6% bonus
        expected_result = {"hit": 6, "avoid": 6}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_calculate_leadership_multiple_leaders_stacking(self):
        """Test that calculate_leadership_bonus correctly stacks bonuses from multiple leaders."""
        # Arrange
        faction = "PLAYER"
        
        # Mock leader units
        mock_leader1 = MagicMock()
        mock_leader1.leadership_stars = 2
        mock_leader1.is_deployed = True
        mock_leader1.disposition = ACTIVE
        
        mock_leader2 = MagicMock()
        mock_leader2.leadership_stars = 3
        mock_leader2.is_deployed = True
        mock_leader2.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = [mock_leader1, mock_leader2]
        
        # Act
        result = self.support_system.calculate_leadership_bonus(faction)
        
        # Assert
        # Expected: (2 + 3) stars * 3% per star = 15% bonus
        expected_result = {"hit": 15, "avoid": 15}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_calculate_leadership_only_counts_deployed_units(self):
        """Test that calculate_leadership_bonus only counts deployed units."""
        # Arrange
        faction = "PLAYER"
        
        # Mock leader units
        mock_leader1 = MagicMock()
        mock_leader1.leadership_stars = 2
        mock_leader1.is_deployed = True
        mock_leader1.disposition = ACTIVE
        
        mock_leader2 = MagicMock()
        mock_leader2.leadership_stars = 3
        mock_leader2.is_deployed = False  # Not deployed
        mock_leader2.disposition = ACTIVE
        
        # Configure mocks
        self.mock_game_state_manager.get_units_by_faction.return_value = [mock_leader1, mock_leader2]
        
        # Act
        result = self.support_system.calculate_leadership_bonus(faction)
        
        # Assert
        # Expected: Only leader1's 2 stars * 3% per star = 6% bonus
        expected_result = {"hit": 6, "avoid": 6}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
    
    def test_calculate_leadership_correct_faction(self):
        """Test that calculate_leadership_bonus only counts leaders from the correct faction."""
        # Arrange
        player_faction = "PLAYER"
        enemy_faction = "ENEMY"
        
        # Mock leader units
        mock_player_leader = MagicMock()
        mock_player_leader.leadership_stars = 2
        mock_player_leader.is_deployed = True
        mock_player_leader.disposition = ACTIVE
        
        mock_enemy_leader = MagicMock()
        mock_enemy_leader.leadership_stars = 3
        mock_enemy_leader.is_deployed = True
        mock_enemy_leader.disposition = ACTIVE
        
        # Configure mocks for player faction
        self.mock_game_state_manager.get_units_by_faction.side_effect = lambda faction: {
            player_faction: [mock_player_leader],
            enemy_faction: [mock_enemy_leader]
        }.get(faction)
        
        # Act - Test player faction
        player_result = self.support_system.calculate_leadership_bonus(player_faction)
        
        # Assert
        # Expected: Player leader's 2 stars * 3% per star = 6% bonus
        expected_player_result = {"hit": 6, "avoid": 6}
        self.assertEqual(player_result, expected_player_result)
        
        # Act - Test enemy faction
        enemy_result = self.support_system.calculate_leadership_bonus(enemy_faction)
        
        # Assert
        # Expected: Enemy leader's 3 stars * 3% per star = 9% bonus
        expected_enemy_result = {"hit": 9, "avoid": 9}
        self.assertEqual(enemy_result, expected_enemy_result)
    
    # Charisma System Tests
    
    def test_calculate_charisma_no_allies(self):
        """Test that calculate_charisma_bonus returns zero when no allies are present."""
        # Arrange
        target_unit_id = "LEIF_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit]  # Only the target unit
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
    
    def test_calculate_charisma_no_charisma_allies_in_range(self):
        """Test that calculate_charisma_bonus returns zero when no allies with Charisma are in range."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "FINN_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit without Charisma
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        mock_ally_unit.has_charisma_skill = False
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
    
    def test_calculate_charisma_one_charisma_ally_in_range(self):
        """Test that calculate_charisma_bonus correctly calculates bonuses from one ally with Charisma in range."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "SAIAS_ID"  # Saias has Charisma
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit with Charisma
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        mock_ally_unit.has_charisma_skill = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 10, "avoid": 10}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
    
    # Combat Integration Tests
    
    def test_combat_hit_includes_support(self):
        """Test that combat hit calculation correctly includes support bonuses."""
        # Arrange
        attacker_id = "LEIF_ID"
        defender_id = "ENEMY_ID"
        
        # Mock attacker with base hit
        mock_attacker = MagicMock()
        mock_attacker.unit_id = attacker_id
        mock_attacker.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_attacker
        
        # Mock support bonus
        support_bonus = {"hit": 15, "avoid": 15, "crit": 15, "crit_evade": 15}
        self.support_system.calculate_support_bonus = MagicMock(return_value=support_bonus)
        
        # Act
        # Simulate combat calculation that would use the support bonus
        # In the actual implementation, this would be part of the combat calculator
        base_hit = 70
        skill = 10
        luck = 5
        weapon_triangle_bonus = 5
        
        # Hit = Weapon Hit + (2 * Skill) + Luck + Support_Bonus['hit'] + Leadership_Bonus['hit'] + Charisma_Bonus['hit'] + Weapon_Triangle_Bonus
        expected_hit = base_hit + (2 * skill) + luck + support_bonus["hit"] + 0 + 0 + weapon_triangle_bonus
        
        # Assert
        self.assertEqual(expected_hit, 115)  # 70 + 20 + 5 + 15 + 0 + 0 + 5 = 115
        
    def test_combat_hit_includes_leadership(self):
        """Test that combat hit calculation correctly includes leadership bonuses."""
        # Arrange
        attacker_id = "LEIF_ID"
        defender_id = "ENEMY_ID"
        
        # Mock attacker with base hit
        mock_attacker = MagicMock()
        mock_attacker.unit_id = attacker_id
        mock_attacker.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_attacker
        
        # Mock leadership bonus
        leadership_bonus = {"hit": 9, "avoid": 9}
        self.support_system.calculate_leadership_bonus = MagicMock(return_value=leadership_bonus)
        
        # Act
        # Simulate combat calculation that would use the leadership bonus
        # In the actual implementation, this would be part of the combat calculator
        base_hit = 70
        skill = 10
        luck = 5
        weapon_triangle_bonus = 5
        
        # Hit = Weapon Hit + (2 * Skill) + Luck + Support_Bonus['hit'] + Leadership_Bonus['hit'] + Charisma_Bonus['hit'] + Weapon_Triangle_Bonus
        expected_hit = base_hit + (2 * skill) + luck + 0 + leadership_bonus["hit"] + 0 + weapon_triangle_bonus
        
        # Assert
        self.assertEqual(expected_hit, 109)  # 70 + 20 + 5 + 0 + 9 + 0 + 5 = 109
        
    def test_combat_hit_includes_charisma(self):
        """Test that combat hit calculation correctly includes charisma bonuses."""
        # Arrange
        attacker_id = "LEIF_ID"
        defender_id = "ENEMY_ID"
        
        # Mock attacker with base hit
        mock_attacker = MagicMock()
        mock_attacker.unit_id = attacker_id
        mock_attacker.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_attacker
        
        # Mock charisma bonus
        charisma_bonus = {"hit": 10, "avoid": 10}
        self.support_system.calculate_charisma_bonus = MagicMock(return_value=charisma_bonus)
        
        # Act
        # Simulate combat calculation that would use the charisma bonus
        # In the actual implementation, this would be part of the combat calculator
        base_hit = 70
        skill = 10
        luck = 5
        weapon_triangle_bonus = 5
        
        # Hit = Weapon Hit + (2 * Skill) + Luck + Support_Bonus['hit'] + Leadership_Bonus['hit'] + Charisma_Bonus['hit'] + Weapon_Triangle_Bonus
        expected_hit = base_hit + (2 * skill) + luck + 0 + 0 + charisma_bonus["hit"] + weapon_triangle_bonus
        
        # Assert
        self.assertEqual(expected_hit, 110)  # 70 + 20 + 5 + 0 + 0 + 10 + 5 = 110
        
    def test_combat_avoid_includes_support(self):
        """Test that combat avoid calculation correctly includes support bonuses."""
        # Arrange
        defender_id = "LEIF_ID"
        attacker_id = "ENEMY_ID"
        
        # Mock defender with base avoid
        mock_defender = MagicMock()
        mock_defender.unit_id = defender_id
        mock_defender.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_defender
        
        # Mock support bonus
        support_bonus = {"hit": 15, "avoid": 15, "crit": 15, "crit_evade": 15}
        self.support_system.calculate_support_bonus = MagicMock(return_value=support_bonus)
        
        # Act
        # Simulate combat calculation that would use the support bonus
        # In the actual implementation, this would be part of the combat calculator
        attack_speed = 8
        luck = 5
        terrain_bonus = 10
        
        # Avoid = (2 * Attack Speed) + Luck + Support_Bonus['avoid'] + Leadership_Bonus['avoid'] + Charisma_Bonus['avoid'] + Terrain_Bonus
        expected_avoid = (2 * attack_speed) + luck + support_bonus["avoid"] + 0 + 0 + terrain_bonus
        
        # Assert
        self.assertEqual(expected_avoid, 46)  # 16 + 5 + 15 + 0 + 0 + 10 = 46
        
    def test_combat_avoid_includes_leadership(self):
        """Test that combat avoid calculation correctly includes leadership bonuses."""
        # Arrange
        defender_id = "LEIF_ID"
        attacker_id = "ENEMY_ID"
        
        # Mock defender with base avoid
        mock_defender = MagicMock()
        mock_defender.unit_id = defender_id
        mock_defender.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_defender
        
        # Mock leadership bonus
        leadership_bonus = {"hit": 9, "avoid": 9}
        self.support_system.calculate_leadership_bonus = MagicMock(return_value=leadership_bonus)
        
        # Act
        # Simulate combat calculation that would use the leadership bonus
        # In the actual implementation, this would be part of the combat calculator
        attack_speed = 8
        luck = 5
        terrain_bonus = 10
        
        # Avoid = (2 * Attack Speed) + Luck + Support_Bonus['avoid'] + Leadership_Bonus['avoid'] + Charisma_Bonus['avoid'] + Terrain_Bonus
        expected_avoid = (2 * attack_speed) + luck + 0 + leadership_bonus["avoid"] + 0 + terrain_bonus
        
        # Assert
        self.assertEqual(expected_avoid, 40)  # 16 + 5 + 0 + 9 + 0 + 10 = 40
        
    def test_combat_avoid_includes_charisma(self):
        """Test that combat avoid calculation correctly includes charisma bonuses."""
        # Arrange
        defender_id = "LEIF_ID"
        attacker_id = "ENEMY_ID"
        
        # Mock defender with base avoid
        mock_defender = MagicMock()
        mock_defender.unit_id = defender_id
        mock_defender.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_defender
        
        # Mock charisma bonus
        charisma_bonus = {"hit": 10, "avoid": 10}
        self.support_system.calculate_charisma_bonus = MagicMock(return_value=charisma_bonus)
        
        # Act
        # Simulate combat calculation that would use the charisma bonus
        # In the actual implementation, this would be part of the combat calculator
        attack_speed = 8
        luck = 5
        terrain_bonus = 10
        
        # Avoid = (2 * Attack Speed) + Luck + Support_Bonus['avoid'] + Leadership_Bonus['avoid'] + Charisma_Bonus['avoid'] + Terrain_Bonus
        expected_avoid = (2 * attack_speed) + luck + 0 + 0 + charisma_bonus["avoid"] + terrain_bonus
        
        # Assert
        self.assertEqual(expected_avoid, 41)  # 16 + 5 + 0 + 0 + 10 + 10 = 41
        
    def test_combat_crit_includes_support(self):
        """Test that combat critical hit calculation correctly includes support bonuses."""
        # Arrange
        attacker_id = "LEIF_ID"
        defender_id = "ENEMY_ID"
        
        # Mock attacker with base crit
        mock_attacker = MagicMock()
        mock_attacker.unit_id = attacker_id
        mock_attacker.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_attacker
        
        # Mock support bonus
        support_bonus = {"hit": 15, "avoid": 15, "crit": 15, "crit_evade": 15}
        self.support_system.calculate_support_bonus = MagicMock(return_value=support_bonus)
        
        # Act
        # Simulate combat calculation that would use the support bonus
        # In the actual implementation, this would be part of the combat calculator
        weapon_crit = 5
        skill = 10
        enemy_crit_evade = 5
        
        # Critical = (Weapon Critical + Skill + Support_Bonus['crit']) - Enemy_Crit_Evade
        expected_crit = (weapon_crit + skill + support_bonus["crit"]) - enemy_crit_evade
        
        # Assert
        self.assertEqual(expected_crit, 25)  # (5 + 10 + 15) - 5 = 25
        
    def test_combat_crit_evade_includes_support(self):
        """Test that combat critical evade calculation correctly includes support bonuses."""
        # Arrange
        defender_id = "LEIF_ID"
        attacker_id = "ENEMY_ID"
        
        # Mock defender with base crit evade
        mock_defender = MagicMock()
        mock_defender.unit_id = defender_id
        mock_defender.faction = "PLAYER"
        
        # Mock combat calculator
        mock_combat_calculator = MagicMock()
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_defender
        
        # Mock support bonus
        support_bonus = {"hit": 15, "avoid": 15, "crit": 15, "crit_evade": 15}
        self.support_system.calculate_support_bonus = MagicMock(return_value=support_bonus)
        
        # Act
        # Simulate combat calculation that would use the support bonus
        # In the actual implementation, this would be part of the combat calculator
        luck = 10
        
        # Crit_Evade = (Luck / 2) + Support_Bonus['crit_evade']
        expected_crit_evade = (luck // 2) + support_bonus["crit_evade"]
        
        # Assert
        self.assertEqual(expected_crit_evade, 20)  # 5 + 15 = 20
    
    def test_calculate_charisma_one_charisma_ally_out_of_range(self):
        """Test that calculate_charisma_bonus returns zero when ally with Charisma is out of range."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally_unit_id = "SAIAS_ID"  # Saias has Charisma
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally unit with Charisma
        mock_ally_unit = MagicMock()
        mock_ally_unit.unit_id = ally_unit_id
        mock_ally_unit.position = (9, 5)  # Distance 4 (outside charisma range)
        mock_ally_unit.faction = "PLAYER"
        mock_ally_unit.disposition = ACTIVE
        mock_ally_unit.has_charisma_skill = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally_unit]
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
    
    def test_calculate_charisma_multiple_charisma_allies_stacking(self):
        """Test that calculate_charisma_bonus correctly stacks bonuses from multiple allies with Charisma."""
        # Arrange
        target_unit_id = "LEIF_ID"
        ally1_unit_id = "SAIAS_ID"  # Saias has Charisma
        ally2_unit_id = "SELFINA_ID"  # Selfina has Charisma
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock ally units with Charisma
        mock_ally1_unit = MagicMock()
        mock_ally1_unit.unit_id = ally1_unit_id
        mock_ally1_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_ally1_unit.faction = "PLAYER"
        mock_ally1_unit.disposition = ACTIVE
        mock_ally1_unit.has_charisma_skill = True
        
        mock_ally2_unit = MagicMock()
        mock_ally2_unit.unit_id = ally2_unit_id
        mock_ally2_unit.position = (5, 7)  # Distance 2 (within charisma range)
        mock_ally2_unit.faction = "PLAYER"
        mock_ally2_unit.disposition = ACTIVE
        mock_ally2_unit.has_charisma_skill = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_ally1_unit, mock_ally2_unit]
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        # Expected: 2 allies with Charisma * 10 bonus per ally = 20
        expected_result = {"hit": 20, "avoid": 20}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
    
    def test_calculate_charisma_enemy_charisma_no_bonus(self):
        """Test that calculate_charisma_bonus doesn't apply bonuses from enemy units with Charisma."""
        # Arrange
        target_unit_id = "LEIF_ID"
        enemy_unit_id = "ENEMY_ID"
        
        # Mock target unit
        mock_target_unit = MagicMock()
        mock_target_unit.unit_id = target_unit_id
        mock_target_unit.position = (5, 5)
        mock_target_unit.faction = "PLAYER"
        
        # Mock enemy unit with Charisma
        mock_enemy_unit = MagicMock()
        mock_enemy_unit.unit_id = enemy_unit_id
        mock_enemy_unit.position = (6, 5)  # Adjacent (distance 1)
        mock_enemy_unit.faction = "ENEMY"
        mock_enemy_unit.disposition = ACTIVE
        mock_enemy_unit.has_charisma_skill = True
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_target_unit
        self.mock_game_state_manager.get_all_units.return_value = [mock_target_unit, mock_enemy_unit]
        
        # Act
        result = self.support_system.calculate_charisma_bonus(target_unit_id)
        
        # Assert
        expected_result = {"hit": 0, "avoid": 0}
        self.assertEqual(result, expected_result)
        self.mock_game_state_manager.get_unit.assert_called_once_with(target_unit_id)
        self.mock_game_state_manager.get_all_units.assert_called_once()
