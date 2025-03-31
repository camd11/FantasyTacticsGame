import random
from enum import Enum, auto
from .data_structures import Stats, Position, UnitType, UnitState, MovementType
from .items import Item, Weapon, WeaponRank, ItemType

# Placeholder for movement cost data (should be loaded from config/data)
MOVEMENT_COSTS = {
    MovementType.INFANTRY: {'PLAIN': 1, 'FOREST': 2, 'MOUNTAIN': 2, 'RIVER': -1, 'BRIDGE': 1, 'ROAD': 1, 'WALL': -1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 2, 'CLIFF': -1, 'SEA': -1, 'INDOOR_FLOOR': 1},
    MovementType.ARMOR: {'PLAIN': 1, 'FOREST': 2, 'MOUNTAIN': 1, 'RIVER': -1, 'BRIDGE': 1, 'ROAD': 1, 'WALL': -1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 3, 'CLIFF': -1, 'SEA': -1, 'INDOOR_FLOOR': 1},
    MovementType.CAVALRY: {'PLAIN': 1, 'FOREST': 3, 'MOUNTAIN': -1, 'RIVER': -1, 'BRIDGE': 1, 'ROAD': 1, 'WALL': -1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 4, 'CLIFF': -1, 'SEA': -1, 'INDOOR_FLOOR': -1}, # Must dismount
    MovementType.FLYING: {'PLAIN': 1, 'FOREST': 1, 'MOUNTAIN': 1, 'RIVER': 1, 'BRIDGE': 1, 'ROAD': 1, 'WALL': 1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 1, 'CLIFF': 1, 'SEA': 1, 'INDOOR_FLOOR': 1},
    MovementType.PIRATE: {'PLAIN': 1, 'FOREST': 2, 'MOUNTAIN': 2, 'RIVER': 4, 'BRIDGE': 1, 'ROAD': 1, 'WALL': -1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 3, 'CLIFF': -1, 'SEA': 4, 'INDOOR_FLOOR': 1},
    MovementType.BRIGAND: {'PLAIN': 1, 'FOREST': 2, 'MOUNTAIN': 2, 'RIVER': -1, 'BRIDGE': 1, 'ROAD': 1, 'WALL': -1, 'DOOR': 1, 'GATE': 1, 'FORT': 1, 'THRONE': 1, 'HOUSE': 1, 'VILLAGE': 1, 'SHOP': 1, 'ARENA': 1, 'DESERT': 3, 'CLIFF': -1, 'SEA': -1, 'INDOOR_FLOOR': 1},
}
MOVEMENT_TYPE_INFANTRY = MovementType.INFANTRY # Constant for dismounted type

class ClassType(Enum):
    # Placeholder types, expand as needed
    LORD = auto()
    CAVALIER = auto()
    KNIGHT = auto()
    FIGHTER = auto()
    ARCHER = auto()
    MAGE = auto()
    PRIEST = auto()
    THIEF = auto()
    DANCER = auto()
    PEGASUS_KNIGHT = auto()
    WYVERN_RIDER = auto()

class SkillType(Enum):
    COMBAT = auto()
    PASSIVE = auto()
    MAP = auto()

class Skill:
    def __init__(self, name: str, skill_type: SkillType, description: str = ""):
        self.name = name
        self.skill_type = skill_type
        self.description = description

    def __str__(self):
        return self.name

