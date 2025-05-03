import os
import yaml
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock


class TestDataProvider:
    """
    Test data provider for gameplay system tests.
    Loads test data from YAML files in the data/scenarios directory.
    """

    def __init__(self, scenario_file: str):
        """
        Initialize the test data provider with a scenario file.
        
        Args:
            scenario_file: Path to the scenario file relative to data/scenarios
        """
        self.scenario_file = scenario_file
        self.data = self._load_scenario_data()
    
    def _load_scenario_data(self) -> Dict:
        """
        Load the scenario data from the YAML file.
        
        Returns:
            Dict containing the scenario data
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        scenario_path = os.path.join(base_dir, "data", "scenarios", self.scenario_file)
        
        try:
            with open(scenario_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error loading scenario data: {e}")
            return {}
    
    def get_unit_data(self, unit_id: str) -> Optional[Dict]:
        """
        Get unit data by ID.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            Dict containing the unit data, or None if not found
        """
        units = self.data.get("units", {})
        return units.get(unit_id)
    
    def get_staff_data(self, staff_id: str) -> Optional[Dict]:
        """
        Get staff data by ID.
        
        Args:
            staff_id: The ID of the staff
            
        Returns:
            Dict containing the staff data, or None if not found
        """
        staves = self.data.get("staves", {})
        return staves.get(staff_id)
    
    def get_map_data(self) -> Dict:
        """
        Get map data from the scenario.
        
        Returns:
            Dict containing the map data
        """
        return self.data.get("map", {})
    
    def create_mock_unit(self, unit_id: str) -> MagicMock:
        """
        Create a mock unit based on the unit data.
        
        Args:
            unit_id: The ID of the unit
            
        Returns:
            MagicMock object representing the unit
        """
        unit_data = self.get_unit_data(unit_id)
        if not unit_data:
            return MagicMock()
        
        mock_unit = MagicMock()
        mock_unit.id = unit_id
        mock_unit.name = unit_data.get("name", "")
        mock_unit.base_class_id = unit_data.get("base_class_id", "")
        
        # Set stats
        for stat, value in unit_data.get("stats", {}).items():
            setattr(mock_unit, stat.lower(), value)
        
        # Set position
        mock_unit.position = unit_data.get("position", (0, 0))
        
        # Set faction
        mock_unit.faction = unit_data.get("faction", "PLAYER")
        
        # Set current HP if specified
        if "current_hp" in unit_data:
            mock_unit.current_hp = unit_data["current_hp"]
            mock_unit.max_hp = unit_data["stats"]["HP"]
        
        # Set status effects if specified
        if "status_effects" in unit_data:
            mock_unit.status_effects = unit_data["status_effects"]
        
        # Set inventory
        mock_unit.inventory = unit_data.get("inventory", [])
        
        return mock_unit
    
    def create_mock_staff(self, staff_id: str) -> MagicMock:
        """
        Create a mock staff based on the staff data.
        
        Args:
            staff_id: The ID of the staff
            
        Returns:
            MagicMock object representing the staff
        """
        staff_data = self.get_staff_data(staff_id)
        if not staff_data:
            return MagicMock()
        
        mock_staff = MagicMock()
        
        # Set all attributes from staff_data
        for key, value in staff_data.items():
            setattr(mock_staff, key, value)
        
        # Set current durability to max_durability if not specified
        if not hasattr(mock_staff, "current_durability"):
            mock_staff.current_durability = staff_data.get("max_durability", 0)
        
        return mock_staff
    
    def create_mock_map_system(self) -> MagicMock:
        """
        Create a mock map system based on the map data.
        
        Returns:
            MagicMock object representing the map system
        """
        map_data = self.get_map_data()
        mock_map_system = MagicMock()
        
        # Store dimensions for reference
        dimensions = map_data.get("dimensions", (10, 10))
        mock_map_system.dimensions = dimensions
        
        # Store terrain grid for reference
        terrain_grid = map_data.get("terrain_grid", [])
        mock_map_system.terrain_grid = terrain_grid
        
        # Mock get_tiles_in_range to return tiles within range
        def mock_get_tiles_in_range(pos, min_range, max_range):
            x, y = pos
            tiles = []
            for dx in range(-max_range, max_range + 1):
                for dy in range(-max_range, max_range + 1):
                    nx, ny = x + dx, y + dy
                    # Check if tile is within map bounds
                    if 0 <= nx < dimensions[0] and 0 <= ny < dimensions[1]:
                        # Check if tile is within range
                        distance = abs(dx) + abs(dy)  # Manhattan distance
                        if min_range <= distance <= max_range:
                            tiles.append((nx, ny))
            return tiles
        
        mock_map_system.get_tiles_in_range.side_effect = mock_get_tiles_in_range
        
        # Mock has_line_of_sight based on terrain grid
        def mock_has_line_of_sight(pos1, pos2):
            # Simple implementation: check if there's a wall between the positions
            # In a real implementation, this would be more complex
            x1, y1 = pos1
            x2, y2 = pos2
            
            # Check if either position is out of bounds
            if not (0 <= x1 < dimensions[0] and 0 <= y1 < dimensions[1] and
                    0 <= x2 < dimensions[0] and 0 <= y2 < dimensions[1]):
                return False
            
            # Check if there's a wall at position 2
            if terrain_grid and y2 < len(terrain_grid) and x2 < len(terrain_grid[y2]):
                if terrain_grid[y2][x2] == "WALL":
                    return False
            
            # Simple check for walls in between (very simplified)
            # In a real implementation, this would use a line-drawing algorithm
            if x1 == x2:  # Vertical line
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    if terrain_grid and y < len(terrain_grid) and x1 < len(terrain_grid[y]):
                        if terrain_grid[y][x1] == "WALL":
                            return False
            elif y1 == y2:  # Horizontal line
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    if terrain_grid and y1 < len(terrain_grid) and x < len(terrain_grid[y1]):
                        if terrain_grid[y1][x] == "WALL":
                            return False
            
            return True
        
        mock_map_system.has_line_of_sight.side_effect = mock_has_line_of_sight
        
        # Mock is_valid_tile to check if tile is within map bounds
        def mock_is_valid_tile(pos):
            x, y = pos
            return 0 <= x < dimensions[0] and 0 <= y < dimensions[1]
        
        mock_map_system.is_valid_tile.side_effect = mock_is_valid_tile
        
        return mock_map_system
    
    def setup_mock_systems_for_staff_tests(self) -> Dict[str, MagicMock]:
        """
        Set up all mock systems needed for staff system tests.
        
        Returns:
            Dict containing all mock systems
        """
        # Create mock systems
        mock_item_system = MagicMock()
        mock_unit_system = MagicMock()
        mock_status_effects_system = MagicMock()
        mock_map_system = self.create_mock_map_system()
        mock_action_system = MagicMock()
        mock_exp_system = MagicMock()
        mock_ai_system = MagicMock()
        mock_data_provider = MagicMock()
        
        # Set up unit system mocks
        unit_data = self.data.get("units", {})
        unit_positions = {}
        
        for unit_id, data in unit_data.items():
            unit_positions[unit_id] = data.get("position", (0, 0))
        
        def mock_get_position(unit):
            if hasattr(unit, "id"):
                return unit_positions.get(unit.id, (0, 0))
            return (0, 0)
        
        mock_unit_system.get_position.side_effect = mock_get_position
        
        def mock_get_stat(unit, stat):
            if hasattr(unit, "id"):
                unit_data = self.get_unit_data(unit.id)
                if unit_data and "stats" in unit_data:
                    return unit_data["stats"].get(stat.upper(), 0)
            return 0
        
        mock_unit_system.get_stat.side_effect = mock_get_stat
        
        def mock_is_ally(unit1, unit2):
            if hasattr(unit1, "id") and hasattr(unit2, "id"):
                unit1_data = self.get_unit_data(unit1.id)
                unit2_data = self.get_unit_data(unit2.id)
                if unit1_data and unit2_data:
                    return unit1_data.get("faction") == unit2_data.get("faction")
            return False
        
        mock_unit_system.is_ally.side_effect = mock_is_ally
        
        def mock_is_enemy(unit1, unit2):
            if hasattr(unit1, "id") and hasattr(unit2, "id"):
                unit1_data = self.get_unit_data(unit1.id)
                unit2_data = self.get_unit_data(unit2.id)
                if unit1_data and unit2_data:
                    return unit1_data.get("faction") != unit2_data.get("faction")
            return False
        
        mock_unit_system.is_enemy.side_effect = mock_is_enemy
        
        def mock_is_at_max_hp(unit):
            if hasattr(unit, "id"):
                unit_data = self.get_unit_data(unit.id)
                if unit_data:
                    current_hp = unit_data.get("current_hp")
                    if current_hp is not None:
                        return current_hp >= unit_data["stats"]["HP"]
            return True  # Default to full HP if not specified
        
        mock_unit_system.is_at_max_hp.side_effect = mock_is_at_max_hp
        
        def mock_get_current_hp(unit):
            if hasattr(unit, "id"):
                unit_data = self.get_unit_data(unit.id)
                if unit_data:
                    return unit_data.get("current_hp", unit_data["stats"]["HP"])
            return 0
        
        mock_unit_system.get_current_hp.side_effect = mock_get_current_hp
        
        def mock_get_max_hp(unit):
            if hasattr(unit, "id"):
                unit_data = self.get_unit_data(unit.id)
                if unit_data and "stats" in unit_data:
                    return unit_data["stats"].get("HP", 0)
            return 0
        
        mock_unit_system.get_max_hp.side_effect = mock_get_max_hp
        
        # Set up map system mocks
        def mock_get_unit_at(pos):
            for unit_id, data in unit_data.items():
                if data.get("position") == pos:
                    return self.create_mock_unit(unit_id)
            return None
        
        mock_map_system.get_unit_at.side_effect = mock_get_unit_at
        
        # Set up data provider mocks
        def mock_get_item_data(item_id):
            return self.get_staff_data(item_id)
        
        mock_data_provider.get_item_data.side_effect = mock_get_item_data
        
        # Return all mock systems
        return {
            "item_system": mock_item_system,
            "unit_system": mock_unit_system,
            "status_effects_system": mock_status_effects_system,
            "map_system": mock_map_system,
            "action_system": mock_action_system,
            "exp_system": mock_exp_system,
            "ai_system": mock_ai_system,
            "data_provider": mock_data_provider
        }