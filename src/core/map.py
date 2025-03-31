from .data_structures import Position, TerrainType, MovementType
from .units import Unit, MOVEMENT_COSTS # Import movement costs for Tile logic

# Placeholder data for terrain properties (load from config/data later)
TERRAIN_PASSABILITY = {
    # Simplified: Assume all terrain passable by default unless cost is -1
    # More complex rules (e.g., walls only passable by specific units) need refinement
    terrain: {mvt: (MOVEMENT_COSTS.get(mvt, {}).get(terrain, -1) > 0) for mvt in MovementType}
    for terrain in TerrainType
}
TERRAIN_AVOID_BONUS = {
    TerrainType.PLAIN: 5, TerrainType.FOREST: 20, TerrainType.MOUNTAIN: 30,
    TerrainType.RIVER: 10, TerrainType.BRIDGE: 0, TerrainType.ROAD: 0,
    TerrainType.FORT: 20, TerrainType.THRONE: 30, TerrainType.GATE: 20,
    TerrainType.HOUSE: 10, TerrainType.VILLAGE: 10, TerrainType.SHOP: 10,
    TerrainType.ARENA: 0, TerrainType.DESERT: 5,
    # Add others
}
TERRAIN_DEFENSE_BONUS = {
    TerrainType.FOREST: 2, TerrainType.MOUNTAIN: 5, TerrainType.FORT: 10,
    TerrainType.THRONE: 10, TerrainType.GATE: 5, TerrainType.HOUSE: 1,
    TerrainType.VILLAGE: 1, TerrainType.SHOP: 1,
    # Add others
}
HEALING_TERRAIN_TYPES = {TerrainType.FORT, TerrainType.THRONE, TerrainType.GATE} # Churches too?

class Tile:
    def __init__(self, terrain: TerrainType, occupying_unit: Unit | None = None, map_object=None):
        self.terrain = terrain
        self.occupying_unit: Unit | None = occupying_unit
        self.map_object = map_object # Placeholder for doors, chests, etc.
        self.is_visible = True # For Fog of War, default to visible

    def is_passable(self, unit: Unit) -> bool:
        """Check if this tile is passable for a specific unit."""
        # Cannot pass if occupied by another unit (unless specific skill/state allows)
        if self.occupying_unit and self.occupying_unit != unit:
            # TODO: Check for friendly vs enemy occupation rules if needed
            return False

        # Check terrain passability based on unit's movement type
        movement_type = unit.get_movement_type()
        cost_map = MOVEMENT_COSTS.get(movement_type, {})
        cost = cost_map.get(self.terrain, -1) # Default to impassable if not defined

        return cost > 0 # Passable if cost is positive

    def get_movement_cost(self, unit: Unit) -> int | None:
        """Get the movement cost for a specific unit to enter this tile."""
        movement_type = unit.get_movement_type()
        cost_map = MOVEMENT_COSTS.get(movement_type, {})
        cost = cost_map.get(self.terrain, -1) # Default to impassable

        return cost if cost > 0 else None # Return None if impassable

    def get_avoid_bonus(self) -> int:
        """Get the avoid bonus provided by this tile's terrain."""
        return TERRAIN_AVOID_BONUS.get(self.terrain, 0)

    def get_defense_bonus(self) -> int:
        """Get the defense bonus provided by this tile's terrain."""
        return TERRAIN_DEFENSE_BONUS.get(self.terrain, 0)

    def has_healing_effect(self) -> bool:
        """Check if this tile has a healing effect."""
        return self.terrain in HEALING_TERRAIN_TYPES

    def __str__(self):
        # Basic representation, CLI will handle detailed drawing
        if self.occupying_unit:
            # Simple representation, maybe first letter of name or class?
            return self.occupying_unit.name[0].upper() if self.occupying_unit.unit_type == 'PLAYER' else self.occupying_unit.name[0].lower()
        elif self.map_object:
            return 'O' # Placeholder for object
        else:
            # Placeholder terrain chars, match CLI design later
            terrain_chars = {TerrainType.PLAIN: '.', TerrainType.FOREST: '+', TerrainType.MOUNTAIN: '^', TerrainType.WALL: '#'}
            return terrain_chars.get(self.terrain, '?')

