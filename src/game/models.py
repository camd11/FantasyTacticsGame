# src/game/models.py (Updated)

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

# --- Enums ---
class Faction:
    PLAYER = "Player"
    ENEMY = "Enemy"
    ALLY = "Ally"

class TerrainType:
    PLAIN = "Plain"
    FOREST = "Forest"
    MOUNTAIN = "Mountain"
    # Add more later: Fort, Peak, Water, etc.

class MoveType:
    INFANTRY = "Infantry"
    ARMOR = "Armor"
    CAVALRY = "Cavalry"
    FLYING = "Flying"
    # Add Brigand, Pirate etc. later

# --- Movement Costs ---
# Structure: terrain_costs[move_type][terrain_type] = cost (or None if impassable)
# Based loosely on research.md / Serenes Forest data for Thracia
TERRAIN_COSTS: Dict[MoveType, Dict[TerrainType, Optional[int]]] = {
    MoveType.INFANTRY: {
        TerrainType.PLAIN: 1,
        TerrainType.FOREST: 2,
        TerrainType.MOUNTAIN: 2, # Thracia infantry can cross mountains
    },
    MoveType.ARMOR: {
        TerrainType.PLAIN: 1,
        TerrainType.FOREST: 2,
        TerrainType.MOUNTAIN: 1, # Thracia armor good on mountains? Check data again later. Defaulting to 1 based on research.md note.
    },
    MoveType.CAVALRY: {
        TerrainType.PLAIN: 1,
        TerrainType.FOREST: 3,
        TerrainType.MOUNTAIN: None, # Impassable
    },
    MoveType.FLYING: {
        TerrainType.PLAIN: 1,
        TerrainType.FOREST: 1,
        TerrainType.MOUNTAIN: 1, # Fliers ignore most costs
    },
    # Add other move types later
}

# --- Weapon ---
@dataclass
class Weapon:
    name: str
    might: int = 0
    hit: int = 0
    crit: int = 0
    weight: int = 0
    wtype: str = "Sword"
    range_min: int = 1
    range_max: int = 1

# --- Tile ---
@dataclass
class Tile:
    terrain_type: TerrainType = TerrainType.PLAIN
    unit_id: Optional[int] = None
    # Add terrain properties later (Avo bonus, Def bonus, Heal)

# --- Unit ---
@dataclass
class Unit:
    # Basic Info
    id: int
    name: str
    faction: Faction
    move_type: MoveType = MoveType.INFANTRY # Added movement type
    position: Tuple[int, int] = (0, 0)
    has_acted: bool = False

    # Core Stats
    max_hp: int = 1
    hp: int = 1
    strength: int = 0
    magic: int = 0
    skill: int = 0
    speed: int = 0
    luck: int = 0
    defense: int = 0
    constitution: int = 0
    mov: int = 0

    # Equipment
    equipped_weapon: Optional[Weapon] = None

    # Status
    is_alive: bool = True

    def __post_init__(self):
        self.hp = min(self.hp, self.max_hp)

# --- Map ---
@dataclass
class GameMap:
    width: int
    height: int
    tiles: List[List[Tile]] = field(default_factory=list)

    def __post_init__(self):
        if not self.tiles:
            self.tiles = [[Tile() for _ in range(self.width)] for _ in range(self.height)]

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return None

    def set_tile_terrain(self, x: int, y: int, terrain_type: TerrainType):
        """Helper to set terrain for specific tiles."""
        tile = self.get_tile(x, y)
        if tile:
            tile.terrain_type = terrain_type

    def place_unit(self, unit: Unit, x: int, y: int):
        tile = self.get_tile(x, y)
        if tile and tile.unit_id is None:
            tile.unit_id = unit.id
            unit.position = (x, y)
            return True
        return False

    def move_unit(self, unit: Unit, new_x: int, new_y: int):
        old_tile = self.get_tile(unit.position[0], unit.position[1])
        if old_tile:
            old_tile.unit_id = None

        new_tile = self.get_tile(new_x, new_y)
        if new_tile and new_tile.unit_id is None:
            new_tile.unit_id = unit.id
            unit.position = (new_x, new_y)
            return True
        else:
            if old_tile:
                old_tile.unit_id = unit.id
            return False

    def get_unit_id_at(self, x: int, y: int) -> Optional[int]:
        tile = self.get_tile(x, y)
        return tile.unit_id if tile else None

    def remove_unit(self, unit: Unit):
        tile = self.get_tile(unit.position[0], unit.position[1])
        if tile and tile.unit_id == unit.id:
            tile.unit_id = None


# --- Game State ---
@dataclass
class GameState:
    game_map: GameMap
    units: Dict[int, Unit] = field(default_factory=dict)
    turn: int = 1
    active_faction: Faction = Faction.PLAYER
    selected_unit_id: Optional[int] = None

    def get_unit(self, unit_id: int) -> Optional[Unit]:
        return self.units.get(unit_id)

    def get_selected_unit(self) -> Optional[Unit]:
        if self.selected_unit_id is not None:
            return self.get_unit(self.selected_unit_id)
        return None

    def add_unit(self, unit: Unit):
        if self.game_map.place_unit(unit, unit.position[0], unit.position[1]):
            self.units[unit.id] = unit
        else:
            print(f"Error: Cannot add unit {unit.name} at {unit.position}")

    def reset_player_actions(self):
        for unit in self.units.values():
            if unit.faction == Faction.PLAYER and unit.is_alive:
                unit.has_acted = False

    def get_units_by_faction(self, faction: Faction) -> List[Unit]:
        return [u for u in self.units.values() if u.faction == faction and u.is_alive]

    def handle_unit_death(self, unit: Unit):
        print(f"{unit.name} has been defeated!")
        unit.is_alive = False
        unit.hp = 0
        self.game_map.remove_unit(unit)