from typing import Dict, Tuple, Optional, List, Set
from .models import MapTile, TerrainType, MovementType, Unit
from .static_data_loader import StaticDataLoader

class MapManager:
    """
    Manages the map state for the current chapter/battle.
    Handles loading map layouts, retrieving and updating tile information,
    and tracking unit positions on the map.
    """
    def __init__(self, static_loader: StaticDataLoader):
        """
        Initializes the MapManager.
        Args:
            static_loader: An instance of StaticDataLoader to fetch terrain data.
        """
        self.static_loader = static_loader
        self._map_tiles: Dict[Tuple[int, int], MapTile] = {}  # Maps (x, y) coordinates to MapTile
        self._map_width: int = 0
        self._map_height: int = 0
        self._unit_positions: Dict[str, Tuple[int, int]] = {}  # Maps unit_id to (x, y) position

    def load_map(self, map_id: str) -> bool:
        """
        Loads a map layout from static data.
        Args:
            map_id: The ID of the map to load.
        Returns:
            True if the map was loaded successfully, False otherwise.
        """
        # Get map data from static loader
        map_data = self.static_loader.get_map_data(map_id)
        if not map_data:
            print(f"Error: Map data for '{map_id}' not found.")
            return False

        # Clear existing map state
        self._map_tiles.clear()
        self._unit_positions.clear()

        # Set map dimensions
        self._map_width = map_data.get("width", 0)
        self._map_height = map_data.get("height", 0)

        # Load terrain data
        terrain_layout = map_data.get("terrain_layout", [])
        
        # Example: Assuming terrain_layout is a 2D array of terrain type strings/IDs
        for y, row in enumerate(terrain_layout):
            for x, terrain_id in enumerate(row):
                # Get terrain data from static loader
                terrain_data = self.static_loader.get_terrain_data(terrain_id)
                if not terrain_data:
                    print(f"Warning: Terrain data for '{terrain_id}' not found. Using default.")
                    # Use a default terrain type if not found
                    self._map_tiles[(x, y)] = MapTile(terrain_type=TerrainType.PLAIN)
                    continue

                # Create MapTile from terrain data
                # This assumes terrain_data has the necessary fields
                try:
                    terrain_type = TerrainType[terrain_data.get("type", "PLAIN").upper()]
                    
                    # Create movement costs dictionary
                    movement_costs = {}
                    for movement_type_str, cost in terrain_data.get("movement_costs", {}).items():
                        try:
                            movement_type = MovementType[movement_type_str.upper()]
                            movement_costs[movement_type] = cost
                        except KeyError:
                            print(f"Warning: Unknown movement type '{movement_type_str}'.")
                    
                    # Create the MapTile
                    tile = MapTile(
                        terrain_type=terrain_type,
                        def_bonus=terrain_data.get("def_bonus", 0),
                        avo_bonus=terrain_data.get("avo_bonus", 0),
                        movement_costs=movement_costs,
                        blocks_vision=terrain_data.get("blocks_vision", False),
                        is_impassable=terrain_data.get("is_impassable", False)
                    )
                    
                    self._map_tiles[(x, y)] = tile
                    
                except KeyError as e:
                    print(f"Error creating MapTile at ({x}, {y}): {e}")
                    # Use a default tile as fallback
                    self._map_tiles[(x, y)] = MapTile(terrain_type=TerrainType.PLAIN)

        print(f"Map '{map_id}' loaded successfully. Dimensions: {self._map_width}x{self._map_height}")
        return True

    def get_tile(self, x: int, y: int) -> Optional[MapTile]:
        """
        Retrieves the MapTile at the specified coordinates.
        Args:
            x: The x-coordinate.
            y: The y-coordinate.
        Returns:
            The MapTile at the specified coordinates, or None if out of bounds.
        """
        if not self.is_valid_coordinate(x, y):
            return None
        return self._map_tiles.get((x, y))

    def set_unit_on_tile(self, unit_id: str, x: int, y: int) -> bool:
        """
        Places a unit on a specific tile.
        Args:
            unit_id: The ID of the unit to place.
            x: The x-coordinate.
            y: The y-coordinate.
        Returns:
            True if the unit was placed successfully, False otherwise.
        """
        if not self.is_valid_coordinate(x, y):
            print(f"Error: Coordinates ({x}, {y}) are out of bounds.")
            return False
            
        # Check if tile is already occupied
        tile = self.get_tile(x, y)
        if tile and tile.occupying_unit_id is not None and tile.occupying_unit_id != unit_id:
            print(f"Error: Tile ({x}, {y}) is already occupied by unit '{tile.occupying_unit_id}'.")
            return False
            
        # If the unit is already on the map, clear its previous position
        if unit_id in self._unit_positions:
            old_x, old_y = self._unit_positions[unit_id]
            old_tile = self.get_tile(old_x, old_y)
            if old_tile:
                old_tile.occupying_unit_id = None
                
        # Update the new tile
        tile = self.get_tile(x, y)
        if tile:
            tile.occupying_unit_id = unit_id
            self._unit_positions[unit_id] = (x, y)
            return True
            
        return False

    def remove_unit_from_map(self, unit_id: str) -> bool:
        """
        Removes a unit from the map.
        Args:
            unit_id: The ID of the unit to remove.
        Returns:
            True if the unit was removed successfully, False if not found.
        """
        if unit_id not in self._unit_positions:
            print(f"Warning: Unit '{unit_id}' not found on map.")
            return False
            
        # Get the unit's position
        x, y = self._unit_positions[unit_id]
        
        # Clear the tile
        tile = self.get_tile(x, y)
        if tile and tile.occupying_unit_id == unit_id:
            tile.occupying_unit_id = None
            
        # Remove from unit positions
        del self._unit_positions[unit_id]
        
        return True

    def get_unit_position(self, unit_id: str) -> Optional[Tuple[int, int]]:
        """
        Gets the position of a unit on the map.
        Args:
            unit_id: The ID of the unit.
        Returns:
            The (x, y) coordinates of the unit, or None if not on the map.
        """
        return self._unit_positions.get(unit_id)

    def is_valid_coordinate(self, x: int, y: int) -> bool:
        """
        Checks if the given coordinates are within the map bounds.
        Args:
            x: The x-coordinate.
            y: The y-coordinate.
        Returns:
            True if the coordinates are valid, False otherwise.
        """
        return 0 <= x < self._map_width and 0 <= y < self._map_height

    def get_map_dimensions(self) -> Tuple[int, int]:
        """
        Gets the dimensions of the current map.
        Returns:
            A tuple of (width, height).
        """
        return (self._map_width, self._map_height)

    def update_tile_state(self, x: int, y: int, **kwargs) -> bool:
        """
        Updates specific properties of a tile.
        Args:
            x: The x-coordinate.
            y: The y-coordinate.
            **kwargs: Key-value pairs of properties to update.
        Returns:
            True if the tile was updated successfully, False otherwise.
        """
        tile = self.get_tile(x, y)
        if not tile:
            print(f"Error: No tile at coordinates ({x}, {y}).")
            return False
            
        # Update tile properties
        for key, value in kwargs.items():
            if hasattr(tile, key):
                setattr(tile, key, value)
            else:
                print(f"Warning: MapTile has no attribute '{key}'.")
                
        return True

    def get_movement_range(self, unit: Unit) -> Set[Tuple[int, int]]:
        """
        Calculates the valid movement range for a unit.
        Args:
            unit: The Unit to calculate movement for.
        Returns:
            A set of (x, y) coordinates representing valid movement destinations.
        """
        # This is a simplified placeholder implementation
        # A real implementation would use pathfinding algorithms (e.g., Dijkstra's)
        # to account for terrain costs and movement type
        
        if unit.id not in self._unit_positions:
            print(f"Warning: Unit '{unit.id}' not found on map.")
            return set()
            
        start_x, start_y = self._unit_positions[unit.id]
        movement = unit.stats.movement
        movement_type = unit.movement_type
        
        # Simple breadth-first search for valid tiles
        valid_tiles = set()
        visited = set()
        queue = [(start_x, start_y, movement)]  # (x, y, remaining_movement)
        
        while queue:
            x, y, remaining = queue.pop(0)
            
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            # Skip starting position for valid destinations
            if (x, y) != (start_x, start_y):
                valid_tiles.add((x, y))
                
            # If no movement left, don't explore further
            if remaining <= 0:
                continue
                
            # Check adjacent tiles
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                
                if not self.is_valid_coordinate(new_x, new_y):
                    continue
                    
                tile = self.get_tile(new_x, new_y)
                if not tile or tile.is_impassable:
                    continue
                    
                # Check if tile is occupied by another unit
                if tile.occupying_unit_id is not None and tile.occupying_unit_id != unit.unit_id:
                    continue
                    
                # Get movement cost for this unit's movement type
                movement_cost = tile.movement_costs.get(movement_type, 1)
                
                # If unit can't move on this terrain, skip
                if movement_cost > remaining:
                    continue
                    
                # Add to queue with reduced movement
                queue.append((new_x, new_y, remaining - movement_cost))
                
        return valid_tiles

    def get_attack_range(self, unit: Unit, equipped_item_range: Tuple[int, int] = (1, 1)) -> Set[Tuple[int, int]]:
        """
        Calculates the attack range for a unit with their equipped weapon.
        Args:
            unit: The Unit to calculate attack range for.
            equipped_item_range: The (min_range, max_range) of the equipped item.
        Returns:
            A set of (x, y) coordinates representing valid attack targets.
        """
        # Simplified placeholder implementation
        if unit.unit_id not in self._unit_positions:
            print(f"Warning: Unit '{unit.unit_id}' not found on map.")
            return set()
            
        x, y = self._unit_positions[unit.unit_id]
        min_range, max_range = equipped_item_range
        
        attack_tiles = set()
        
        # Check all tiles within max_range
        for dx in range(-max_range, max_range + 1):
            for dy in range(-max_range, max_range + 1):
                # Calculate Manhattan distance
                distance = abs(dx) + abs(dy)
                
                # Skip if outside range bounds
                if distance < min_range or distance > max_range:
                    continue
                    
                # Skip the unit's own position
                if dx == 0 and dy == 0:
                    continue
                    
                target_x, target_y = x + dx, y + dy
                
                # Check if coordinates are valid
                if self.is_valid_coordinate(target_x, target_y):
                    attack_tiles.add((target_x, target_y))
                    
        return attack_tiles

# Example Usage (requires StaticDataLoader)
if __name__ == "__main__":
    # This example won't run without StaticDataLoader instance
    print("MapManager example usage (requires dependencies)")
    # loader = StaticDataLoader() # Needs proper setup
    # loader.load_all_data()
    # map_manager = MapManager(loader)
    # map_manager.load_map("ch1")
    # print(f"Map dimensions: {map_manager.get_map_dimensions()}")
    # tile = map_manager.get_tile(0, 0)
    # if tile:
    #     print(f"Terrain at (0,0): {tile.terrain_type}")
