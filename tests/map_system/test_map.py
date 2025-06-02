import pytest

# Placeholder for eventual imports
# from src.map_system.map import Map
from src.map_system.tileset import Tileset # Import the actual Tileset
from src.map_system.tile import TileInstance # Import the actual TileInstance
from tests.map_system.test_tile import MockTerrainType, mock_terrain # Import the correct MockTerrainType and its fixture

# Mock Tileset class for now, as it's not the focus of these initial tests
class MockTileset(Tileset): # Inherit from Tileset
    def __init__(self, tileset_id, num_graphic_tiles=1, num_palettes=1): # Simplified args
        super().__init__(tileset_id=tileset_id)
        # Populate with mock GraphicTile and Palette objects based on counts
        # This allows checking valid ID ranges (0 to num-1)
        from src.map_system.tileset import GraphicTile, Palette, Color # For mock population
        
        self.tiles = [GraphicTile(bit_depth=4, pixel_data=b'\x00'*32) for _ in range(num_graphic_tiles)]
        
        mock_color = Color(0,0,0)
        self.palettes = [Palette(colors=[mock_color]*16) for _ in range(num_palettes)]

    def has_tile_id(self, tile_id: int) -> bool:
        return 0 <= tile_id < len(self.tiles)

    def has_palette_id(self, palette_id: int) -> bool:
        return 0 <= palette_id < len(self.palettes)

@pytest.fixture
def mock_tileset_with_content():
    # Provides a tileset with a known number of tiles/palettes for validation tests
    return MockTileset("test_tileset_with_content", num_graphic_tiles=2, num_palettes=2)

@pytest.fixture
def mock_tileset_empty():
    # Provides a tileset with no tiles/palettes
    return MockTileset("test_tileset_empty", num_graphic_tiles=0, num_palettes=0)

# Local MockTerrainType and mock_terrain_type fixture are removed, using imported ones.

# Mock TileInstance class for testing get_tile and set_tile
class MockTileInstance(TileInstance): # Inherit from TileInstance
    def __init__(self, tile_id_val=0, palette_id_val=0, h_flip_val=False, v_flip_val=False, terrain_val=None):
        # Provide default values for TileInstance's constructor
        # The 'tile_id' in MockTileInstance was a string, but TileInstance expects an int.
        # For the mock, we'll keep the string for self.tile_id for existing assertions,
        # but pass an int to super().
        super().__init__(
            tile_id=tile_id_val, # Actual TileInstance expects int
            palette_id=palette_id_val,
            horizontal_flip=h_flip_val,
            vertical_flip=v_flip_val,
            terrain=terrain_val
        )
        # Keep the original string tile_id for mock's direct attribute if tests rely on it
        self.tile_id_str = str(tile_id_val) if isinstance(tile_id_val, int) else "mock_tile_default"
        # self.terrain is handled by super().__init__

    # __eq__ might need adjustment if superclass __eq__ is sufficient or different
    # For now, let's assume the superclass __eq__ will be used or this one will be refined.
    # If direct comparison of self.tile_id_str is needed by tests, that logic remains.
    # However, the TypeError was about isinstance(mock, TileInstance), which inheritance solves.

# mock_terrain_type fixture is removed, using imported mock_terrain

@pytest.fixture
def mock_tile_instance(mock_terrain): # Default tile with no specific terrain, uses imported mock_terrain
    # Adjusting to pass appropriate int tile_id to the new MockTileInstance constructor
    return MockTileInstance(tile_id_val=1)

@pytest.fixture
def mock_tile_with_terrain(mock_terrain): # Uses imported mock_terrain
    # Adjusting to pass appropriate int tile_id and the terrain object
    # Using tile_id_val=1, which is valid for mock_tileset_with_content (num_graphic_tiles=2)
    # Also adding flip arguments as required by MockTileInstance constructor
    return MockTileInstance(tile_id_val=1, palette_id_val=0, h_flip_val=False, v_flip_val=False, terrain_val=mock_terrain)


