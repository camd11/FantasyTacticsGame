"""
Game State Manager Module

This module is responsible for holding and managing all dynamic data related to the current game session.
It provides interfaces for the Engine Core and other components to query and modify this data safely and consistently.
"""

import logging
import random
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Set, Union

# Import the data provider for accessing static data
from src.core_engine.data_provider import DataProvider, TerrainTypeEnum, MovementTypeEnum

# Enums
class FactionEnum(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

class PhaseEnum(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()
    EVENT = auto()  # Added for event phase

class StatusEffectEnum(Enum):
    POISON = auto()
    SLEEP = auto()
    SILENCE = auto()
    BERSERK = auto()
    STAT_BOOST = auto()  # For temporary stat boosts

class DispositionEnum(Enum):
    ACTIVE = auto()  # Unit is active in the current chapter
    DEAD = auto()    # Unit has been killed
    ESCAPED = auto() # Unit has escaped the map
    CAPTURED_BY_ENEMY = auto()  # Unit has been captured by an enemy
    BENCHED = auto() # Unit is not deployed in the current chapter

class ObjectStateEnum(Enum):
    NORMAL = auto()
    VISITED = auto()  # For villages
    OPENED = auto()   # For doors
    LOOTED = auto()   # For chests

# Constants
LEIF_ID = "LEIF"  # ID for the main character
CHAPTER_8_ID = "CH8"  # Chapter where fatigue starts to matter

# Fatigue costs for different actions
FATIGUE_COMBAT = 1
FATIGUE_STAFF_E = 1
FATIGUE_STAFF_D = 2
FATIGUE_STAFF_C = 3
FATIGUE_STAFF_B = 4
FATIGUE_STAFF_A = 5
FATIGUE_SPECIAL_ACTION = 2  # For actions like Dance, Steal

# Data Structures
class ItemInstance:
    """Represents an item instance in a unit's inventory."""
    def __init__(self, item_id: str, current_durability: int):
        self.item_id = item_id
        self.current_durability = current_durability

class StatusEffectInstance:
    """Represents an active status effect on a unit."""
    def __init__(self, type: StatusEffectEnum, duration: int, magnitude: int = 0):
        self.type = type
        self.duration = duration  # Turns remaining, -1 for permanent until cured/chapter end
        self.magnitude = magnitude  # For stat boosts

class UnitState:
    """Represents the current state of a unit on the map."""
    
    def __init__(self):
        self.id: str = ""
        self.name: str = ""
        self.class_id: str = ""
        self.faction: FactionEnum = FactionEnum.PLAYER
        self.position: Tuple[int, int] = (0, 0)
        
        self.current_hp: int = 0
        self.max_hp: int = 0
        
        # Base Stats
        self.base_stats: Dict[str, int] = {}
        
        # Growths
        self.growth_rates: Dict[str, int] = {}
        
        self.level: int = 1
        self.experience: int = 0
        
        self.inventory: List[ItemInstance] = []
        self.equipped_weapon_index: int = -1  # -1 if none
        
        self.weapon_ranks: Dict[str, str] = {}  # WeaponType -> Rank
        self.weapon_exp: Dict[str, int] = {}    # WeaponType -> Experience points
        
        self.current_fatigue: int = 0
        
        self.status_effects: List[StatusEffectInstance] = []
        
        # Action state for current turn
        self.has_moved: bool = False
        self.has_acted: bool = False
        
        # Relationships/Bonuses
        self.support_partner_ids: List[str] = []
        self.leadership_stars: int = 0
        self.pcc: int = 0  # Pursuit Critical Coefficient
        
        # Capture/Rescue State
        self.is_captured: bool = False
        self.carrying_unit_id: Optional[str] = None
        
        # Overall Status
        self.disposition: DispositionEnum = DispositionEnum.ACTIVE
    
    def has_status(self, status_type: StatusEffectEnum) -> bool:
        """Check if the unit has a specific status effect."""
        return any(status.type == status_type for status in self.status_effects)

class MapState:
    """Represents the current state of the map."""
    
    def __init__(self):
        self.map_id: str = ""
        self.dimensions: Tuple[int, int] = (0, 0)  # width, height
        self.terrain_grid: List[List[TerrainTypeEnum]] = []
        self.unit_positions: Dict[str, Tuple[int, int]] = {}  # unit_id -> (x, y)
        self.object_states: Dict[Tuple[int, int], ObjectStateEnum] = {}  # (x, y) -> state

class GameState:
    """Main container for all dynamic game state data."""
    
    def __init__(self):
        self.chapter_id: str = ""
        self.current_turn: int = 1
        self.current_phase: PhaseEnum = PhaseEnum.PLAYER
        
        self.map_state: MapState = MapState()
        self.unit_states: Dict[str, UnitState] = {}  # unit_id -> UnitState
        
        self.event_flags: Dict[str, bool] = {}  # flag_name -> triggered_status
        
        # Player convoy/gold if applicable
        self.player_gold: int = 0
        self.player_convoy: List[ItemInstance] = []
        
        # Currently selected unit (for player phase)
        self.selected_unit_id: Optional[str] = None

class GameStateManager:
    """
    Manages all dynamic game state data.
    Provides interfaces to query and modify this data safely and consistently.
    """
    
    def __init__(self, data_provider: DataProvider):
        self.current_game_state: Optional[GameState] = None
        self.data_provider = data_provider
    
    def load_map(self, map_data: Any) -> None:
        """Initialize a new game state with the specified map data."""
        state = GameState()
        state.map_state = MapState()
        state.map_state.map_id = map_data.id
        state.map_state.dimensions = map_data.dimensions
        
        # Convert string terrain codes to TerrainTypeEnum values
        terrain_grid = []
        for row in map_data.terrain_grid:
            terrain_row = []
            for terrain_code in row:
                # Try to convert the string code to TerrainTypeEnum
                try:
                    # If it's already a TerrainTypeEnum, use it directly
                    if isinstance(terrain_code, TerrainTypeEnum):
                        terrain_row.append(terrain_code)
                    else:
                        # Map string codes to TerrainTypeEnum values
                        code_to_enum = {
                            'P': TerrainTypeEnum.PLAIN,
                            'F': TerrainTypeEnum.FOREST,
                            'W': TerrainTypeEnum.RIVER,
                            'D': TerrainTypeEnum.BRIDGE,
                            'V': TerrainTypeEnum.VILLAGE,
                            'S': TerrainTypeEnum.THRONE,  # Seize point is represented as throne
                            'M': TerrainTypeEnum.MOUNTAIN,
                            'H': TerrainTypeEnum.CASTLE,
                            'T': TerrainTypeEnum.THRONE
                        }
                        
                        if terrain_code in code_to_enum:
                            terrain_row.append(code_to_enum[terrain_code])
                        else:
                            # If code not found in mapping, try direct enum lookup
                            try:
                                terrain_row.append(TerrainTypeEnum[terrain_code])
                            except (KeyError, ValueError):
                                # If all conversion attempts fail, use INVALID as fallback
                                logging.warning(f"Invalid terrain code '{terrain_code}', using INVALID")
                                terrain_row.append(TerrainTypeEnum.INVALID)
                except Exception as e:
                    logging.warning(f"Error converting terrain code '{terrain_code}': {str(e)}, using INVALID")
                    terrain_row.append(TerrainTypeEnum.INVALID)
            terrain_grid.append(terrain_row)
            
        state.map_state.terrain_grid = terrain_grid
        state.map_state.unit_positions = {}
        state.map_state.object_states = {}
        state.unit_states = {}
        state.event_flags = {}
        state.chapter_id = map_data.id  # Assuming map_id is the same as chapter_id
        
        self.current_game_state = state
        logging.info(f"Map loaded: {map_data.id}")
    
    def deploy_units(self, unit_placements: List, data_provider: DataProvider) -> None:
        """Deploy units on the map based on the provided placements."""
        if not self.current_game_state:
            logging.error("Cannot deploy units: No game state initialized")
            return
        
        for placement in unit_placements:
            unit_id = placement.unit_id
            base_data = data_provider.get_unit_base_data(unit_id)
            
            if not base_data:
                logging.warning(f"Unit base data not found for {unit_id}")
                continue
            
            unit = UnitState()
            unit.id = unit_id
            unit.name = base_data.name
            unit.class_id = base_data.base_class_id
            
            # Convert string faction to FactionEnum
            if placement.faction == 'PLAYER':
                unit.faction = FactionEnum.PLAYER
            elif placement.faction == 'ENEMY':
                unit.faction = FactionEnum.ENEMY
            elif placement.faction == 'NPC':
                unit.faction = FactionEnum.NPC
            else:
                logging.warning(f"Unknown faction '{placement.faction}' for unit {unit_id}, defaulting to PLAYER")
                unit.faction = FactionEnum.PLAYER
                
            unit.position = tuple(placement.position)
            
            unit.max_hp = base_data.stats.get("HP", 0)
            unit.current_hp = unit.max_hp
            
            unit.base_stats = base_data.stats
            unit.growth_rates = base_data.growths
            unit.level = placement.level
            unit.experience = 0
            
            # Initialize inventory
            unit.inventory = []
            for item_id in placement.start_inventory:
                item_data = data_provider.get_item_data(item_id)
                if item_data:
                    unit.inventory.append(ItemInstance(
                        item_id=item_id,
                        current_durability=item_data.max_durability
                    ))
            
            # Find initial equipped weapon
            unit.equipped_weapon_index = self._find_initial_equipped_weapon(unit.inventory, data_provider)
            
            unit.weapon_ranks = base_data.base_weapon_ranks
            unit.weapon_exp = {wt: 0 for wt in unit.weapon_ranks}
            
            unit.current_fatigue = placement.starting_fatigue
            unit.status_effects = []
            
            unit.has_moved = False
            unit.has_acted = False
            
            unit.support_partner_ids = data_provider.get_support_partners(unit_id)
            unit.leadership_stars = base_data.leadership_stars
            unit.pcc = base_data.pcc
            
            unit.is_captured = False
            unit.carrying_unit_id = None
            unit.disposition = DispositionEnum.ACTIVE
            
            # Handle autoleveling if needed
            if placement.needs_autolevel:
                self._autolevel_unit(unit, placement.target_level, data_provider)
            
            self.current_game_state.unit_states[unit_id] = unit
            self.current_game_state.map_state.unit_positions[unit_id] = tuple(unit.position)
        
        logging.info("Units deployed")
    
    # --- Query Functions ---
    
    def get_unit(self, unit_id: str) -> Optional[UnitState]:
        """Get a unit by ID."""
        if not self.current_game_state:
            return None
        return self.current_game_state.unit_states.get(unit_id)
    
    def get_units_by_faction(self, faction: FactionEnum) -> List[UnitState]:
        """Get all active units of a specific faction."""
        if not self.current_game_state:
            return []
        
        return [
            unit for unit in self.current_game_state.unit_states.values()
            if unit.faction == faction and unit.disposition == DispositionEnum.ACTIVE
        ]
    
    def get_units_within_range(self, position: Tuple[int, int], range_val: int, include_faction: Optional[FactionEnum] = None) -> List[UnitState]:
        """Get all units within a certain range of a position."""
        if not self.current_game_state:
            return []
        
        result = []
        x, y = position
        
        for unit in self.current_game_state.unit_states.values():
            if unit.disposition != DispositionEnum.ACTIVE:
                continue
            
            if include_faction and unit.faction != include_faction:
                continue
            
            unit_x, unit_y = unit.position
            distance = abs(x - unit_x) + abs(y - unit_y)  # Manhattan distance
            
            if distance <= range_val:
                result.append(unit)
        
        return result
    
    def get_terrain_type(self, position: Tuple[int, int]) -> TerrainTypeEnum:
        """Get the terrain type at a specific position."""
        if not self.current_game_state:
            return TerrainTypeEnum.INVALID
        
        x, y = position
        dimensions = self.current_game_state.map_state.dimensions
        
        if 0 <= x < dimensions[0] and 0 <= y < dimensions[1]:
            return self.current_game_state.map_state.terrain_grid[y][x]
        
        return TerrainTypeEnum.INVALID
    
    def get_terrain_movement_cost(self, position: Tuple[int, int], unit_id: str) -> int:
        """Get the movement cost for a unit to move to a specific position."""
        if not self.current_game_state:
            return 99  # IMPASSABLE
        
        unit = self.get_unit(unit_id)
        if not unit:
            return 99  # IMPASSABLE
        
        terrain_type = self.get_terrain_type(position)
        class_data = self.data_provider.get_class_data(unit.class_id)
        
        if not class_data:
            return 99  # IMPASSABLE
        
        movement_type = class_data.movement_type
        
        # Handle dismount: if unit is mounted and terrain is indoor, use infantry movement type
        if self.is_unit_mounted(unit_id) and self.data_provider.is_terrain_indoor(terrain_type):
            movement_type = MovementTypeEnum.INFANTRY
        
        cost = self.data_provider.get_terrain_cost(terrain_type, movement_type)
        return cost
    
    def get_terrain_bonus(self, position: Tuple[int, int]) -> Dict[str, int]:
        """Get the defensive bonuses for a specific position."""
        if not self.current_game_state:
            return {'def': 0, 'avo': 0}
        
        terrain_type = self.get_terrain_type(position)
        return self.data_provider.get_terrain_bonuses(terrain_type)
    
    def is_tile_occupied(self, position: Tuple[int, int]) -> bool:
        """Check if a tile is occupied by a unit."""
        if not self.current_game_state:
            return False
        
        return position in self.current_game_state.map_state.unit_positions.values()
    
    def is_tile_seize_point(self, position: Tuple[int, int]) -> bool:
        """Check if a tile is a seize point."""
        if not self.current_game_state:
            return False
        
        map_data = self.data_provider.get_map_data(self.current_game_state.chapter_id)
        if not map_data:
            return False
        
        return map_data.seize_point == position
    
    def get_unit_movement_stars(self, unit_id: str) -> int:
        """Get the number of movement stars for a unit."""
        unit = self.get_unit(unit_id)
        if not unit:
            return 0
        
        return unit.base_stats.get("MOV_STARS", 0)
    
    def is_unit_fatigued_for_deployment(self, unit_id: str) -> bool:
        """Check if a unit is too fatigued to be deployed."""
        if not self.current_game_state:
            return False
        
        # Leif is exempt from fatigue
        if unit_id == LEIF_ID:
            return False
        
        # Fatigue check only applies from Chapter 8 onwards
        if self.current_game_state.chapter_id < CHAPTER_8_ID:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        return unit.current_fatigue >= unit.max_hp
    
    def is_unit_mounted(self, unit_id: str) -> bool:
        """Check if a unit is mounted."""
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        class_data = self.data_provider.get_class_data(unit.class_id)
        if not class_data:
            return False
        
        # A class is considered mounted if it has a dismount_class_id
        return class_data.dismount_class_id is not None
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get the dimensions of the current map (width, height)."""
        if not self.current_game_state:
            return (0, 0)
        
        return self.current_game_state.map_state.dimensions
    
    def has_npc_units(self) -> bool:
        """Check if there are any active NPC units on the map."""
        if not self.current_game_state:
            return False
        
        return any(
            unit.faction == FactionEnum.NPC and unit.disposition == DispositionEnum.ACTIVE
            for unit in self.current_game_state.unit_states.values()
        )
    
    # --- Modification Functions ---
    
    def move_unit(self, unit_id: str, new_position: Tuple[int, int]) -> bool:
        """Move a unit to a new position."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        old_position = unit.position
        unit.position = tuple(new_position)
        
        # Update map_state.unit_positions dictionary
        self.current_game_state.map_state.unit_positions[unit_id] = tuple(new_position)
        
        logging.info(f"Unit {unit_id} moved from {old_position} to {new_position}")
        return True
    
    def apply_damage(self, unit_id: str, damage: int, is_capture_attempt: bool = False) -> bool:
        """Apply damage to a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        unit.current_hp = max(0, unit.current_hp - damage)
        logging.info(f"Unit {unit_id} takes {damage} damage. HP: {unit.current_hp}/{unit.max_hp}")
        
        if unit.current_hp <= 0:
            if is_capture_attempt:
                # Unit is captured by the attacker
                logging.info(f"Unit {unit_id} was captured!")
                unit.disposition = DispositionEnum.CAPTURED_BY_ENEMY
            else:
                unit.disposition = DispositionEnum.DEAD
                logging.info(f"Unit {unit_id} has fallen!")
                # Remove unit from map positions
                if unit_id in self.current_game_state.map_state.unit_positions:
                    del self.current_game_state.map_state.unit_positions[unit_id]
        
        return True
    
    def apply_healing(self, unit_id: str, amount: int) -> bool:
        """Apply healing to a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        unit.current_hp = min(unit.max_hp, unit.current_hp + amount)
        logging.info(f"Unit {unit_id} healed for {amount}. HP: {unit.current_hp}/{unit.max_hp}")
        return True
    
    def add_status_effect(self, unit_id: str, status_type: StatusEffectEnum, duration: int, magnitude: int = 0) -> bool:
        """Add a status effect to a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        # Check if already present, maybe refresh duration
        existing_status = next((s for s in unit.status_effects if s.type == status_type), None)
        
        if existing_status:
            # Update existing status
            existing_status.duration = duration
            existing_status.magnitude = magnitude
        else:
            # Add new status
            unit.status_effects.append(StatusEffectInstance(
                type=status_type,
                duration=duration,
                magnitude=magnitude
            ))
        
        logging.info(f"Unit {unit_id} afflicted with {status_type.name}")
        return True
    
    def remove_status_effect(self, unit_id: str, status_type: StatusEffectEnum) -> bool:
        """Remove a status effect from a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        unit.status_effects = [s for s in unit.status_effects if s.type != status_type]
        logging.info(f"Unit {unit_id} cured of {status_type.name}")
        return True
    
    def update_fatigue(self, unit_id: str, amount: int) -> bool:
        """Update the fatigue level of a unit."""
        if not self.current_game_state:
            return False
        
        unit = self.get_unit(unit_id)
        if not unit:
            return False
        
        unit.current_fatigue += amount
        logging.info(f"Unit {unit_id} fatigue increased by {amount}. Current: {unit.current_fatigue}")
        return True
    
    def apply_combat_results(self, combat_result: Dict[str, Any]) -> bool:
        """Apply the results of combat to the units involved."""
        if not self.current_game_state:
            return False
        
        # Extract data from combat_result
        attacker_id = combat_result.get('attacker_id')
        defender_id = combat_result.get('defender_id')
        attacker_damage = combat_result.get('attacker_damage', 0)
        defender_damage = combat_result.get('defender_damage', 0)
        attacker_exp = combat_result.get('attacker_exp', 0)
        defender_exp = combat_result.get('defender_exp', 0)
        attacker_wexp = combat_result.get('attacker_wexp', 0)
        defender_wexp = combat_result.get('defender_wexp', 0)
        is_capture = combat_result.get('is_capture', False)
        
        # Apply damage
        if attacker_id:
            self.apply_damage(attacker_id, defender_damage)
        
        if defender_id:
            self.apply_damage(defender_id, attacker_damage, is_capture)
        
        # Apply experience
        if attacker_id:
            self._apply_experience(attacker_id, attacker_exp)
        
        if defender_id:
            self._apply_experience(defender_id, defender_exp)
        
        # Apply weapon experience
        if attacker_id and attacker_wexp > 0:
            self._apply_weapon_experience(attacker_id, combat_result.get('attacker_weapon_type'), attacker_wexp)
        
        if defender_id and defender_wexp > 0:
            self._apply_weapon_experience(defender_id, combat_result.get('defender_weapon_type'), defender_wexp)
        
        # Apply fatigue
        if attacker_id:
            self.update_fatigue(attacker_id, FATIGUE_COMBAT)
        
        if defender_id:
            self.update_fatigue(defender_id, FATIGUE_COMBAT)
        
        return True
    
    def finalize_chapter_fatigue(self) -> None:
        """Update fatigue status for all units at the end of a chapter."""
        if not self.current_game_state:
            return
        
        for unit in self.current_game_state.unit_states.values():
            if unit.faction == FactionEnum.PLAYER and unit.disposition == DispositionEnum.ACTIVE:
                # Check if unit is fatigued for next deployment
                if unit.id != LEIF_ID and unit.current_fatigue >= unit.max_hp:
                    logging.info(f"Unit {unit.id} is fatigued for next deployment")
        
        logging.info("Chapter fatigue finalized")
    
    def finalize_escape_map_captures(self) -> None:
        """Mark units left on an escape map as captured if Leif escaped."""
        if not self.current_game_state:
            return
        
        # Check if this is an escape map and if Leif escaped
        leif = self.get_unit(LEIF_ID)
        if not leif or leif.disposition != DispositionEnum.ESCAPED:
            return
        
        # Mark remaining player units as captured
        for unit in self.current_game_state.unit_states.values():
            if unit.faction == FactionEnum.PLAYER and unit.disposition == DispositionEnum.ACTIVE:
                unit.disposition = DispositionEnum.CAPTURED_BY_ENEMY
                logging.info(f"Unit {unit.id} was left behind and captured")
        
        logging.info("Escape map captures finalized")
    
    # --- Helper Functions ---
    
    def _find_initial_equipped_weapon(self, inventory: List[ItemInstance], data_provider: DataProvider) -> int:
        """Find the index of the first equippable weapon in the inventory."""
        for i, item in enumerate(inventory):
            item_data = data_provider.get_item_data(item.item_id)
            if item_data and item_data.type == "WEAPON":
                return i
        return -1
    
    def _autolevel_unit(self, unit: UnitState, target_level: int, data_provider: DataProvider) -> None:
        """Apply automatic level ups to a unit to reach the target level."""
        if unit.level >= target_level:
            return
        
        levels_to_gain = target_level - unit.level
        
        for _ in range(levels_to_gain):
            # Apply growths to stats
            for stat, growth in unit.growth_rates.items():
                if stat == "HP":
                    continue  # Handle HP separately if needed
                
                # Check if growth triggers (e.g., 60% = 0.6 chance)
                if random.random() < (growth / 100.0):
                    unit.base_stats[stat] = unit.base_stats.get(stat, 0) + 1
            
            unit.level += 1
        
        logging.info(f"Unit {unit.id} autoleveled to level {unit.level}")
    
    def _apply_experience(self, unit_id: str, exp_amount: int) -> None:
        """Apply experience to a unit, handling level ups if necessary."""
        unit = self.get_unit(unit_id)
        if not unit:
            return
        
        unit.experience += exp_amount
        
        # Check for level up
        if unit.experience >= 100:
            unit.level += 1
            unit.experience -= 100
            
            # Apply stat growths for level up
            self._apply_level_up_growths(unit)
            
            logging.info(f"Unit {unit_id} leveled up to {unit.level}")
    
    def _apply_level_up_growths(self, unit: UnitState) -> None:
        """Apply random stat growths for a level up."""
        for stat, growth in unit.growth_rates.items():
            if stat == "HP":
                continue  # Handle HP separately if needed
            
            # Check if growth triggers (e.g., 60% = 0.6 chance)
            if random.random() < (growth / 100.0):
                unit.base_stats[stat] = unit.base_stats.get(stat, 0) + 1
    
    def _apply_weapon_experience(self, unit_id: str, weapon_type: str, wexp_amount: int) -> None:
        """Apply weapon experience to a unit, handling rank ups if necessary."""
        unit = self.get_unit(unit_id)
        if not unit or not weapon_type:
            return
        
        if weapon_type not in unit.weapon_exp:
            return
        
        unit.weapon_exp[weapon_type] += wexp_amount
        
        # Check for rank up (simplified, would need actual WExp thresholds)
        # This is just a placeholder for the actual rank up logic
        logging.info(f"Unit {unit_id} gained {wexp_amount} WExp in {weapon_type}")
