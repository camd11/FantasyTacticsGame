# src/game/models.py (Updated)

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Union # Add Union

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

# --- Fatigue Costs ---
FATIGUE_COST_COMBAT = 1
FATIGUE_COST_ITEM = 1 # Simplified cost for using items like Vulnerary
# Add costs for Staff, Dance, Steal later


# --- Item Base Class ---
@dataclass
class Item:
    name: str
    uses: Optional[int] = None # None for infinite, or number for limited uses
    max_uses: Optional[int] = None

    def is_usable(self) -> bool:
        """Check if the item has remaining uses."""
        return self.uses is None or self.uses > 0

    def use(self):
        """Consume one use if applicable. Returns True if use was successful (or infinite)."""
        if self.uses is None: # Infinite uses
             return True
        if self.uses > 0:
            self.uses -= 1
            # print(f"Used {self.name}. {self.uses}/{self.max_uses} uses remaining.") # Moved print to action
            return True
        else: # uses == 0
            # print(f"Cannot use {self.name}, no uses left.") # Moved print to action
            return False


# --- Specific Item Example ---
@dataclass
class Vulnerary(Item):
    name: str = "Vulnerary"
    uses: int = 3
    max_uses: int = 3
    heal_amount: int = 10 # Thracia Vulnerary heals 10 HP

# --- Weapon (inherits from Item for potential uses later) ---
@dataclass
class Weapon(Item):
    name: str = "Unnamed Weapon"
    might: int = 0
    hit: int = 0
    crit: int = 0
    weight: int = 0
    wtype: str = "Sword"
    range_min: int = 1
    range_max: int = 1
    uses: Optional[int] = 50 # Example default uses
    max_uses: Optional[int] = 50

# --- Tile ---
@dataclass
class Tile:
    terrain_type: TerrainType = TerrainType.PLAIN
    unit_id: Optional[int] = None
    # Add terrain properties later (Avo bonus, Def bonus, Heal)