class Inventory:
    def __init__(self, max_items: int = 7): # Thracia inventory limit is 7
        self.items: list[Item] = []
        self.max_items = max_items
        self.equipped_weapon_index: int | None = None

    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.max_items:
            self.items.append(item)
            # Auto-equip first weapon if none equipped
            if isinstance(item, Weapon) and self.equipped_weapon_index is None:
                 self.equip_weapon_by_index(len(self.items) - 1)
            return True
        return False

    def remove_item(self, item_to_remove: Item) -> bool:
        try:
            index_to_remove = self.items.index(item_to_remove)
            del self.items[index_to_remove]
            # If the removed item was equipped, unequip
            if self.equipped_weapon_index == index_to_remove:
                self.equipped_weapon_index = None
            # Adjust equipped index if it was after the removed item
            elif self.equipped_weapon_index is not None and self.equipped_weapon_index > index_to_remove:
                self.equipped_weapon_index -= 1
            return True
        except ValueError:
            return False # Item not found

    def remove_item_by_index(self, index: int) -> Item | None:
        if 0 <= index < len(self.items):
            item = self.items.pop(index)
            # If the removed item was equipped, unequip
            if self.equipped_weapon_index == index:
                self.equipped_weapon_index = None
            # Adjust equipped index if it was after the removed item
            elif self.equipped_weapon_index is not None and self.equipped_weapon_index > index:
                self.equipped_weapon_index -= 1
            return item
        return None

    def get_equipped_weapon(self) -> Weapon | None:
        if self.equipped_weapon_index is not None and 0 <= self.equipped_weapon_index < len(self.items):
            item = self.items[self.equipped_weapon_index]
            if isinstance(item, Weapon):
                return item
        return None

    def equip_weapon_by_index(self, index: int) -> bool:
        if 0 <= index < len(self.items) and isinstance(self.items[index], Weapon):
            self.equipped_weapon_index = index
            return True
        return False

    def equip_weapon(self, weapon_to_equip: Weapon) -> bool:
        try:
            index = self.items.index(weapon_to_equip)
            return self.equip_weapon_by_index(index)
        except ValueError:
            return False

    def has_item_type(self, item_type: ItemType) -> bool:
        return any(item.item_type == item_type for item in self.items)

    def get_item_by_index(self, index: int) -> Item | None:
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def is_full(self) -> bool:
        return len(self.items) >= self.max_items

    def __str__(self):
        return ", ".join(str(item) for item in self.items) if self.items else "Empty"


class Class:
    def __init__(self, name: str, class_type: ClassType, base_stats: Stats, max_stats: Stats,
                 usable_weapons: list[WeaponType], weapon_ranks: dict[WeaponType, WeaponRank],
                 class_skills: list[Skill], movement_type: MovementType,
                 promotes_to: 'Class' | None = None, can_dismount: bool = False,
                 dismounted_stats: Stats | None = None, dismounted_weapons: list[WeaponType] | None = None):
        self.name = name
        self.class_type = class_type
        self.base_stats = base_stats # Base stats for the class itself
        self.max_stats = max_stats
        self.usable_weapons = usable_weapons
        self.weapon_ranks = weapon_ranks # Max ranks for the class
        self.class_skills = class_skills
        self.movement_type = movement_type
        self.promotes_to = promotes_to
        self.can_dismount = can_dismount
        self.dismounted_stats = dismounted_stats # Stat changes when dismounted
        self.dismounted_weapons = dismounted_weapons

    def can_use_weapon_type(self, weapon_type: WeaponType, is_dismounted: bool = False) -> bool:
        """Check if this class can use the specified weapon type (considering dismount)."""
        if is_dismounted and self.can_dismount:
            return weapon_type in (self.dismounted_weapons or [])
        else:
            return weapon_type in self.usable_weapons

    def get_max_weapon_rank(self, weapon_type: WeaponType) -> WeaponRank | None:
        """Get the class's maximum rank with the specified weapon type."""
        return self.weapon_ranks.get(weapon_type)

    def get_movement_cost(self, terrain_type, is_dismounted: bool = False) -> int | None:
        """Get the movement cost for this class on the specified terrain type."""
        current_movement_type = MOVEMENT_TYPE_INFANTRY if is_dismounted else self.movement_type
        cost_map = MOVEMENT_COSTS.get(current_movement_type, {})
        cost = cost_map.get(terrain_type)
        return cost if cost is not None and cost > 0 else None # Return None if impassable (-1 or missing)

    def get_dismounted_class(self) -> 'Class' | None:
        """Get the dismounted version of this class."""
        if not self.can_dismount:
            return None

        # Create a new class representing the dismounted version
        # Note: This is a simplified representation. A better approach might be
        # to have a separate 'DismountedClass' instance linked or modify unit state.
        dismounted = Class(
            name=f"Dismounted {self.name}",
            class_type=self.class_type,
            base_stats=self.dismounted_stats or self.base_stats, # Apply stat changes
            max_stats=self.max_stats,
            usable_weapons=self.dismounted_weapons or [],
            weapon_ranks=self.weapon_ranks, # Ranks usually don't change
            class_skills=self.class_skills,
            movement_type=MOVEMENT_TYPE_INFANTRY, # Dismounted units use infantry movement
            promotes_to=self.promotes_to,
            can_dismount=False, # Can't dismount again
            dismounted_stats=None,
            dismounted_weapons=None
        )
        return dismounted

    def __str__(self):
        return self.name

