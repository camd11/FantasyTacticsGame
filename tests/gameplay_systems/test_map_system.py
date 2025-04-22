import unittest
from unittest.mock import MagicMock, patch, call, Mock

from src.gameplay_systems.map_system import MapSystem, PathfindingAlgorithm, IMPASSABLE, TERRAIN_INVALID
from src.core_engine.data_provider import TerrainTypeEnum, MovementTypeEnum
from src.core_engine.game_state import FactionEnum

# Constants for testing
MOV = "MOV"
WEAPON = "WEAPON"

class TestMapSystem(unittest.TestCase):
    """Test cases for the MapSystem class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock objects for dependencies
        self.mock_game_state_manager = MagicMock(name="GameStateManager")
        self.mock_data_provider = MagicMock(name="DataProvider")
        
        # Create the MapSystem instance
        self.map_system = MapSystem()
        self.map_system.initialize(self.mock_game_state_manager, self.mock_data_provider)
        
        # Mock the pathfinder to isolate MapSystem tests
        self.map_system.pathfinder = MagicMock(name="PathfindingAlgorithm")

    # TDD: Test get_terrain_properties returns correct data for various terrain types
    def test_get_terrain_properties_returns_correct_data(self):
        """Test that get_terrain_properties returns the correct terrain data."""
        # Arrange
        position = (3, 4)
        terrain_type = TerrainTypeEnum.PLAIN
        terrain_data = MagicMock()
        terrain_data.name = "Plains"
        terrain_data.bonuses = {"def": 0, "avo": 0}
        terrain_data.is_healing = False
        terrain_data.is_indoor = False
        
        self.mock_game_state_manager.get_terrain_type.return_value = terrain_type
        self.mock_data_provider.get_terrain_data.return_value = terrain_data
        
        # Act
        result = self.map_system.get_terrain_properties(position)
        
        # Assert
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)
        self.mock_data_provider.get_terrain_data.assert_called_once_with(terrain_type)
        self.assertEqual(result['type'], terrain_type)
        self.assertEqual(result['name'], "Plains")
        self.assertEqual(result['bonuses'], {"def": 0, "avo": 0})
        self.assertEqual(result['is_healing'], False)
        self.assertEqual(result['is_indoor'], False)
    
    def test_get_terrain_properties_returns_none_for_invalid_terrain(self):
        """Test that get_terrain_properties returns None for invalid terrain."""
        # Arrange
        position = (10, 10)  # Position outside the map
        self.mock_game_state_manager.get_terrain_type.return_value = TERRAIN_INVALID
        
        # Act
        result = self.map_system.get_terrain_properties(position)
        
        # Assert
        self.assertIsNone(result)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)
        self.mock_data_provider.get_terrain_data.assert_not_called()
    # TDD: Test get_movement_cost returns correct cost for different units/terrain/states
    def test_get_movement_cost_for_normal_unit(self):
        """Test get_movement_cost returns correct cost for a normal unit."""
        # Arrange
        position = (3, 4)
        unit_id = "U001"
        terrain_type = TerrainTypeEnum.PLAIN
        movement_type = MovementTypeEnum.INFANTRY
        expected_cost = 1
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.class_id = "C001"
        mock_unit.faction = "PLAYER"
        
        # Mock class data
        mock_class_data = MagicMock()
        mock_class_data.movement_type = movement_type
        mock_class_data.dismount_class_id = None
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_game_state_manager.get_terrain_type.return_value = terrain_type
        self.mock_data_provider.get_class_data.return_value = mock_class_data
        self.mock_data_provider.get_terrain_cost.return_value = expected_cost
        
        # Mock _get_unit_at to return None (no unit at position)
        self.map_system._get_unit_at = MagicMock(return_value=None)
        
        # Act
        result = self.map_system.get_movement_cost(position, unit_id)
        
        # Assert
        self.assertEqual(result, expected_cost)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_game_state_manager.get_terrain_type.assert_called_once_with(position)
        self.mock_data_provider.get_class_data.assert_called_with(mock_unit.class_id)
        self.mock_data_provider.get_terrain_cost.assert_called_once_with(terrain_type, movement_type)
    
    def test_get_movement_cost_allows_movement_through_enemy_occupied_tile(self):
        """Test that get_movement_cost returns a valid cost (not IMPASSABLE) for enemy-occupied tiles."""
        # Arrange
        position = (5, 5)
        unit_id = "PLAYER_UNIT"
        enemy_id = "ENEMY_UNIT"

        # Mock units
        mock_unit = MagicMock()
        mock_unit.faction = FactionEnum.PLAYER # Use Enum

        mock_enemy = MagicMock()
        mock_enemy.faction = FactionEnum.ENEMY # Use Enum

        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit if id == unit_id else mock_enemy
        # Ensure unit_positions is set for the lookup
        self.mock_game_state_manager.current_game_state.map_state.unit_positions = {enemy_id: position}
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN

        # Mock _get_unit_at is not needed anymore as we mock unit_positions directly
        # self.map_system._get_unit_at = MagicMock(return_value=enemy_id)

        # Ensure get_terrain_cost returns a valid cost (e.g., 1) for the plain terrain
        expected_cost = 1
        self.mock_data_provider.get_terrain_cost.return_value = expected_cost
        # Mock the class data needed to determine movement type
        mock_class_data = Mock()
        mock_class_data.movement_type = MovementTypeEnum.INFANTRY
        self.mock_data_provider.get_class_data.return_value = mock_class_data

        # Act
        result = self.map_system.get_movement_cost(position, unit_id)

        # Assert
        # The cost should be the normal terrain cost, NOT IMPASSABLE
        self.assertEqual(result, expected_cost)
        self.assertNotEqual(result, IMPASSABLE)

    # Add a new test for the ally case
    def test_get_movement_cost_returns_impassable_for_ally_occupied_tile(self):
        """Test that get_movement_cost returns IMPASSABLE for ally-occupied tiles."""
        # Arrange
        position = (5, 5)
        unit_id = "PLAYER_UNIT_1"
        ally_id = "PLAYER_UNIT_2"

        mock_unit = MagicMock()
        mock_unit.faction = FactionEnum.PLAYER

        mock_ally = MagicMock()
        mock_ally.faction = FactionEnum.PLAYER

        self.mock_game_state_manager.get_unit.side_effect = lambda id: mock_unit if id == unit_id else mock_ally
        self.mock_game_state_manager.current_game_state.map_state.unit_positions = {ally_id: position}
        self.mock_game_state_manager.get_terrain_type.return_value = TerrainTypeEnum.PLAIN
        self.mock_data_provider.get_terrain_cost.return_value = 1
        mock_class_data = Mock()
        mock_class_data.movement_type = MovementTypeEnum.INFANTRY
        self.mock_data_provider.get_class_data.return_value = mock_class_data

        # Act
        result = self.map_system.get_movement_cost(position, unit_id)

        # Assert
        self.assertEqual(result, IMPASSABLE)

    def test_get_movement_cost_for_mounted_unit_on_indoor_terrain(self):
        """Test get_movement_cost returns IMPASSABLE for a mounted unit on indoor terrain."""
        # Arrange
        position = (3, 4)
        unit_id = "U001"
        terrain_type = TerrainTypeEnum.CASTLE
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.class_id = "C001"
        
        # Mock class data
        mock_class_data = MagicMock()
        mock_class_data.dismount_class_id = "C002"  # Has dismount class, so it's mounted
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_game_state_manager.get_terrain_type.return_value = terrain_type
        self.mock_data_provider.get_class_data.return_value = mock_class_data
        
        # Mock helper methods
        self.map_system._get_unit_at = MagicMock(return_value=None)
        self.map_system._is_class_mounted = MagicMock(return_value=True)
        self.map_system._is_unit_dismounted = MagicMock(return_value=False)
        self.map_system._is_terrain_indoor = MagicMock(return_value=True)
        
        # Act
        result = self.map_system.get_movement_cost(position, unit_id)
        
        # Assert
        self.assertEqual(result, IMPASSABLE)
        self.map_system._is_terrain_indoor.assert_called_once_with(position)
        
    # TDD: Test get_reachable_tiles calculates correct range considering terrain and movement points
    def test_get_reachable_tiles_delegates_to_pathfinder(self):
        """Test get_reachable_tiles delegates to the pathfinder and returns the correct set of tiles."""
        # Arrange
        unit_id = "U001"
        start_pos = (5, 5)
        movement_points = 5
        reachable_nodes = {(5, 5): 0, (5, 6): 1, (6, 5): 1, (4, 5): 1, (5, 4): 1}
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.position = start_pos
        mock_unit.base_stats = {MOV: movement_points}
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.map_system.pathfinder.find_reachable.return_value = reachable_nodes
        
        # Act
        result = self.map_system.get_reachable_tiles(unit_id)
        
        # Assert
        self.assertEqual(result, set(reachable_nodes.keys()))
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.map_system.pathfinder.find_reachable.assert_called_once_with(start_pos, movement_points, unit_id)
    
    def test_get_reachable_tiles_returns_empty_set_for_invalid_unit(self):
        """Test get_reachable_tiles returns an empty set for an invalid unit."""
        # Arrange
        unit_id = "INVALID"
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.map_system.get_reachable_tiles(unit_id)
        
        # Assert
        self.assertEqual(result, set())
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.map_system.pathfinder.find_reachable.assert_not_called()

    # TDD: Test get_path returns a valid sequence of coordinates
    def test_get_path_delegates_to_pathfinder(self):
        """Test get_path delegates to the pathfinder and returns the correct path."""
        # Arrange
        unit_id = "U001"
        start_pos = (5, 5)
        end_pos = (7, 7)
        expected_path = [(5, 5), (6, 5), (6, 6), (7, 6), (7, 7)]
        
        # Mock unit
        mock_unit = MagicMock()
        mock_unit.position = start_pos
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.map_system.pathfinder.reconstruct_path.return_value = expected_path
        
        # Act
        result = self.map_system.get_path(unit_id, end_pos)
        
        # Assert
        self.assertEqual(result, expected_path)
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.map_system.pathfinder.reconstruct_path.assert_called_once_with(start_pos, end_pos, unit_id)
    
    def test_get_path_returns_empty_list_for_invalid_unit(self):
        """Test get_path returns an empty list for an invalid unit."""
        # Arrange
        unit_id = "INVALID"
        end_pos = (7, 7)
        self.mock_game_state_manager.get_unit.return_value = None
        
        # Act
        result = self.map_system.get_path(unit_id, end_pos)
        
        # Assert
        self.assertEqual(result, [])
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.map_system.pathfinder.reconstruct_path.assert_not_called()

    # TDD: Test get_attackable_tiles calculates range correctly for different weapons/positions
    def test_get_attackable_tiles_calculates_correct_range(self):
        """Test get_attackable_tiles calculates the correct attack range."""
        # Arrange
        unit_id = "U001"
        start_pos = (5, 5)
        min_range = 1
        max_range = 2
        map_dimensions = (10, 10)
        
        # Mock unit with equipped weapon
        mock_unit = MagicMock()
        mock_unit.position = start_pos
        mock_unit.equipped_weapon_index = 0
        mock_unit.inventory = [MagicMock()]
        
        # Mock weapon data
        mock_item_data = MagicMock()
        mock_item_data.type = WEAPON
        mock_item_data.range_min = min_range
        mock_item_data.range_max = max_range
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        self.mock_data_provider.get_item_data.return_value = mock_item_data
        self.mock_game_state_manager.get_map_dimensions.return_value = map_dimensions
        
        # Mock has_line_of_sight to always return True for this test
        self.map_system.has_line_of_sight = MagicMock(return_value=True)
        # Mock calculate_manhattan_distance to return the actual Manhattan distance
        self.map_system.calculate_manhattan_distance = MagicMock(
            side_effect=lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Act
        result = self.map_system.get_attackable_tiles(unit_id)
        
        # Assert
        # For a unit at (5,5) with range 1-2, there should be 12 attackable tiles:
        # Range 1: (4,5), (5,4), (6,5), (5,6) = 4 tiles
        # Range 2: (3,5), (4,4), (5,3), (6,4), (7,5), (6,6), (5,7), (4,6) = 8 tiles
        expected_tiles = {
            (4, 5), (5, 4), (6, 5), (5, 6),  # Range 1
            (3, 5), (4, 4), (5, 3), (6, 4), (7, 5), (6, 6), (5, 7), (4, 6)  # Range 2
        }
        
        # Check that all expected tiles are in the result
        for tile in expected_tiles:
            self.assertIn(tile, result, f"Tile {tile} should be attackable")
        
        # Check that the result doesn't contain any unexpected tiles
        self.assertEqual(len(result), len(expected_tiles))
    
    def test_get_attackable_tiles_returns_empty_set_for_no_equipped_weapon(self):
        """Test get_attackable_tiles returns an empty set when no weapon is equipped."""
        # Arrange
        unit_id = "U001"
        
        # Mock unit with no equipped weapon
        mock_unit = MagicMock()
        mock_unit.equipped_weapon_index = -1
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.return_value = mock_unit
        
        # Act
        result = self.map_system.get_attackable_tiles(unit_id)
        
        # Assert
        self.assertEqual(result, set())
        self.mock_game_state_manager.get_unit.assert_called_once_with(unit_id)
        self.mock_data_provider.get_item_data.assert_not_called()

    # TDD: Test get_units_in_attack_range finds correct enemy units
    def test_get_units_in_attack_range_finds_enemy_units(self):
        """Test get_units_in_attack_range finds enemy units within attack range."""
        # Arrange
        unit_id = "U001"
        attackable_tiles = {(3, 3), (4, 4), (5, 5)}
        
        # Mock attacker
        mock_attacker = MagicMock()
        mock_attacker.faction = "PLAYER"
        
        # Mock enemy units
        mock_enemy1 = MagicMock()
        mock_enemy1.faction = "ENEMY"
        mock_enemy1.disposition = "ACTIVE"
        
        mock_enemy2 = MagicMock()
        mock_enemy2.faction = "ENEMY"
        mock_enemy2.disposition = "ACTIVE"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            unit_id: mock_attacker,
            "E001": mock_enemy1,
            "E002": mock_enemy2
        }.get(id)
        
        # Mock get_attackable_tiles to return a predefined set
        self.map_system.get_attackable_tiles = MagicMock(return_value=attackable_tiles)
        
        # Mock _get_unit_at to return enemy units at specific positions
        self.map_system._get_unit_at = MagicMock(side_effect=lambda pos: {
            (3, 3): "E001",
            (4, 4): "E002",
            (5, 5): None
        }.get(pos))
        
        # Act
        result = self.map_system.get_units_in_attack_range(unit_id)
        
        # Assert
        self.assertEqual(set(result), {"E001", "E002"})
        self.map_system.get_attackable_tiles.assert_called_once_with(unit_id)
    
    def test_get_units_in_attack_range_excludes_allies_and_inactive_units(self):
        """Test get_units_in_attack_range excludes allies and inactive units."""
        # Arrange
        unit_id = "U001"
        attackable_tiles = {(3, 3), (4, 4), (5, 5)}
        
        # Mock attacker
        mock_attacker = MagicMock()
        mock_attacker.faction = "PLAYER"
        
        # Mock ally unit
        mock_ally = MagicMock()
        mock_ally.faction = "PLAYER"
        mock_ally.disposition = "ACTIVE"
        
        # Mock inactive enemy
        mock_inactive_enemy = MagicMock()
        mock_inactive_enemy.faction = "ENEMY"
        mock_inactive_enemy.disposition = "DEAD"
        
        # Configure mocks
        self.mock_game_state_manager.get_unit.side_effect = lambda id: {
            unit_id: mock_attacker,
            "U002": mock_ally,
            "E001": mock_inactive_enemy
        }.get(id)
        
        # Mock get_attackable_tiles to return a predefined set
        self.map_system.get_attackable_tiles = MagicMock(return_value=attackable_tiles)
        
        # Mock _get_unit_at to return units at specific positions
        self.map_system._get_unit_at = MagicMock(side_effect=lambda pos: {
            (3, 3): "U002",  # Ally
            (4, 4): "E001",  # Inactive enemy
            (5, 5): None     # Empty
        }.get(pos))
        
        # Act
        result = self.map_system.get_units_in_attack_range(unit_id)
        
        # Assert
        self.assertEqual(result, [])
        self.map_system.get_attackable_tiles.assert_called_once_with(unit_id)
    # TDD: Test get_visible_tiles calculates vision correctly with units, torches, fog
    def test_get_visible_tiles_returns_all_tiles_when_no_fog(self):
        """Test get_visible_tiles returns all map tiles when fog of war is not active."""
        # Arrange
        faction = "PLAYER"
        map_dimensions = (10, 10)
        
        # Configure mocks
        self.map_system._is_fog_of_war_active = MagicMock(return_value=False)
        self.mock_game_state_manager.get_map_dimensions.return_value = map_dimensions
        
        # Act
        result = self.map_system.get_visible_tiles(faction)
        
        # Assert
        expected_tiles = set((x, y) for x in range(10) for y in range(10))
        self.assertEqual(result, expected_tiles)
        self.map_system._is_fog_of_war_active.assert_called_once()
        self.mock_game_state_manager.get_units_by_faction.assert_not_called()
    
    def test_get_visible_tiles_calculates_vision_with_fog(self):
        """Test get_visible_tiles calculates vision correctly when fog of war is active."""
        # Arrange
        faction = "PLAYER"
        
        # Mock units
        mock_unit1 = MagicMock()
        mock_unit1.position = (5, 5)
        mock_unit1.class_id = "C001"
        
        mock_unit2 = MagicMock()
        mock_unit2.position = (8, 8)
        mock_unit2.class_id = "C002"
        
        # Configure mocks
        self.map_system._is_fog_of_war_active = MagicMock(return_value=True)
        self.mock_game_state_manager.get_units_by_faction.return_value = [mock_unit1, mock_unit2]
        
        # Mock vision calculation methods
        self.map_system._get_class_vision_range = MagicMock(side_effect=lambda class_id: 3 if class_id == "C001" else 4)
        self.map_system._get_status_effect_bonus = MagicMock(return_value=0)  # No torch bonus
        
        # Mock line of sight calculation
        unit1_visible_area = {(4, 5), (5, 4), (5, 5), (5, 6), (6, 5)}
        unit2_visible_area = {(7, 8), (8, 7), (8, 8), (8, 9), (9, 8)}
        self.map_system.calculate_line_of_sight_area = MagicMock(side_effect=lambda pos, range_val:
                                                                unit1_visible_area if pos == (5, 5) else unit2_visible_area)
        
        # Act
        result = self.map_system.get_visible_tiles(faction)
        
        # Assert
        expected_tiles = unit1_visible_area.union(unit2_visible_area)
        self.assertEqual(result, expected_tiles)
        self.map_system._is_fog_of_war_active.assert_called_once()
        self.mock_game_state_manager.get_units_by_faction.assert_called_once_with(faction)
        self.map_system.calculate_line_of_sight_area.assert_has_calls([
            call((5, 5), 3),
            call((8, 8), 4)
        ])

    # TDD: Test is_tile_visible checks against the calculated visible set
    def test_is_tile_visible_checks_against_visible_set(self):
        """Test is_tile_visible correctly checks if a tile is in the visible set."""
        # Arrange
        faction = "PLAYER"
        visible_position = (5, 5)
        invisible_position = (10, 10)
        
        # Mock get_visible_tiles to return a predefined set
        self.map_system.get_visible_tiles = MagicMock(return_value={visible_position})
        
        # Act
        visible_result = self.map_system.is_tile_visible(visible_position, faction)
        invisible_result = self.map_system.is_tile_visible(invisible_position, faction)
        
        # Assert
        self.assertTrue(visible_result)
        self.assertFalse(invisible_result)
        self.map_system.get_visible_tiles.assert_has_calls([
            call(faction),
            call(faction)
        ])

    # TDD: Test line of sight is blocked correctly by walls/terrain
    def test_has_line_of_sight_basic_implementation(self):
        """Test the basic implementation of has_line_of_sight."""
        # Note: The current implementation always returns True
        # This test will need to be updated when the real implementation is added
        
        # Arrange
        start_pos = (5, 5)
        end_pos = (8, 8)
        
        # Act
        result = self.map_system.has_line_of_sight(start_pos, end_pos)
        
        # Assert
        self.assertTrue(result)

    # TDD: Test line of sight area calculation handles range and obstacles
    def test_calculate_line_of_sight_area_with_range(self):
        """Test calculate_line_of_sight_area correctly handles vision range."""
        # Arrange
        center_pos = (5, 5)
        range_val = 2
        map_dimensions = (10, 10)
        
        # Configure mocks
        self.mock_game_state_manager.get_map_dimensions.return_value = map_dimensions
        
        # Mock has_line_of_sight to always return True for this test
        self.map_system.has_line_of_sight = MagicMock(return_value=True)
        # Mock calculate_manhattan_distance to return the actual Manhattan distance
        self.map_system.calculate_manhattan_distance = MagicMock(
            side_effect=lambda pos1, pos2: abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        )
        
        # Act
        result = self.map_system.calculate_line_of_sight_area(center_pos, range_val)
        
        # Assert
        # For a unit at (5,5) with vision range 2, there should be 13 visible tiles:
        # Range 0: (5,5) = 1 tile
        # Range 1: (4,5), (5,4), (6,5), (5,6) = 4 tiles
        # Range 2: (3,5), (4,4), (5,3), (6,4), (7,5), (6,6), (5,7), (4,6) = 8 tiles
        expected_tiles = {
            (5, 5),  # Range 0
            (4, 5), (5, 4), (6, 5), (5, 6),  # Range 1
            (3, 5), (4, 4), (5, 3), (6, 4), (7, 5), (6, 6), (5, 7), (4, 6)  # Range 2
        }
        
        self.assertEqual(result, expected_tiles)
        self.mock_game_state_manager.get_map_dimensions.assert_called_once()


class TestPathfindingAlgorithm(unittest.TestCase):
    """Test cases for the PathfindingAlgorithm class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create mock functions for cost and adjacency
        self.mock_cost_func = MagicMock()
        self.mock_get_adjacent_func = MagicMock()

        # Create the PathfindingAlgorithm instance with both mocks
        self.pathfinder = PathfindingAlgorithm(self.mock_cost_func, self.mock_get_adjacent_func)

    def test_find_reachable_with_simple_grid(self):
        # ... existing test code ...
        # Setup adjacent function mock for this test
        def simple_adjacent(pos):
            x, y = pos
            adj = []
            if x > 0: adj.append((x-1, y))
            if x < 4: adj.append((x+1, y))
            if y > 0: adj.append((x, y-1))
            if y < 4: adj.append((x, y+1))
            return adj
        self.mock_get_adjacent_func.side_effect = simple_adjacent
        self.mock_cost_func.return_value = 1 # Simple cost

        start_pos = (0, 0)
        movement_points = 2
        reachable = self.pathfinder.find_reachable(start_pos, movement_points, "unit1")

        expected_reachable = {
            (0, 0): 0,
            (1, 0): 1,
            (0, 1): 1,
            (2, 0): 2,
            (1, 1): 2,
            (0, 2): 2
        }
        self.assertDictEqual(reachable, expected_reachable)

    def test_reconstruct_path_builds_correct_path(self):
        # Setup adjacent function mock for this test
        def simple_adjacent(pos):
            x, y = pos
            adj = []
            if x > 0: adj.append((x-1, y))
            if x < 4: adj.append((x+1, y))
            if y > 0: adj.append((x, y-1))
            if y < 4: adj.append((x, y+1))
            return adj
        self.mock_get_adjacent_func.side_effect = simple_adjacent
        self.mock_cost_func.return_value = 1 # Simple cost

        start_pos = (0, 0)
        end_pos = (2, 1)
        unit_id = "unit1" # Define a unit_id
        
        # Call reconstruct_path, which will internally call find_reachable
        path = self.pathfinder.reconstruct_path(start_pos, end_pos, unit_id)

        # The expected path depends on the find_reachable implementation.
        # Assuming find_reachable prefers lower x/y, the path might be:
        # (0,0) -> (1,0) -> (2,0) -> (2,1) OR
        # (0,0) -> (0,1) -> (1,1) -> (2,1) OR
        # (0,0) -> (1,0) -> (1,1) -> (2,1) 
        # The previous expected path [(0, 0), (1, 0), (1, 1), (2, 1)] seems plausible.
        expected_path = [(0, 0), (1, 0), (1, 1), (2, 1)] 
        # If this still fails, we might need to inspect find_reachable's behavior more closely.
        self.assertEqual(path, expected_path)


if __name__ == '__main__':
    unittest.main()