class TestMapCreation:
    def test_map_creation_valid_dimensions(self, mock_tileset_with_content): # Use fixture that provides a tileset
        """
        TEST: Map dimensions must be positive integers.
        TEST: TileGrid dimensions must match Width and Height.
        """
        from src.map_system.map import Map  # Import here to ensure it fails if not found
        map_id = "Chapter1"
        width = 30
        height = 20
        game_map = Map(map_id, width, height, mock_tileset_with_content)

        assert game_map.map_id == map_id
        assert game_map.width == width
        assert game_map.height == height
        assert game_map.map_tileset == mock_tileset_with_content
        assert len(game_map.tile_grid) == height
        assert all(len(row) == width for row in game_map.tile_grid)
        # Ensure tile_grid is initialized (e.g., with None or default TileInstance)
        # For now, just checking structure. Content check will come with TileInstance tests.

    def test_map_creation_invalid_dimensions_zero(self, mock_tileset_with_content): # Use fixture
        """Test map creation with zero width or height."""
        from src.map_system.map import Map
        with pytest.raises(ValueError, match=r"Map (width|height) must be a positive integer"):
            Map("Chapter0", 0, 20, mock_tileset_with_content)
        with pytest.raises(ValueError, match=r"Map (width|height) must be a positive integer"):
            Map("Chapter0", 30, 0, mock_tileset_with_content)

    def test_map_creation_invalid_dimensions_negative(self, mock_tileset_with_content): # Use fixture
        """Test map creation with negative width or height."""
        from src.map_system.map import Map
        with pytest.raises(ValueError, match=r"Map (width|height) must be a positive integer"):
            Map("ChapterN", -5, 20, mock_tileset_with_content)
        with pytest.raises(ValueError, match=r"Map (width|height) must be a positive integer"):
            Map("ChapterN", 30, -5, mock_tileset_with_content)

    def test_map_objective_property(self, mock_tileset_with_content):
        """Tests the objective property of the map."""
        from src.map_system.map import Map
        game_map = Map("ObjectiveMap", 10, 10, mock_tileset_with_content)
        
        # Check initial value
        assert game_map.objective == "", "Objective should be an empty string initially."
        
        # Set and check new value
        new_objective = "Seize the throne."
        game_map.objective = new_objective
        assert game_map.objective == new_objective

class TestMapCoordinateValidation:
    @pytest.fixture
    def sample_map(self, mock_tileset_with_content): # Use fixture
        from src.map_system.map import Map
        return Map("SampleMap", 10, 8, mock_tileset_with_content)

    @pytest.mark.parametrize("x, y, expected", [
        (0, 0, True),      # Top-left corner
        (9, 7, True),      # Bottom-right corner
        (5, 4, True),      # Middle of the map
        (0, 7, True),      # Bottom-left
        (9, 0, True),      # Top-right
    ])
    def test_is_valid_coordinate_valid(self, sample_map, x, y, expected):
        """TEST: Checks if coordinates are within map bounds (valid cases)."""
        assert sample_map.is_valid_coordinate(x, y) == expected

    @pytest.mark.parametrize("x, y, expected", [
        (-1, 0, False),     # Negative X
        (0, -1, False),     # Negative Y
        (10, 0, False),     # X equals width (out of bounds)
        (0, 8, False),      # Y equals height (out of bounds)
        (10, 7, False),     # X out of bounds, Y in bounds
        (9, 8, False),      # X in bounds, Y out of bounds
        (15, 10, False),    # Far out of bounds
    ])
    def test_is_valid_coordinate_invalid(self, sample_map, x, y, expected):
        """TEST: Checks if coordinates are within map bounds (invalid cases)."""
        assert sample_map.is_valid_coordinate(x, y) == expected

