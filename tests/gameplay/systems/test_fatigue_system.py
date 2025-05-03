import unittest
from unittest.mock import MagicMock, patch, call

from src.gameplay_systems.fatigue_system import FatigueManager
from src.core_engine.game_state import DispositionEnum, StatusEffectEnum


class TestFatigueSystem(unittest.TestCase):
    """Test cases for the Fatigue System."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_inventory_manager = MagicMock(name="InventoryManager")
        
        # Create the FatigueManager instance
        self.fatigue_manager = FatigueManager()
        self.fatigue_manager.initialize(
            self.mock_game_state_manager, 
            self.mock_data_provider,
            self.mock_inventory_manager
        )
        
        # Set up common mock objects
        self.mock_game_state = MagicMock(name="GameState")
        self.mock_game_state_manager.current_game_state = self.mock_game_state

    # TDD_ANCHOR: test_increment_fatigue_combat
    def test_increment_fatigue_combat(self):
        """Test that combat actions increment fatigue correctly."""
        # Arrange
        unit_id = "U001"
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 5
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.fatigue_manager.increment_fatigue(mock_unit, "COMBAT")
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 6)  # 5 + 1 for combat
    
    # TDD_ANCHOR: test_increment_fatigue_staff_various_ranks
    def test_increment_fatigue_staff_various_ranks(self):
        """Test that staff usage increments fatigue correctly based on rank."""
        # Arrange
        unit_id = "U001"
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 5
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act & Assert - Test each staff rank
        # E rank staff
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="E")
        self.assertEqual(mock_unit.current_fatigue, 6)  # 5 + 1 for E rank
        
        # Reset fatigue for next test
        mock_unit.current_fatigue = 5
        
        # D rank staff
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="D")
        self.assertEqual(mock_unit.current_fatigue, 7)  # 5 + 2 for D rank
        
        # Reset fatigue for next test
        mock_unit.current_fatigue = 5
        
        # C rank staff
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="C")
        self.assertEqual(mock_unit.current_fatigue, 8)  # 5 + 3 for C rank
        
        # Reset fatigue for next test
        mock_unit.current_fatigue = 5
        
        # B rank staff
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="B")
        self.assertEqual(mock_unit.current_fatigue, 9)  # 5 + 4 for B rank
        
        # Reset fatigue for next test
        mock_unit.current_fatigue = 5
        
        # A rank staff
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="A")
        self.assertEqual(mock_unit.current_fatigue, 10)  # 5 + 5 for A rank
        
        # Reset fatigue for next test
        mock_unit.current_fatigue = 5
        
        # * rank staff (should be same as A)
        self.fatigue_manager.increment_fatigue(mock_unit, "STAFF", staff_rank="*")
        self.assertEqual(mock_unit.current_fatigue, 10)  # 5 + 5 for * rank
    
    # TDD_ANCHOR: test_increment_fatigue_steal
    def test_increment_fatigue_steal(self):
        """Test that steal actions increment fatigue correctly."""
        # Arrange
        unit_id = "U001"
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 5
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.fatigue_manager.increment_fatigue(mock_unit, "STEAL")
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 6)  # 5 + 1 for steal
    
    # TDD_ANCHOR: test_increment_fatigue_dance
    def test_increment_fatigue_dance(self):
        """Test that dance actions increment fatigue correctly."""
        # Arrange
        unit_id = "U001"
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 5
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.fatigue_manager.increment_fatigue(mock_unit, "DANCE")
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 6)  # 5 + 1 for dance
    
    # TDD_ANCHOR: test_increment_fatigue_lord_accumulates
    def test_increment_fatigue_lord_accumulates(self):
        """Test that the Lord unit accumulates fatigue like other units."""
        # Arrange
        unit_id = "Leif"  # Lord unit ID
        mock_unit = MagicMock()
        mock_unit.id = "Leif"
        mock_unit.current_fatigue = 5
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        self.fatigue_manager.increment_fatigue(mock_unit, "COMBAT")
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 6)  # Lord should accumulate fatigue
    
    # TDD_ANCHOR: test_increment_fatigue_only_after_chapter_7
    def test_increment_fatigue_only_after_chapter_7(self):
        """Test that fatigue only accumulates after Chapter 7."""
        # Arrange
        unit_id = "U001"
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 5
        
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act & Assert - Before Chapter 8
        self.mock_game_state.current_chapter = 7
        self.fatigue_manager.increment_fatigue(mock_unit, "COMBAT")
        self.assertEqual(mock_unit.current_fatigue, 5)  # Should not change
        
        # Act & Assert - At Chapter 8
        self.mock_game_state.current_chapter = 8
        self.fatigue_manager.increment_fatigue(mock_unit, "COMBAT")
        self.assertEqual(mock_unit.current_fatigue, 6)  # Should increment
    
    # TDD_ANCHOR: test_set_fatigue_status_below_threshold
    def test_set_fatigue_status_below_threshold(self):
        """Test setting fatigue status when fatigue is below the threshold."""
        # Arrange
        mock_unit1 = MagicMock()
        mock_unit1.current_fatigue = 15
        mock_unit1.max_hp = 20
        mock_unit1.id = "U001"
        
        all_player_units = [mock_unit1]
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        
        # Act
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        
        # Assert
        self.assertFalse(mock_unit1.is_fatigued)  # Below threshold, not fatigued
        self.assertEqual(mock_unit1.current_fatigue, 0)  # Reset for next chapter
    
    # TDD_ANCHOR: test_set_fatigue_status_at_threshold
    def test_set_fatigue_status_at_threshold(self):
        """Test setting fatigue status when fatigue is at the threshold."""
        # Arrange
        mock_unit1 = MagicMock()
        mock_unit1.current_fatigue = 20
        mock_unit1.max_hp = 20
        mock_unit1.id = "U001"
        
        all_player_units = [mock_unit1]
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        
        # Act
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        
        # Assert
        self.assertTrue(mock_unit1.is_fatigued)  # At threshold, should be fatigued
        self.assertEqual(mock_unit1.current_fatigue, 0)  # Reset for next chapter
    
    # TDD_ANCHOR: test_set_fatigue_status_above_threshold
    def test_set_fatigue_status_above_threshold(self):
        """Test setting fatigue status when fatigue is above the threshold."""
        # Arrange
        mock_unit1 = MagicMock()
        mock_unit1.current_fatigue = 25
        mock_unit1.max_hp = 20
        mock_unit1.id = "U001"
        
        all_player_units = [mock_unit1]
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        
        # Act
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        
        # Assert
        self.assertTrue(mock_unit1.is_fatigued)  # Above threshold, should be fatigued
        self.assertEqual(mock_unit1.current_fatigue, 0)  # Reset for next chapter
    
    # TDD_ANCHOR: test_set_fatigue_status_lord_never_fatigued_for_deployment
    def test_set_fatigue_status_lord_never_fatigued_for_deployment(self):
        """Test that the Lord unit is never marked as fatigued for deployment."""
        # Arrange
        mock_lord = MagicMock()
        mock_lord.current_fatigue = 25  # Above threshold
        mock_lord.max_hp = 20
        mock_lord.id = "Leif"  # Lord unit ID
        
        all_player_units = [mock_lord]
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        
        # Act
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        
        # Assert
        self.assertFalse(mock_lord.is_fatigued)  # Lord should never be fatigued
        self.assertEqual(mock_lord.current_fatigue, 0)  # Reset for next chapter
    
    # TDD_ANCHOR: test_set_fatigue_status_only_after_chapter_7
    def test_set_fatigue_status_only_after_chapter_7(self):
        """Test that fatigue status is only set after Chapter 7."""
        # Arrange
        mock_unit1 = MagicMock()
        mock_unit1.current_fatigue = 25  # Above threshold
        mock_unit1.max_hp = 20
        mock_unit1.id = "U001"
        mock_unit1.is_fatigued = False
        
        all_player_units = [mock_unit1]
        
        # Act & Assert - Before Chapter 8
        self.mock_game_state.current_chapter = 7
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        self.assertFalse(mock_unit1.is_fatigued)  # Should not be fatigued before Ch8
        
        # Act & Assert - At Chapter 8
        self.mock_game_state.current_chapter = 8
        mock_unit1.current_fatigue = 25  # Reset for the test
        self.fatigue_manager.check_and_set_fatigue_status_post_chapter(all_player_units)
        self.assertTrue(mock_unit1.is_fatigued)  # Should be fatigued at Ch8
    
    # TDD_ANCHOR: test_reset_fatigue_clears_flag_and_counter
    def test_reset_fatigue_clears_flag_and_counter(self):
        """Test that resetting fatigue clears both the flag and counter."""
        # Arrange
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 10
        mock_unit.is_fatigued = True
        
        # Act
        self.fatigue_manager.reset_fatigue_for_unit(mock_unit)
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 0)  # Counter reset
        self.assertFalse(mock_unit.is_fatigued)  # Flag cleared
    
    # TDD_ANCHOR: test_handle_deployment_resets_benched_unit_fatigue
    def test_handle_deployment_resets_benched_unit_fatigue(self):
        """Test that handling deployment resets fatigue for benched units."""
        # Arrange
        mock_deployed1 = MagicMock()
        mock_deployed1.id = "D001"
        mock_deployed1.is_fatigued = False
        
        mock_benched1 = MagicMock()
        mock_benched1.id = "B001"
        mock_benched1.is_fatigued = True
        mock_benched1.current_fatigue = 10
        
        mock_benched2 = MagicMock()
        mock_benched2.id = "B002"
        mock_benched2.is_fatigued = True
        mock_benched2.current_fatigue = 15
        
        deployed_units = [mock_deployed1]
        benched_units = [mock_benched1, mock_benched2]
        
        # Act
        self.fatigue_manager.handle_deployment_fatigue(deployed_units, benched_units)
        
        # Assert
        # Deployed units should remain unchanged
        self.assertFalse(mock_deployed1.is_fatigued)
        
        # Benched units should have fatigue reset
        self.assertFalse(mock_benched1.is_fatigued)
        self.assertEqual(mock_benched1.current_fatigue, 0)
        
        self.assertFalse(mock_benched2.is_fatigued)
        self.assertEqual(mock_benched2.current_fatigue, 0)
    
    # TDD_ANCHOR: test_handle_deployment_keeps_deployed_unit_fatigue_status
    def test_handle_deployment_keeps_deployed_unit_fatigue_status(self):
        """Test that handling deployment keeps fatigue status for deployed units."""
        # Arrange
        # This test is a bit redundant since deployed units should never be fatigued
        # (they wouldn't be allowed to deploy), but we'll test the logic anyway
        mock_deployed1 = MagicMock()
        mock_deployed1.id = "D001"
        mock_deployed1.is_fatigued = False
        mock_deployed1.current_fatigue = 0
        
        mock_benched1 = MagicMock()
        mock_benched1.id = "B001"
        
        deployed_units = [mock_deployed1]
        benched_units = [mock_benched1]
        
        # Act
        self.fatigue_manager.handle_deployment_fatigue(deployed_units, benched_units)
        
        # Assert
        # Deployed units should remain unchanged
        self.assertFalse(mock_deployed1.is_fatigued)
        self.assertEqual(mock_deployed1.current_fatigue, 0)
    
    # TDD_ANCHOR: test_can_deploy_not_fatigued
    def test_can_deploy_not_fatigued(self):
        """Test that non-fatigued units can be deployed."""
        # Arrange
        mock_unit = MagicMock()
        mock_unit.is_fatigued = False
        mock_unit.id = "U001"
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.fatigue_manager.can_deploy_unit(mock_unit)
        
        # Assert
        self.assertTrue(result)  # Not fatigued, can deploy
    
    # TDD_ANCHOR: test_can_deploy_fatigued_non_lord
    def test_can_deploy_fatigued_non_lord(self):
        """Test that fatigued non-lord units cannot be deployed."""
        # Arrange
        mock_unit = MagicMock()
        mock_unit.is_fatigued = True
        mock_unit.id = "U001"  # Not the lord
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.fatigue_manager.can_deploy_unit(mock_unit)
        
        # Assert
        self.assertFalse(result)  # Fatigued non-lord, cannot deploy
    
    # TDD_ANCHOR: test_can_deploy_fatigued_lord
    def test_can_deploy_fatigued_lord(self):
        """Test that the Lord unit can be deployed even when fatigued."""
        # Arrange
        mock_lord = MagicMock()
        mock_lord.is_fatigued = True  # Should never happen, but testing the logic
        mock_lord.id = "Leif"  # Lord unit ID
        
        self.mock_game_state.current_chapter = 8  # After fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_lord
        
        # Act
        result = self.fatigue_manager.can_deploy_unit(mock_lord)
        
        # Assert
        self.assertTrue(result)  # Lord can always deploy
    
    # TDD_ANCHOR: test_can_deploy_before_chapter_8
    def test_can_deploy_before_chapter_8(self):
        """Test that all units can be deployed before Chapter 8 regardless of fatigue."""
        # Arrange
        mock_unit = MagicMock()
        mock_unit.is_fatigued = True
        mock_unit.id = "U001"  # Not the lord
        
        self.mock_game_state.current_chapter = 7  # Before fatigue starts
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.fatigue_manager.can_deploy_unit(mock_unit)
        
        # Assert
        self.assertTrue(result)  # Before Ch8, can deploy regardless of fatigue
    
    # TDD_ANCHOR: test_use_stamina_drink_resets_fatigue
    def test_use_stamina_drink_resets_fatigue(self):
        """Test that using a Stamina Drink resets fatigue."""
        # Arrange
        mock_unit = MagicMock()
        mock_unit.current_fatigue = 15
        mock_unit.is_fatigued = True
        
        # Act
        self.fatigue_manager.use_stamina_drink(mock_unit)
        
        # Assert
        self.assertEqual(mock_unit.current_fatigue, 0)  # Counter reset
        self.assertFalse(mock_unit.is_fatigued)  # Flag cleared
        self.mock_inventory_manager.remove_item.assert_called_once_with(mock_unit, "S-Drink", 1)


if __name__ == '__main__':
    unittest.main()