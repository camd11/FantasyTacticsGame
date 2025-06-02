# src/map_system/tileset.py

from typing import List, Dict # Added Dict

# Global registry for Tilesets to ensure ID uniqueness
TILESET_REGISTRY: Dict[str, 'Tileset'] = {} # Forward reference 'Tileset'

class Color:
    """
    Represents a color with Red, Green, Blue, and Alpha components.

    As per spec `docs/spec/01_MapSystem.md#23-tileset-data`:
    CLASS Color
        PROPERTIES
            INTEGER R, G, B, A // Red, Green, Blue, Alpha components
        TEST: Color components must be within valid range (e.g., 0-255)
    """
    def __init__(self, r: int, g: int, b: int, a: int = 255):
        """
        Initializes a Color object.

        Args:
            r: Red component (0-255).
            g: Green component (0-255).
            b: Blue component (0-255).
            a: Alpha component (0-255), defaults to 255 (opaque).

        Raises:
            ValueError: If any color component is outside the 0-255 range.
            TypeError: If any color component is not an integer.
        """
        if not isinstance(r, int):
            raise TypeError(f"Red component R must be an int, got {type(r)}")
        if not (0 <= r <= 255):
            raise ValueError(f"Red component R must be between 0-255, got {r}")
        if not isinstance(g, int):
            raise TypeError(f"Green component G must be an int, got {type(g)}")
        if not (0 <= g <= 255):
            raise ValueError(f"Green component G must be between 0-255, got {g}")
        if not isinstance(b, int):
            raise TypeError(f"Blue component B must be an int, got {type(b)}")
        if not (0 <= b <= 255):
            raise ValueError(f"Blue component B must be between 0-255, got {b}")
        if not isinstance(a, int):
            raise TypeError(f"Alpha component A must be an int, got {type(a)}")
        if not (0 <= a <= 255):
            raise ValueError(f"Alpha component A must be between 0-255, got {a}")
        
        self.r: int = r
        self.g: int = g
        self.b: int = b
        self.a: int = a

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Color):
            return NotImplemented
        return self.r == other.r and \
               self.g == other.g and \
               self.b == other.b and \
               self.a == other.a
    
    def __repr__(self) -> str:
        return f"Color(r={self.r}, g={self.g}, b={self.b}, a={self.a})"

class Palette:
    """
    Represents a color palette, typically containing 16 colors.

    As per spec `docs/spec/01_MapSystem.md#23-tileset-data`:
    CLASS Palette
        PROPERTIES
            ARRAY<Color> Colors // Array of 16 Color objects
        TEST: Palette must contain exactly 16 colors
    """
    def __init__(self, colors: List[Color]):
        """
        Initializes a Palette object.

        Args:
            colors: A list containing exactly 16 Color objects.

        Raises:
            ValueError: If the colors list does not contain exactly 16 Color objects.
            TypeError: If any item in the colors list is not a Color object or if 'colors' is not a list.
        """
        if not isinstance(colors, list):
            raise TypeError(f"Colors must be a list, got {type(colors)}")
        if len(colors) != 16:
            raise ValueError(f"Palette must contain exactly 16 colors, got {len(colors)}.")
        
        if not all(isinstance(color, Color) for color in colors):
            raise TypeError("All items in colors list must be Color objects.")
            
        self.colors: List[Color] = colors

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Palette):
            return NotImplemented
        return self.colors == other.colors

    def __repr__(self) -> str:
        return f"Palette(colors=[{', '.join(repr(c) for c in self.colors)}])"

