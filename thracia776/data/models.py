from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum, auto

# --- Enums and Constants ---

class Affiliation(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

class StatusEffect(Enum):
    NORMAL = auto()
    POISON = auto()
    SLEEP = auto()
    SILENCE = auto()
    BERSERK = auto()
    PETRIFY = auto()
    FATIGUED = auto() # Added for clarity, distinct from fatigue points

class WeaponType(Enum):
    SWORD = auto()
    LANCE = auto()
    AXE = auto()
    BOW = auto()
    STAFF = auto()
    FIRE = auto()
    THUNDER = auto()
    WIND = auto()
    LIGHT = auto()
    DARK = auto()
    ITEM = auto() # For non-weapon/tome items

class ItemType(Enum):
    WEAPON = auto()
    STAFF = auto()
    USABLE = auto()
    SCROLL = auto()
    KEY = auto()
    ACCESSORY = auto() # Example, might need refinement
    MONEY = auto()     # Example
    OTHER = auto()

class WeaponRank(Enum):
    NONE = 0 # For units/items that don't use ranks
    E = 1
    D = 2
    C = 3
    B = 4
    A = 5
    S = 6 # Often represented as Star/Prf in FE5, using S for simplicity
    PRF = 7 # For personal/unique weapons

class Skill(Enum):
    # Placeholder for specific skills
    WRATH = auto()
    ADEPT = auto()
    CHARISMA = auto()
    NIHIL = auto()
    VANTAGE = auto()
    # ... add all Thracia skills

class TerrainType(Enum):
    PLAIN = auto()
    FOREST = auto()
    THICKET = auto()
    MOUNTAIN = auto()
    PEAK = auto()
    FORT = auto()
    GATE = auto()
    THRONE = auto()
    CHURCH = auto()
    HOUSE = auto()
    ARMORY = auto()
    VENDOR = auto()
    ARENA = auto()
    SEA = auto()
    LAKE = auto()
    RIVER = auto()
    BRIDGE = auto()
    WASTELAND = auto()
    SAND = auto()
    WALL = auto()
    SNAG = auto()
    FLOOR = auto()
    PILLAR = auto()
    ROOF = auto()
    # ... add others as needed

class MovementType(Enum):
    # Based on common FE archetypes, adjust for Thracia specifics
    INFANTRY = auto()
    ARMOR = auto()
    CAVALRY = auto()
    FLIER = auto()
    MOUNTED_ARMOR = auto() # e.g., Great Knight - adjust if not in Thracia
    BANDIT = auto() # For specific terrain interactions
    # ... add others as needed

class GamePhase(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

# --- Helper Data Structures ---

@dataclass
class UnitStats:
    hp: int
    max_hp: int
    skill: int
    speed: int
    luck: int
    defense: int
    constitution: int
    movement: int
    strength: int = 0 # Use 'strength' generically, applies to Mag for magic classes
    magic: int = 0
    build: int = 0 # Thracia's 'Build' stat, often linked to Con

@dataclass
class UnitGrowths:
    hp: int
    strength: int
    magic: int
    skill: int
    speed: int
    luck: int
    defense: int
    constitution: int # Growth for Con/Build if applicable
    movement: int # Growth for Mov if applicable

@dataclass
class WeaponExp:
    sword: int = 0
    lance: int = 0
    axe: int = 0
    bow: int = 0
    staff: int = 0
    fire: int = 0
    thunder: int = 0
    wind: int = 0
    light: int = 0
    dark: int = 0

@dataclass
class WeaponRanks:
    sword: WeaponRank = WeaponRank.NONE
    lance: WeaponRank = WeaponRank.NONE
    axe: WeaponRank = WeaponRank.NONE
    bow: WeaponRank = WeaponRank.NONE
    staff: WeaponRank = WeaponRank.NONE
    fire: WeaponRank = WeaponRank.NONE
    thunder: WeaponRank = WeaponRank.NONE
    wind: WeaponRank = WeaponRank.NONE
    light: WeaponRank = WeaponRank.NONE
    dark: WeaponRank = WeaponRank.NONE

# --- Core Data Models ---

@dataclass
class Item:
    id: str # Unique identifier for the item type (e.g., "iron_sword")
    name: str
    type: ItemType
    instance_id: Optional[str] = None # Unique ID for this specific instance if needed (e.g., for durability tracking on non-stackables)
    weapon_type: Optional[WeaponType] = None # Only if type is WEAPON or STAFF (for rank)
    might: int = 0
    hit: int = 0
    crit: int = 0
    weight: int = 0
    range_min: int = 1
    range_max: int = 1
    uses: Optional[int] = None # None for infinite uses
    max_uses: Optional[int] = None
    rank_req: WeaponRank = WeaponRank.NONE
    effects: List[Any] = field(default_factory=list) # Define effect structure later
    value: int = 0 # Gold value

@dataclass
class Unit:
    id: str # Unique identifier (e.g., "leif", "enemy_fighter_1")
    name: str
    cls_name: str # Class name (e.g., "Lord", "Fighter")
    affiliation: Affiliation
    stats: UnitStats
    growths: UnitGrowths
    movement_type: MovementType # Derived from class, needed for MapTile interaction
    level: int = 1
    exp: int = 0
    status: StatusEffect = StatusEffect.NORMAL
    fatigue: int = 0
    inventory: List[Optional[Item]] = field(default_factory=lambda: [None] * 7) # Max 7 items
    equipped_weapon_index: Optional[int] = None # Index in inventory (0-6)
    weapon_ranks: WeaponRanks = field(default_factory=WeaponRanks)
    wexp: WeaponExp = field(default_factory=WeaponExp)
    skills: List[Skill] = field(default_factory=list)
    pcc: int = 0 # Pursuit Critical Coefficient (0-5)
    leadership_stars: int = 0
    supports: Dict[str, Any] = field(default_factory=dict) # Key: Unit ID, Value: Support level/data
    position: Tuple[int, int] = (-1, -1) # (x, y), -1 indicates off-map/deployed
    is_mounted: bool = False
    is_rescuing: Optional[str] = None # ID of unit being rescued/captured
    has_acted: bool = False
    ai_flags: Dict[str, Any] = field(default_factory=dict) # AI behavior settings
    vision_range: int = 5 # Base vision

@dataclass
class MapTile:
    terrain_type: TerrainType
    def_bonus: int = 0
    avo_bonus: int = 0
    movement_costs: Dict[MovementType, int] = field(default_factory=dict) # Cost per movement type
    blocks_vision: bool = False
    is_impassable: bool = False
    occupying_unit_id: Optional[str] = None
    event_trigger: Optional[Any] = None # Event ID or data
    is_seize_point: bool = False
    is_escape_point: bool = False
    is_visit_target: bool = False
    # Add other special flags as needed (e.g., is_supply_point)

@dataclass
class GameState:
    chapter_id: str
    turn_number: int = 1
    current_phase: GamePhase = GamePhase.PLAYER
    active_units: Dict[str, Unit] = field(default_factory=dict) # All units currently on the map
    map_state: Dict[Tuple[int, int], MapTile] = field(default_factory=dict) # Key: (x,y), Value: MapTile
    event_flags: Dict[str, bool] = field(default_factory=dict) # Track triggered events
    player_roster: Dict[str, Unit] = field(default_factory=dict) # All player units (incl. benched)
    convoy: List[Item] = field(default_factory=list)
    victory_condition: Any = None # Define structure later (e.g., seize throne, defeat boss)
    loss_conditions: List[Any] = field(default_factory=list) # e.g., Leif defeated, turn limit exceeded
    fog_of_war_active: bool = False
    visibility_map: Optional[Any] = None # Placeholder for visibility data structure