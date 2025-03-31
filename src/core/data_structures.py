import math
from enum import Enum, auto

class Phase(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

class UnitType(Enum):
    PLAYER = auto()
    ENEMY = auto()
    NPC = auto()

class UnitState(Enum):
    NORMAL = auto()
    FATIGUED = auto()
    CAPTURED = auto()
    RESCUED = auto()
    SLEEP = auto()
    SILENCE = auto()
    BERSERK = auto()
    POISON = auto()
    STONE = auto() # Added based on mechanics doc

class TerrainType(Enum):
    PLAIN = auto()
    FOREST = auto()
    MOUNTAIN = auto()
    RIVER = auto()
    BRIDGE = auto()
    ROAD = auto()
    WALL = auto()
    DOOR = auto()
    GATE = auto()
    FORT = auto()
    THRONE = auto()
    HOUSE = auto()
    VILLAGE = auto()
    SHOP = auto()
    ARENA = auto()
    DESERT = auto()
    CLIFF = auto()
    SEA = auto()
    INDOOR_FLOOR = auto()
    # Add more specific types as needed

class MovementType(Enum):
    INFANTRY = auto()
    ARMOR = auto()
    CAVALRY = auto()
    FLYING = auto()
    PIRATE = auto()
    BRIGAND = auto()
    # Add more specific types as needed

class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"({self.x},{self.y})"

    def get_distance(self, other: 'Position') -> float:
        """Get the Euclidean distance to another position."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def get_manhattan_distance(self, other: 'Position') -> int:
        """Get the Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_adjacent_positions(self) -> list['Position']:
        """Get all positions adjacent to this one."""
        return [
            Position(self.x + 1, self.y),
            Position(self.x - 1, self.y),
            Position(self.x, self.y + 1),
            Position(self.x, self.y - 1)
        ]

    def is_adjacent(self, other: 'Position') -> bool:
        """Check if this position is adjacent to another."""
        return self.get_manhattan_distance(other) == 1

class Stats:
    def __init__(self, hp=0, strength=0, magic=0, skill=0, speed=0, luck=0,
                 defense=0, constitution=0, movement=0, current_hp=None):
        self.hp = hp
        self.strength = strength
        self.magic = magic
        self.skill = skill
        self.speed = speed
        self.luck = luck
        self.defense = defense
        self.constitution = constitution
        self.movement = movement
        self.current_hp = current_hp if current_hp is not None else hp

    def calculate_attack_speed(self, weapon):
        """
        Calculate Attack Speed based on Speed and weapon weight.
        Formula from Thracia 776 mechanics.
        """
        if not weapon:
            return self.speed # No weapon, AS is just Speed

        if weapon.is_magic():
            # For magic weapons, Con doesn't offset weight
            return self.speed - weapon.weight
        else:
            # For physical weapons: AS = Speed - max(0, (Weapon Weight - Constitution))
            weight_penalty = max(0, weapon.weight - self.constitution)
            return self.speed - weight_penalty

    def calculate_hit_rate(self, weapon):
        """
        Calculate Hit Rate based on Skill, Luck, and weapon hit.
        Formula: Hit = Weapon Hit + (2 × Skill) + Luck
        (Bonuses like support, leadership, etc., handled by CombatSystem)
        """
        if not weapon:
            return 0 # Cannot hit without a weapon
        return weapon.hit + (2 * self.skill) + self.luck

    def calculate_avoid(self, current_as=None):
        """
        Calculate Avoid based on Attack Speed and Luck.
        Formula: Avoid = (2 × Attack Speed) + Luck
        (Bonuses like support, leadership, terrain, etc., handled by CombatSystem)
        """
        # AS depends on the equipped weapon, which might not be available here.
        # CombatSystem should calculate AS with the weapon and pass it.
        # If no AS provided, use base speed as a fallback (less accurate).
        effective_as = current_as if current_as is not None else self.speed
        return (2 * effective_as) + self.luck

    def calculate_critical(self, weapon):
        """
        Calculate Critical Rate based on Skill and weapon critical.
        Formula: Critical = Weapon Critical + Skill
        (Bonuses/reductions handled by CombatSystem)
        """
        if not weapon:
            return 0
        return weapon.critical + self.skill

    def calculate_dodge(self):
        """
        Calculate Critical Evade (Dodge) based on Luck.
        Formula: Dodge = Luck / 2
        (Bonuses handled by CombatSystem)
        """
        return self.luck // 2

# Placeholder for Weapon class needed by Stats methods
class Weapon:
    def __init__(self, name="Placeholder Weapon", hit=0, might=0, critical=0, weight=0, is_magic=False):
        self.name = name
        self.hit = hit
        self.might = might
        self.critical = critical
        self.weight = weight
        self._is_magic = is_magic

    def is_magic(self):
        return self._is_magic