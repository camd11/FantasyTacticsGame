from typing import List, Dict, Optional, Any

# Type Aliases (as per spec and test placeholders)
ClassID = str
ItemID = str
SkillID = str
MovementTypeID = str  # Placeholder, could be an Enum from map_system later
WeaponTypeID = str    # Placeholder # Should match WeaponType.id
# RankLevel could be an Enum (e.g., E, D, C, B, A, S) or int in a full system.
RankLevel = str # Simplified for now

STAT_KEY_MAP_INPUT_TO_INTERNAL = {
    "HP": "hp", "Strength": "strength", "Magic": "magic", "Skill": "skill",
    "Speed": "speed", "Luck": "luck", "Defense": "defense",
    "Constitution": "constitution", "Movement": "movement"
}

DEFAULT_MAX_STATS = {
    "hp": 80, "strength": 20, "magic": 20, "skill": 20, "speed": 20,
    "luck": 30, "defense": 20, "constitution": 20, "movement": 15
}


class WeaponRankEntry:
    """
    Represents a weapon rank proficiency for a class.
    Based on spec:
    CLASS WeaponRankEntry
        WeaponTypeID WeaponType
        RankLevel InitialRank
        RankLevel MaxRankInClass
    """
    def __init__(self, weapon_type_id: WeaponTypeID, initial_rank: RankLevel, max_rank_in_class: RankLevel):
        # In a full implementation, RankLevel would likely be an Enum or a class
        # with defined progression and comparison logic.
        # Validation (e.g., valid RankLevel values, max_rank >= initial_rank) would go here.
        self.weapon_type_id: WeaponTypeID = weapon_type_id
        self.initial_rank: RankLevel = initial_rank
        self.max_rank_in_class: RankLevel = max_rank_in_class


class GameClass:
    """
    Represents a unit class (job) in the game.
    Stores base stats, max stats, growth rates, skills, and other class-specific information.
    Based on docs/spec/02_CharacterAndClassSystem.md
    """
    def __init__(self,
                 class_id: ClassID,
                 name_str: str, # Renamed to avoid conflict with 'name' attribute if it were a property
                 promotion_info: Dict[str, Any],  # Expected: {"PromotesToClassID": Optional[ClassID], "PromotionItem": Optional[ItemID]}
                 base_stats_dict: Dict[str, int],    # Expected keys: "HP", "Strength", etc.
                 max_stats_dict: Dict[str, int],     # Expected keys: "HP", "Strength", etc.
                 class_growths_dict: Dict[str, int], # Expected keys: "HP", "Strength", etc.
                 class_skills: List[SkillID],
                 movement_type: MovementTypeID,
                 weapon_ranks: List[WeaponRankEntry], # List of WeaponRankEntry objects
                 mounted_info: Dict[str, Any]  # Expected: {"IsMounted": bool, "DismountedClassID": Optional[ClassID]}
                 ):

        if not name_str: # Use the parameter name
            raise ValueError("Class Name must not be empty.")

        self.id: ClassID = class_id
        self.name: str = name_str # Assign to self.name

        # Initialize individual stat attributes (e.g., self.base_hp, self.max_strength, self.growth_magic)
        for input_key, internal_key in STAT_KEY_MAP_INPUT_TO_INTERNAL.items():
            # Base Stats
            setattr(self, f"base_{internal_key}", base_stats_dict.get(input_key, 0))
            # Max Stats (with defaults)
            setattr(self, f"max_{internal_key}", max_stats_dict.get(input_key, DEFAULT_MAX_STATS[internal_key]))
            # Class Growths (Movement growth is included here, defaults to 0 if not specified)
            setattr(self, f"growth_{internal_key}", class_growths_dict.get(input_key, 0))
            
        # Validate MaxStats >= BaseStats for all common stats using the newly set internal attributes
        for internal_stat_key in STAT_KEY_MAP_INPUT_TO_INTERNAL.values():
            base_val = getattr(self, f"base_{internal_stat_key}")
            max_val = getattr(self, f"max_{internal_stat_key}")
            if max_val < base_val:
                raise ValueError(
                    f"MaxStat for {internal_stat_key} ({max_val}) in class {self.id} "
                    f"must be greater than or equal to BaseStat ({base_val})."
                )
        
        # Promotion Info
        self.promotes_to_class_id: Optional[ClassID] = promotion_info.get("PromotesToClassID")
        self.promotion_item: Optional[ItemID] = promotion_info.get("PromotionItem")

        self.class_skills: List[SkillID] = class_skills
        self.movement_type: MovementTypeID = movement_type
        self.weapon_ranks: List[WeaponRankEntry] = weapon_ranks # Assumes WeaponRankEntry objects are passed in

        # Mounted Info
        self.is_mounted: bool = mounted_info.get("IsMounted", False)
        self.dismounted_class_id: Optional[ClassID] = mounted_info.get("DismountedClassID")

        if self.is_mounted and self.dismounted_class_id is None:
            raise ValueError(f"Mounted class '{self.id}' must have a DismountedClassID if IsMounted is True.")