# --- Unit ---
InventoryItem = Union[Weapon, Item] # Type hint for inventory contents

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
    fatigue: int = 0 # NEW: Fatigue counter

    # Equipment & Inventory
    inventory: List[InventoryItem] = field(default_factory=list)
    equipped_weapon_index: Optional[int] = None # Index in inventory, None if unarmed

    # Status
    is_alive: bool = True
    is_captured: bool = False
    is_capturing: Optional[int] = None

    def __post_init__(self):
        self.hp = min(self.hp, self.max_hp)
        # Automatically equip the first weapon in inventory if not set and inventory exists
        if self.equipped_weapon_index is None and self.inventory:
            self._auto_equip_first_weapon()

    def _auto_equip_first_weapon(self):
        """Internal helper to equip the first available weapon."""
        self.equipped_weapon_index = None # Reset first
        for i, item in enumerate(self.inventory):
            if isinstance(item, Weapon):
                self.equipped_weapon_index = i
                # print(f"Auto-equipped {item.name} for {self.name}") # Debug
                break

    @property
    def equipped_weapon(self) -> Optional[Weapon]:
        """Gets the currently equipped weapon object."""
        if self.equipped_weapon_index is not None and 0 <= self.equipped_weapon_index < len(self.inventory):
            item = self.inventory[self.equipped_weapon_index]
            if isinstance(item, Weapon):
                return item
        return None

    def get_item_by_name(self, item_name: str) -> Optional[InventoryItem]:
        """Finds the first item in inventory matching the name (case-insensitive)."""
        search_name = item_name.lower()
        for item in self.inventory:
            if item.name.lower() == search_name:
                return item
        return None

    def add_item(self, item: InventoryItem):
        """Adds an item to inventory if there's space."""
        # Thracia inventory limit is 7
        if len(self.inventory) < 7:
            self.inventory.append(item)
            # Auto-equip if it's the first weapon added and none equipped
            if self.equipped_weapon_index is None and isinstance(item, Weapon):
                self.equipped_weapon_index = len(self.inventory) - 1
            return True
        else:
            print(f"Inventory full for {self.name}.")
            return False

    def remove_item(self, item_instance: InventoryItem):
        """Removes a specific item instance from inventory."""
        try:
            current_equipped_index = self.equipped_weapon_index
            item_index = self.inventory.index(item_instance)

            # Remove the item
            del self.inventory[item_index]

            # Handle equipped weapon index shift or removal
            if current_equipped_index is not None:
                if item_index == current_equipped_index:
                    # If the removed item was equipped, unequip and try auto-equipping next
                    self.equipped_weapon_index = None
                    self._auto_equip_first_weapon()
                elif item_index < current_equipped_index:
                    # If an item before the equipped one was removed, shift index down
                    self.equipped_weapon_index -= 1

        except ValueError:
            # Item not found in inventory
            pass


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
        # Prevent moving if capturing someone (for now - Thracia allows this with penalties)
        if unit.is_capturing is not None:
            print(f"Cannot move while capturing.") # Simple block for now
            return False

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
                old_tile.unit_id = unit.id # Put back if move failed
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
        # Return unit only if it exists
        unit = self.units.get(unit_id)
        return unit

    def get_selected_unit(self) -> Optional[Unit]:
        if self.selected_unit_id is not None:
            return self.get_unit(self.selected_unit_id)
        return None

    def add_unit(self, unit: Unit):
        # Ensure unit has position before placing
        if unit.position is None:
             print(f"Error: Unit {unit.name} has no position.")
             return

        if self.game_map.place_unit(unit, unit.position[0], unit.position[1]):
            self.units[unit.id] = unit
            # Ensure unit equips first weapon *after* being added and having inventory
            if not unit.equipped_weapon and unit.inventory:
                 unit._auto_equip_first_weapon()
        else:
            print(f"Error: Cannot add unit {unit.name} at {unit.position}")

    def reset_player_actions(self):
        """Resets action flag for Player units. Fatigue is NOT reset here."""
        for unit in self.units.values():
            # Only reset actions for alive, non-captured player units
            if unit.faction == Faction.PLAYER and unit.is_alive and not unit.is_captured:
                unit.has_acted = False
                # Fatigue persists across turns within a chapter

    def get_units_by_faction(self, faction: Faction) -> List[Unit]:
        # Return only alive, non-captured units with HP > 0
        return [
            u for u in self.units.values()
            if u.faction == faction and u.is_alive and not u.is_captured and u.hp > 0
        ]

    def handle_unit_death(self, unit: Unit):
        """Handles setting unit status on death (NOT capture)."""
        # --- DEBUG ---
        print(f"  DEBUG: handle_unit_death called for {unit.name}. Current HP: {unit.hp}")
        # -----------
        # Add check to ensure HP is actually 0 before proceeding with death state
        if unit.hp > 0 and not unit.is_captured:
            print(f"  ERROR: handle_unit_death called for {unit.name} but HP is {unit.hp}. NOT setting dead.")
            # Potentially log this error, but don't mark as dead if HP > 0
            return # Do not proceed if HP is not 0 (unless captured)

        if not unit.is_captured: # Only print death message if not captured
            print(f"{unit.name} has been defeated!")
        unit.is_alive = False
        # unit.hp = 0 # HP should already be 0 if this is called correctly

        # If unit was capturing someone, release the captive
        if unit.is_capturing is not None:
            captured_unit = self.units.get(unit.is_capturing) # Use .units.get()
            if captured_unit: # Check if captured unit still exists in dictionary
                 print(f"{unit.name} drops {captured_unit.name}!")
                 # Mark the dropped unit as no longer captured
                 captured_unit.is_captured = False
                 # TODO: Place dropped unit on map later at attacker's position
            unit.is_capturing = None
        self.game_map.remove_unit(unit) # Remove from map tile

    def handle_unit_capture(self, attacker: Unit, target: Unit):
        """Handles setting unit status on capture."""
        print(f"{attacker.name} captured {target.name}!")
        target.is_alive = True # Still technically "alive" but incapacitated
        target.is_captured = True
        target.hp = 0 # Set HP to 0 for consistency
        attacker.is_capturing = target.id
        self.game_map.remove_unit(target) # Remove captured unit from map tile