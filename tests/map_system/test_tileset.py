import pytest

class TestColorCreation:
    def test_color_creation_valid(self):
        """Test creating a Color object with valid RGBA values."""
        from src.map_system.tileset import Color # Fails if not exists

        r, g, b, a = 100, 150, 200, 255
        color = Color(r, g, b, a)
        assert color.r == r
        assert color.g == g
        assert color.b == b
        assert color.a == a

        color_min = Color(0, 0, 0, 0)
        assert color_min.r == 0
        assert color_min.g == 0
        assert color_min.b == 0
        assert color_min.a == 0

        color_max = Color(255, 255, 255, 255)
        assert color_max.r == 255
        assert color_max.g == 255
        assert color_max.b == 255
        assert color_max.a == 255
        
    def test_color_creation_default_alpha(self):
        """Test creating a Color object with default alpha."""
        from src.map_system.tileset import Color
        r, g, b = 50, 60, 70
        color = Color(r, g, b) # Alpha defaults to 255
        assert color.r == r
        assert color.g == g
        assert color.b == b
        assert color.a == 255

    @pytest.mark.parametrize("r, g, b, a, expected_exception_pattern", [
        (-1, 100, 100, 100, r"Red component R must be between 0-255, got -1"),
        (256, 100, 100, 100, r"Red component R must be between 0-255, got 256"),
        (100, -1, 100, 100, r"Green component G must be between 0-255, got -1"),
        (100, 256, 100, 100, r"Green component G must be between 0-255, got 256"),
        (100, 100, -1, 100, r"Blue component B must be between 0-255, got -1"),
        (100, 100, 256, 100, r"Blue component B must be between 0-255, got 256"),
        (100, 100, 100, -1, r"Alpha component A must be between 0-255, got -1"),
        (100, 100, 100, 256, r"Alpha component A must be between 0-255, got 256"),
    ])
    def test_color_creation_invalid_values(self, r, g, b, a, expected_exception_pattern):
        """TEST: Color components must be within valid range (e.g., 0-255)."""
        from src.map_system.tileset import Color
        with pytest.raises(ValueError, match=expected_exception_pattern):
            Color(r, g, b, a)

class TestPaletteCreation:
    @pytest.fixture
    def sixteen_colors(self):
        """Helper to create a list of 16 mock Color objects."""
        from src.map_system.tileset import Color
        return [Color(i, i, i) for i in range(16)]

    def test_palette_creation_valid(self, sixteen_colors):
        """TEST: Palette must contain exactly 16 colors."""
        from src.map_system.tileset import Palette # Fails if not exists
        
        palette = Palette(sixteen_colors)
        assert len(palette.colors) == 16
        assert palette.colors == sixteen_colors
        assert palette.colors[0].r == 0
        assert palette.colors[15].b == 15

    def test_palette_creation_invalid_length_too_few(self, sixteen_colors):
        """Test Palette creation with fewer than 16 colors."""
        from src.map_system.tileset import Palette
        colors_too_few = sixteen_colors[:15]
        with pytest.raises(ValueError, match="Palette must contain exactly 16 colors."):
            Palette(colors_too_few)

    def test_palette_creation_invalid_length_too_many(self, sixteen_colors):
        """Test Palette creation with more than 16 colors."""
        from src.map_system.tileset import Palette, Color
        colors_too_many = sixteen_colors + [Color(16, 16, 16)]
        with pytest.raises(ValueError, match="Palette must contain exactly 16 colors."):
            Palette(colors_too_many)
            
    def test_palette_creation_invalid_type_in_list(self):
        """Test Palette creation with a list containing non-Color objects."""
        from src.map_system.tileset import Palette, Color
        invalid_colors_list = [Color(0,0,0)] * 15 + ["not_a_color"]
        with pytest.raises(TypeError, match="All items in colors list must be Color objects."):
            Palette(invalid_colors_list)

    def test_palette_creation_empty_list(self):
        """Test Palette creation with an empty list."""
        from src.map_system.tileset import Palette
        with pytest.raises(ValueError, match="Palette must contain exactly 16 colors."):
            Palette([])