class Map:
    def __init__(self, map_id: str, name: str, width: int, height: int):
        self.map_id = map_id
        self.name = name
        self.width = width
        self.height = height
        # Initialize grid with default terrain (e.g., PLAIN)
        self.tiles: list[list[Tile]] = [
            [Tile(TerrainType.PLAIN) for _ in range(height)] for _ in range(width)
        ]
        self.units_by_pos: dict[Position, Unit] = {}
        self.units_by_id: dict[str, Unit] = {}
        # TODO: Add spawn points, objective points, map objects, fog of war settings

    def load_map_data(self, terrain_data: list[list[TerrainType]], objects_data=None, unit_placements=None):
        """Load terrain, objects, and initial unit placements."""
        if len(terrain_data) != self.width or any(len(row) != self.height for row in terrain_data):
            raise ValueError("Terrain data dimensions do not match map dimensions")

        self.tiles = [
            [Tile(terrain_data[x][y]) for y in range(self.height)] for x in range(self.width)
        ]
        # TODO: Load objects and place them on tiles
        # TODO: Place initial units

    def is_valid_position(self, position: Position) -> bool:
        """Check if a position is within the map boundaries."""
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def get_tile(self, position: Position) -> Tile | None:
        """Get the tile at the specified position."""
        if not self.is_valid_position(position):
            return None
        return self.tiles[position.x][position.y]

    def get_unit_at(self, position: Position) -> Unit | None:
        """Get the unit at the specified position."""
        return self.units_by_pos.get(position)

    def place_unit(self, unit: Unit, position: Position) -> bool:
        """Place a unit on the map at the specified position."""
        if not self.is_valid_position(position):
            print(f"Error: Cannot place unit {unit.name} at invalid position {position}")
            return False
        tile = self.get_tile(position)
        if tile.occupying_unit:
            print(f"Error: Cannot place unit {unit.name} at occupied position {position}")
            return False
        if not tile.is_passable(unit):
             print(f"Error: Cannot place unit {unit.name} at impassable terrain {tile.terrain.name} at {position}")
             return False

        # Remove unit from old position if it was already on the map
        if unit.position and unit.position in self.units_by_pos and self.units_by_pos[unit.position] == unit:
            old_tile = self.get_tile(unit.position)
            if old_tile:
                old_tile.occupying_unit = None
            del self.units_by_pos[unit.position]

        # Place unit at new position
        tile.occupying_unit = unit
        unit.position = position
        self.units_by_pos[position] = unit
        self.units_by_id[unit.unit_id] = unit
        return True

    def remove_unit(self, unit: Unit):
        """Remove a unit from the map."""
        if unit.position and unit.position in self.units_by_pos and self.units_by_pos[unit.position] == unit:
            tile = self.get_tile(unit.position)
            if tile:
                tile.occupying_unit = None
            del self.units_by_pos[unit.position]
            unit.position = None
        if unit.unit_id in self.units_by_id:
            del self.units_by_id[unit.unit_id]

    def move_unit(self, unit: Unit, new_position: Position) -> bool:
        """Move a unit from its current position to a new position."""
        if not unit.position:
            print(f"Error: Unit {unit.name} is not on the map.")
            return False
        if unit.position == new_position:
            return True # Moving to the same spot is valid (costs 0)

        # Basic validation (pathfinding should handle range/cost)
        if not self.is_valid_position(new_position):
             print(f"Error: Cannot move unit {unit.name} to invalid position {new_position}")
             return False
        new_tile = self.get_tile(new_position)
        if new_tile.occupying_unit:
            print(f"Error: Cannot move unit {unit.name} to occupied position {new_position}")
            return False
        if not new_tile.is_passable(unit):
            print(f"Error: Cannot move unit {unit.name} to impassable terrain {new_tile.terrain.name} at {new_position}")
            return False

        # Update old tile
        old_tile = self.get_tile(unit.position)
        if old_tile:
            old_tile.occupying_unit = None
        if unit.position in self.units_by_pos:
             del self.units_by_pos[unit.position]

        # Update new tile and unit position
        new_tile.occupying_unit = unit
        unit.position = new_position
        self.units_by_pos[new_position] = unit
        return True

    def get_adjacent_tiles(self, position: Position) -> list[tuple[Position, Tile]]:
        """Get valid adjacent tiles."""
        adjacent = []
        for adj_pos in position.get_adjacent_positions():
            tile = self.get_tile(adj_pos)
            if tile:
                adjacent.append((adj_pos, tile))
        return adjacent

    def get_units_in_range(self, center: Position, min_range: int, max_range: int) -> list[Unit]:
        """Find units within a specified Manhattan distance range."""
        units_found = []
        for x in range(max(0, center.x - max_range), min(self.width, center.x + max_range + 1)):
            for y in range(max(0, center.y - max_range), min(self.height, center.y + max_range + 1)):
                pos = Position(x, y)
                dist = center.get_manhattan_distance(pos)
                if min_range <= dist <= max_range:
                    unit = self.get_unit_at(pos)
                    if unit:
                        units_found.append(unit)
        return units_found

    def __str__(self):
        # Basic text representation for debugging
        map_str = f"Map: {self.name} ({self.width}x{self.height})\n"
        for y in range(self.height):
            row_str = ""
            for x in range(self.width):
                tile = self.tiles[x][y]
                row_str += str(tile) + " "
            map_str += row_str.strip() + "\n"
        return map_str

# TODO: Add FogOfWar class
# TODO: Add MapObject class and types (Door, Chest, etc.)
# TODO: Add PathFinder class (using A* or Dijkstra)