from enum import Enum
from typing import List, Any, Tuple, Optional
from enum import Enum

from .character import Character, UnitStats as CharacterUnitStats # Renamed to avoid clash if needed
from .game_class import GameClass

# Placeholder type aliases
ItemID = str # Should match Item.id
StatusEffect = Any # Placeholder for status effect system
Point = Tuple[int, int] # For (X, Y) coordinates
MapType = Any # Actual: from src.map_system.map import Map


class UnitState(Enum):
    """
    Represents the current state of a unit on the map.
    """
    IDLE = 0      # Has not acted this turn
    MOVED = 1     # Has moved but not acted
    ACTED = 2     # Has completed their action for the turn
    GREYED_OUT = 3 # Cannot act (e.g. status effect, already acted)
    RESCUED = 4   # Unit is being rescued
    RESCUING = 5  # Unit is rescuing another
    DEFEATED = 6  # Unit has been defeated


class UnitInstance:
    """
    Represents a unit currently active on the game map.
    It holds the character's data, their current class, stats, state, and inventory.
    """
    def __init__(self,
                 character_data: Character,
                 initial_position: Point,
                 initial_class: GameClass,
                 is_player_unit: bool = True):

        if not isinstance(character_data, Character):
            raise TypeError("character_data must be an instance of Character.")
        if not isinstance(initial_class, GameClass):
            raise TypeError("initial_class must be an instance of GameClass.")

        self.character_data: Character = character_data
        self.current_class: GameClass = initial_class
        
        self.current_level: int = self.character_data.level
        self.current_experience: int = self.character_data.experience_points
        
        # Base stats for the current class (e.g., final max HP, strength, magic)
        # These are populated by _recalculate_stats
        self.stat_hp: int = 0
        self.stat_strength: int = 0
        self.stat_magic: int = 0
        self.stat_skill: int = 0
        self.stat_speed: int = 0
        self.stat_luck: int = 0
        self.stat_defense: int = 0
        self.stat_constitution: int = 0
        self.stat_movement: int = 0
        
        # Derived combat stats (placeholders for now, calculation needs item/skill system)
        self.combat_attack_power: int = 0
        self.combat_magic_attack_power: int = 0
        self.combat_hit_rate: int = 0
        self.combat_avoid_rate: int = 0
        self.combat_critical_rate: int = 0
        self.combat_attack_speed: int = 0

        self.current_hp: int = 0
        self._recalculate_stats(is_initial_setup=True) # Sets initial stats and current_hp to max

        self.position: Point = initial_position
        self.state: UnitState = UnitState.IDLE
        self.inventory: List[ItemID] = list(self.character_data.initial_inventory)
        self.active_status_effects: List[StatusEffect] = []
        self.is_player_unit: bool = is_player_unit

        self.mounted_class_before_dismount: Optional[GameClass] = None
        if self.current_class.is_mounted:
             self.mounted_class_before_dismount = self.current_class


    def _recalculate_stats(self, is_initial_setup: bool = False) -> None:
        """
        Recalculates the unit's stats based on character_data and current_class.
        Updates current_hp carefully, preserving it relative to max HP changes.
        Also responsible for (eventually) calculating derived combat stats.
        """
        old_max_hp = 0 if is_initial_setup else self.stat_hp # self.stat_hp stores the max HP
        current_hp_value_before_recalc = self.current_hp

        # Get the combined base stats from Character + GameClass (capped by class max)
        # This returns a CharacterUnitStats object (defined in character.py)
        base_stats_bundle: CharacterUnitStats = self.character_data.get_current_stats(self.current_class)

        # Assign these to the UnitInstance's direct stat attributes
        self.stat_hp = base_stats_bundle.hp # This is the new Max HP
        self.stat_strength = base_stats_bundle.strength
        self.stat_magic = base_stats_bundle.magic
        self.stat_skill = base_stats_bundle.skill
        self.stat_speed = base_stats_bundle.speed
        self.stat_luck = base_stats_bundle.luck
        self.stat_defense = base_stats_bundle.defense
        self.stat_constitution = base_stats_bundle.constitution
        self.stat_movement = base_stats_bundle.movement

        # Preserve current_hp relative to max_hp changes
        if is_initial_setup:
            self.current_hp = self.stat_hp # Set to new max HP
        else:
            hp_increase_in_max = self.stat_hp - old_max_hp
            self.current_hp = min(self.stat_hp, current_hp_value_before_recalc + hp_increase_in_max)
        
        self.current_hp = max(0, self.current_hp) # Ensure HP isn't negative

        # Placeholder for derived combat stat calculations
        # These would typically depend on self.stat_strength, items, skills, etc.
        self.combat_attack_power = self.stat_strength # Simplistic placeholder
        self.combat_magic_attack_power = self.stat_magic # Simplistic placeholder
        self.combat_hit_rate = self.stat_skill * 2 + self.stat_luck # Common FE formula part
        self.combat_avoid_rate = self.stat_speed * 2 + self.stat_luck # Common FE formula part
        self.combat_critical_rate = self.stat_skill // 2 # Common FE formula part
        # Attack Speed = Speed - (WeaponWeight - Constitution), if WeaponWeight > Constitution, else Speed
        # For now, simplified:
        self.combat_attack_speed = self.stat_speed


    def take_damage(self, amount: int) -> None:
        if amount < 0:
            # Consider raising ValueError or logging for negative damage attempts
            return
        self.current_hp = max(0, self.current_hp - amount)
        if self.current_hp == 0:
            self.state = UnitState.DEFEATED

    def heal(self, amount: int) -> None:
        if amount < 0:
            # Consider raising ValueError or logging for negative heal attempts
            return
        if self.state == UnitState.DEFEATED:
            return
        self.current_hp = min(self.stat_hp, self.current_hp + amount) # Use self.stat_hp for max

    def add_experience(self, amount: int) -> None:
        if self.state == UnitState.DEFEATED or amount <= 0:
            return
        
        # Delegate experience gain and level-up logic to Character instance
        # Character.add_experience handles EXP accumulation, level increment, and stat growths.
        level_up_stat_increases_history = self.character_data.add_experience(
            amount, self.current_class
        )
        
        # Sync UnitInstance's level and experience with Character's state
        self.current_level = self.character_data.level
        self.current_experience = self.character_data.experience_points

        if level_up_stat_increases_history: # If any level-ups occurred
            self._recalculate_stats() # Recalculate stats to reflect changes

    def can_move_to(self, target_x: int, target_y: int, game_map: MapType) -> bool:
        # Placeholder: Actual implementation requires map data, terrain costs, and pathfinding.
        # Depends on self.stat_movement and game_map properties.
        return False

    def get_attack_range(self, weapon: ItemID) -> List[Point]:
        # Placeholder: Actual implementation requires weapon data (range min/max) from ItemSystem.
        return []

    def get_movement_range(self, game_map: MapType) -> List[Point]:
        # Placeholder: Actual implementation requires map data, terrain costs,
        # self.stat_movement, and a range calculation algorithm (e.g., BFS).
        return []

    def dismount(self, dismounted_class_data: GameClass) -> bool:
        if not isinstance(dismounted_class_data, GameClass):
            raise TypeError("dismounted_class_data must be an instance of GameClass.")

        if self.current_class.is_mounted and \
           self.current_class.dismounted_class_id == dismounted_class_data.id:
            self.mounted_class_before_dismount = self.current_class
            self.current_class = dismounted_class_data
            self._recalculate_stats()
            return True
        return False

    def mount(self, mounted_class_data: GameClass, game_map: Optional[MapType] = None) -> bool:
        if not isinstance(mounted_class_data, GameClass):
            raise TypeError("mounted_class_data must be an instance of GameClass.")

        if game_map and getattr(game_map, 'is_indoors', False): # Assuming MapType might have is_indoors
            return False # Cannot mount indoors

        can_mount_this_class = False
        if not self.current_class.is_mounted and \
           mounted_class_data.is_mounted and \
           self.mounted_class_before_dismount and \
           self.mounted_class_before_dismount.id == mounted_class_data.id:
            can_mount_this_class = True
        
        if can_mount_this_class:
            self.current_class = mounted_class_data
            self._recalculate_stats()
            # self.mounted_class_before_dismount = None # Optional: clear once remounted, or keep for re-dismount logic
            return True
        return False