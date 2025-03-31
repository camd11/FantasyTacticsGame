# src/game/models.py (Updated)

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict

# --- Enums (Better than strings) ---
class Faction:
    PLAYER = "Player"
    ENEMY = "Enemy"
    ALLY = "Ally" # Added for future use

class TerrainType:
    PLAIN = "Plain"
    # Add Forest, Mountain etc. later

# --- Weapon ---
@dataclass
class Weapon:
    name: str
    might: int = 0
    hit: int = 0
    crit: int = 0 # Added for future use
    weight: int = 0
    wtype: str = "Sword" # Sword, Lance, Axe, Bow, Anima, Light, Dark, Staff
    range_min: int = 1
    range_max: int = 1
    # durability: int = -1 # Infinite uses for now

# --- Tile ---
@dataclass
class Tile:
    terrain_type: TerrainType = TerrainType.PLAIN
    unit_id: Optional[int] = None

# --- Unit ---
@dataclass
class Unit:
    # Basic Info
    id: int
    name: str
    faction: Faction
    position: Tuple[int, int] # (x, y)
    has_acted: bool = False

    # Core Stats (Based on research.md)
    max_hp: int = 1
    hp: int = 1
    strength: int = 0
    magic: int = 0
    skill: int = 0
    speed: int = 0
    luck: int = 0
    defense: int = 0
    constitution: int = 0 # Con / Build
    mov: int = 0

    # Inventory/Equipment (Simplified for now)
    equipped_weapon: Optional[Weapon] = None
    # inventory: List[Weapon | Item] = field(default_factory=list) # Add later

    # Status
    is_alive: bool = True # Track if defeated

    def __post_init__(self):
        # Ensure current HP doesn't exceed max HP on init
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
        """Removes a unit from the map tile."""
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
        """Handles setting unit status on death."""
        print(f"{unit.name} has been defeated!")
        unit.is_alive = False
        unit.hp = 0
        self.game_map.remove_unit(unit) # Remove from map tile
        # Note: Unit remains in the units dictionary but is marked as not alive.
        # We might remove them entirely later or handle permadeath/capture state.