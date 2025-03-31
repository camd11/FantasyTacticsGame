from enum import Enum, auto

class ItemType(Enum):
    WEAPON = auto()
    STAFF = auto()
    CONSUMABLE = auto()
    PROMOTION = auto()
    KEY = auto()
    SCROLL = auto()
    MISC = auto()

class WeaponType(Enum):
    SWORD = auto()
    LANCE = auto()
    AXE = auto()
    BOW = auto()
    FIRE = auto()
    THUNDER = auto()
    WIND = auto()
    LIGHT = auto()
    DARK = auto()
    STAFF = auto() # Staves are technically weapons in FE

class WeaponRank(Enum):
    E = 1
    D = 2
    C = 3
    B = 4
    A = 5
    S = 6 # Thracia uses A, but S is common in later games, might be useful
    STAR = 7 # For legendary weapons

class Item:
    def __init__(self, name: str, item_type: ItemType, description: str = "",
                 uses: int = -1, max_uses: int = -1, weight: int = 0):
        self.name = name
        self.item_type = item_type
        self.description = description
        self.uses = uses
        self.max_uses = max_uses if max_uses > 0 else uses
        self.weight = weight # Weight is relevant for stealing

    def __str__(self):
        use_str = f" ({self.uses}/{self.max_uses})" if self.max_uses > 0 else ""
        return f"{self.name}{use_str}"

    def use(self):
        """Decrement uses if the item has limited uses."""
        if self.uses > 0:
            self.uses -= 1
        return self.uses > 0 or self.max_uses < 0 # Return True if still usable

    def is_broken(self) -> bool:
        """Check if the item is broken (0 uses)."""
        return self.max_uses > 0 and self.uses <= 0

class Weapon(Item):
    def __init__(self, name: str, weapon_type: WeaponType, might: int, hit: int,
                 critical: int, weight: int, min_range: int, max_range: int,
                 rank: WeaponRank, uses: int, description: str = "",
                 effective_against: list = None, is_magic: bool = False):
        super().__init__(name, ItemType.WEAPON, description, uses, uses, weight)
        self.weapon_type = weapon_type
        self.might = might
        self.hit = hit
        self.critical = critical
        # Weight is inherited from Item
        self.min_range = min_range
        self.max_range = max_range
        self.rank = rank
        self.effective_against = effective_against or []
        self._is_magic = is_magic or weapon_type in [WeaponType.FIRE, WeaponType.THUNDER, WeaponType.WIND, WeaponType.LIGHT, WeaponType.DARK]

    def is_magic(self) -> bool:
        return self._is_magic

    def get_range_str(self) -> str:
        if self.min_range == self.max_range:
            return str(self.min_range)
        else:
            return f"{self.min_range}-{self.max_range}"

class Staff(Item):
    def __init__(self, name: str, rank: WeaponRank, uses: int, description: str = "",
                 range_val: int = 1, weight: int = 0, effect=None):
        # Staves use Magic stat for range in Thracia, but some have fixed range
        super().__init__(name, ItemType.STAFF, description, uses, uses, weight)
        self.weapon_type = WeaponType.STAFF
        self.rank = rank
        self.range = range_val # Can be overridden by calculation using Magic stat
        self.effect = effect # Function or identifier for the staff's effect

    def calculate_range(self, magic_stat: int) -> int:
        # Thracia staff range is typically Mag / 2
        return magic_stat // 2

class Consumable(Item):
    def __init__(self, name: str, uses: int, description: str = "", effect=None):
        super().__init__(name, ItemType.CONSUMABLE, description, uses, uses)
        self.effect = effect # Function or identifier for the consumable's effect

# Example definitions (replace with actual data loading later)
# VULNERARY = Consumable("Vulnerary", 3, "Restores 10 HP.", effect="heal_10")
# IRON_SWORD = Weapon("Iron Sword", WeaponType.SWORD, 5, 90, 0, 3, 1, 1, WeaponRank.E, 45)
# LIGHT_BRAND = Weapon("Light Brand", WeaponType.SWORD, 9, 70, 10, 6, 1, 2, WeaponRank.C, 60, is_magic=True)
# HEAL_STAFF = Staff("Heal", WeaponRank.E, 30, "Restores HP.", effect="heal_target")