class TestGraphicTileCreation:
    def test_graphic_tile_creation_valid_4bpp(self):
        """Test GraphicTile creation with valid 4bpp data for an 8x8 tile."""
        from src.map_system.tileset import GraphicTile # Fails if not exists
        
        bit_depth = 4
        # For an 8x8 tile at 4bpp, 64 pixels / 2 pixels per byte = 32 bytes
        pixel_data = b'\x00' * 32
        
        graphic_tile = GraphicTile(bit_depth, pixel_data)
        assert graphic_tile.bit_depth == bit_depth
        assert graphic_tile.pixel_data == pixel_data

    def test_graphic_tile_creation_valid_8bpp(self):
        """Test GraphicTile creation with valid 8bpp data for an 8x8 tile."""
        from src.map_system.tileset import GraphicTile
        
        bit_depth = 8
        # For an 8x8 tile at 8bpp, 64 pixels / 1 pixel per byte = 64 bytes
        pixel_data = b'\x00' * 64
        
        graphic_tile = GraphicTile(bit_depth, pixel_data)
        assert graphic_tile.bit_depth == bit_depth
        assert graphic_tile.pixel_data == pixel_data

    @pytest.mark.parametrize("bit_depth, data_length, expected_message_part", [
        (4, 31, "Expected 32 bytes for 4bpp 8x8 tile, got 31"),
        (4, 33, "Expected 32 bytes for 4bpp 8x8 tile, got 33"),
        (8, 63, "Expected 64 bytes for 8bpp 8x8 tile, got 63"),
        (8, 65, "Expected 64 bytes for 8bpp 8x8 tile, got 65"),
    ])
    def test_graphic_tile_creation_invalid_data_length(self, bit_depth, data_length, expected_message_part):
        """TEST: PixelData length must match expected size for BitDepth."""
        from src.map_system.tileset import GraphicTile
        
        pixel_data = b'\x00' * data_length
        with pytest.raises(ValueError, match=expected_message_part):
            GraphicTile(bit_depth, pixel_data)

    def test_graphic_tile_creation_unsupported_bpp(self):
        """Test GraphicTile creation with an unsupported bit depth."""
        from src.map_system.tileset import GraphicTile
        
        pixel_data = b'\x00' * 16 # Arbitrary length
        with pytest.raises(ValueError, match="Unsupported bit depth: 2. Only 4 and 8 bpp are supported."):
            GraphicTile(2, pixel_data)

class TestTilesetCreation:
    def test_tileset_creation_basic(self):
        """Test basic Tileset creation with an ID."""
        from src.map_system.tileset import Tileset # Fails if not exists
        
        tileset_id = "Chapter1Tileset"
        tileset = Tileset(tileset_id)
        
        assert tileset.tileset_id == tileset_id
        assert tileset.tiles == [] # Expected to be initialized as empty list
        assert tileset.palettes == [] # Expected to be initialized as empty list

    def test_tileset_creation_requires_id(self):
        """Test that Tileset ID is required."""
        from src.map_system.tileset import Tileset
        with pytest.raises(TypeError): # TypeError if constructor argument is missing
            Tileset()

# These fixtures are used by multiple test classes, so define them at module level.
@pytest.fixture
def valid_tileset_data_json_str():
    # 16 colors for one palette
    palette_colors_data = [[i, i, i, 255] for i in range(16)]
    # 32 bytes for one 4bpp 8x8 tile
    tile_pixel_data_hex = "00" * 32
    
    return f"""
    {{
        "tileset_id_from_data": "TestSet_Load",
        "palettes": [
            {{ "colors": {palette_colors_data} }}
        ],
        "tiles": [
            {{ "bit_depth": 4, "pixel_data_hex": "{tile_pixel_data_hex}" }}
        ]
    }}
    """

@pytest.fixture
def mock_file_open(mocker):
    return mocker.patch("builtins.open", mocker.mock_open())

