from typing import List, Any, Dict
import random

# Placeholder type aliases - these will be defined properly in other modules
PortraitID = Any
ClassID = str  # Should match GameClass.id
SkillID = str  # Should match Skill.id
ItemID = str   # Should match Item.id
SupportData = Any # Placeholder for support system data structure

# ==============================================================================
# --- Placeholder classes (to be replaced by actual imports/definitions later) ---
# --- These are simplified versions for Character class functionality.         ---
# --- The full definitions will reside in their respective files, e.g.,        ---
# --- src.character_system.unit_stats and src.character_system.game_class    ---
# ==============================================================================
class UnitStats: # Placeholder: Full definition in src.character_system.unit_stats
    """
    Helper structure for current/max stats of a unit.
    """
    def __init__(self, hp: int, strength: int, magic: int, skill: int, speed: int,
                 luck: int, defense: int, constitution: int, movement: int):
        self.hp: int = hp
        self.strength: int = strength
        self.magic: int = magic
        self.skill: int = skill
        self.speed: int = speed
        self.luck: int = luck
        self.defense: int = defense
        self.constitution: int = constitution
        self.movement: int = movement
        # In a full implementation, MaxHP might be distinct from HP (e.g. for current HP tracking)
        # For calculated stats, HP represents the maximum HP.

    def __eq__(self, other): # For testing purposes
        if not isinstance(other, UnitStats):
            return NotImplemented
        return (self.hp == other.hp and
                self.strength == other.strength and
                self.magic == other.magic and
                self.skill == other.skill and
                self.speed == other.speed and
                self.luck == other.luck and
                self.defense == other.defense and
                self.constitution == other.constitution and
                self.movement == other.movement)

    def __repr__(self): # For debugging
        return (f"UnitStats(HP={self.hp}, Str={self.strength}, Mag={self.magic}, Skl={self.skill}, "
                f"Spd={self.speed}, Lck={self.luck}, Def={self.defense}, Con={self.constitution}, Mov={self.movement})")

class GameClass: # Placeholder: Full definition in src.character_system.game_class
    """
    Minimal placeholder for a game class, providing necessary attributes
    for Character stat calculation and level up.
    Actual implementation will be in game_class.py.
    """
    def __init__(self, class_id: ClassID, name: str, base_stats: Dict[str, int],
                 max_stats: Dict[str, int], growth_rates: Dict[str, int]):
        self.id: ClassID = class_id
        self.name: str = name

        # These attributes are lowercase, matching Character.STAT_FIELDS for easier getattr access
        self.base_hp: int = base_stats.get("HP", 0)
        self.base_strength: int = base_stats.get("Strength", 0)
        self.base_magic: int = base_stats.get("Magic", 0)
        self.base_skill: int = base_stats.get("Skill", 0)
        self.base_speed: int = base_stats.get("Speed", 0)
        self.base_luck: int = base_stats.get("Luck", 0)
        self.base_defense: int = base_stats.get("Defense", 0)
        self.base_constitution: int = base_stats.get("Constitution", 0)
        self.base_movement: int = base_stats.get("Movement", 0)

        self.max_hp: int = max_stats.get("HP", 80)
        self.max_strength: int = max_stats.get("Strength", 20)
        self.max_magic: int = max_stats.get("Magic", 20)
        self.max_skill: int = max_stats.get("Skill", 20)
        self.max_speed: int = max_stats.get("Speed", 20)
        self.max_luck: int = max_stats.get("Luck", 30)
        self.max_defense: int = max_stats.get("Defense", 20)
        self.max_constitution: int = max_stats.get("Constitution", 20)
        self.max_movement: int = max_stats.get("Movement", 15)

        self.growth_hp: int = growth_rates.get("HP", 0)
        self.growth_strength: int = growth_rates.get("Strength", 0)
        self.growth_magic: int = growth_rates.get("Magic", 0)
        self.growth_skill: int = growth_rates.get("Skill", 0)
        self.growth_speed: int = growth_rates.get("Speed", 0)
        self.growth_luck: int = growth_rates.get("Luck", 0)
        self.growth_defense: int = growth_rates.get("Defense", 0)
        self.growth_constitution: int = growth_rates.get("Constitution", 0)
        self.growth_movement: int = growth_rates.get("Movement", 0) # Class movement growth
