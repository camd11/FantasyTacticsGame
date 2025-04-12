"""
Test module for the enhanced ASCII display system.
Tests the rendering of units, terrain, fog of war, and status information.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Import the necessary modules
from src.input.cli_display import CLIDisplay, Colors
from src.core_engine.game_state import GameStateManager


class TestAsciiDisplay:
    """Test suite for the enhanced ASCII display system."""

    @pytest.fixture
    def mock_game_state(self):
        """Create a mock game state for testing."""
        mock_gs = Mock()
        mock_gs.current_game_state.current_turn = 1
        mock_gs.current_game_state.current_phase.name = "PLAYER"
        mock_gs.get_map_dimensions.return_value = (5, 5)
        
        # Mock unit_states dictionary
        mock_gs.current_game_state.unit_states = {}
        
        return mock_gs
    
    @pytest.fixture
    def mock_map_system(self):
        """Create a mock map system for testing."""
        mock_map = Mock()
        mock_map.get_width.return_value = 5
        mock_map.get_height.return_value = 5
        
        # Default terrain type is PLAIN
        mock_map.get_terrain_type.return_value = Mock(name="PLAIN")
        
        return mock_map
    
    @pytest.fixture
    def mock_unit_system(self):
        """Create a mock unit system for testing."""
        mock_units = Mock()
        return mock_units
    
    @pytest.fixture
    def mock_fog_system(self):
        """Create a mock fog of war system for testing."""
        mock_fog = Mock()
        
        # Default visibility is VISIBLE
        visibility_grid = [[Mock(name="VISIBLE") for _ in range(5)] for _ in range(5)]
        mock_fog.get_visibility_grid.return_value = visibility_grid
        
        # By default, all units should be displayed
        mock_fog.should_display_unit.return_value = True
        
        return mock_fog
    
    @pytest.fixture
    def cli_display(self):
        """Create a CLIDisplay instance for testing."""
        display = CLIDisplay()
        return display

    def test_unit_rendering_player(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that player units are rendered with the correct character and color."""
        # Arrange
        player_unit = Mock()
        player_unit.faction = "PLAYER"
        player_unit.position = (2, 2)
        player_unit.current_hp = 20
        player_unit.max_hp = 20
        player_unit.is_mounted = False
        player_unit.is_captured = False
        player_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": player_unit}
        mock_game_state.get_all_units.return_value = [player_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # Check that the player unit character 'P' was printed with the correct color
        mock_print.assert_any_call(f"{Colors.CYAN}P{Colors.RESET}", end="")

    def test_unit_rendering_enemy(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that enemy units are rendered with the correct character and color."""
        # Arrange
        enemy_unit = Mock()
        enemy_unit.faction = "ENEMY"
        enemy_unit.position = (2, 2)
        enemy_unit.current_hp = 20
        enemy_unit.max_hp = 20
        enemy_unit.is_mounted = False
        enemy_unit.is_captured = False
        enemy_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"ENEMY1": enemy_unit}
        mock_game_state.get_all_units.return_value = [enemy_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # Check that the enemy unit character 'E' was printed with the correct color
        mock_print.assert_any_call(f"{Colors.RED}E{Colors.RESET}", end="")

    def test_unit_rendering_npc(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that NPC units are rendered with the correct character and color."""
        # Arrange
        npc_unit = Mock()
        npc_unit.faction = "NPC"
        npc_unit.position = (2, 2)
        npc_unit.current_hp = 20
        npc_unit.max_hp = 20
        npc_unit.is_mounted = False
        npc_unit.is_captured = False
        npc_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"NPC1": npc_unit}
        mock_game_state.get_all_units.return_value = [npc_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # Check that the NPC unit character 'N' was printed with the correct color
        mock_print.assert_any_call(f"{Colors.YELLOW}N{Colors.RESET}", end="")

    def test_unit_rendering_mounted(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that mounted units are rendered with the correct character modifier."""
        # Arrange
        mounted_unit = Mock()
        mounted_unit.faction = "PLAYER"
        mounted_unit.position = (2, 2)
        mounted_unit.current_hp = 20
        mounted_unit.max_hp = 20
        mounted_unit.is_mounted = True  # Unit is mounted
        mounted_unit.is_captured = False
        mounted_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": mounted_unit}
        mock_game_state.get_all_units.return_value = [mounted_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't support mounted status
        # The expected behavior would be to print a different character or modifier for mounted units
        mock_print.assert_any_call(f"{Colors.CYAN}^{Colors.RESET}", end="")

    def test_unit_rendering_captured(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that captured units are rendered with the correct character modifier."""
        # Arrange
        captured_unit = Mock()
        captured_unit.faction = "PLAYER"
        captured_unit.position = (2, 2)
        captured_unit.current_hp = 20
        captured_unit.max_hp = 20
        captured_unit.is_mounted = False
        captured_unit.is_captured = True  # Unit is captured
        captured_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": captured_unit}
        mock_game_state.get_all_units.return_value = [captured_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't support captured status
        # The expected behavior would be to print a different character or modifier for captured units
        mock_print.assert_any_call(f"{Colors.CYAN}c{Colors.RESET}", end="")

    def test_unit_rendering_low_hp(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that units with low HP are rendered with the correct color."""
        # Arrange
        low_hp_unit = Mock()
        low_hp_unit.faction = "PLAYER"
        low_hp_unit.position = (2, 2)
        low_hp_unit.current_hp = 2  # Low HP
        low_hp_unit.max_hp = 20
        low_hp_unit.is_mounted = False
        low_hp_unit.is_captured = False
        low_hp_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": low_hp_unit}
        mock_game_state.get_all_units.return_value = [low_hp_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't change color for low HP
        # The expected behavior would be to print the unit character with a different color for low HP
        mock_print.assert_any_call(f"{Colors.YELLOW}P{Colors.RESET}", end="")

    def test_terrain_rendering(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that different terrain types are rendered with the correct characters."""
        # Arrange
        # Set up different terrain types at different positions
        terrain_types = {
            (0, 0): Mock(name="PLAIN"),
            (0, 1): Mock(name="FOREST"),
            (0, 2): Mock(name="RIVER"),
            (0, 3): Mock(name="MOUNTAIN"),
            (0, 4): Mock(name="VILLAGE")
        }
        
        # Update the mock_map_system to return different terrain types based on position
        def get_terrain_type(position):
            return terrain_types.get(position, Mock(name="PLAIN"))
        
        mock_map_system.get_terrain_type.side_effect = get_terrain_type
        
        # No units on the map
        mock_game_state.current_game_state.unit_states = {}
        mock_game_state.get_all_units.return_value = []
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # Check that each terrain type was printed with the correct character
        # These assertions should match the ASCII_TERRAIN dictionary in cli_display.py
        mock_print.assert_any_call(f"{Colors.GREEN}.{Colors.RESET}", end="")  # PLAIN
        mock_print.assert_any_call(f"{Colors.GREEN}T{Colors.RESET}", end="")  # FOREST
        mock_print.assert_any_call(f"{Colors.BLUE}~{Colors.RESET}", end="")  # RIVER
        mock_print.assert_any_call(f"{Colors.BLACK + Colors.BG_WHITE}^{Colors.RESET}", end="")  # MOUNTAIN
        mock_print.assert_any_call(f"{Colors.YELLOW}v{Colors.RESET}", end="")  # VILLAGE

    def test_fog_of_war_rendering(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that fog of war is rendered correctly."""
        # Arrange
        # Set up different visibility states at different positions
        visibility_grid = [
            [Mock(name="VISIBLE"), Mock(name="FOG"), Mock(name="SHROUD"), Mock(name="VISIBLE"), Mock(name="VISIBLE")],
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE")],
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE")],
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE")],
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE")]
        ]
        
        mock_fog_system.get_visibility_grid.return_value = visibility_grid
        
        # No units on the map
        mock_game_state.current_game_state.unit_states = {}
        mock_game_state.get_all_units.return_value = []
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't support fog of war
        # The expected behavior would be to print different characters for FOG and SHROUD tiles
        mock_print.assert_any_call(f"{Colors.GRAY}░{Colors.RESET}", end="")  # FOG
        mock_print.assert_any_call(f"{Colors.BLACK}█{Colors.RESET}", end="")  # SHROUD

    def test_unit_visibility_in_fog(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that units in fog are rendered correctly based on faction."""
        # Arrange
        # Set up a visibility grid with a FOG tile at (2, 2)
        visibility_grid = [[Mock(name="VISIBLE") for _ in range(5)] for _ in range(5)]
        visibility_grid[2][2] = Mock(name="FOG")
        mock_fog_system.get_visibility_grid.return_value = visibility_grid
        
        # Set up a player unit and an enemy unit in the FOG
        player_unit = Mock()
        player_unit.faction = "PLAYER"
        player_unit.position = (2, 2)
        player_unit.current_hp = 20
        player_unit.max_hp = 20
        player_unit.is_mounted = False
        player_unit.is_captured = False
        player_unit.get_primary_visual_status.return_value = None
        
        enemy_unit = Mock()
        enemy_unit.faction = "ENEMY"
        enemy_unit.position = (2, 3)
        enemy_unit.current_hp = 20
        enemy_unit.max_hp = 20
        enemy_unit.is_mounted = False
        enemy_unit.is_captured = False
        enemy_unit.get_primary_visual_status.return_value = None
        
        # Player units should be visible in FOG, enemy units should not
        mock_fog_system.should_display_unit.side_effect = lambda unit, grid: unit.faction == "PLAYER"
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": player_unit, "ENEMY1": enemy_unit}
        mock_game_state.get_all_units.return_value = [player_unit, enemy_unit]
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't support fog of war
        # The expected behavior would be to print the player unit in FOG but not the enemy unit
        mock_print.assert_any_call(f"{Colors.CYAN}P{Colors.RESET}", end="")  # Player unit should be visible
        # The enemy unit should not be visible, so the FOG character should be printed instead
        mock_print.assert_any_call(f"{Colors.GRAY}░{Colors.RESET}", end="")

    def test_status_info_display(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test that status information is displayed correctly."""
        # Arrange
        mock_game_state.current_game_state.current_turn = 5
        mock_game_state.current_game_state.current_phase.name = "ENEMY"
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # Check that the turn and phase information is displayed
        mock_print.assert_any_call(f"\n=== ASCII MAP (Turn 5, ENEMY Phase) ===")

    def test_full_render_output(self, cli_display, mock_game_state, mock_map_system, mock_unit_system, mock_fog_system):
        """Test the full render output for a specific game state."""
        # Arrange
        # Set up a small 3x3 map with specific terrain and units
        mock_game_state.get_map_dimensions.return_value = (3, 3)
        
        # Set up terrain
        terrain_types = {
            (0, 0): Mock(name="PLAIN"),
            (0, 1): Mock(name="FOREST"),
            (0, 2): Mock(name="RIVER"),
            (1, 0): Mock(name="MOUNTAIN"),
            (1, 1): Mock(name="VILLAGE"),
            (1, 2): Mock(name="PLAIN"),
            (2, 0): Mock(name="PLAIN"),
            (2, 1): Mock(name="PLAIN"),
            (2, 2): Mock(name="PLAIN")
        }
        
        def get_terrain_type(position):
            return terrain_types.get(position, Mock(name="PLAIN"))
        
        mock_map_system.get_terrain_type.side_effect = get_terrain_type
        
        # Set up units
        player_unit = Mock()
        player_unit.faction = "PLAYER"
        player_unit.position = (0, 0)
        player_unit.current_hp = 20
        player_unit.max_hp = 20
        player_unit.is_mounted = False
        player_unit.is_captured = False
        player_unit.get_primary_visual_status.return_value = None
        
        enemy_unit = Mock()
        enemy_unit.faction = "ENEMY"
        enemy_unit.position = (2, 2)
        enemy_unit.current_hp = 20
        enemy_unit.max_hp = 20
        enemy_unit.is_mounted = False
        enemy_unit.is_captured = False
        enemy_unit.get_primary_visual_status.return_value = None
        
        mock_game_state.current_game_state.unit_states = {"PLAYER1": player_unit, "ENEMY1": enemy_unit}
        mock_game_state.get_all_units.return_value = [player_unit, enemy_unit]
        
        # Set up visibility
        visibility_grid = [
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="VISIBLE")],
            [Mock(name="VISIBLE"), Mock(name="VISIBLE"), Mock(name="FOG")],
            [Mock(name="VISIBLE"), Mock(name="FOG"), Mock(name="SHROUD")]
        ]
        
        mock_fog_system.get_visibility_grid.return_value = visibility_grid
        
        # Player units should be visible in FOG, enemy units should not
        mock_fog_system.should_display_unit.side_effect = lambda unit, grid: unit.faction == "PLAYER" or (unit.position[0] < 2 and unit.position[1] < 2)
        
        # Initialize the display
        cli_display.initialize(mock_game_state, mock_unit_system, None, mock_map_system, None)
        
        # Act
        # Capture the output of render_enhanced_ascii_map
        with patch('builtins.print') as mock_print:
            output = cli_display.render_ascii_map(mock_game_state)
            
        # Assert
        # This test should fail initially because the current implementation doesn't match the expected output
        # The expected output would be a specific ASCII representation of the game state
        expected_output = (
            "\n=== ASCII MAP (Turn 1, PLAYER Phase) ===\n"
            "   012\n"
            " 0|P..\n"
            " 1|T^v\n"
            " 2|~.E\n"
            "\n"
            "Legend:\n"
            "Terrain: .=Plain, T=Forest, ~=Water, ==Bridge\n"
            "        v=Village, S=Seize, ^=Mountain, H=Castle, O=Throne\n"
            "Units:  P=Player, E=Enemy, N=NPC\n"
        )
        
        # Check that the output matches the expected output
        # This is a simplified check that doesn't account for colors
        assert output == expected_output