class GraphicTile:
    """
    Represents an individual graphical tile (e.g., 8x8 pixel data).

    As per spec `docs/spec/01_MapSystem.md#23-tileset-data`:
    CLASS GraphicTile
        PROPERTIES
            INTEGER BitDepth // e.g., 4 for 4bpp
            RAWDATA PixelData // Raw pixel data for an 8x8 tile
        TEST: PixelData length must match expected size for BitDepth
    """
    def __init__(self, bit_depth: int, pixel_data: bytes):
        """
        Initializes a GraphicTile.

        Args:
            bit_depth: Bits per pixel (e.g., 4 for 4bpp, 8 for 8bpp).
            pixel_data: Raw byte data for an 8x8 tile.

        Raises:
            ValueError: If bit_depth is unsupported or pixel_data length
                        does not match the expected size for the given bit_depth.
            TypeError: If bit_depth is not an int or pixel_data is not bytes.
        """
        if not isinstance(bit_depth, int):
            raise TypeError(f"BitDepth must be an integer, got {type(bit_depth)}")
        if not isinstance(pixel_data, bytes):
            raise TypeError(f"PixelData must be bytes, got {type(pixel_data)}")

        self.bit_depth: int = bit_depth
        self.pixel_data: bytes = pixel_data

        expected_bytes = 0
        if bit_depth == 4:
            expected_bytes = 32 # 8x8 pixels * 4 bits/pixel / 8 bits/byte
        elif bit_depth == 8:
            expected_bytes = 64 # 8x8 pixels * 8 bits/pixel / 8 bits/byte
        else:
            raise ValueError(f"Unsupported bit depth: {bit_depth}. Only 4 and 8 bpp are supported.")

        if len(pixel_data) != expected_bytes:
            raise ValueError(f"Expected {expected_bytes} bytes for {bit_depth}bpp 8x8 tile, got {len(pixel_data)} bytes.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GraphicTile):
            return NotImplemented
        return self.bit_depth == other.bit_depth and \
               self.pixel_data == other.pixel_data

    def __repr__(self) -> str:
        return f"GraphicTile(bit_depth={self.bit_depth}, pixel_data_len={len(self.pixel_data)})"

class Tileset:
    """
    Represents a collection of tiles and their properties for rendering maps.

    As per spec `docs/spec/01_MapSystem.md#23-tileset-data`:
    CLASS Tileset
        PROPERTIES
            STRING TilesetID // Unique identifier for the tileset
            ARRAY<GraphicTile> Tiles // Array of individual graphical tiles
            ARRAY<Palette> Palettes // Array of color palettes
        METHODS
            CONSTRUCTOR(TilesetID)
            LoadFromSource(PathToData)
            GetTileGraphic(TileID, PaletteID, HFlip, VFlip) RETURNS ImageData
    """
    def __init__(self, tileset_id: str):
        """
        Initializes a new Tileset.

        Args:
            tileset_id: Unique identifier for the tileset.

        Raises:
            ValueError: If tileset_id is not a non-empty string.
            TypeError: If tileset_id is not a string.
        """
        if not isinstance(tileset_id, str):
            raise TypeError(f"TilesetID must be a string, got {type(tileset_id)}")
        if not tileset_id:
             raise ValueError("TilesetID must be a non-empty string.")

        self.tileset_id: str = tileset_id
        self.tiles: List[GraphicTile] = []
        self.palettes: List[Palette] = []

        if tileset_id in TILESET_REGISTRY:
            raise ValueError(f"TilesetID '{tileset_id}' already exists in the registry. Tileset IDs must be unique.")
        TILESET_REGISTRY[tileset_id] = self

    def load_from_source(self, path_to_data: str) -> None:
        """
        Loads tiles and palettes from a source data file (e.g., JSON).
        The current implementation expects a JSON file with 'palettes' and 'tiles' keys.
        'palettes' should be a list of palette objects, each with a 'colors' key
        containing a list of 3 or 4-integer lists (R,G,B or R,G,B,A).
        'tiles' should be a list of tile objects, each with 'bit_depth' (int)
        and 'pixel_data_hex' (string of hex bytes).

        Args:
            path_to_data: Path to the data file.

        Raises:
            FileNotFoundError: If the path_to_data does not exist.
            json.JSONDecodeError: If the file is not valid JSON.
            ValueError: If the JSON structure or data types are incorrect,
                        or if data for Color, Palette, GraphicTile is invalid.
            TypeError: If parts of the JSON structure have unexpected types.
        """
        import json

        try:
            with open(path_to_data, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            # Propagate FileNotFoundError as per test expectation
            raise
        except json.JSONDecodeError:
            # Propagate JSONDecodeError as per test expectation
            raise
        
        if not isinstance(data, dict):
            raise TypeError("Tileset data file must contain a JSON object.")

        loaded_palettes: List[Palette] = []
        if "palettes" in data:
            if not isinstance(data["palettes"], list):
                raise TypeError("'palettes' key must correspond to a list.")
            for i, p_data in enumerate(data["palettes"]):
                if not isinstance(p_data, dict):
                    raise TypeError(f"Palette entry at index {i} is not a dictionary.")
                colors_data = p_data.get("colors")
                if colors_data is None:
                    raise ValueError(f"Palette entry at index {i} missing 'colors' key.")
                if not isinstance(colors_data, list):
                    raise TypeError(f"'colors' for palette at index {i} is not a list.")
                
                palette_colors: List[Color] = []
                for j, c_val_list in enumerate(colors_data):
                    if not isinstance(c_val_list, list):
                        raise TypeError(f"Color value list at index {j} in palette {i} is not a list.")
                    try:
                        if len(c_val_list) == 4:
                            palette_colors.append(Color(c_val_list[0], c_val_list[1], c_val_list[2], c_val_list[3]))
                        elif len(c_val_list) == 3:
                            palette_colors.append(Color(c_val_list[0], c_val_list[1], c_val_list[2]))
                        else:
                            raise ValueError(f"Color value list at index {j} in palette {i} has an invalid number of components: {len(c_val_list)} (expected 3 or 4).")
                    except (TypeError, ValueError) as e:
                         raise ValueError(f"Error creating Color for entry at index {j} in palette {i}: {e}")
                
                try:
                    loaded_palettes.append(Palette(palette_colors))
                except (TypeError, ValueError) as e:
                    raise ValueError(f"Error creating Palette from data at index {i}: {e}")
        
        loaded_tiles: List[GraphicTile] = []
        if "tiles" in data:
            if not isinstance(data["tiles"], list):
                raise TypeError("'tiles' key must correspond to a list.")
            for i, t_data in enumerate(data["tiles"]):
                if not isinstance(t_data, dict):
                    raise TypeError(f"Tile entry at index {i} is not a dictionary.")
                
                bit_depth = t_data.get("bit_depth")
                pixel_data_hex = t_data.get("pixel_data_hex")

                if bit_depth is None:
                    raise ValueError(f"Tile entry at index {i} missing 'bit_depth' key.")
                if pixel_data_hex is None:
                    raise ValueError(f"Tile entry at index {i} missing 'pixel_data_hex' key.")
                
                if not isinstance(bit_depth, int):
                     raise TypeError(f"Tile 'bit_depth' at index {i} must be an integer, got {type(bit_depth)}.")
                if not isinstance(pixel_data_hex, str):
                    raise TypeError(f"Tile 'pixel_data_hex' at index {i} must be a string, got {type(pixel_data_hex)}.")

                try:
                    pixel_data = bytes.fromhex(pixel_data_hex)
                    loaded_tiles.append(GraphicTile(bit_depth, pixel_data))
                except ValueError as e: 
                    # This can be from bytes.fromhex (invalid hex string)
                    # or from GraphicTile constructor (wrong length for bit_depth)
                    raise ValueError(f"Error processing tile data for entry at index {i} (pixel_data_hex: '{pixel_data_hex}', bit_depth: {bit_depth}): {e}")

        self.palettes = loaded_palettes
        self.tiles = loaded_tiles
        
        # Per spec, TilesetID is set at construction.
        # If the loaded data also contains a tileset_id, it could be used for validation:
        # file_tileset_id = data.get("tileset_id")
        # if file_tileset_id is not None and file_tileset_id != self.tileset_id:
        #     raise ValueError(f"Tileset ID in file ('{file_tileset_id}') does not match "
        #                      f"instance ID ('{self.tileset_id}').")

    def _generate_image_data_from_tile_and_palette(self, graphic_tile: GraphicTile, palette: Palette, h_flip: bool, v_flip: bool) -> str:
        """
        Private helper to simulate generating image data.
        In a real scenario, this would involve pixel manipulation based on tile data,
        palette, and flips, likely returning an image object or raw pixel buffer.
        For TDD purposes, this is simplified or mocked by tests.
        This method's signature and return type are for illustrative purposes.
        """
        # This is where actual image rendering logic would go.
        # For TDD purposes, the tests often mock this out or expect a specific
        # string/object if this method were to be tested directly without full rendering.
        # The current tests for get_tile_graphic mock this method.
        # If this method were to be called directly by a test, it would need a concrete return.
        # For now, matching the existing behavior of being called by get_tile_graphic
        # and being mocked by tests, raising NotImplementedError is appropriate.
        _ = graphic_tile # Suppress unused variable warning to satisfy linters if not used
        _ = palette      # Suppress unused variable warning
        _ = h_flip       # Suppress unused variable warning
        _ = v_flip       # Suppress unused variable warning
        raise NotImplementedError("Actual image generation from tile and palette is not implemented in this TDD step.")

    def get_tile_graphic(self, tile_id: int, palette_id: int, h_flip: bool, v_flip: bool): # -> MockImageData or actual ImageData
        """
        Retrieves the graphical data for a specific tile, applying palette and flips.
        This method relies on `_generate_image_data_from_tile_and_palette` for the
        actual data generation, which is typically mocked in unit tests.

        Args:
            tile_id: The index of the tile in the tileset's tile list.
            palette_id: The index of the palette in the tileset's palette list.
            h_flip: Boolean indicating if the tile should be horizontally flipped.
            v_flip: Boolean indicating if the tile should be vertically flipped.

        Returns:
            ImageData (or a mock representation) for the specified tile.
            The actual return type depends on the implementation of
            `_generate_image_data_from_tile_and_palette`.

        Raises:
            IndexError: If tile_id or palette_id is out of bounds, or if
                        tiles/palettes lists are empty.
        """
        if not self.tiles:
            raise IndexError("Cannot get tile graphic: No tiles loaded in this tileset.")
        if not self.palettes:
            raise IndexError("Cannot get tile graphic: No palettes loaded in this tileset.")

        if not (isinstance(tile_id, int) and 0 <= tile_id < len(self.tiles)):
            raise IndexError(f"TileID {tile_id} is out of bounds for {len(self.tiles)} tiles.")
        if not (isinstance(palette_id, int) and 0 <= palette_id < len(self.palettes)):
            raise IndexError(f"PaletteID {palette_id} is out of bounds for {len(self.palettes)} palettes.")

        selected_tile = self.tiles[tile_id]
        selected_palette = self.palettes[palette_id]
        
        # The actual image generation is complex and would involve pixel manipulation.
        # For TDD, the tests mock the call to a helper method that would do this.
        # Here, we call the (not fully implemented) helper.
        return self._generate_image_data_from_tile_and_palette(selected_tile, selected_palette, h_flip, v_flip)

    def has_tile_id(self, tile_id: int) -> bool:
        """Checks if the given tile_id is a valid index for the tiles list."""
        if not isinstance(tile_id, int):
            return False # Or raise TypeError depending on desired strictness
        return 0 <= tile_id < len(self.tiles)

    def has_palette_id(self, palette_id: int) -> bool:
        """Checks if the given palette_id is a valid index for the palettes list."""
        if not isinstance(palette_id, int):
            return False # Or raise TypeError
        return 0 <= palette_id < len(self.palettes)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tileset):
            return NotImplemented
        return self.tileset_id == other.tileset_id and \
               self.tiles == other.tiles and \
               self.palettes == other.palettes

    def __repr__(self) -> str:
        return f"Tileset(id='{self.tileset_id}', num_tiles={len(self.tiles)}, num_palettes={len(self.palettes)})"