# --- End Placeholder classes ---


class Character:
    """
    Represents a specific character in the game, including their personal base stats,
    growth rates, and level.
    The base_stats stored on this object are the character's current personal stats.
    """
    STAT_FIELDS = ["hp", "strength", "magic", "skill", "speed", "luck", "defense", "constitution", "movement"]
    
    # Maps capitalized input keys (from data files/configs) to lowercase internal attribute suffixes
    INPUT_STAT_KEY_MAP = {
        "HP": "hp", "Strength": "strength", "Magic": "magic", "Skill": "skill",
        "Speed": "speed", "Luck": "luck", "Defense": "defense",
        "Constitution": "constitution", "Movement": "movement"
    }

    def __init__(self,
                 character_id: str,
                 name: str,
                 portrait: PortraitID,
                 initial_class_id: ClassID,
                 level: int,
                 base_stats: Dict[str, int],    # Expected keys: "HP", "Strength", etc.
                 growth_rates: Dict[str, int],  # Expected keys: "HP", "Strength", etc.
                 innate_skills: List[SkillID],
                 initial_inventory: List[ItemID],
                 support_data: SupportData):

        if not character_id:
            raise ValueError("CharacterID cannot be empty.")
        if not name:
            raise ValueError("Name cannot be empty.")
        if level < 1:
            raise ValueError("Level cannot be less than 1.")

        # Validate base_stats and growth_rates from input before assignment
        for stat_key_input, val in base_stats.items():
            if val < 0:
                raise ValueError(f"Base stat {stat_key_input} cannot be negative: {val}")
        for stat_key_input, val in growth_rates.items():
            if val < 0:
                raise ValueError(f"Growth rate {stat_key_input} cannot be negative: {val}")

        self.character_id: str = character_id
        self.name: str = name
        self.portrait: PortraitID = portrait
        self.initial_class_id: ClassID = initial_class_id
        self.level: int = level
        self.experience_points: int = 0 # EXP towards next level

        # Personal current stats and growth rates of the character
        # Attributes are named e.g., self.base_hp, self.growth_strength
        for input_key, internal_suffix in self.INPUT_STAT_KEY_MAP.items():
            setattr(self, f"base_{internal_suffix}", base_stats.get(input_key, 0))
            setattr(self, f"growth_{internal_suffix}", growth_rates.get(input_key, 0))
        
        # Ensure all stat fields defined in STAT_FIELDS have a base and growth attribute if not in map
        # This is mostly for safety if INPUT_STAT_KEY_MAP or STAT_FIELDS get out of sync.
        # However, the current INPUT_STAT_KEY_MAP covers all of STAT_FIELDS.
        for stat_field_lower in self.STAT_FIELDS:
            if not hasattr(self, f"base_{stat_field_lower}"):
                 setattr(self, f"base_{stat_field_lower}", 0)
            if not hasattr(self, f"growth_{stat_field_lower}"):
                 setattr(self, f"growth_{stat_field_lower}", 0)


        self.innate_skills: List[SkillID] = innate_skills
        self.initial_inventory: List[ItemID] = initial_inventory
        self.character_support_data: SupportData = support_data

    def get_current_stats(self, game_class: GameClass) -> UnitStats:
        """
        Calculates the character's current stats when in the given game_class.
        Stats are character's personal stats + class base stats, capped by class maximums.
        """
        if not isinstance(game_class, GameClass):
            raise TypeError("game_class must be an instance of GameClass.")

        current_stats_args = {}
        for stat_key_lower in self.STAT_FIELDS: # e.g., "hp", "strength"
            personal_stat_val = getattr(self, f"base_{stat_key_lower}")
            # Assumes game_class has attributes like game_class.base_hp, game_class.max_hp (lowercase)
            class_base_val = getattr(game_class, f"base_{stat_key_lower}")
            class_max_val = getattr(game_class, f"max_{stat_key_lower}")

            calculated_stat = personal_stat_val + class_base_val
            current_stats_args[stat_key_lower] = min(calculated_stat, class_max_val)
        
        return UnitStats(**current_stats_args) # Assumes UnitStats.__init__ takes lowercase stat names

    def level_up(self, game_class: GameClass, fixed_growths: Dict[str, bool] = None) -> Dict[str, int]:
        """
        Levels up the character by one level.
        Applies growth rates to personal stats, considering class growth bonuses
        and ensuring stats (personal + class base) do not exceed class maximums.
        Movement can also grow if its growth rate is non-zero.

        Args:
            game_class: The GameClass the character is currently in.
            fixed_growths: Optional dictionary to force specific stat increases for testing
                           (e.g., {"hp": True, "strength": False}). Keys should be lowercase.

        Returns:
            A dictionary indicating which stats increased (e.g., {"hp": 1, "strength": 0}).
        """
        if not isinstance(game_class, GameClass):
            raise TypeError("game_class must be an instance of GameClass.")

        self.level += 1
        # self.experience_points = 0 # This is handled by the add_experience method

        stat_increases = {stat_key_lower: 0 for stat_key_lower in self.STAT_FIELDS}

        # Define a helper to process each stat growth
        def _try_grow_stat_internal(stat_key_lower: str):
            personal_base_attr = f"base_{stat_key_lower}"
            personal_growth_attr = f"growth_{stat_key_lower}"
            
            # Assumes game_class has attributes like game_class.base_hp, game_class.max_hp, game_class.growth_hp
            class_base_attr = f"base_{stat_key_lower}"
            class_max_attr = f"max_{stat_key_lower}"
            class_growth_attr = f"growth_{stat_key_lower}"
            
            current_personal_stat = getattr(self, personal_base_attr)
            class_base_stat = getattr(game_class, class_base_attr)
            class_max_stat = getattr(game_class, class_max_attr)

            # If already at cap (personal + class base >= class max), no growth possible for this stat
            if current_personal_stat + class_base_stat >= class_max_stat:
                return

            total_growth_rate = getattr(self, personal_growth_attr) + getattr(game_class, class_growth_attr)
            
            grew: bool
            if fixed_growths and stat_key_lower in fixed_growths: # fixed_growths keys are lowercase
                grew = fixed_growths[stat_key_lower]
            else:
                grew = random.randint(1, 100) <= total_growth_rate
            
            if grew:
                setattr(self, personal_base_attr, current_personal_stat + 1)
                stat_increases[stat_key_lower] = 1
                # Double check cap after growth.
                # This ensures the personal stat itself doesn't cause an overflow if class_base is 0,
                # and correctly caps personal_stat relative to class_max and class_base.
                if getattr(self, personal_base_attr) + class_base_stat > class_max_stat:
                     setattr(self, personal_base_attr, class_max_stat - class_base_stat)

        for stat_key_lower in self.STAT_FIELDS:
            _try_grow_stat_internal(stat_key_lower)
        
        return stat_increases

    def add_experience(self, amount: int, game_class: GameClass, fixed_growths: Dict[str, bool] = None) -> List[Dict[str, int]]:
        """
        Adds experience points to the character. If EXP reaches 100,
        the character levels up. Can trigger multiple level ups.

        Args:
            amount: The amount of experience to add.
            game_class: The current GameClass of the character for level up.
            fixed_growths: Optional dictionary to force specific stat increases for testing,
                           passed to level_up.

        Returns:
            A list of dictionaries, where each dictionary represents stat increases
            from a level up. Empty if no level up occurred.
        """
        if amount <= 0:
            return []

        self.experience_points += amount
        level_up_stats_history = []

        while self.experience_points >= 100:
            # Max level cap (e.g., 20 or 30, depends on game rules, not enforced here yet)
            # For now, assume level can go up indefinitely or capped elsewhere.
            self.experience_points -= 100
            stat_increases = self.level_up(game_class, fixed_growths=fixed_growths) # Pass fixed_growths
            level_up_stats_history.append(stat_increases)
            if not any(stat_increases.values()): # Stop if a level up yields no stats (e.g. all capped)
                # This condition might need refinement based on game rules for "empty" level ups.
                # If exp should still be consumed, this break might be removed.
                pass # Continue leveling if EXP allows, even if stats are capped.

        return level_up_stats_history