class TestTilesetLoading: # This is the original class, the duplicate below will be removed by the absence of its content in REPLACE
    @pytest.fixture
    def sample_tileset(self):
        from src.map_system.tileset import Tileset
        return Tileset("TestSet_Load")

    def test_load_from_source_valid_data(self, sample_tileset, valid_tileset_data_json_str, mock_file_open, mocker):
        """TEST: Successfully loads valid tileset data."""
        from src.map_system.tileset import GraphicTile, Palette, Color
        
        mock_file_open.return_value.read.return_value = valid_tileset_data_json_str
        
        sample_tileset.load_from_source("dummy/path/to/valid_tileset.json")

        assert len(sample_tileset.palettes) == 1
        assert isinstance(sample_tileset.palettes[0], Palette)
        assert len(sample_tileset.palettes[0].colors) == 16
        assert sample_tileset.palettes[0].colors[0] == Color(0,0,0)
        assert sample_tileset.palettes[0].colors[15] == Color(15,15,15)

        assert len(sample_tileset.tiles) == 1
        assert isinstance(sample_tileset.tiles[0], GraphicTile)
        assert sample_tileset.tiles[0].bit_depth == 4
        assert sample_tileset.tiles[0].pixel_data == bytes.fromhex("00" * 32)
        
        # Check if the original tileset_id is preserved or updated (spec implies it's set at construction)
        assert sample_tileset.tileset_id == "TestSet_Load"


    def test_load_from_source_file_not_found(self, sample_tileset, mock_file_open):
        """TEST: Handles errors for missing data (FileNotFoundError)."""
        mock_file_open.side_effect = FileNotFoundError("File not found at path")
        
        with pytest.raises(FileNotFoundError, match="File not found at path"):
            sample_tileset.load_from_source("dummy/path/to/nonexistent.json")

    def test_load_from_source_invalid_json(self, sample_tileset, mock_file_open, mocker):
        """TEST: Handles errors for invalid data format (e.g., corrupt JSON)."""
        import json # For json.JSONDecodeError
        mock_file_open.return_value.read.return_value = "{'invalid_json': "
        
        # The actual exception might be json.JSONDecodeError or a custom one
        # depending on implementation. For now, assume json.JSONDecodeError.
        with pytest.raises(json.JSONDecodeError):
            sample_tileset.load_from_source("dummy/path/to/corrupt.json")

    def test_load_from_source_data_invalid_palette_length(self, sample_tileset, mock_file_open, mocker):
        """Test loading data where a palette has an invalid number of colors."""
        palette_colors_data_short = [[i, i, i, 255] for i in range(15)] # 15 colors
        tile_pixel_data_hex = "00" * 32
        invalid_palette_data_json_str = f"""
        {{
            "palettes": [
                {{ "colors": {palette_colors_data_short} }}
            ],
            "tiles": [
                {{ "bit_depth": 4, "pixel_data_hex": "{tile_pixel_data_hex}" }}
            ]
        }}
        """
        mock_file_open.return_value.read.return_value = invalid_palette_data_json_str
        with pytest.raises(ValueError, match="Palette must contain exactly 16 colors."):
            sample_tileset.load_from_source("dummy/path/to/invalid_palette.json")

    def test_load_from_source_data_invalid_tile_data_length(self, sample_tileset, mock_file_open, mocker):
        """Test loading data where a tile has incorrect pixel data length."""
        palette_colors_data = [[i, i, i, 255] for i in range(16)]
        tile_pixel_data_hex_short = "00" * 31 # 31 bytes for 4bpp
        invalid_tile_data_json_str = f"""
        {{
            "palettes": [
                {{ "colors": {palette_colors_data} }}
            ],
            "tiles": [
                {{ "bit_depth": 4, "pixel_data_hex": "{tile_pixel_data_hex_short}" }}
            ]
        }}
        """
        mock_file_open.return_value.read.return_value = invalid_tile_data_json_str
        with pytest.raises(ValueError, match="Expected 32 bytes for 4bpp 8x8 tile, got 31"):
            sample_tileset.load_from_source("dummy/path/to/invalid_tile.json")

class MockImageData:
    def __init__(self, description: str):
        self.description = description
    def __repr__(self):
        return f"MockImageData({self.description})"
    def __eq__(self, other):
        if not isinstance(other, MockImageData):
            return NotImplemented
        return self.description == other.description

