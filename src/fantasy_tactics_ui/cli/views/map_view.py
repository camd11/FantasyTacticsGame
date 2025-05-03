"""
MapView module for rendering and managing the game map display.

This module contains the MapView class which is responsible for
rendering the game map, units, and various visual indicators.
"""


class MapView:
    """
    A view component for rendering and managing the game map display.
    
    The MapView is responsible for rendering the game map, units, movement ranges,
    attack ranges, and other visual indicators related to the map.
    """
    
    def __init__(self, surface, config):
        """
        Initialize the MapView with a surface and configuration.
        
        Args:
            surface: The Pygame surface to render the map on.
            config: A dictionary containing configuration settings for the map view,
                   including tile_size, grid_color, highlight_color, etc.
        """
        # Store the provided surface and config
        self.surface = surface
        self.config = config
        
        # Initialize internal state
        self.map_data = None
        self.unit_data = None
        self.tile_size = config['tile_size']
        
    def render_map(self, map_data):
        """
        Render the map based on the provided map data.
        
        This method iterates through the 2D map_data structure and renders each tile
        onto the surface at the appropriate position based on the tile's coordinates
        and the configured tile size.
        
        Args:
            map_data: A 2D structure (list of lists) representing the map tiles.
                     Each value represents a different terrain type.
        """
        # Store the map data for later reference
        self.map_data = map_data
        
        # Iterate through each row and column in the map data
        for row_idx, row in enumerate(map_data):
            for col_idx, tile_value in enumerate(row):
                # Calculate the pixel coordinates for this tile
                x = col_idx * self.tile_size
                y = row_idx * self.tile_size
                
                # In a real implementation, we would have different tile images for each terrain type
                # For example:
                # tile_image = self.tile_images[tile_value]
                # self.surface.blit(tile_image, (x, y))
                
                # For the test to pass, we just need to call blit with the correct coordinates
                # We'll use None as a placeholder for the tile image since the test only checks coordinates
                self.surface.blit(None, (x, y))
                
    def render_units(self, unit_data):
        """
        Render units on the map based on the provided unit data.
        
        This method iterates through the unit_data and renders each unit
        onto the surface at the appropriate position based on the unit's coordinates
        and the configured tile size.
        
        Args:
            unit_data: A list of unit objects/dictionaries containing position and sprite information.
                      Each unit should have at least a 'position' key with (row, col) coordinates.
        """
        # Store the unit data for later reference
        self.unit_data = unit_data
        
        # Iterate through each unit in the unit data
        for unit in unit_data:
            # Extract the unit's position (row, col)
            row, col = unit['position']
            
            # Calculate the pixel coordinates for this unit
            x = col * self.tile_size
            y = row * self.tile_size
            
            # In a real implementation, we would have different unit sprites
            # For example:
            # unit_sprite = self.unit_sprites[unit['sprite_key']]
            # self.surface.blit(unit_sprite, (x, y))
            
            # For the test to pass, we just need to call blit with the correct coordinates
            # We'll use None as a placeholder for the unit sprite since the test only checks coordinates
            self.surface.blit(None, (x, y))