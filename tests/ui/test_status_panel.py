"""
Test module for the status panel of the enhanced ASCII display system.
Tests the rendering of status information including turn, phase, and unit details.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the necessary modules
from src.input.cli_display import CLIDisplay, Colors
from src.core_engine.game_state import GameStateManager


class TestStatusPanel:
    """Test suite for the status panel of the enhanced ASCII display system."""

    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state for testing."""
        mock_gs = Mock()
        # Create a mock current_game_state
        mock_gs.current_game_state = Mock()
        mock_gs.current_game_state.current_turn = 1
        mock_gs.current_game_state.current_phase = Mock()
        mock_gs.current_game_state.current_phase.name = "PLAYER"
        mock_gs.get_current_turn = Mock(return_value=1)
        mock_gs.get_current_phase = Mock(return_value=Mock(name="PLAYER"))
        
        return mock_gs
    
    @pytest.fixture
    def mock_unit_system(self):
        """Create a mock unit system for testing."""
        mock_units = Mock()
        
        # Mock get_unit_details method
        mock_units.get_unit_details = Mock(return_value=None)
        
        # Mock get_equipped_weapon_details method
        mock_units.get_equipped_weapon_details = Mock(return_value=None)
        
        return mock_units
    
    @pytest.fixture
    def cli_display(self):
        """Create a CLIDisplay instance for testing."""
        display = CLIDisplay()
        return display

    def test_status_panel_no_selection(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel displays correctly when no unit is selected."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 3
        mock_game_state.get_current_phase.return_value = Mock(name="ENEMY")
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            output = cli_display.render_status_panel(mock_game_state, None, mock_unit_system)
            
        # Assert
        # Check that the turn and phase information is displayed
        mock_print.assert_any_call("Turn: 3  Phase: ENEMY")
        mock_print.assert_any_call("Selected: None")
        
        # Check that the output contains the expected information
        expected_output = (
            "Turn: 3  Phase: ENEMY\n"
            "--------------------\n"
            "Selected: None\n"
            "--------------------\n"
        )
        
        assert output == expected_output

    def test_status_panel_with_selection(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel displays correctly when a unit is selected."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 5
        mock_game_state.get_current_phase.return_value = Mock(name="PLAYER")
        
        # Set up a selected unit
        selected_unit = Mock()
        selected_unit.name = "Hero"
        selected_unit.class_name = "Paladin"
        selected_unit.current_hp = 15
        selected_unit.max_hp = 20
        selected_unit.current_fatigue = 3
        selected_unit.status_effects = ["Poison", "Fatigue"]
        
        mock_unit_system.get_unit_details.return_value = selected_unit
        
        # Set up an equipped weapon
        equipped_weapon = Mock()
        equipped_weapon.name = "Silver Lance"
        equipped_weapon.current_durability = 12
        equipped_weapon.max_durability = 20
        
        mock_unit_system.get_equipped_weapon_details.return_value = equipped_weapon
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            output = cli_display.render_status_panel(mock_game_state, "HERO1", mock_unit_system)
            
        # Assert
        # Check that the turn, phase, and unit information is displayed
        mock_print.assert_any_call("Turn: 5  Phase: PLAYER")
        mock_print.assert_any_call("Selected: Hero (Paladin)")
        mock_print.assert_any_call(f"HP: {Colors.YELLOW}15/20{Colors.RESET}")
        mock_print.assert_any_call("Fatigue: 3")
        mock_print.assert_any_call("Status: Poison, Fatigue")
        mock_print.assert_any_call("Weapon: Silver Lance (12/20)")
        
        # Check that the output contains the expected information
        # This is a simplified check that doesn't account for colors
        expected_output_parts = [
            "Turn: 5  Phase: PLAYER",
            "Selected: Hero (Paladin)",
            "HP: 15/20",
            "Fatigue: 3",
            "Status: Poison, Fatigue",
            "Weapon: Silver Lance (12/20)"
        ]
        
        for part in expected_output_parts:
            # Strip color codes for comparison
            stripped_output = output
            stripped_output = stripped_output.replace(Colors.YELLOW, "").replace(Colors.RESET, "")
            stripped_part = part.replace(Colors.YELLOW, "").replace(Colors.RESET, "")
            assert stripped_part in stripped_output

    def test_status_panel_low_hp(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel displays low HP with the correct color."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 5
        mock_game_state.get_current_phase.return_value = Mock(name="PLAYER")
        
        # Set up a selected unit with low HP
        selected_unit = Mock()
        selected_unit.name = "Hero"
        selected_unit.class_name = "Paladin"
        selected_unit.current_hp = 4  # Low HP (20% of max)
        selected_unit.max_hp = 20
        selected_unit.current_fatigue = 3
        selected_unit.status_effects = []
        
        mock_unit_system.get_unit_details.return_value = selected_unit
        
        # Set up an equipped weapon
        equipped_weapon = Mock()
        equipped_weapon.name = "Silver Lance"
        equipped_weapon.current_durability = 12
        equipped_weapon.max_durability = 20
        
        mock_unit_system.get_equipped_weapon_details.return_value = equipped_weapon
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            cli_display.render_status_panel(mock_game_state, "HERO1", mock_unit_system)
            
        # Assert
        # Check that the HP is displayed with the correct color for low HP
        mock_print.assert_any_call(f"HP: {Colors.YELLOW}4/20{Colors.RESET}")

    def test_status_panel_very_low_hp(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel displays very low HP with the correct color."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 5
        mock_game_state.get_current_phase.return_value = Mock(name="PLAYER")
        
        # Set up a selected unit with very low HP
        selected_unit = Mock()
        selected_unit.name = "Hero"
        selected_unit.class_name = "Paladin"
        selected_unit.current_hp = 2  # Very low HP (10% of max)
        selected_unit.max_hp = 20
        selected_unit.current_fatigue = 3
        selected_unit.status_effects = []
        
        mock_unit_system.get_unit_details.return_value = selected_unit
        
        # Set up an equipped weapon
        equipped_weapon = Mock()
        equipped_weapon.name = "Silver Lance"
        equipped_weapon.current_durability = 12
        equipped_weapon.max_durability = 20
        
        mock_unit_system.get_equipped_weapon_details.return_value = equipped_weapon
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            cli_display.render_status_panel(mock_game_state, "HERO1", mock_unit_system)
            
        # Assert
        # Check that the HP is displayed with the correct color for very low HP
        mock_print.assert_any_call(f"HP: {Colors.RED}2/20{Colors.RESET}")

    def test_status_panel_no_fatigue(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel handles units without fatigue correctly."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 5
        mock_game_state.get_current_phase.return_value = Mock(name="PLAYER")
        
        # Set up a selected unit without fatigue
        selected_unit = Mock()
        selected_unit.name = "Hero"
        selected_unit.class_name = "Paladin"
        selected_unit.current_hp = 15
        selected_unit.max_hp = 20
        selected_unit.current_fatigue = None  # No fatigue
        selected_unit.status_effects = []
        
        mock_unit_system.get_unit_details.return_value = selected_unit
        
        # Set up an equipped weapon
        equipped_weapon = Mock()
        equipped_weapon.name = "Silver Lance"
        equipped_weapon.current_durability = 12
        equipped_weapon.max_durability = 20
        
        mock_unit_system.get_equipped_weapon_details.return_value = equipped_weapon
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            output = cli_display.render_status_panel(mock_game_state, "HERO1", mock_unit_system)
            
        # Assert
        # Check that fatigue is not displayed
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str):
                assert "Fatigue:" not in args[0]

    def test_status_panel_no_weapon(self, cli_display, mock_game_state, mock_unit_system):
        """Test that the status panel handles units without weapons correctly."""
        # Arrange
        mock_game_state.get_current_turn.return_value = 5
        mock_game_state.get_current_phase.return_value = Mock(name="PLAYER")
        
        # Set up a selected unit
        selected_unit = Mock()
        selected_unit.name = "Hero"
        selected_unit.class_name = "Paladin"
        selected_unit.current_hp = 15
        selected_unit.max_hp = 20
        selected_unit.current_fatigue = 3
        selected_unit.status_effects = []
        
        mock_unit_system.get_unit_details.return_value = selected_unit
        
        # No equipped weapon
        mock_unit_system.get_equipped_weapon_details.return_value = None
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, None, None)
        
        # Act
        # Capture the output of render_status_panel
        with patch('builtins.print') as mock_print:
            # Call the status panel render method that should be implemented
            cli_display.render_status_panel(mock_game_state, "HERO1", mock_unit_system)
            
        # Assert
        # Check that "Weapon: None" is displayed
        mock_print.assert_any_call("Weapon: None")