class Unit:
    def __init__(self, unit_id: str, name: str, unit_type: UnitType, unit_class: Class,
                 base_stats: Stats, growth_rates: Stats, level: int = 1, experience: int = 0,
                 skills: list[Skill] | None = None, pcc: int = 0, movement_stars: int = 0,
                 leadership_stars: int = 0, inventory: list[Item] | None = None,
                 weapon_exp: dict[WeaponType, int] | None = None):
        self.unit_id = unit_id # Unique identifier for the unit
        self.name = name
        self.unit_type = unit_type
        self.unit_class = unit_class
        self.base_stats = base_stats # Personal base stats
        self.current_stats = Stats(**vars(base_stats)) # Working stats, start as copy of base
        self.growth_rates = growth_rates
        self.level = level
        self.experience = experience
        self.inventory = Inventory()
        if inventory:
            for item in inventory:
                self.inventory.add_item(item)

        self.personal_skills = skills or []
        self.all_skills = list(set(self.personal_skills + self.unit_class.class_skills))

        self.fatigue = 0
        self.pcc = pcc # Pursuit Critical Coefficient
        self.movement_stars = movement_stars
        self.leadership_stars = leadership_stars
        self.position: Position | None = None
        self.state = UnitState.NORMAL
        self.is_mounted = unit_class.can_dismount # Start mounted if the class can dismount
        self.has_moved = False
        self.has_acted = False
        self.weapon_exp = weapon_exp or {wt: 0 for wt in WeaponType}
        self.current_weapon_ranks = self._calculate_initial_weapon_ranks()

        self.captured_unit: 'Unit' | None = None # For capture mechanic
        self.rescuing_unit: 'Unit' | None = None # For rescue mechanic

        self.recalculate_stats() # Initial calculation

    def _calculate_initial_weapon_ranks(self) -> dict[WeaponType, WeaponRank]:
        # Start with E rank if usable, unless class specifies higher base
        ranks = {}
        for w_type in self.unit_class.usable_weapons:
            class_max_rank = self.unit_class.get_max_weapon_rank(w_type)
            # TODO: Load initial ranks from unit data if specified, otherwise default to E
            ranks[w_type] = WeaponRank.E # Default starting rank
        return ranks

    def can_use_weapon(self, weapon: Weapon) -> bool:
        """Check if the unit can use the specified weapon."""
        if not self.unit_class.can_use_weapon_type(weapon.weapon_type, not self.is_mounted):
            return False
        current_rank = self.current_weapon_ranks.get(weapon.weapon_type)
        if current_rank is None or current_rank.value < weapon.rank.value:
            return False
        return True

    def equip_weapon(self, weapon: Weapon) -> bool:
        """Equip a weapon from inventory if usable."""
        if self.can_use_weapon(weapon):
            return self.inventory.equip_weapon(weapon)
        return False

    def equip_weapon_by_index(self, index: int) -> bool:
        """Equip a weapon from inventory by index if usable."""
        item = self.inventory.get_item_by_index(index)
        if isinstance(item, Weapon) and self.can_use_weapon(item):
            return self.inventory.equip_weapon_by_index(index)
        return False

    def get_equipped_weapon(self) -> Weapon | None:
        return self.inventory.get_equipped_weapon()

    def get_movement_type(self) -> MovementType:
        """Get the current movement type (handles dismounting)."""
        return MOVEMENT_TYPE_INFANTRY if not self.is_mounted else self.unit_class.movement_type

    def get_movement_points(self) -> int:
        """Get the current movement points."""
        # TODO: Apply status effects (e.g., halved movement when capturing)
        return self.current_stats.movement

    def recalculate_stats(self):
        """Recalculate current stats based on base, class, items, status."""
        # Start with personal base stats
        self.current_stats = Stats(**vars(self.base_stats))

        # Add class base stats (if applicable - Thracia doesn't add class bases directly to unit bases)
        # Instead, class determines caps and weapon ranks.

        # Apply dismount penalties/changes if applicable
        if not self.is_mounted and self.unit_class.can_dismount:
            # Apply stat changes defined in the dismounted_stats of the class
            if self.unit_class.dismounted_stats:
                # This needs careful handling - are they offsets or replacements?
                # Assuming offsets for now, needs verification.
                # Example: self.current_stats.strength += self.unit_class.dismounted_stats.strength
                pass # TODO: Implement dismount stat changes based on Thracia rules

        # Apply status effects (e.g., Sleep sets stats to 0, Capture halves stats)
        if self.state == UnitState.SLEEP:
            self.current_stats.strength = 0
            self.current_stats.magic = 0
            self.current_stats.skill = 0
            self.current_stats.speed = 0
            self.current_stats.defense = 0
        elif self.state == UnitState.CAPTURED or self.rescuing_unit is not None:
            # Halve stats when captured or rescuing (Thracia rule)
            self.current_stats.strength //= 2
            self.current_stats.magic //= 2
            self.current_stats.skill //= 2
            self.current_stats.speed //= 2
            self.current_stats.defense //= 2

        # Apply item bonuses (e.g., equipped shields, rings)
        # TODO: Iterate through inventory for stat-boosting items

        # Ensure stats don't exceed class caps
        for stat_name, max_val in vars(self.unit_class.max_stats).items():
            if hasattr(self.current_stats, stat_name):
                current_val = getattr(self.current_stats, stat_name)
                setattr(self.current_stats, stat_name, min(current_val, max_val))

        # Ensure current HP doesn't exceed max HP
        self.current_stats.current_hp = min(self.current_stats.current_hp, self.current_stats.hp)


    def calculate_attack_speed(self) -> int:
        """Calculate current Attack Speed with equipped weapon."""
        weapon = self.get_equipped_weapon()
        return self.current_stats.calculate_attack_speed(weapon)

    def calculate_avoid(self) -> int:
        """Calculate current Avoid."""
        current_as = self.calculate_attack_speed()
        # Base avoid calculation, CombatSystem adds bonuses
        return self.current_stats.calculate_avoid(current_as)

    def add_experience(self, amount: int):
        """Add experience and handle level ups."""
        if self.level >= 20: # Max level
            return {}

        self.experience += amount
        stat_increases = {}
        while self.experience >= 100:
            if self.level >= 20:
                self.experience = 0 # Cap EXP at max level
                break
            self.experience -= 100
            stat_increases = self.level_up()

        return stat_increases # Return last level up increases

    def level_up(self) -> dict[str, int]:
        """Process a level up, increasing stats based on growth rates."""
        if self.level >= 20:
            return {}

        self.level += 1
        increases = {}

        # Thracia uses 1 RN system
        for stat_name, growth_rate in vars(self.growth_rates).items():
            if stat_name == 'current_hp' or growth_rate <= 0:
                continue

            if random.randint(1, 100) <= growth_rate:
                current_val = getattr(self.base_stats, stat_name)
                max_val = getattr(self.unit_class.max_stats, stat_name)
                if current_val < max_val:
                    setattr(self.base_stats, stat_name, current_val + 1)
                    increases[stat_name] = 1
                else:
                    increases[stat_name] = 0 # Capped
            else:
                increases[stat_name] = 0

        # Update current HP if max HP increased
        if increases.get('hp', 0) > 0:
            self.base_stats.current_hp += increases['hp']

        self.recalculate_stats() # Update current stats after base stats change
        return increases

    def add_weapon_exp(self, amount: int, weapon_type: WeaponType):
        """Add weapon experience and handle rank ups."""
        if weapon_type not in self.current_weapon_ranks:
            return # Cannot gain exp for unusable weapon types

        current_rank = self.current_weapon_ranks[weapon_type]
        max_rank = self.unit_class.get_max_weapon_rank(weapon_type)

        if max_rank is None or current_rank == max_rank or current_rank == WeaponRank.STAR:
            return # Already at max rank or legendary

        self.weapon_exp[weapon_type] = self.weapon_exp.get(weapon_type, 0) + amount

        # Thracia WExp thresholds are 50 per rank up to A
        threshold = 50
        if self.weapon_exp[weapon_type] >= threshold:
            # Rank up!
            next_rank_val = current_rank.value + 1
            if next_rank_val <= max_rank.value:
                self.current_weapon_ranks[weapon_type] = WeaponRank(next_rank_val)
                self.weapon_exp[weapon_type] -= threshold # Reset exp for the new rank
                print(f"{self.name} reached {self.current_weapon_ranks[weapon_type].name} rank in {weapon_type.name}!") # TODO: Use logger/event system

    def add_fatigue(self, amount: int):
        """Add fatigue points."""
        # Leif is exempt
        if self.name == "Leif": # TODO: Use a flag or ID instead of name check
            return
        self.fatigue += amount

    def reset_fatigue(self):
        """Reset fatigue to 0."""
        self.fatigue = 0

    def is_fatigued(self) -> bool:
        """Check if the unit is fatigued (fatigue >= max HP)."""
        # Leif is exempt
        if self.name == "Leif":
             return False
        # TODO: Check if fatigue system is active (starts Chapter 8)
        return self.fatigue >= self.current_stats.hp

    def take_damage(self, amount: int):
        """Apply damage to the unit."""
        self.current_stats.current_hp -= amount
        if self.current_stats.current_hp < 0:
            self.current_stats.current_hp = 0

    def heal(self, amount: int):
        """Heal the unit."""
        self.current_stats.current_hp += amount
        if self.current_stats.current_hp > self.current_stats.hp:
            self.current_stats.current_hp = self.current_stats.hp

    def is_defeated(self) -> bool:
        """Check if the unit is defeated (HP <= 0)."""
        return self.current_stats.current_hp <= 0

    def can_act(self) -> bool:
        """Check if the unit can perform an action."""
        return not self.has_acted and self.state in [UnitState.NORMAL] # Add other valid states

    def can_move(self) -> bool:
        """Check if the unit can move."""
        return not self.has_moved and self.state in [UnitState.NORMAL] # Add other valid states

    def start_turn(self):
        """Reset turn-based flags."""
        self.has_moved = False
        self.has_acted = False
        # TODO: Handle status effect ticks (e.g., poison damage)
        # TODO: Handle terrain healing (forts, thrones)

    def end_turn(self):
        """Mark the unit as having finished their turn."""
        self.has_moved = True
        self.has_acted = True

    def __str__(self):
        pos_str = str(self.position) if self.position else "N/A"
        return f"{self.name} ({self.unit_class.name}) [{pos_str}] HP: {self.current_stats.current_hp}/{self.current_stats.hp}"

# Example Class/Unit definitions (load from data later)
# LORD_CLASS = Class(...)
# LEIF_UNIT = Unit(...)