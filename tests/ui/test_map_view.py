"""
Test module for the MapView component.
Tests the initialization and basic functionality of the map view.
"""

import pytest
from unittest.mock import Mock, patch

# Import the MapView class (this will fail until the class is implemented)
# The test is expected to fail initially
from src.ui.views.map_view import MapView


class TestMapView:
    """Test suite for the MapView component."""

    @pytest.fixture
    def mock_pygame_surface(self):
        """Create a mock Pygame surface for testing."""
        mock_surface = Mock()
        mock_surface.get_width.return_value = 800
        mock_surface.get_height.return_value = 600
        return mock_surface

    @pytest.fixture
    def mock_config(self):
        """Create mock configuration settings for the MapView."""
        return {
            'tile_size': 32,
            'grid_color': (100, 100, 100),
            'highlight_color': (255, 255, 0),
            'selection_color': (0, 255, 0),
            'move_range_color': (0, 0, 255, 128),
            'attack_range_color': (255, 0, 0, 128)
        }

    def test_map_view_initialization(self, mock_pygame_surface, mock_config):
        """Test that MapView can be instantiated with the required dependencies."""
        # Create a MapView instance
        map_view = MapView(
            surface=mock_pygame_surface,
            config=mock_config
        )
        
        # Assert that MapView was initialized with the mock surface and config
        assert map_view.surface == mock_pygame_surface
        assert map_view.config == mock_config
        
        # Assert that MapView initialized its internal state
        assert hasattr(map_view, 'map_data')
        assert hasattr(map_view, 'unit_data')
        assert hasattr(map_view, 'tile_size')
        
        # Assert that the tile_size was set from the config
        assert map_view.tile_size == mock_config['tile_size']
        
    def test_render_map(self, mock_pygame_surface, mock_config):
        """Test that the render_map method correctly renders the map data."""
        # Create a MapView instance
        map_view = MapView(
            surface=mock_pygame_surface,
            config=mock_config
        )
        
        # Create mock map data (a simple 2D array representing terrain tiles)
        # 0 = grass, 1 = water, 2 = mountain, etc.
        mock_map_data = [
            [0, 0, 1, 1],
            [0, 2, 1, 0],
            [2, 2, 0, 0]
        ]
        
        # Call the render_map method (this should fail until implemented)
        map_view.render_map(mock_map_data)
        
        # Assert that the surface's drawing methods were called with expected arguments
        # The surface.blit method should be called for each tile in the map
        assert mock_pygame_surface.blit.call_count == len(mock_map_data) * len(mock_map_data[0])
        
        # Check that the correct coordinates were used for drawing
        # For each tile, the x,y coordinates should be calculated based on the tile's position and size
        calls = mock_pygame_surface.blit.call_args_list
        
        # Verify a few specific calls to ensure correct positioning
        # First tile (0,0) should be at pixel position (0,0)
        first_call = calls[0]
        assert first_call[0][1] == (0, 0)
        
        # Tile at (1,0) should be at pixel position (32,0) with tile_size=32
        second_call = calls[1]
        assert second_call[0][1] == (32, 0)
        
    def test_render_units(self, mock_pygame_surface, mock_config):
        """Test that the render_units method correctly renders units on the map."""
        # Create a MapView instance
        map_view = MapView(
            surface=mock_pygame_surface,
            config=mock_config
        )
        
        # Create mock unit data
        # Each unit has a position (row, col) and an identifier/image key
        mock_unit_data = [
            {'position': (0, 1), 'id': 'unit1', 'sprite_key': 'soldier'},
            {'position': (1, 2), 'id': 'unit2', 'sprite_key': 'archer'},
            {'position': (2, 0), 'id': 'unit3', 'sprite_key': 'knight'}
        ]
        
        # Call the render_units method (this should fail until implemented)
        map_view.render_units(mock_unit_data)
        
        # Assert that the surface's drawing methods were called for each unit
        # The surface.blit method should be called once for each unit
        assert mock_pygame_surface.blit.call_count == len(mock_unit_data)
        
        # Check that the correct coordinates were used for drawing each unit
        calls = mock_pygame_surface.blit.call_args_list
        
        # Verify each call to ensure correct positioning based on unit positions and tile size
        # Unit at position (0,1) should be at pixel position (32,0) with tile_size=32
        first_unit_call = calls[0]
        assert first_unit_call[0][1] == (32, 0)
        
        # Unit at position (1,2) should be at pixel position (64,32) with tile_size=32
        second_unit_call = calls[1]
        assert second_unit_call[0][1] == (64, 32)
        
        # Unit at position (2,0) should be at pixel position (0,64) with tile_size=32
        third_unit_call = calls[2]
        assert third_unit_call[0][1] == (0, 64)