class TestTilesetGetTileGraphic:
    @pytest.fixture
    def populated_tileset(self, valid_tileset_data_json_str, mock_file_open, mocker):
        from src.map_system.tileset import Tileset
        # This reuses the valid_tileset_data_json_str which defines one tile and one palette
        mock_file_open.return_value.read.return_value = valid_tileset_data_json_str
        tileset = Tileset("PopulatedSet")
        tileset.load_from_source("dummy/path.json")
        
        # For clarity in tests, let's mock the actual image generation part
        # The core logic is selecting the right GraphicTile and Palette
        mocker.patch(
            'src.map_system.tileset.Tileset._generate_image_data_from_tile_and_palette',
            side_effect=lambda gt, pal, hf, vf: MockImageData(f"Tile:{gt.bit_depth}bpp_Pal:{len(pal.colors)}cols_H:{hf}_V:{vf}")
        )
        return tileset

    def test_get_tile_graphic_valid(self, populated_tileset):
        """TEST: Tileset_GetTileGraphic_Correct - Returns correct visual data."""
        # Tileset has 1 tile (index 0) and 1 palette (index 0) from valid_tileset_data_json_str
        
        image_data_no_flip = populated_tileset.get_tile_graphic(0, 0, False, False)
        assert image_data_no_flip == MockImageData("Tile:4bpp_Pal:16cols_H:False_V:False")

        image_data_h_flip = populated_tileset.get_tile_graphic(0, 0, True, False)
        assert image_data_h_flip == MockImageData("Tile:4bpp_Pal:16cols_H:True_V:False")

        image_data_v_flip = populated_tileset.get_tile_graphic(0, 0, False, True)
        assert image_data_v_flip == MockImageData("Tile:4bpp_Pal:16cols_H:False_V:True")

        image_data_both_flip = populated_tileset.get_tile_graphic(0, 0, True, True)
        assert image_data_both_flip == MockImageData("Tile:4bpp_Pal:16cols_H:True_V:True")

    def test_get_tile_graphic_invalid_tile_id(self, populated_tileset):
        """Test get_tile_graphic with an out-of-bounds TileID."""
        with pytest.raises(IndexError, match=r"TileID 1 is out of bounds for 1 tiles."):
            populated_tileset.get_tile_graphic(1, 0, False, False) # Only 1 tile at index 0
        
        with pytest.raises(IndexError, match=r"TileID -1 is out of bounds for 1 tiles."):
            populated_tileset.get_tile_graphic(-1, 0, False, False)

    def test_get_tile_graphic_invalid_palette_id(self, populated_tileset):
        """Test get_tile_graphic with an out-of-bounds PaletteID."""
        with pytest.raises(IndexError, match=r"PaletteID 1 is out of bounds for 1 palettes."):
            populated_tileset.get_tile_graphic(0, 1, False, False) # Only 1 palette at index 0

        with pytest.raises(IndexError, match=r"PaletteID -1 is out of bounds for 1 palettes."):
            populated_tileset.get_tile_graphic(0, -1, False, False)

    def test_get_tile_graphic_empty_tiles(self):
        """Test get_tile_graphic when tiles list is empty."""
        from src.map_system.tileset import Tileset, Palette, Color
        tileset = Tileset("EmptyTiles")
        # Add a palette so PaletteID is valid, but no tiles
        tileset.palettes.append(Palette([Color(0,0,0)]*16))
        with pytest.raises(IndexError, match="Cannot get tile graphic: No tiles loaded in this tileset."):
            tileset.get_tile_graphic(0, 0, False, False)

    def test_get_tile_graphic_empty_palettes(self):
        """Test get_tile_graphic when palettes list is empty."""
        from src.map_system.tileset import Tileset, GraphicTile
        tileset = Tileset("EmptyPalettes")
        # Add a tile so TileID is valid, but no palettes
        tileset.tiles.append(GraphicTile(4, b'\x00'*32))
        with pytest.raises(IndexError, match="Cannot get tile graphic: No palettes loaded in this tileset."):
            tileset.get_tile_graphic(0, 0, False, False)