# src/game/models.py

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# Using Enums would be better later, but starting simple
TerrainType = str # e.g., "Plain"
Faction = str # e.g., "Player", "Enemy"

@dataclass
class Tile:
    terrain_type: TerrainType = "Plain"
    unit_id: Optional[int] = None # Store ID of unit occupying the tile

@dataclass
class Unit:
    id: int
    name: str
    faction: Faction
    position: Tuple[int, int] # (x, y)
    hp: int
    max_hp: int
    mov: int
    # Other stats like Str, Def, etc., will be added later
    has_acted: bool = False # Track if the unit has moved/waited this turn

@dataclass
class GameMap:
    width: int
    height: int
    tiles: List[List[Tile]] = field(default_factory=list)

    def __post_init__(self):
        if not self.tiles:
            # Note: Corrected indexing to [y][x] for typical grid representation
            self.tiles = [[Tile() for _ in range(self.width)] for _ in range(self.height)]

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x] # Corrected indexing
        return None

    def place_unit(self, unit: Unit, x: int, y: int):
        tile = self.get_tile(x, y)
        if tile and tile.unit_id is None: # Only place if tile is empty
            tile.unit_id = unit.id
            unit.position = (x, y)
            return True
        return False # Failed to place (tile occupied or out of bounds)

    def move_unit(self, unit: Unit, new_x: int, new_y: int):
        old_tile = self.get_tile(unit.position[0], unit.position[1])
        if old_tile:
            old_tile.unit_id = None

        new_tile = self.get_tile(new_x, new_y)
        if new_tile and new_tile.unit_id is None: # Check if destination is empty
            new_tile.unit_id = unit.id
            unit.position = (new_x, new_y)
            return True
        else: # Failed move, revert old tile if needed (though it should be None already)
            if old_tile:
                old_tile.unit_id = unit.id # Put unit back if move failed
            return False


    def get_unit_id_at(self, x: int, y: int) -> Optional[int]:
        tile = self.get_tile(x, y)
        return tile.unit_id if tile else None

@dataclass
class GameState:
    game_map: GameMap
    units: Dict[int, Unit] = field(default_factory=dict) # Store units by ID
    turn: int = 1
    active_faction: Faction = "Player"
    selected_unit_id: Optional[int] = None

    def get_unit(self, unit_id: int) -> Optional[Unit]:
        return self.units.get(unit_id)

    def get_selected_unit(self) -> Optional[Unit]:
        if self.selected_unit_id is not None:
            return self.get_unit(self.selected_unit_id)
        return None

    def add_unit(self, unit: Unit):
        # Check if position is valid and empty before adding
        if self.game_map.place_unit(unit, unit.position[0], unit.position[1]):
            self.units[unit.id] = unit
        else:
            # Handle error: Cannot add unit at occupied/invalid position
            print(f"Error: Cannot add unit {unit.name} at {unit.position}")


    def reset_player_actions(self):
        for unit in self.units.values():
            if unit.faction == "Player":
                unit.has_acted = False