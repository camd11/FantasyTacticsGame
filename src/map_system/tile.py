# src/map_system/tile.py

from typing import Optional
# Import TerrainType for type hinting.
# The 'src.' prefix assumes this file is part of a package 'src'
# and terrain.py is in the same map_system subpackage.
from .terrain import TerrainType 
# Tileset is not directly used for validation in TileInstance constructor per current spec,
# but would be needed if TileID/PaletteID validation against a specific tileset were added here.
# from .tileset import Tileset

class TileInstance:
    """
    Represents a specific instance of a tile on the map grid, including its
    graphical properties and terrain information.

    As per spec `docs/spec/01_MapSystem.md#22-tile-instance-data`:
    CLASS TileInstance
        PROPERTIES
            INTEGER TileID      // Index of the tile graphic within the tileset
            INTEGER PaletteID   // Index of the palette used for this tile
            BOOLEAN HorizontalFlip // Whether the tile graphic is flipped horizontally
            BOOLEAN VerticalFlip   // Whether the tile graphic is flipped vertically
            TerrainType Terrain // The terrain type of this tile
        METHODS
            CONSTRUCTOR(TileID, PaletteID, HorizontalFlip, VerticalFlip, Terrain)
        TEST: TileID and PaletteID must be valid for the associated MapTileset
              (This test is more applicable at the Map or loading level, where the
               Tileset context is available)
    """
    def __init__(self,
                 tile_id: int,
                 palette_id: int,
                 horizontal_flip: bool,
                 vertical_flip: bool,
                 terrain: Optional[TerrainType]):
        """
        Initializes a new TileInstance.

        Args:
            tile_id: Index of the tile graphic within the map's tileset.
                     Must be a non-negative integer.
            palette_id: Index of the palette within the map's tileset.
                        Must be a non-negative integer.
            horizontal_flip: Boolean indicating if the tile graphic is flipped horizontally.
            vertical_flip: Boolean indicating if the tile graphic is flipped vertically.
            terrain: An instance of TerrainType representing the terrain of this tile,
                     or None if no specific terrain is assigned.

        Raises:
            TypeError: If any argument is of an incorrect type.
            ValueError: If tile_id or palette_id are negative.
        """
        if not isinstance(tile_id, int):
            raise TypeError(f"TileID must be an integer, got {type(tile_id)}")
        if tile_id < 0:
            raise ValueError(f"TileID must be non-negative, got {tile_id}")

        if not isinstance(palette_id, int):
            raise TypeError(f"PaletteID must be an integer, got {type(palette_id)}")
        if palette_id < 0:
            raise ValueError(f"PaletteID must be non-negative, got {palette_id}")

        if not isinstance(horizontal_flip, bool):
            raise TypeError(f"HorizontalFlip must be a boolean, got {type(horizontal_flip)}")
        
        if not isinstance(vertical_flip, bool):
            raise TypeError(f"VerticalFlip must be a boolean, got {type(vertical_flip)}")

        if terrain is not None and not isinstance(terrain, TerrainType):
            raise TypeError(f"Terrain must be an instance of TerrainType or None, got {type(terrain)}")

        self.tile_id: int = tile_id
        self.palette_id: int = palette_id
        self.horizontal_flip: bool = horizontal_flip
        self.vertical_flip: bool = vertical_flip
        self.terrain: Optional[TerrainType] = terrain
        
        # Note on validation:
        # The spec mentions "TEST: TileID and PaletteID must be valid for the associated MapTileset".
        # This validation is context-dependent (requires the Map's Tileset).
        # It's typically handled during map loading or by a factory that has access
        # to the Tileset, rather than in the TileInstance constructor itself,
        # unless the Tileset is passed in, which is not current practice per tests/spec.

    def __repr__(self) -> str:
        terrain_name = self.terrain.name if self.terrain else "None"
        return (f"TileInstance(id={self.tile_id}, pal={self.palette_id}, "
                f"hflip={self.horizontal_flip}, vflip={self.vertical_flip}, "
                f"terrain='{terrain_name}')")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TileInstance):
            return NotImplemented
        return (self.tile_id == other.tile_id and
                self.palette_id == other.palette_id and
                self.horizontal_flip == other.horizontal_flip and
                self.vertical_flip == other.vertical_flip and
                self.terrain == other.terrain)