from enum import IntEnum, Enum

class RankLevel(IntEnum):
    """
    Represents the proficiency level for a weapon type.
    Values allow for direct comparison.
    """
    NONE = 0
    E = 1
    D = 2
    C = 3
    B = 4
    A = 5
    S = 6

class WeaponTypeID(Enum):
    """
    Represents the different types of weapons available in the game.
    """
    SWORD = "Sword"
    LANCE = "Lance"
    AXE = "Axe"
    BOW = "Bow"
    FIRE = "Fire"
    THUNDER = "Thunder"
    WIND = "Wind"
    LIGHT = "Light"
    DARK = "Dark"
    STAFF = "Staff"
    # Potentially others like Ballista, etc.

class WeaponRankEntry:
    """
    Represents a class's proficiency with a specific weapon type,
    including its initial and maximum achievable rank within that class.

    Attributes:
        weapon_type (WeaponTypeID): The type of weapon.
        initial_rank (RankLevel): The starting rank for this weapon type in the class.
        max_rank_in_class (RankLevel): The highest rank achievable for this weapon type in the class.
    """
    def __init__(self, weapon_type: WeaponTypeID, initial_rank: RankLevel, max_rank_in_class: RankLevel):
        if not isinstance(weapon_type, WeaponTypeID):
            raise TypeError("weapon_type must be an instance of WeaponTypeID.")
        if not isinstance(initial_rank, RankLevel):
            raise TypeError("initial_rank must be an instance of RankLevel.")
        if not isinstance(max_rank_in_class, RankLevel):
            raise TypeError("max_rank_in_class must be an instance of RankLevel.")

        if initial_rank != RankLevel.NONE and max_rank_in_class != RankLevel.NONE:
            if max_rank_in_class < initial_rank:
                raise ValueError(
                    f"MaxRankInClass ({max_rank_in_class.name}) cannot be less than "
                    f"InitialRank ({initial_rank.name})."
                )

        self._weapon_type = weapon_type
        self._initial_rank = initial_rank
        self._max_rank_in_class = max_rank_in_class

    @property
    def weapon_type(self) -> WeaponTypeID:
        return self._weapon_type

    @property
    def initial_rank(self) -> RankLevel:
        return self._initial_rank

    @property
    def max_rank_in_class(self) -> RankLevel:
        return self._max_rank_in_class

    def __repr__(self):
        return (f"WeaponRankEntry(weapon_type={self.weapon_type.name}, "
                f"initial_rank={self.initial_rank.name}, "
                f"max_rank_in_class={self.max_rank_in_class.name})")