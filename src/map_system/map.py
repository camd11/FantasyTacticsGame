# src/map_system/map.py

from typing import List, Optional, Dict # Added Dict

# Global registry for Maps to ensure ID uniqueness
MAP_REGISTRY: Dict[str, 'Map'] = {} # Forward reference 'Map'

# Import necessary classes for type hinting
from .tile import TileInstance
from .tileset import Tileset
from .terrain import TerrainType # TerrainType is part of TileInstance

# Placeholders for future complex types if needed
# from ..character_system.unit import UnitPlacement # Example
# from ..event_system.event import Event           # Example

class Map:
    """
    Represents a single game map, including its grid of tiles, associated tileset,
    and other map-specific data like unit placements and events.

    As per spec `docs/spec/01_MapSystem.md#21-map-data`:
    CLASS Map
        PROPERTIES
            STRING MapID
            INTEGER Width
            INTEGER Height
            ARRAY<ARRAY<TileInstance>> TileGrid
            Tileset MapTileset
            ARRAY<UnitPlacement> InitialUnitPlacements // Future
            ARRAY<Event> MapEvents                     // Future
            STRING Objective                           // Future
        METHODS
            CONSTRUCTOR(MapID, Width, Height, Tileset)
            GetTile(X, Y) RETURNS TileInstance
            SetTile(X, Y, TileInstance)
            IsValidCoordinate(X, Y) RETURNS BOOLEAN
            GetTerrainType(X, Y) RETURNS TerrainType
    """
    def __init__(self, map_id: str, width: int, height: int, tileset: Tileset):
        """
        Initializes a new Map object.

        Args:
            map_id: Unique identifier for the map (e.g., "Chapter1").
            width: Map width in number of tiles. Must be a positive integer.
            height: Map height in number of tiles. Must be a positive integer.
            tileset: The Tileset object used for rendering this map.

        Raises:
            TypeError: If any argument is of an incorrect type.
            ValueError: If map_id is empty, or width/height are not positive integers.
        """
        if not isinstance(map_id, str):
            raise TypeError(f"MapID must be a string, got {type(map_id)}")
        if not map_id:
            raise ValueError("MapID cannot be empty.")

        if not isinstance(width, int):
            raise TypeError(f"Width must be an integer, got {type(width)}")
        if width <= 0:
            raise ValueError(f"Map width must be a positive integer, got {width}")

        if not isinstance(height, int):
            raise TypeError(f"Height must be an integer, got {type(height)}")
        if height <= 0:
            raise ValueError(f"Map height must be a positive integer, got {height}")

        if not isinstance(tileset, Tileset):
            raise TypeError(f"Tileset must be an instance of Tileset, got {type(tileset)}")

        self.map_id: str = map_id
        self.width: int = width
        self.height: int = height
        self.map_tileset: Tileset = tileset # Renamed from self.tileset for clarity

        if map_id in MAP_REGISTRY:
            raise ValueError(f"MapID '{map_id}' already exists in the registry. Map IDs must be unique.")
        MAP_REGISTRY[map_id] = self
        
        # Initialize TileGrid as a 2D list of lists, filled with None initially.
        # Each element will be a TileInstance or None.
        self.tile_grid: List[List[Optional[TileInstance]]] = \
            [[None for _ in range(width)] for _ in range(height)]
        
        # Future properties based on spec:
        self.objective: str = "" # Initialize objective property
        # self.initial_unit_placements: List[UnitPlacement] = []
        # self.map_events: List[Event] = []

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        """
        Checks if the given (x, y) coordinates are within the map bounds.

        Args:
            x: The x-coordinate (column index).
            y: The y-coordinate (row index).

        Returns:
            True if the coordinates are valid, False otherwise.
        """
        if not isinstance(x, int) or not isinstance(y, int):
            # Or raise TypeError, depending on desired strictness for internal methods.
            # For now, returning False for non-int inputs is safer.
            return False
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x: int, y: int) -> Optional[TileInstance]:
        """
        Retrieves the TileInstance at the specified (x, y) coordinates.

        Args:
            x: The x-coordinate of the tile.
            y: The y-coordinate of the tile.

        Returns:
            The TileInstance at the given coordinates, or None if the
            coordinates are out of bounds or no tile is set.
        
        Raises:
            TypeError: If x or y are not integers.
        """
        if not isinstance(x, int):
            raise TypeError(f"X-coordinate must be an integer, got {type(x)}")
        if not isinstance(y, int):
            raise TypeError(f"Y-coordinate must be an integer, got {type(y)}")

        if self.is_valid_coordinate(x, y):
            return self.tile_grid[y][x]
        return None

    def set_tile(self, x: int, y: int, tile_instance: Optional[TileInstance]) -> None:
        """
        Sets or replaces the TileInstance at the specified (x, y) coordinates.
        Can also be used to clear a tile by passing None.

        Args:
            x: The x-coordinate where the tile should be set.
            y: The y-coordinate where the tile should be set.
            tile_instance: The TileInstance object to place on the map,
                           or None to clear the tile at this position.

        Raises:
            TypeError: If x, y are not integers or if tile_instance is not
                       a TileInstance or None.
            IndexError: If the coordinates (x, y) are out of map bounds.
        """
        if not isinstance(x, int):
            raise TypeError(f"X-coordinate must be an integer, got {type(x)}")
        if not isinstance(y, int):
            raise TypeError(f"Y-coordinate must be an integer, got {type(y)}")
        
        if tile_instance is not None and not isinstance(tile_instance, TileInstance):
            raise TypeError(f"tile_instance must be a TileInstance object or None, got {type(tile_instance)}")

        if self.is_valid_coordinate(x, y):
            if tile_instance is not None:
                # Validate TileInstance's IDs against the map's tileset
                # Assumes self.map_tileset has has_tile_id and has_palette_id methods
                # (as provided by MockTileset in tests, or a real Tileset should implement them)
                if not hasattr(self.map_tileset, 'has_tile_id') or \
                   not hasattr(self.map_tileset, 'has_palette_id'):
                    # This case should ideally not happen if Tileset interface is consistent.
                    # For robustness, one might log a warning or have a fallback,
                    # but for TDD, we expect the tests to use a tileset that supports this.
                    pass # Or raise a different error if interface is violated

                if not self.map_tileset.has_tile_id(tile_instance.tile_id):
                    raise ValueError(f"TileID {tile_instance.tile_id} is not valid for the map's tileset.")
                if not self.map_tileset.has_palette_id(tile_instance.palette_id):
                    raise ValueError(f"PaletteID {tile_instance.palette_id} is not valid for the map's tileset.")
            
            self.tile_grid[y][x] = tile_instance
        else:
            raise IndexError(f"Coordinates ({x}, {y}) are out of map bounds (Width: {self.width}, Height: {self.height}).")

    def get_terrain_type(self, x: int, y: int) -> Optional[TerrainType]:
        """
        Retrieves the TerrainType of the tile at the specified (x, y) coordinates.

        Args:
            x: The x-coordinate of the tile.
            y: The y-coordinate of the tile.

        Returns:
            The TerrainType of the tile at the given coordinates, or None if
            the coordinates are invalid, no tile is present at that location,
            or the tile has no terrain information.
            
        Raises:
            TypeError: If x or y are not integers.
        """
        tile = self.get_tile(x, y) # get_tile handles x,y type checks
        if tile and tile.terrain: # tile.terrain is already Optional[TerrainType]
            return tile.terrain
        return None

    def __repr__(self) -> str:
        return f"Map(map_id='{self.map_id}', width={self.width}, height={self.height}, tileset='{self.map_tileset.tileset_id}')"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Map):
            return NotImplemented
        return (self.map_id == other.map_id and
                self.width == other.width and
                self.height == other.height and
                self.map_tileset == other.map_tileset and
                self.tile_grid == other.tile_grid)
                # Comparing initial_unit_placements, map_events, objective
                # would be added here if they were fully implemented.