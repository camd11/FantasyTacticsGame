import unittest
from unittest.mock import MagicMock, patch

from src.core_engine.game_state import GameStateManager
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum
from src.gameplay_systems.map_system import MapSystem
from src.gameplay_systems.movement_system import MovementSystem


class TestMovementRange(unittest.TestCase):
    """Test cases specifically for movement range calculation."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_data_provider = MagicMock(name="DataProvider")
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        
        # Create the MapSystem instance
        self.map_system = MapSystem()
        self.map_system.initialize(self.mock_game_state_manager, self.mock_data_provider)
        
        # Mock the class data
        mock_class = MagicMock(name="ClassData")
        mock_class.movement_type = MovementTypeEnum.INFANTRY
        self.mock_data_provider.get_class_data.return_value = mock_class
        
        # Create the MovementSystem instance
        self.movement_system = MovementSystem()
        self.movement_system.initialize(self.mock_game_state_manager, self.map_system)
        
    def test_unit_with_mov_greater_than_one_on_plains(self):
        """Test that a unit with MOV > 1 on plains terrain has a range greater than just the starting tile."""
        # Create a mock unit with MOV = 5
        mock_unit = MagicMock(name="Unit")
        mock_unit.position = (5, 5)
        mock_unit.stats = {"MOV": 5}
        mock_unit.class_id = "INFANTRY"
        # Don't set movement_type on the unit, it should come from the class data
        
        # Configure mock game state manager
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_game_state_manager.get_map_dimensions.return_value = (10, 10)
        
        # Configure mock terrain types
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN
        
        # Configure mock data provider to return terrain costs
        # This is the key part that tests the fix - using TerrainTypeEnum.PLAIN
        self.mock_data_provider.get_terrain_cost.side_effect = lambda terrain_type, movement_type: 1 if terrain_type == TerrainTypeEnum.PLAIN else 99
        
        # Calculate movement range
        reachable_tiles = self.map_system.get_reachable_tiles("UNIT1")
        
        # Verify that the range includes more than just the starting tile
        self.assertGreater(len(reachable_tiles), 1, "Movement range should include more than just the starting tile")
        
        # Verify that the range includes tiles at the maximum distance (MOV = 5)
        max_distance_tiles = [(5, 0), (0, 5), (10, 5), (5, 10)]  # Tiles at distance 5 from (5, 5)
        for tile in max_distance_tiles:
            if 0 <= tile[0] < 10 and 0 <= tile[1] < 10:  # Check if tile is within map bounds
                self.assertIn(tile, reachable_tiles, f"Tile {tile} at maximum distance should be reachable")
        
        # Verify that the data provider was called with TerrainTypeEnum.PLAIN
        self.mock_data_provider.get_terrain_cost.assert_any_call(TerrainTypeEnum.PLAIN, MovementTypeEnum.INFANTRY)


if __name__ == '__main__':
    unittest.main()