class TestMapTileOperations:
    @pytest.fixture
    def game_map(self, mock_tileset_with_content): # Use fixture that has content
        from src.map_system.map import Map
        return Map("TileOpMap", 5, 3, mock_tileset_with_content)

    def test_get_tile_initially_none(self, game_map):
        """Test that get_tile returns None for all cells in a newly created map."""
        for y in range(game_map.height):
            for x in range(game_map.width):
                assert game_map.get_tile(x, y) is None, f"Expected None at ({x},{y})"

    def test_set_and_get_tile_valid_coordinates(self, game_map, mock_tile_instance):
        """TEST: Returns correct tile for valid coordinates after setting."""
        game_map.set_tile(2, 1, mock_tile_instance)
        retrieved_tile = game_map.get_tile(2, 1)
        assert retrieved_tile is not None
        assert retrieved_tile == mock_tile_instance
        # If mock_tile_instance.tile_id was the int, use that.
        # If it was the string, use mock_tile_instance.tile_id_str
        # The original test checked against "test_tile_1", which was a string.
        # The MockTileInstance now takes an int for super, but we can keep a string version.
        # Let's assume the test wants to check the conceptual ID used when creating the mock.
        # The mock_tile_instance fixture was updated to pass tile_id_val=1.
        # So, we should check against the int value or the string representation of it.
        # The original TileInstance stores tile_id as int.
        assert retrieved_tile.tile_id == 1 # mock_tile_instance was created with tile_id_val=1

        # Check other tiles are still None
        assert game_map.get_tile(0, 0) is None
        assert game_map.get_tile(2, 0) is None

    def test_get_tile_invalid_coordinates(self, game_map):
        """TEST: Map_GetTile_InvalidCoordinates - handles out-of-bounds requests."""
        assert game_map.get_tile(-1, 0) is None
        assert game_map.get_tile(0, -1) is None
        assert game_map.get_tile(game_map.width, 0) is None
        assert game_map.get_tile(0, game_map.height) is None
        assert game_map.get_tile(game_map.width, game_map.height) is None

    def test_set_tile_invalid_coordinates(self, game_map, mock_tile_instance):
        """Test that set_tile raises an error for out-of-bounds coordinates."""
        with pytest.raises(IndexError, match=r"Coordinates \(-1, 0\) are out of map bounds \(Width: 5, Height: 3\)\."):
            game_map.set_tile(-1, 0, mock_tile_instance)
        with pytest.raises(IndexError, match=r"Coordinates \(0, -1\) are out of map bounds \(Width: 5, Height: 3\)\."):
            game_map.set_tile(0, -1, mock_tile_instance)
        with pytest.raises(IndexError, match=r"Coordinates \(5, 0\) are out of map bounds \(Width: 5, Height: 3\)\."):
            game_map.set_tile(game_map.width, 0, mock_tile_instance)
        with pytest.raises(IndexError, match=r"Coordinates \(0, 3\) are out of map bounds \(Width: 5, Height: 3\)\."):
            game_map.set_tile(0, game_map.height, mock_tile_instance)
        with pytest.raises(IndexError, match=r"Coordinates \(5, 3\) are out of map bounds \(Width: 5, Height: 3\)\."):
            game_map.set_tile(game_map.width, game_map.height, mock_tile_instance)

    def test_get_terrain_type_valid_coordinates_with_terrain(self, game_map, mock_tile_with_terrain, mock_terrain): # Uses imported mock_terrain
        """TEST: Map_GetTerrainType_Correct - Returns correct terrain for tile."""
        game_map.set_tile(1, 1, mock_tile_with_terrain)
        terrain = game_map.get_terrain_type(1, 1)
        assert terrain is not None
        assert terrain == mock_terrain # Compare with the imported mock_terrain
        assert terrain.name == "Plains" # The imported mock_terrain from test_tile is "Plains" by default in its fixture

    def test_get_terrain_type_valid_coordinates_tile_without_terrain(self, game_map, mock_tile_instance):
        """Test get_terrain_type when tile exists but has no terrain data."""
        # mock_tile_instance by default has terrain=None
        game_map.set_tile(1, 1, mock_tile_instance)
        terrain = game_map.get_terrain_type(1, 1)
        assert terrain is None

    def test_get_terrain_type_valid_coordinates_no_tile(self, game_map):
        """Test get_terrain_type when no tile is set at the coordinates."""
        # No tile set at (0,0) initially
        terrain = game_map.get_terrain_type(0, 0)
        assert terrain is None

    def test_get_terrain_type_invalid_coordinates(self, game_map):
        """Test get_terrain_type for out-of-bounds coordinates."""
        assert game_map.get_terrain_type(-1, 0) is None
        assert game_map.get_terrain_type(0, -1) is None
        assert game_map.get_terrain_type(game_map.width, 0) is None
        assert game_map.get_terrain_type(0, game_map.height) is None

    def test_set_tile_invalid_tile_id_for_tileset(self, game_map, mock_terrain): # game_map uses mock_tileset_with_content
        """Test set_tile with a TileInstance having a tile_id invalid for the map's tileset."""
        # mock_tileset_with_content has num_graphic_tiles=2 (so valid tile_ids are 0, 1)
        invalid_tile_id = 2
        tile_with_invalid_id = TileInstance(
            tile_id=invalid_tile_id, palette_id=0, horizontal_flip=False, vertical_flip=False, terrain=mock_terrain
        )
        with pytest.raises(ValueError, match=f"TileID {invalid_tile_id} is not valid for the map's tileset."):
            game_map.set_tile(0, 0, tile_with_invalid_id)

    def test_set_tile_invalid_palette_id_for_tileset(self, game_map, mock_terrain): # game_map uses mock_tileset_with_content
        """Test set_tile with a TileInstance having a palette_id invalid for the map's tileset."""
        # mock_tileset_with_content has num_palettes=2 (so valid palette_ids are 0, 1)
        invalid_palette_id = 2
        tile_with_invalid_palette = TileInstance(
            tile_id=0, palette_id=invalid_palette_id, horizontal_flip=False, vertical_flip=False, terrain=mock_terrain
        )
        with pytest.raises(ValueError, match=f"PaletteID {invalid_palette_id} is not valid for the map's tileset."):
            game_map.set_tile(0, 0, tile_with_invalid_palette)

    def test_set_tile_valid_ids_for_tileset(self, game_map, mock_terrain): # game_map uses mock_tileset_with_content
        """Test set_tile with a TileInstance having valid tile_id and palette_id."""
        # mock_tileset_with_content has num_graphic_tiles=2, num_palettes=2
        valid_tile_id = 1
        valid_palette_id = 1
        tile_with_valid_ids = TileInstance(
            tile_id=valid_tile_id, palette_id=valid_palette_id, horizontal_flip=False, vertical_flip=False, terrain=mock_terrain
        )
        # This should not raise an error
        game_map.set_tile(0, 0, tile_with_valid_ids)
        retrieved = game_map.get_tile(0,0)
        assert retrieved is not None
        assert retrieved.tile_id == valid_tile_id
        assert retrieved.palette_id == valid_palette_id

