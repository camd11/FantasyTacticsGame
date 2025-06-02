from enum import Enum, auto
from typing import List, Optional

# Type Aliases for IDs from other systems (placeholders)
SkillID = str
ClassID = str

class ItemType(Enum):
    SWORD = auto()
    LANCE = auto()
    AXE = auto()
    BOW = auto()
    DAGGER = auto()
    FIRE_TOME = auto()
    THUNDER_TOME = auto()
    WIND_TOME = auto()
    LIGHT_TOME = auto()
    DARK_TOME = auto()
    STAFF = auto()
    CONSUMABLE = auto()
    SCROLL = auto()
    KEY = auto()
    VALUABLE = auto()
    # RING = auto() # If rings with passive effects exist as a distinct category
    # SHIELD = auto() # If shields with defensive properties exist as a distinct category

class WeaponRankID(Enum):
    E_RANK = auto()
    D_RANK = auto()
    C_RANK = auto()
    B_RANK = auto()
    A_RANK = auto()
    S_RANK = auto() # Or PRF rank

class WeaponTypeID(Enum):
    SWORD = auto()
    LANCE = auto()
    AXE = auto()
    BOW = auto()
    DAGGER = auto()
    FIRE_TOME = auto()
    THUNDER_TOME = auto()
    WIND_TOME = auto()
    LIGHT_TOME = auto()
    DARK_TOME = auto()
    BALLISTA = auto()

class TargetAttribute(Enum):
    ARMORED = auto()
    FLYING = auto()
    MOUNTED = auto()
    DRAGON = auto()
    MAGICAL_BEAST = auto()
    INFANTRY = auto()
    # Add other specific Thracia 776 effectiveness categories as identified

class WeaponSpecialProperty(Enum):
    BRAVE_EFFECT = auto()
    POISON_STRIKE = auto()
    DEVIL_EFFECT = auto()
    UNBREAKABLE = auto()
    NEGATES_CRITICALS = auto()
    ECLIPSE = auto()
    STEALS_HP = auto()
    CANNOT_BE_COUNTERED = auto()
    REAVER_EFFECT = auto()
    CRITICAL_BOOST = auto()
    MOVEMENT_COST_MODIFIER = auto()
    EFFECTIVE_DAMAGE_ONLY = auto()
    # Add other specific Thracia 776 weapon properties as identified

class StaffEffectType(Enum):
    HEAL_SINGLE_FIXED = auto()
    HEAL_SINGLE_USER_MAG = auto()
    HEAL_AREA_FIXED = auto()
    FORTIFY = auto() # Heal all allies in defined range
    RESTORE_SINGLE = auto()
    RESTORE_ALL_IN_RANGE = auto()
    SILENCE_TARGET = auto()
    SLEEP_TARGET = auto()
    BERSERK_TARGET = auto()
    WARP_ALLY = auto()
    RESCUE_ALLY = auto()
    REWARP_SELF = auto()
    UNLOCK = auto()
    REPAIR_ITEM = auto()
    TORCH_STAFF = auto()
    BARRIER = auto()
    HAMMERNE = auto()
    THIEF_STAFF = auto()
    # TODO: Add any other specific Thracia 776 staff effects

class UsableEffectType(Enum):
    HEAL_FIXED_HP = auto()
    HEAL_MAX_HP = auto()
    ANTITOXIN = auto()
    PURE_WATER = auto()
    TORCH_ITEM = auto()
    LOCKPICK = auto()
    CHEST_KEY = auto()
    DOOR_KEY = auto()
    BRIDGE_KEY = auto()
    STAMINA_DRINK = auto()
    ENERGY_RING = auto() # Permanent STR boost
    SECRET_BOOK = auto() # Permanent SKL boost
    SPEED_RING = auto() # Permanent SPD boost
    GODDESS_ICON = auto() # Permanent LCK boost
    DRACOSHIELD = auto() # Permanent DEF boost
    BODY_RING = auto() # Permanent CON/Build boost
    MAGIC_RING = auto() # Permanent MAG boost
    LIFE_RING = auto() # Permanent Max HP boost
    SKILL_BOOK = auto() # Permanent Weapon Rank EXP boost
    PROMOTION_ITEM = auto()
    STAT_DROP_ITEM = auto()
    MEMBER_CARD = auto()
    LIGHT_RUNE = auto()
    MINE = auto()
    # TODO: Add other specific Thracia 776 consumables

class RangeData:
    def __init__(self, min_range: int, max_range: int):
        # TEST: MinRange must be > 0.
        if min_range <= 0:
            raise ValueError("MinRange must be > 0.")
        # TEST: MaxRange must be >= MinRange.
        if max_range < min_range:
            raise ValueError("MaxRange must be >= MinRange.")
        self.min_range: int = min_range
        self.max_range: int = max_range

    def __str__(self) -> str:
        if self.min_range == self.max_range:
            return str(self.min_range)
        return f"{self.min_range}-{self.max_range}"

class ItemStatBonuses:
    """Direct stat boosts when equipped."""
    def __init__(self,
                 hp_bonus: int = 0,
                 str_bonus: int = 0,
                 mag_bonus: int = 0,
                 skl_bonus: int = 0,
                 spd_bonus: int = 0,
                 def_bonus: int = 0,
                 con_bonus: int = 0, # CON_Bonus in spec, assuming CON
                 luk_bonus: int = 0,
                 mov_bonus: int = 0):
        # TEST: All bonus values must be integers. (Python typing handles this)
        self.hp_bonus: int = hp_bonus
        self.str_bonus: int = str_bonus
        self.mag_bonus: int = mag_bonus
        self.skl_bonus: int = skl_bonus
        self.spd_bonus: int = spd_bonus
        self.def_bonus: int = def_bonus
        self.con_bonus: int = con_bonus
        self.luk_bonus: int = luk_bonus
        self.mov_bonus: int = mov_bonus