class TestMapRegistryAndUniqueness:
    # The clear_map_registry_globally fixture from conftest.py will handle registry clearing.
    # The clear_tileset_registry_globally fixture from conftest.py handles tileset registry.

    def test_map_id_uniqueness_enforced(self, mock_tileset_with_content):
        """
        TEST: MapID must be unique across all maps.
        Attempts to create two maps with the same ID, expecting an error.
        """
        from src.map_system.map import Map

        map_id = "UniqueMapID_1"
        # First creation should succeed
        map1 = Map(map_id, 10, 10, mock_tileset_with_content)
        assert map1.map_id == map_id

        # Second creation with the same ID should fail
        with pytest.raises(ValueError, match=f"MapID '{map_id}' already exists in the registry. Map IDs must be unique."):
            Map(map_id, 15, 15, mock_tileset_with_content)

    def test_different_map_ids_are_allowed(self, mock_tileset_with_content):
        """Tests that different MapIDs can be registered without error."""
        from src.map_system.map import Map
        import src.map_system.map as map_module # To access MAP_REGISTRY

        map_id1 = "AllowedMapID_1"
        map_id2 = "AllowedMapID_2"

        map1 = Map(map_id1, 10, 10, mock_tileset_with_content)
        assert map1.map_id == map_id1
        assert map_id1 in map_module.MAP_REGISTRY

        map2 = Map(map_id2, 12, 12, mock_tileset_with_content)
        assert map2.map_id == map_id2
        assert map_id2 in map_module.MAP_REGISTRY
        
        assert len(map_module.MAP_REGISTRY) == 2