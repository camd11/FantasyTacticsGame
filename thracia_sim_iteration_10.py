# -*- coding: utf-8 -*-
"""
thracia_sim_iteration_10.py

A text-based tactical RPG simulation inspired by Fire Emblem: Thracia 776.
This version (Iteration 10) includes:
- Grid map with terrain effects (movement cost, def/avo bonus)
- Units with detailed stats (HP, Str, Mag, Skl, Spd, Lck, Def, Res, Con, Mov, PCC, Ldr*)
- Inventory system with Weapons (durability, crit) and Consumables
- Turn-based combat system including:
    - Attack, Counterattack, Follow-up attacks (based on Attack Speed)
    - Weapon Triangle (Sword > Axe > Lance > Sword)
    - Critical Hits (Base + PCC bonus vs Crit Avoid)
    - Terrain combat bonuses
- Skills: Wrath, Vantage, Adept (basic implementation)
- Capture mechanic: CON check, halved stats for captor, carrying penalties, take/release captive
- Fatigue system: Accumulates per action, exhausted units cannot act
- Leadership system: Aura bonuses to Hit/Avoid based on nearby leaders
- Event system: Handles house visits and turn-based reinforcements
- AI: Heuristic-based decision making, basic pathfinding, awareness of terrain/skills
- Objective: Leif must escape the map
- Text-based command interface
"""

import math
import random
import os
import collections
import copy

# --- Constants ---
MAP_WIDTH = 15
MAP_HEIGHT = 15
EMPTY_TILE = '.' # Plains
FOREST_SYMBOL = '^'
FORT_SYMBOL = '+'
HOUSE_SYMBOL = 'H' # Visitable House
VISITED_HOUSE_SYMBOL = 'h' # Visited House
ESCAPE_SYMBOL = 'X' # Escape Point
OBSTACLE_SYMBOL = '#' # Wall/Impassable
PLAYER_SYMBOL = 'P' # Base symbol
ENEMY_SYMBOL = 'E'  # Base symbol
CAPTURING_SYMBOL_SUFFIX = '+' # Symbol for units carrying another

FOLLOW_UP_THRESHOLD = 4 # Attacker AS must be this much higher to double
INVENTORY_SIZE = 7 # Standard inventory size

# Weapon Triangle Bonuses
WT_BONUS_MT = 1
WT_BONUS_HIT = 10

# Leadership Constants
LEADERSHIP_RANGE = 3 # How many tiles away leadership affects allies
LEADERSHIP_BONUS_PER_STAR = 3 # Bonus to Hit and Avoid per star

# Skill Constants (used as identifiers)
SKILL_WRATH = "Wrath"
SKILL_VANTAGE = "Vantage"
SKILL_ADEPT = "Adept"

# --- Terrain Data Definition ---
# Defines properties for each terrain type on the map.
TERRAIN_DATA = {
    EMPTY_TILE: {'name': 'Plains', 'move_cost': 1, 'defense': 0, 'avoid': 0, 'is_passable': True},
    FOREST_SYMBOL: {'name': 'Forest', 'move_cost': 2, 'defense': 1, 'avoid': 20, 'is_passable': True},
    FORT_SYMBOL: {'name': 'Fort', 'move_cost': 1, 'defense': 2, 'avoid': 30, 'is_passable': True},
    HOUSE_SYMBOL: {'name': 'House', 'move_cost': 1, 'defense': 0, 'avoid': 0, 'is_passable': True},
    VISITED_HOUSE_SYMBOL: {'name': 'Visited', 'move_cost': 1, 'defense': 0, 'avoid': 0, 'is_passable': True},
    OBSTACLE_SYMBOL: {'name': 'Wall', 'move_cost': 99, 'defense': 0, 'avoid': 0, 'is_passable': False},
    ESCAPE_SYMBOL: {'name': 'Escape', 'move_cost': 1, 'defense': 0, 'avoid': 0, 'is_passable': True},
}

# --- Default Map Layout (Approx. Thracia Ch 1) ---
# Defines the initial terrain layout. Stored as list of lists for mutability (houses).
DEFAULT_MAP_LAYOUT = [
    list("^^.....H.H....."), # 0 Y=0 (Top)
    list("^..D.T........X"), # 1 Y=1
    list("^^..###........"), # 2 Y=2
    list("...#...#......."), # 3 Y=3
    list("..##...##......"), # 4 Y=4
    list("..............."), # 5 Y=5
    list("....#...#...H.."), # 6 Y=6
    list("...##...##..b.."), # 7 Y=7
    list("............b.."), # 8 Y=8
    list("..............."), # 9 Y=9
    list("......++++....."), # 10 Y=10
    list("..H...++++...E."), # 11 Y=11
    list("......W....O.H."), # 12 Y=12
    list("...........L..."), # 13 Y=13
    list("..........H...."), # 14 Y=14 (Bottom)
#        012345678901234 <- X Indices
]
# Dynamically set Map Height/Width based on layout
MAP_HEIGHT = len(DEFAULT_MAP_LAYOUT)
MAP_WIDTH = len(DEFAULT_MAP_LAYOUT[0])

# --- Item Base Classes ---
class Item:
    """Base class for all items in inventory."""
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
    def __str__(self):
        return self.name

class Weapon(Item):
    """Represents equippable weapons with combat stats and durability."""
    def __init__(self, name, might, weight, hit, crit, wpn_range, wpn_type, max_uses, description=""):
        super().__init__(name, description)
        self.might = might        # Base damage bonus
        self.weight = weight      # Affects Attack Speed penalty
        self.hit = hit            # Base hit rate %
        self.crit = crit          # Base critical hit bonus %
        self.range = wpn_range    # List/Tuple of attack ranges (e.g., [1] for melee, [2] for bow, [1,2] for hand axe)
        self.type = wpn_type      # String identifier (e.g., 'Sword', 'Axe', 'Lance', 'Bow', 'Tome')
        self.max_uses = max_uses  # Maximum durability (-1 for infinite)
        self.uses = max_uses      # Current durability

    def is_physical(self):
        """Checks if the weapon deals physical damage (vs magical)."""
        return self.type in ['Sword', 'Axe', 'Lance', 'Bow']

    def use(self):
        """Decrements weapon uses. Returns False if broken before use, True otherwise."""
        if self.uses == -1: # Indestructible
            return True
        if self.uses > 0:
            self.uses -= 1
            return True
        return False # Weapon was already broken or just broke

    def is_broken(self):
        """Checks if the weapon has 0 uses left."""
        return self.uses == 0

    def __str__(self):
        """String representation including uses and key stats."""
        uses_str = f"({self.uses}/{self.max_uses})" if self.max_uses != -1 else "(Inf)"
        return f"{self.name} {uses_str} [Mt:{self.might} Wt:{self.weight} Hit:{self.hit} Crit:{self.crit} Rng:{self.range}]"

class Consumable(Item):
    """Represents single-use items like Vulneraries or Stat Boosters."""
    def __init__(self, name, effect_type, power, description=""):
        super().__init__(name, description)
        self.effect_type = effect_type # String identifier for the effect (e.g., 'heal', 'stat_spd')
        self.power = power             # Magnitude of the effect (e.g., 10 HP for heal, +2 for stat boost)

    def apply_effect(self, target_unit):
        """Applies the item's effect to the target unit. Handled by Unit.use_item for stat boosters."""
        if self.effect_type == 'heal':
            healed = target_unit.heal(self.power)
            print(f"Recovered {healed} HP.")
            return True
        # Stat boosters are handled directly in Unit.use_item to modify base stats
        if self.effect_type.startswith('stat_'):
            print("DEBUG: apply_effect called for stat booster - should be handled by Unit.use_item")
            return True # Indicate success, but logic is elsewhere
        print(f"ERROR: Unknown effect type in Consumable.apply_effect: {self.effect_type}")
        return False

    def __str__(self):
        """String representation showing the effect."""
        return f"{self.name} [{self.effect_type.capitalize()} {self.power}]"

# --- Default Item Instances ---
# Create instances of common items used in setup. Use deepcopy when adding to inventories.
IRON_SWORD = Weapon("Iron Sword", 5, 7, 90, 0, [1], 'Sword', 40)
STEEL_SWORD = Weapon("Steel Sword", 8, 12, 75, 0, [1], 'Sword', 30)
IRON_LANCE = Weapon("Iron Lance", 7, 10, 80, 0, [1], 'Lance', 40)
IRON_AXE = Weapon("Iron Axe", 8, 12, 70, 0, [1], 'Axe', 40)
STEEL_AXE = Weapon("Steel Axe", 11, 15, 60, 0, [1], 'Axe', 30)
PUGI = Weapon("Pugi", 10, 8, 80, 20, [1, 2], 'Axe', 50, "Osian's personal axe.")
IRON_BOW = Weapon("Iron Bow", 6, 5, 85, 5, [2], 'Bow', 40)
VULNERARY = Consumable("Vulnerary", 'heal', 10, "Restores 10 HP.")
SPEED_RING = Consumable("Speed Ring", 'stat_spd', 2, "Permanently increases Speed by 2.")


# --- Unit Class ---
class Unit:
    """Represents a character unit on the map."""
    def __init__(self, name, symbol, team, max_hp, strength, magic, skill, speed, luck, defense, resistance, constitution, move, pcc, leadership_stars, x, y, initial_inventory=None, required_to_escape=False, initial_skills=None):
        self.name = name                    # Unit's name
        self.symbol = symbol                # Map symbol (base)
        self.team = team                    # 'Player' or 'Enemy'

        # --- Base Stats (Immutable after init, unless stat boosters used) ---
        self._base_max_hp = max_hp
        self._base_strength = strength
        self._base_magic = magic
        self._base_skill = skill
        self._base_speed = speed
        self._base_luck = luck
        self._base_defense = defense
        self._base_resistance = resistance
        self._base_constitution = constitution # Build (affects AS penalty, Capture)
        self._base_move = move             # Movement range

        self.pcc = pcc                      # Pursuit Critical Coefficient (Thracia specific)
        self.leadership_stars = leadership_stars # Number of stars for leadership aura

        # --- Current State ---
        self.hp = max_hp                    # Current Hit Points
        self.x = x                          # Current X coordinate
        self.y = y                          # Current Y coordinate

        # Inventory
        self.inventory = [None] * INVENTORY_SIZE # Fixed size list for items
        self._equipped_weapon_index = -1          # Index of equipped weapon in inventory (-1 = none)
        if initial_inventory: # Populate initial items safely
            for i, item in enumerate(initial_inventory):
                if i < INVENTORY_SIZE:
                    self.inventory[i] = copy.deepcopy(item) # Ensure each unit gets unique item instances

        # Status Flags / Trackers
        self.is_alive = True                # Is the unit currently active?
        self.has_moved = False              # Has the unit moved this turn?
        self.has_acted = False              # Has the unit performed an action (attack, wait, use, etc.) this turn?
        self.is_capturing = False           # Is the unit currently carrying another unit?
        self.captured_unit = None           # Reference to the unit being carried (if is_capturing)
        self.is_captured = False            # Is the unit currently being carried by another?
        self.has_escaped = False            # Has the unit escaped the map?
        self.required_to_escape = required_to_escape # Is this unit (e.g., Leif) required for victory?
        self.fatigue = 0                    # Current fatigue level
        self.skills = set(initial_skills) if initial_skills else set() # Set of skill identifiers (strings)
        self.is_exhausted = False           # Flag set if fatigue >= max_hp at start of turn

    # --- Effective Stats Properties ---
    # These calculate the unit's current stats, considering penalties like Capture.
    @property
    def max_hp(self): return self._base_max_hp
    @property
    def strength(self): return math.floor(self._base_strength / 2) if self.is_capturing else self._base_strength
    @property
    def magic(self): return math.floor(self._base_magic / 2) if self.is_capturing else self._base_magic
    @property
    def skill(self): return math.floor(self._base_skill / 2) if self.is_capturing else self._base_skill
    @property
    def speed(self): return math.floor(self._base_speed / 2) if self.is_capturing else self._base_speed
    @property
    def luck(self): return self._base_luck # Luck not halved when capturing
    @property
    def defense(self): return math.floor(self._base_defense / 2) if self.is_capturing else self._base_defense
    @property
    def resistance(self): return math.floor(self._base_resistance / 2) if self.is_capturing else self._base_resistance
    @property
    def constitution(self): return self._base_constitution # CON not halved
    @property
    def move(self): return math.floor(self._base_move / 2) if self.is_capturing else self._base_move

    def get_base_stat(self, stat_name):
        """Helper to get base stat value for display purposes."""
        return getattr(self, f"_base_{stat_name}", getattr(self, stat_name, 0)) # Fallback to current if _base doesn't exist (e.g. pcc)

    # --- Inventory Management Methods ---
    @property
    def equipped_weapon(self):
        """Returns the currently equipped Weapon instance, or None if none/broken."""
        if 0 <= self._equipped_weapon_index < INVENTORY_SIZE:
            item = self.inventory[self._equipped_weapon_index]
            if isinstance(item, Weapon) and not item.is_broken():
                return item
        return None

    def get_item(self, index):
        """Gets the item at a specific inventory index (0-based)."""
        if 0 <= index < INVENTORY_SIZE:
            return self.inventory[index]
        return None

    def add_item(self, item_to_add):
        """Adds an item to the first empty inventory slot. Returns True on success."""
        for i in range(INVENTORY_SIZE):
            if self.inventory[i] is None:
                self.inventory[i] = item_to_add
                print(f"{self.name} obtained {item_to_add.name}.")
                return True
        print(f"{self.name}'s inventory is full!")
        return False

    def remove_item(self, index):
        """Removes and returns the item from a slot. Unequips if it was equipped."""
        if 0 <= index < INVENTORY_SIZE and self.inventory[index] is not None:
            removed_item = self.inventory[index]
            self.inventory[index] = None
            # If equipped weapon was removed, clear equipped index
            if self._equipped_weapon_index == index:
                self._equipped_weapon_index = -1
            return removed_item
        return None

    def equip_item(self, index):
        """Equips the weapon at the given inventory index. Does not cost an action."""
        item = self.get_item(index)
        if item and isinstance(item, Weapon):
            if item.is_broken():
                print(f"{item.name} is broken.")
                return False
            self._equipped_weapon_index = index
            print(f"{self.name} equipped {item.name}.")
            return True
        elif item:
            print(f"{item.name} is not a weapon.")
            return False
        else:
            print(f"No item in slot {index + 1}.")
            return False

    def use_item(self, index):
        """Uses a consumable item at the index. Costs an action. Returns True on success."""
        if not self.can_act():
            print(f"{self.name} cannot act.")
            return False
        item = self.get_item(index)
        if item and isinstance(item, Consumable):
            success = False
            if item.effect_type.startswith('stat_'): # Handle stat boosters separately to modify base stats
                stat_to_boost = item.effect_type.split('_')[1]
                base_stat_attr = f"_base_{stat_to_boost}"
                if hasattr(self, base_stat_attr):
                    current_base = getattr(self, base_stat_attr)
                    setattr(self, base_stat_attr, current_base + item.power)
                    print(f"{self.name} used {item.name}! {stat_to_boost.capitalize()} +{item.power} (Base {current_base} -> {getattr(self, base_stat_attr)}).")
                    success = True
                else:
                    print(f"ERROR: Invalid base stat attribute for boost: {base_stat_attr}")
            elif item.apply_effect(self): # Handle other effects like 'heal'
                success = True

            if success:
                self.inventory[index] = None # Remove used item
                self.set_acted() # Using item costs action/fatigue
                return True
            else:
                print(f"Failed to use {item.name}.")
                return False
        elif item:
            print(f"{item.name} is not a usable item.")
            return False
        else:
            print(f"No item in slot {index + 1}.")
            return False

    def drop_item(self, index):
        """Drops an item from inventory. Costs an action. Returns True on success."""
        if not self.can_act():
            print(f"{self.name} cannot act.")
            return False
        item = self.remove_item(index)
        if item:
            print(f"{self.name} dropped {item.name}.")
            self.set_acted() # Dropping costs action/fatigue
            return True
        else:
            print(f"No item in slot {index + 1}.")
            return False

    # --- Calculated Combat Stats Properties ---
    @property
    def attack_speed(self):
        """Calculates Attack Speed (AS = Effective Speed - Weapon Weight Penalty)."""
        weapon = self.equipped_weapon
        weapon_weight = weapon.weight if weapon else 0
        # Weight Penalty = max(0, Weapon Weight - Constitution)
        penalty = max(0, weapon_weight - self.constitution) # Uses base CON
        # AS uses effective speed (halved if capturing)
        return max(0, self.speed - penalty)

    @property
    def attack_power(self):
        """Calculates base Attack Power (Effective Str/Mag + Weapon Might)."""
        weapon = self.equipped_weapon
        if not weapon: return 0
        # Uses effective Str/Mag (halved if capturing)
        base_stat = self.strength if weapon.is_physical() else self.magic
        return base_stat + weapon.might

    @property
    def hit_rate(self):
        """Calculates base Hit Rate (Factors in Skl, Lck, Weapon Hit). Leadership/WT added in combat."""
        weapon = self.equipped_weapon
        if not weapon: return 0
        # Uses effective Skill (halved if capturing)
        return weapon.hit + (self.skill * 2) + math.floor(self.luck / 2)

    @property
    def avoid(self):
        """Calculates base Avoid (Factors in AS, Lck). Terrain/Leadership added in combat."""
        # Uses calculated Attack Speed (which uses effective Spd) and base Luck
        return (self.attack_speed * 2) + self.luck

    @property
    def crit_rate_base(self):
        """Calculates base Crit rate (Factors in Skl, Weapon Crit). PCC added in combat."""
        weapon = self.equipped_weapon
        if not weapon: return 0
        # Uses effective Skill (halved if capturing)
        base_crit = math.floor(self.skill / 2) + weapon.crit
        return max(0, base_crit)

    @property
    def crit_avoid(self):
        """Calculates Crit Avoid (usually just Luck)."""
        return self.luck # Uses base Luck

    @property
    def attack_range(self):
        """Gets attack range list from equipped weapon."""
        weapon = self.equipped_weapon
        return weapon.range if weapon else []

    # --- Action and Status Methods ---
    def set_acted(self):
        """Marks the unit as having acted and increments fatigue. Called by action handlers."""
        if not self.has_acted:
            self.has_acted = True
            self.fatigue += 1
            # Optional: More detailed fatigue message
            # print(f"({self.name} fatigue +1 -> {self.fatigue}/{self.max_hp})")

    def heal(self, amount):
        """Heals the unit up to max HP, returns amount healed."""
        needed = self.max_hp - self.hp
        heal_amount = min(amount, needed)
        self.hp += heal_amount
        return heal_amount

    def take_damage(self, final_damage):
        """Applies final calculated damage (after mitigation). Called by _resolve_attack."""
        if not self.is_alive or self.is_captured: return 0
        actual_damage = max(0, final_damage)
        self.hp -= actual_damage
        # Combat log prints damage taken, this just confirms when unit falls
        if self.hp <= 0:
             self.hp = 0
             print(f" -> {self.name} has fallen!") # Indicate consequence of damage
        return actual_damage

    def can_act(self):
        """Checks if the unit can perform an action this turn."""
        return self.is_alive and not self.has_acted and not self.is_captured and not self.has_escaped and not self.is_exhausted

    def wait(self):
        """Performs the Wait action."""
        if self.can_act():
            print(f"{self.name} waits.")
            self.set_acted() # Waiting costs action/fatigue
        else:
            print(f"{self.name} cannot wait.")

    def reset_turn(self):
        """Resets turn-based flags at the start of the unit's phase."""
        self.has_moved = False
        self.has_acted = False
        self.is_exhausted = False # Cleared at start of turn (check happens before this)

    # --- Capture State Methods ---
    def _become_captured(self, captor):
        """Sets state when this unit is captured."""
        self.hp = 0 # Captured units have 0 effective HP
        self.is_captured = True
        self.x, self.y = -1, -1 # Remove from map coordinates
        # Reset temporary statuses? Fatigue? TBD.
        print(f"{self.name} has been captured by {captor.name}!")

    def _become_captor(self, captive):
        """Sets state when this unit captures another."""
        self.is_capturing = True
        self.captured_unit = captive
        print(f"{self.name} is now carrying {captive.name}.")

    def release_captive(self, game, target_x, target_y):
        """Releases the carried unit. Returns True on success. Caller handles action cost."""
        if not self.is_capturing or not self.captured_unit: return False
        captive = self.captured_unit
        # Place captive on map
        captive.x, captive.y = target_x, target_y
        captive.hp = 1 # Recover 1 HP
        captive.is_captured = False
        captive.has_acted = True # Cannot act same turn they are released
        print(f"{captive.name} was released at ({target_x}, {target_y}) with 1 HP.")
        # Clear captor state
        self.is_capturing = False
        self.captured_unit = None
        return True

    def take_captive_item(self, captive_slot_index):
        """Takes an item from captive. Returns True on success. Caller handles action cost."""
        if not self.is_capturing or not self.captured_unit: return False
        captive = self.captured_unit
        item_to_take = captive.get_item(captive_slot_index)

        if not item_to_take:
            print(f"{captive.name} has no item in slot {captive_slot_index + 1}.")
            return False

        # Attempt to add a copy to own inventory, remove original from captive if successful
        temp_item_copy = copy.deepcopy(item_to_take)
        if self.add_item(temp_item_copy):
            captive.remove_item(captive_slot_index) # Remove original
            print(f"{self.name} took {item_to_take.name} from {captive.name}.")
            return True
        else:
            # add_item prints inventory full message
            return False

    # --- Escape Method ---
    def escape(self):
        """Handles the unit escaping. Returns True on success. Caller handles action cost."""
        self.has_escaped = True
        self.x, self.y = -1, -1 # Remove from map
        print(f"{self.name} has escaped!")
        # Handle dropping captive if carrying
        if self.is_capturing:
             print(f"{self.name} leaves {self.captured_unit.name} behind!")
             if self.captured_unit:
                 self.captured_unit.is_captured = False
                 self.captured_unit.is_alive = False # Mark as removed from play
             self.is_capturing = False
             self.captured_unit = None
        return True

    # --- String Representation ---
    def __str__(self):
        """Provides a concise summary string for the unit."""
        # Determine primary status
        if self.is_exhausted: status = "[Exh]"
        elif self.has_escaped: status = "[Esc]"
        elif self.is_captured: status = "[Cap]"
        elif not self.is_alive: status = "[Def]"
        else: status = f"[{self.hp}/{self.max_hp}HP]"
        # Add secondary statuses/info
        cap_status = " <Carry>" if self.is_capturing else ""
        fatigue_status = f"(FTG:{self.fatigue})"
        skill_str = f" Skl:{','.join(sorted(list(self.skills)))}" if self.skills else "" # Sort skills for consistency
        return f"{self.name}({self.symbol}) {status}{cap_status}{fatigue_status}{skill_str}"


# --- Event System Class ---
class EventManager:
    """Manages turn-based and location-based events like reinforcements and visits."""
    def __init__(self, game_instance):
        self.game = game_instance # Reference to the main game object
        self.turn_events = {}      # { turn_number: [list of event dicts] }
        self.visit_events = {}     # { (x, y): event_dict }

    def register_reinforcement(self, turn, template, coords):
        """Registers a reinforcement event for a specific turn."""
        if turn not in self.turn_events: self.turn_events[turn] = []
        self.turn_events[turn].append({
            'type': 'reinforcement',
            'template': template, # Unit template dict
            'coords': coords     # List of (x, y) spawn points
        })

    def register_house_visit(self, x, y, item_reward=None, message=None):
        """Registers a visit event for a specific house coordinate."""
        self.visit_events[(x, y)] = {
            'type': 'visit',
            'item': item_reward, # Item instance or None
            'message': message or ("...It seems empty." if not item_reward else None), # Default message
            'visited': False     # Tracks if this specific house has been visited
        }

    def trigger_turn_events(self, turn_number):
        """Triggers all events scheduled for the current turn number."""
        if turn_number in self.turn_events:
            print(f"--- Events Occurring (Turn {turn_number}) ---")
            events_to_trigger = self.turn_events.pop(turn_number) # Remove to prevent re-triggering
            for event in events_to_trigger:
                if event['type'] == 'reinforcement':
                    self._handle_reinforcement_event(event)
                # Add other event types here (e.g., map changes, status effects)

    def trigger_visit_event(self, visiting_unit, x, y):
        """Triggers a visit event if available at the coords. Returns True if event triggered."""
        coord = (x, y)
        if coord in self.visit_events and not self.visit_events[coord]['visited']:
            event = self.visit_events[coord]
            print(f"{visiting_unit.name} visits the house...")
            if event['message']:
                print(f"  \"{event['message']}\"") # Display message first

            reward = event['item']
            if reward:
                 # Give a fresh copy of the item
                 if visiting_unit.add_item(copy.deepcopy(reward)):
                      pass # Success message handled by add_item
                 # else: inventory full message handled by add_item

            event['visited'] = True # Mark this specific house event as done
            # Update the map display symbol in the Game instance
            if self.game.is_valid_coordinate(x, y):
                 self.game.map_layout[y][x] = VISITED_HOUSE_SYMBOL
            return True # Event successfully triggered
        return False # No unvisited event at this location

    def _handle_reinforcement_event(self, event):
        """Handles the spawning of reinforcement units."""
        template = event['template']
        print(f"  Reinforcements sighted!")
        for x, y in event['coords']:
            if self.game.is_valid_coordinate(x, y):
                if self.game.get_unit_at(x, y) is None: # Check if spawn point is empty
                    # Create a new Unit instance from the template
                    inv = [copy.deepcopy(i) for i in template.get('inventory', [])] # Deep copy inventory
                    # Use dictionary unpacking, requires template keys match Unit init args
                    # Add defaults for missing args like skills, escape req
                    template_args = template.copy()
                    template_args.setdefault('initial_inventory', inv)
                    template_args.setdefault('required_to_escape', False)
                    template_args.setdefault('initial_skills', None)
                    # Ensure x,y are passed correctly
                    template_args['x'] = x
                    template_args['y'] = y
                    new_unit = Unit(**template_args)

                    # Auto-equip first weapon if available
                    if new_unit.inventory and isinstance(new_unit.inventory[0], Weapon):
                        new_unit.equip_item(0)

                    self.game.add_unit(new_unit) # Add to the main game unit list
                    print(f"   A {new_unit.name} appeared at ({x}, {y})!")
                else:
                    print(f"   Spawn blocked at ({x}, {y}).")
            else:
                print(f"   Invalid reinforcement coordinate: ({x}, {y}).")


# --- Game Class ---
class Game:
    """Main game class, manages state, turns, units, map, commands, combat."""
    def __init__(self, map_layout):
        # Initialize map using the provided layout (list of lists)
        self.map_layout = [list(row) for row in map_layout]
        self.height = len(map_layout)
        self.width = len(map_layout[0])
        self.terrain_data = TERRAIN_DATA # Reference to terrain properties
        self.units = []                    # List to hold all Unit objects
        self.current_turn = 'Player'       # Current phase ('Player' or 'Enemy')
        self.selected_unit = None          # The player unit currently selected
        self.game_over = False             # Game ends when True
        self.winner = None                 # 'Player' or 'Enemy' on game over
        self.turn_count = 1                # Current turn number
        # Trade state variables
        self.trading_unit1 = None
        self.trading_unit2 = None
        self.is_trading = False            # Flag for trading mode UI
        # Event manager instance
        self.event_manager = EventManager(self)
        self._register_chapter_events()   # Populate events for this chapter

    def _register_chapter_events(self):
        """Registers all predefined house visits and reinforcements via EventManager."""
        # House Rewards
        for coord, data in HOUSE_REWARDS.items():
             self.event_manager.register_house_visit(coord[0], coord[1], item_reward=data.get('item'), message=data.get('message'))
        # Reinforcements
        for event in REINFORCEMENTS:
             self.event_manager.register_reinforcement(event['turn'], event['template'], event['coords'])

    def add_unit(self, unit):
        """Adds a unit to the game if the space is valid and empty."""
        if self.is_valid_coordinate(unit.x, unit.y) and self.get_unit_at(unit.x, unit.y) is None:
            self.units.append(unit)
        else:
            print(f"Warning: Could not place {unit.name} at ({unit.x}, {unit.y}). Invalid or occupied.")

    def get_unit_at(self, x, y):
        """Returns the active (alive, not captured/escaped) unit at (x, y), or None."""
        for unit in self.units:
            if unit.is_alive and not unit.is_captured and not unit.has_escaped and unit.x == x and unit.y == y:
                return unit
        return None

    def is_valid_coordinate(self, x, y):
        """Checks if coordinates are within map bounds."""
        return 0 <= y < self.height and 0 <= x < self.width

    def get_terrain_at(self, x, y):
        """Gets the terrain symbol character at (x, y)."""
        if self.is_valid_coordinate(x, y):
            return self.map_layout[y][x]
        return None

    def get_terrain_props(self, x, y):
        """Gets the property dictionary for the terrain at (x, y)."""
        terrain_symbol = self.get_terrain_at(x, y)
        # Default to Plains if terrain symbol is unknown
        return self.terrain_data.get(terrain_symbol, TERRAIN_DATA[EMPTY_TILE])

    def calculate_leadership_bonus(self, unit):
        """Calculates total leadership bonus from nearby allies."""
        total_stars = 0
        for other_unit in self.units:
            if (other_unit != unit and other_unit.team == unit.team and
                    other_unit.is_alive and not other_unit.is_captured and not other_unit.has_escaped and
                    other_unit.leadership_stars > 0 and
                    self.distance(unit.x, unit.y, other_unit.x, other_unit.y) <= LEADERSHIP_RANGE):
                total_stars += other_unit.leadership_stars
        return total_stars * LEADERSHIP_BONUS_PER_STAR

    # --- Display Methods ---
    def display_map(self):
        """Prints the current map state, units, and basic info to the console."""
        print(f"\n--- Turn {self.turn_count} ({self.current_turn}'s Turn) ---")
        # Draw Grid Header
        print("   ", end=""); [print(f"{x:<2}", end="") for x in range(self.width)]; print("\n  " + "-"*(self.width*2+1))
        # Create display grid with terrain
        temp_grid = [[self.map_layout[y][x] for x in range(self.width)] for y in range(self.height)]
        # Overlay units
        for unit in self.units:
            if unit.is_alive and not unit.is_captured and not unit.has_escaped:
                symbol = unit.symbol
                if unit.is_capturing: symbol += CAPTURING_SYMBOL_SUFFIX
                # Apply selection/acted markers
                if unit == self.selected_unit: symbol = f"*{symbol}*"
                elif unit.team == self.current_turn and not unit.can_act(): symbol = symbol.lower() # Includes exhausted
                # Ensure symbol fits (basic truncate if needed for highlighting)
                temp_grid[unit.y][unit.x] = symbol[:2]
        # Print Grid Rows
        for y in range(self.height): print(f"{y:<2}|", end=""); [print(f"{temp_grid[y][x]:<2}", end="") for x in range(self.width)]; print("|")
        print("  " + "-"*(self.width*2+1))

        # Print Unit Lists
        print("\nUnits:")
        player_units = sorted([u for u in self.units if u.team=='Player' and not u.is_captured and not u.has_escaped], key=lambda u:u.name)
        enemy_units = sorted([u for u in self.units if u.team=='Enemy' and u.is_alive and not u.is_captured], key=lambda u:u.name)
        captured_enemies = [u for u in self.units if u.team=='Enemy' and u.is_captured]
        escaped_players = [u for u in self.units if u.team=='Player' and u.has_escaped]

        print("  Player:")
        if player_units:
            for unit in player_units:
                status = "(Can Act)" if unit.can_act() else "(Acted)" if not unit.is_exhausted else "(Exh)"
                t_name = self.get_terrain_props(unit.x, unit.y)['name']
                ldr_bonus = self.calculate_leadership_bonus(unit)
                ldr_str = f"(Ldr+{ldr_bonus})" if ldr_bonus > 0 else ""
                print(f"    - {unit} at ({unit.x},{unit.y}) on {t_name} {ldr_str} {status}") # Unit __str__ shows FTG/Skills
        else: print("    - None active")
        if escaped_players: print("  Escaped:"); [print(f"    - {unit}") for unit in escaped_players]

        print("  Enemy:")
        if enemy_units:
             for unit in enemy_units:
                  t_name = self.get_terrain_props(unit.x, unit.y)['name']
                  ldr_bonus = self.calculate_leadership_bonus(unit)
                  ldr_str = f"(Ldr+{ldr_bonus})" if ldr_bonus > 0 else ""
                  print(f"    - {unit} at ({unit.x},{unit.y}) on {t_name} {ldr_str}") # Unit __str__ shows FTG/Skills
        else: print("    - None")
        if captured_enemies: print("  Captured:"); [print(f"    - {unit}") for unit in captured_enemies]

        # Display Selected Unit Info or Trade UI
        if self.is_trading: self.display_trade_ui()
        elif self.selected_unit: self.display_selected_unit_info()

    def display_selected_unit_info(self):
        """Displays detailed info for the currently selected unit."""
        unit = self.selected_unit
        print(f"\nSelected: {unit}") # Uses unit.__str__
        t_props = self.get_terrain_props(unit.x, unit.y)
        ldr_bonus = self.calculate_leadership_bonus(unit)
        ldr_str = f"(Ldr+{ldr_bonus})" if ldr_bonus > 0 else ""
        print(f"  Pos: ({unit.x},{unit.y}) on {t_props['name']} (Def+{t_props['defense']}, Avo+{t_props['avoid']}) {ldr_str}")
        print(f"  Stats (Base -> Eff):")
        stats_to_show = ["strength", "magic", "skill", "speed", "luck", "defense", "resistance", "constitution", "move", "pcc", "leadership_stars"]
        stat_lines = []
        for stat in stats_to_show:
            is_special_stat = stat in ["pcc", "leadership_stars"]
            base = unit.get_base_stat(stat)
            eff = getattr(unit, stat) if hasattr(unit, stat) else base # Use property for effective value
            # Show difference only for stats affected by capture/other effects
            show_eff = base != eff and not is_special_stat
            stat_lines.append(f"{stat.capitalize()[:3]} {base}{'->'+str(eff) if show_eff else ''}")
        # Print stats in groups of ~3
        for i in range(0, len(stat_lines), 3): print("    " + " | ".join(stat_lines[i:i+3]))

        wpn = unit.equipped_weapon
        print(f"  Weapon: {wpn or 'None'}")
        if wpn:
            eff_hit = unit.hit_rate + ldr_bonus
            eff_avo = unit.avoid + t_props['avoid'] + ldr_bonus
            # Base crit doesn't include PCC, show that separately? Or calculate effective crit? Let's calc eff.
            # Need opponent AS for PCC, can't show here easily. Show Base Crit + PCC stat.
            print(f"  Combat: AS={unit.attack_speed} Hit={eff_hit} Avo={eff_avo} Crit={unit.crit_rate_base}(+{unit.pcc}*ASΔ) C.Avo={unit.crit_avoid} Atk={unit.attack_power}")
        else: print("  Combat: N/A")
        print(f"  Status: Act={'Y' if unit.has_acted else 'N'}, Mov={'Y' if unit.has_moved else 'N'}, Exh={'Y' if unit.is_exhausted else 'N'}")
        self.display_inventory(unit)
        if unit.is_capturing: print(f"  Carrying: {unit.captured_unit.name}")

    def display_inventory(self, unit, title="Inventory"):
        """Displays the inventory for a given unit."""
        print(f"  {title}:")
        equipped_idx = unit._equipped_weapon_index
        for i, item in enumerate(unit.inventory):
            prefix = " E" if i == equipped_idx else "  "
            item_str = str(item) if item else "----"
            print(f"    {prefix} {i+1}: {item_str}")

    def display_trade_ui(self):
        """Displays the UI during a trade action."""
        print("\n--- Trading ---")
        if not self.trading_unit1 or not self.trading_unit2: return # Safety check
        print(f"{self.trading_unit1.name}:"); self.display_inventory(self.trading_unit1, title="")
        print(f"\n{self.trading_unit2.name}:"); self.display_inventory(self.trading_unit2, title="")
        print("\nTrade Commands: give <unit_num (1 or 2)> <slot_num> | cancel")

    # --- Movement & Targeting ---
    def get_valid_moves(self, unit):
        """Calculates reachable squares using BFS and terrain costs."""
        if not unit.can_act() or unit.has_moved: return {}
        max_move = unit.move # Unit's effective move range
        q = collections.deque([(0, unit.x, unit.y)]) # (cost, x, y)
        visited = {(unit.x, unit.y): 0} # Store min cost to reach tile
        reachable = {} # Store reachable tiles { (x, y): cost }

        while q:
            cost, x, y = q.popleft()
            # Explore neighbors (Up, Down, Left, Right)
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                # Check bounds
                if not self.is_valid_coordinate(nx, ny): continue
                # Check terrain passability and cost
                terrain_props = self.get_terrain_props(nx, ny)
                if not terrain_props['is_passable']: continue
                move_cost = terrain_props['move_cost'] # TODO: Adjust for unit movement type (flying, cavalry)
                new_cost = cost + move_cost
                # Check if move cost exceeds unit's max movement
                if new_cost > max_move: continue
                # Check if occupied by another non-captured/escaped unit
                occupying_unit = self.get_unit_at(nx, ny)
                if occupying_unit and occupying_unit != unit: continue
                # Check if path is better or newly discovered
                if (nx, ny) not in visited or new_cost < visited[(nx, ny)]:
                    visited[(nx, ny)] = new_cost
                    reachable[(nx, ny)] = new_cost # Add to reachable dictionary
                    q.append((new_cost, nx, ny))
        # Remove starting position from reachable destinations
        reachable.pop((unit.x, unit.y), None)
        return reachable

    def get_attack_targets(self, unit):
        """Finds all enemy units within the equipped weapon's range."""
        targets = []
        if not unit or not unit.can_act() or not unit.equipped_weapon: return []
        possible_ranges = unit.attack_range
        for other_unit in self.units:
            # Can only target units that are alive, not captured, and on the enemy team
            if other_unit.is_alive and not other_unit.is_captured and other_unit.team != unit.team:
                dist = self.distance(unit.x, unit.y, other_unit.x, other_unit.y)
                if dist in possible_ranges:
                    targets.append(other_unit)
        return targets

    def move_unit(self, unit, target_x, target_y):
        """Moves the unit if the target coordinates are valid and reachable."""
        # Note: Moving alone does not cost an action/fatigue in this model yet.
        if not unit or not unit.can_act() or unit.has_moved:
            print("Cannot move this unit (acted, moved, exhausted, etc.).")
            return False
        valid_moves = self.get_valid_moves(unit)
        if (target_x, target_y) in valid_moves:
            unit.x = target_x
            unit.y = target_y
            unit.has_moved = True # Mark as moved for this turn
            print(f"{unit.name} moved to ({target_x}, {target_y}).")
            return True
        else:
            print("Invalid move target (out of range, blocked, or occupied).")
            return False

    # --- Combat System ---
    def perform_combat(self, attacker, defender, is_capture_attempt=False):
        """Initiates and resolves a combat or capture sequence between two units."""
        # --- Pre-Combat Checks ---
        if not attacker or not defender: print("Error: Invalid combat units."); return False
        if not attacker.is_alive or not defender.is_alive or defender.is_captured: print("Invalid combat state."); return False
        if not attacker.can_act(): print(f"{attacker.name} cannot act."); return False
        if attacker.team == defender.team: print("Cannot target allies."); return False
        weapon = attacker.equipped_weapon
        if not weapon: print(f"{attacker.name} has no weapon equipped."); return False
        dist = self.distance(attacker.x, attacker.y, defender.x, defender.y)
        if dist not in attacker.attack_range: print(f"{defender.name} is out of range."); return False

        # --- Capture Specific Checks ---
        if is_capture_attempt:
            if attacker.is_capturing: print("Cannot capture while carrying."); return False
            if weapon.range != [1]: print("Capture must be initiated with a melee weapon (Range 1)."); return False
            if attacker.constitution < defender.constitution:
                print(f"Capture failed: {attacker.name}'s CON ({attacker.constitution}) < {defender.name}'s CON ({defender.constitution}).")
                # Don't consume action if pre-check fails
                return False # Failed before combat started

        # --- Start Combat ---
        attacker.set_acted() # Performing combat costs the action/fatigue

        if is_capture_attempt:
            print(f"\n--- {attacker.name} attempts to CAPTURE {defender.name} ---")
            self._resolve_capture_combat(attacker, defender, self)
        else:
            print(f"\n--- {attacker.name} attacks {defender.name} ---")
            self._resolve_normal_combat(attacker, defender, self)

        # --- Post-Combat Resolution ---
        print(f"--- Combat End ---")
        # Check for defeat
        if defender.hp <= 0 and not defender.is_captured: # Defeated in normal combat
            defender.is_alive = False
            print(f"*** {defender.name} was defeated! ***")
        if attacker.hp <= 0:
            attacker.is_alive = False
            print(f"*** {attacker.name} was defeated! ***")
            # If captor died, drop captive
            if attacker.is_capturing and attacker.captured_unit:
                print(f"{attacker.name} drops {attacker.captured_unit.name}!")
                # Find best spot to release (prioritize current, then adjacent)
                release_x, release_y = attacker.x, attacker.y; found_spot = False
                for dx, dy in [(0,0), (0,1), (0,-1), (1,0), (-1,0)]:
                    check_x, check_y = attacker.x + dx, attacker.y + dy
                    if self.is_valid_coordinate(check_x, check_y) and self.get_unit_at(check_x, check_y) is None:
                        release_x, release_y = check_x, check_y; found_spot = True; break
                if not found_spot: print("WARNING: No empty adjacent space to drop captive!") # Should ideally not happen
                # Release captive (doesn't cost action here since captor is defeated)
                attacker.release_captive(self, release_x, release_y) # Pass self

        # Deselect unit if they died/escaped/were captured
        if self.selected_unit and (not self.selected_unit.is_alive or self.selected_unit.is_captured or self.selected_unit.has_escaped):
             self.selected_unit = None

        return True # Combat sequence occurred

    def _resolve_normal_combat(self, attacker, defender, game):
        """Handles the sequence of attacks in normal combat, including skills."""
        # Flags to track state changes during the round
        a_wpn_broke, d_wpn_broke = False, False
        a_adepted, d_adepted = False, False # Limit Adept to one proc per round per unit

        # 1. Vantage Check
        vantage_activates = (SKILL_VANTAGE in defender.skills and
                             defender.hp <= defender.max_hp / 2 and
                             defender.equipped_weapon and not defender.is_capturing and
                             self.distance(attacker.x, attacker.y, defender.x, defender.y) in defender.attack_range)

        if vantage_activates:
            print(f" <{SKILL_VANTAGE}!>")
            d_wpn_broke = self._resolve_attack(defender, attacker, game)
            # Check Defender Adept after Vantage strike
            if defender.is_alive and not d_wpn_broke and SKILL_ADEPT in defender.skills and not d_adepted and random.randint(1, 100) <= defender.speed:
                print(f" <{SKILL_ADEPT}!> (Defender)")
                d_wpn_broke = self._resolve_attack(defender, attacker, game) # Update break status
                d_adepted = True

        # 2. Attacker's First Strike (if attacker still alive)
        if attacker.is_alive and not a_wpn_broke:
            a_wpn_broke = self._resolve_attack(attacker, defender, game)
            # Check Attacker Adept
            if attacker.is_alive and not a_wpn_broke and SKILL_ADEPT in attacker.skills and not a_adepted and random.randint(1, 100) <= attacker.speed:
                print(f" <{SKILL_ADEPT}!> (Attacker)")
                a_wpn_broke = self._resolve_attack(attacker, defender, game)
                a_adepted = True

        # 3. Defender's Counterattack (if possible and Vantage didn't trigger/resolve)
        can_counter = (defender.is_alive and defender.equipped_weapon and
                       not d_wpn_broke and not a_wpn_broke and # Neither weapon broke
                       self.distance(attacker.x, attacker.y, defender.x, defender.y) in defender.attack_range)

        if can_counter and not vantage_activates: # Only counter if Vantage didn't already happen
            print(" <Counter> ")
            d_wpn_broke = self._resolve_attack(defender, attacker, game)
            # Check Defender Adept on Counter
            if defender.is_alive and not d_wpn_broke and SKILL_ADEPT in defender.skills and not d_adepted and random.randint(1, 100) <= defender.speed:
                print(f" <{SKILL_ADEPT}!> (Defender Counter)")
                d_wpn_broke = self._resolve_attack(defender, attacker, game)
                d_adepted = True

        # 4. Follow-Up Attacks (if both alive and weapons intact)
        if attacker.is_alive and defender.is_alive and not a_wpn_broke and not d_wpn_broke:
            # Attacker Follow-up
            if attacker.attack_speed - defender.attack_speed >= FOLLOW_UP_THRESHOLD:
                print(" <Follow-Up> ")
                a_wpn_broke = self._resolve_attack(attacker, defender, game)
                # Check Attacker Adept on Follow-up
                if attacker.is_alive and not a_wpn_broke and SKILL_ADEPT in attacker.skills and not a_adepted and random.randint(1, 100) <= attacker.speed:
                     print(f" <{SKILL_ADEPT}!> (Attacker Follow-up)")
                     # Call attack again, but don't update break flag as it doesn't matter for subsequent defender follow-up
                     self._resolve_attack(attacker, defender, game)
                     # Don't set a_adepted=True here if we allow multiple Adepts per round (Thracia rule?) - Assume 1 for now.

            # Defender Follow-up (Check counter conditions again)
            can_counter_again = (defender.equipped_weapon and
                                 self.distance(attacker.x, attacker.y, defender.x, defender.y) in defender.attack_range)
            if can_counter_again and defender.attack_speed - attacker.attack_speed >= FOLLOW_UP_THRESHOLD:
                print(" <Counter Follow-Up> ")
                d_wpn_broke = self._resolve_attack(defender, attacker, game)
                # Check Defender Adept on Follow-up
                if defender.is_alive and not d_wpn_broke and SKILL_ADEPT in defender.skills and not d_adepted and random.randint(1, 100) <= defender.speed:
                     print(f" <{SKILL_ADEPT}!> (Defender Follow-up)")
                     self._resolve_attack(defender, attacker, game)

    def _resolve_capture_combat(self, captor, captive, game):
        """Handles the sequence of attacks during a capture attempt."""
        # Note: Assuming skills like Vantage/Adept/Wrath do NOT activate during capture attempts.
        cpt_wpn_broke = self._resolve_attack(captor, captive, game, use_capture_stats=True)
        cpv_wpn_broke = False

        # Captive Counterattack
        can_counter = (captive.hp > 0 and captive.equipped_weapon and not cpt_wpn_broke and
                       self.distance(captor.x, captor.y, captive.x, captive.y) in captive.attack_range)
        if can_counter:
            print(" <Counter> ")
            cpv_wpn_broke = self._resolve_attack(captive, captor, game) # Captive uses normal stats

        # Follow-ups (if relevant and weapons okay)
        if captor.hp > 0 and captive.hp > 0 and not cpt_wpn_broke and not cpv_wpn_broke:
            # Calculate captor's effective AS for capture attempt
            wpn=captor.equipped_weapon; wt=wpn.weight if wpn else 0; pen=max(0,wt-captor.constitution)
            cpt_eff_as_capture = max(0, math.floor(captor._base_speed / 2) - pen) # Use halved speed

            # Captor Follow-up
            if cpt_eff_as_capture - captive.attack_speed >= FOLLOW_UP_THRESHOLD:
                print(" <Follow-Up (Capture)> ")
                self._resolve_attack(captor, captive, game, use_capture_stats=True) # Ignore break status return

            # Captive Follow-up
            if can_counter and captive.attack_speed - cpt_eff_as_capture >= FOLLOW_UP_THRESHOLD:
                print(" <Counter Follow-Up (Capture)> ")
                self._resolve_attack(captive, captor, game) # Ignore break status return

        # Check if capture succeeded (captive HP reduced to 0)
        if captive.hp <= 0:
            captive._become_captured(captor)
            captor._become_captor(captive)
        else:
            print(f"Capture failed: {captive.name} survived.")

    def _resolve_attack(self, attacker, defender, game, use_capture_stats=False):
        """Calculates and applies a single attack hit, including WT, Ldr, PCC, Crit, Terrain. Returns True if weapon broke."""
        # --- Pre-checks ---
        if not attacker.is_alive or not defender.is_alive or defender.is_captured: return False
        weapon = attacker.equipped_weapon
        if not weapon: print("DEBUG: _resolve_attack called without weapon?"); return False

        # --- Weapon Use ---
        if not weapon.use():
            print(f"{attacker.name}'s {weapon.name} broke!")
            return True # Weapon broke

        # --- Calculate Attacker Combat Stats ---
        atk_eff_str = math.floor(attacker._base_strength / 2) if use_capture_stats else attacker.strength
        atk_eff_mag = math.floor(attacker._base_magic / 2) if use_capture_stats else attacker.magic
        atk_eff_skl = math.floor(attacker._base_skill / 2) if use_capture_stats else attacker.skill
        atk_eff_spd = math.floor(attacker._base_speed / 2) if use_capture_stats else attacker.speed
        atk_lck = attacker.luck
        atk_con = attacker.constitution
        wpn_wt = weapon.weight
        penalty = max(0, wpn_wt - atk_con)
        atk_eff_as = max(0, atk_eff_spd - penalty)
        atk_base_crit = max(0, math.floor(atk_eff_skl / 2) + weapon.crit)
        atk_base_hit = weapon.hit + (atk_eff_skl * 2) + math.floor(atk_lck / 2)
        ldr_bonus_atk = game.calculate_leadership_bonus(attacker)

        # --- Calculate Defender Combat Stats ---
        def_trn = game.get_terrain_props(defender.x, defender.y)
        ldr_bonus_def = game.calculate_leadership_bonus(defender)
        def_eff_avo_base = defender.avoid # Uses defender's current AS/Luck
        def_eff_avo = def_eff_avo_base + def_trn['avoid'] + ldr_bonus_def
        is_phys_atk = weapon.is_physical()
        def_base_mit_stat = defender.defense if is_phys_atk else defender.resistance # Uses effective Def/Res
        def_trn_def = def_trn['defense'] if is_phys_atk else 0
        def_eff_mit = def_base_mit_stat + def_trn_def
        def_crit_avo = defender.crit_avoid # Just Luck

        # --- Weapon Triangle Calculation ---
        wt_hit, wt_mt = self.calculate_weapon_triangle(weapon, defender.equipped_weapon)

        # --- Final Hit Calculation ---
        effective_hit_rate = atk_base_hit + wt_hit + ldr_bonus_atk
        accuracy = max(0, min(100, effective_hit_rate - def_eff_avo))

        # --- Wrath Check ---
        is_wrath = SKILL_WRATH in attacker.skills and attacker.hp <= attacker.max_hp / 2 and game.current_turn != attacker.team
        wrath_msg = f" <{SKILL_WRATH}!>" if is_wrath else ""

        # --- Display Attack Info ---
        wt_disp = f"(WT{wt_hit:+})" if wt_hit != 0 else ""
        ldr_disp = f"(LDR{ldr_bonus_atk:+})" if ldr_bonus_atk != 0 else ""
        print(f"{attacker.name}({weapon.name})...{wt_disp}{ldr_disp}{wrath_msg} ", end="")

        # --- Hit Roll ---
        hit_roll = random.randint(1, 100)
        if hit_roll <= accuracy:
            # --- Critical Hit Calculation ---
            pcc_bonus = max(0, atk_eff_as - defender.attack_speed) * attacker.pcc if attacker.pcc > 0 else 0
            effective_crit_rate = atk_base_crit + pcc_bonus
            crit_chance = max(0, min(100, effective_crit_rate - def_crit_avo))
            is_crit = is_wrath or (random.randint(1, 100) <= crit_chance) # Wrath guarantees crit

            crit_msg = "CRITICAL HIT! " if is_crit else ""
            pcc_msg = f"(PCC+{pcc_bonus})" if pcc_bonus > 0 else ""
            print(f"Hit! {crit_msg}({accuracy}%, roll {hit_roll}) {pcc_msg}")

            # --- Damage Calculation ---
            atk_pwr_stat = atk_eff_str if is_phys_atk else atk_eff_mag
            effective_atk_power = atk_pwr_stat + weapon.might + wt_mt # Add WT Mt
            base_damage = max(0, effective_atk_power - def_eff_mit)
            final_damage = base_damage * 3 if is_crit else base_damage

            print(f" -> {defender.name} takes {final_damage} damage.")
            defender.take_damage(final_damage) # Apply damage

        else: # Miss
            print(f"Miss! ({accuracy}%, roll {hit_roll})")

        return weapon.is_broken() # Return True if uses hit 0 THIS turn

    def calculate_weapon_triangle(self, atk_weapon, def_weapon):
        """Calculates WT Hit/Mt modifiers for attacker. Returns (hit_mod, mt_mod)."""
        if not atk_weapon or not def_weapon: return 0, 0 # No triangle if one side unarmed
        atk_type = atk_weapon.type; def_type = def_weapon.type
        hit_mod, mt_mod = 0, 0
        if atk_type == 'Sword':
            if def_type == 'Axe': hit_mod, mt_mod = WT_BONUS_HIT, WT_BONUS_MT
            elif def_type == 'Lance': hit_mod, mt_mod = -WT_BONUS_HIT, -WT_BONUS_MT
        elif atk_type == 'Axe':
            if def_type == 'Lance': hit_mod, mt_mod = WT_BONUS_HIT, WT_BONUS_MT
            elif def_type == 'Sword': hit_mod, mt_mod = -WT_BONUS_HIT, -WT_BONUS_MT
        elif atk_type == 'Lance':
            if def_type == 'Sword': hit_mod, mt_mod = WT_BONUS_HIT, WT_BONUS_MT
            elif def_type == 'Axe': hit_mod, mt_mod = -WT_BONUS_HIT, -WT_BONUS_MT
        # Add Magic/Bow later if needed
        return hit_mod, mt_mod

    # --- Utility & Turn Management ---
    def distance(self, x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def check_game_over(self): # Unchanged
        leif=next((u for u in self.units if u.name=="Leif"),None)
        if leif and (not leif.is_alive or leif.is_captured): self.game_over=True; self.winner='Enemy'; print("Leif defeated!")
        elif leif and leif.has_escaped: self.game_over=True; self.winner='Player'; print("Leif escaped!")
    def next_turn(self): # Unchanged
        # Fatigue check
        if self.current_turn=='Enemy': print("--- Fatigue Check ---"); [setattr(u,'is_exhausted',True) or print(f"{u.name} exhausted!") for u in self.units if u.team=='Player' and u.is_alive and not u.is_captured and not u.has_escaped and u.fatigue>=u.max_hp]; [setattr(u,'is_exhausted',False) for u in self.units if u.team=='Player' and u.is_alive and not u.is_captured and not u.has_escaped and u.fatigue<u.max_hp]
        self.selected_unit=None; self.is_trading=False; self.trading_unit1=None; self.trading_unit2=None
        # Events
        if self.current_turn=='Player': self.event_manager.trigger_turn_events(self.turn_count)
        # Switch Turn
        if self.current_turn=='Player': self.current_turn='Enemy' else: self.current_turn='Player'; self.turn_count+=1
        print(f"\n--- Start {self.current_turn}'s Turn {self.turn_count if self.current_turn=='Player' else ''} ---")
        [u.reset_turn() for u in self.units if u.team==self.current_turn and u.is_alive and not u.is_captured and not u.has_escaped]; self.check_game_over()

    # --- Player Turn Command Handling ---
    def handle_player_turn(self): # Unchanged Structure
        if self.is_trading: self.handle_trade_input(); return
        # Determine available actions based on state
        carrying=self.selected_unit and self.selected_unit.is_capturing; on_esc=False; on_house=False
        if self.selected_unit: x,y=self.selected_unit.x,self.selected_unit.y; terrain=self.get_terrain_at(x,y); on_esc=terrain==ESCAPE_SYMBOL
        if self.selected_unit and terrain==HOUSE_SYMBOL and (x,y) in self.event_manager.visit_events and not self.event_manager.visit_events[(x,y)]['visited']: on_house=True
        actions=["s"]; # Build dynamic actions list
        if self.selected_unit: actions.extend(["m","a"]); actions.extend(["take","release"] if carrying else ["c","eq","tr"]); actions.extend(["w","item","use","drop"]); actions.append("esc") if on_esc else None; actions.append("vis") if on_house else None; actions.extend(["i","mv","tg"])
        actions.extend(["e","h"]); print(f"\nPlayer Actions: {', '.join(actions)}")
        # Command Loop
        while True:
            if not any(u.can_act() for u in self.units if u.team=='Player' and u.is_alive and not u.is_captured and not u.has_escaped): print("\nAll Player Units Acted/Exhausted."); break
            cmd=input("> ").lower().strip(); parts=cmd.split(); action=parts[0] if parts else ""; handled=False
            # Process actions using helper methods...
            if action in ["s"]: self.handle_select_command(parts); handled=True
            elif self.selected_unit:
                # Use 'in' check against dynamically generated list for context validity? Might be cleaner.
                if not carrying and action in ["c","eq","tr"]: # Non-carrying actions
                    if action=="c": self.handle_capture_command(parts)
                    elif action=="eq": self.handle_equip_command(parts)
                    elif action=="tr": self.handle_trade_init_command(parts)
                    handled=True
                elif carrying and action in ["take","release"]: # Carrying actions
                    if action=="take": self.handle_take_command(parts)
                    elif action=="release": self.handle_release_command(parts)
                    handled=True
                # Shared selected unit actions
                elif action in ["m"]: self.handle_move_command(parts); handled=True
                elif action in ["a"]: self.handle_attack_command(parts); handled=True
                elif action in ["w"]: self.handle_wait_command(parts); handled=True
                elif action=="item": self.handle_item_command(parts); handled=True
                elif action=="use": self.handle_use_command(parts); handled=True
                elif action=="drop": self.handle_drop_command(parts); handled=True
                elif action=="esc" and on_esc: self.handle_escape_command(parts); handled=True
                elif action=="vis" and on_house: self.handle_visit_command(parts); handled=True
                elif action in ["i"]: self.handle_info_command(parts); handled=True
                elif action in ["mv"]: self.handle_moves_command(parts); handled=True
                elif action in ["tg"]: self.handle_targets_command(parts); handled=True
            # Non-unit-specific actions
            if action in ["e"]:
                if any(u.can_act() for u in self.units if u.team=='Player' and u.is_alive and not u.is_captured and not u.has_escaped):
                     if input("Some units can still act. End turn anyway? (y/n): ").lower() != 'y': continue
                print("Ending Player Turn."); handled=True; break
            elif action in ["h"]: print(f"Available actions: {', '.join(actions)}"); handled=True
            # Error / Unknown
            if not handled and action: print(f"Unknown command '{action}' or invalid in current state.")
            if self.game_over: return # Exit if game ended mid-turn
        # End of loop
        if not self.is_trading and not self.game_over: self.next_turn()

    # --- Command Handler Methods ---
    # These methods validate input and call the appropriate Unit or Game methods.
    # They ensure actions cost fatigue via unit.set_acted() where appropriate.
    def handle_select_command(self, parts):
        if len(parts)==3:
            try: x,y=int(parts[1]),int(parts[2]); unit=self.get_unit_at(x,y)
            except ValueError: print("Invalid coordinates."); return
            if unit and unit.team=='Player': self.selected_unit=unit; print(f"Selected {unit.name}."); self.display_map()
            elif unit: print("Cannot select enemy units.")
            else: print(f"No active player unit at ({x},{y}).")
        else: print("Usage: s <x> <y>")

    def handle_move_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act() or self.selected_unit.has_moved: print("Cannot move."); return
        if len(parts)==3:
            try: x,y=int(parts[1]),int(parts[2])
            except ValueError: print("Invalid coordinates."); return
            if self.move_unit(self.selected_unit, x, y): self.display_map() # move_unit handles messages
        else: print("Usage: m <x> <y>")

    def handle_attack_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        # perform_combat handles can_act, weapon checks, messages, and set_acted
        if len(parts)==3:
            try: x,y=int(parts[1]),int(parts[2]); target=self.get_unit_at(x,y)
            except ValueError: print("Invalid coordinates."); return
            if target:
                if self.perform_combat(self.selected_unit, target): self.display_map() # Update after combat
            else: print(f"No target at ({x},{y}).")
        else: print("Usage: a <x> <y>")

    def handle_capture_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if self.selected_unit.is_capturing: print("Cannot capture while carrying."); return
        # perform_combat handles can_act, weapon checks, messages, and set_acted
        if len(parts)==3:
            try: x,y=int(parts[1]),int(parts[2]); target=self.get_unit_at(x,y)
            except ValueError: print("Invalid coordinates."); return
            if target and target.team!='Player':
                 if self.perform_combat(self.selected_unit, target, is_capture_attempt=True): self.display_map()
            elif not target: print(f"No target at ({x},{y}).")
            else: print("Cannot capture allies.")
        else: print("Usage: c <x> <y>")

    def handle_wait_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if self.selected_unit.wait(): self.display_map() # wait calls set_acted

    def handle_item_command(self, parts): # View items - Free action
        if not self.selected_unit: print("No unit selected."); return
        self.display_inventory(self.selected_unit)
        if self.selected_unit.is_capturing:
             print(f"\n--- {self.selected_unit.captured_unit.name}'s Items (Captive) ---")
             self.display_inventory(self.selected_unit.captured_unit, title="Captive")
             print("  (Use 'take <slot>' to take)")

    def handle_equip_command(self, parts): # Equip - Free action
        if not self.selected_unit: print("No unit selected."); return
        if len(parts)==2:
            try: index = int(parts[1]) - 1
            except ValueError: print("Invalid slot number."); return
            if self.selected_unit.equip_item(index): self.display_map() # equip_item prints messages
        else: print("Usage: eq <slot_number>")

    def handle_use_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if len(parts)==2:
            try: index = int(parts[1]) - 1
            except ValueError: print("Invalid slot number."); return
            # unit.use_item handles messages and calls set_acted
            if self.selected_unit.use_item(index): self.display_map()
        else: print("Usage: use <slot_number>")

    def handle_trade_init_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        if len(parts)==3:
            try: x,y=int(parts[1]),int(parts[2]); target_unit = self.get_unit_at(x,y)
            except ValueError: print("Invalid coordinates."); return
            if target_unit and target_unit.team=='Player' and self.distance(self.selected_unit.x, self.selected_unit.y, x, y)==1:
                self.trading_unit1 = self.selected_unit; self.trading_unit2 = target_unit; self.is_trading = True
                self.selected_unit.set_acted() # Initiator uses action
                print(f"Initiating trade: {self.trading_unit1.name} & {self.trading_unit2.name}."); self.display_map()
            elif not target_unit: print("No unit there.")
            elif target_unit.team != 'Player': print("Cannot trade with non-player.")
            else: print("Target not adjacent.")
        else: print("Usage: tr <x> <y>")

    def handle_trade_input(self): # Actions within trade are free
        command = input("Trade> ").lower().strip(); parts = command.split(); action = parts[0] if parts else ""
        if action == "give":
             if len(parts) == 3:
                 try: unit_num = int(parts[1]); slot = int(parts[2]) - 1
                 except ValueError: print("Invalid number format."); return
                 giver = self.trading_unit1 if unit_num == 1 else self.trading_unit2 if unit_num == 2 else None
                 receiver = self.trading_unit2 if unit_num == 1 else self.trading_unit1 if unit_num == 2 else None
                 if giver and receiver and 0 <= slot < INVENTORY_SIZE:
                     item = giver.get_item(slot)
                     if item:
                         temp_item = copy.deepcopy(item) # Give a copy
                         if receiver.add_item(temp_item): giver.remove_item(slot); print("Item given."); self.display_trade_ui()
                     else: print(f"{giver.name} has no item in slot {slot+1}.")
                 else: print("Invalid unit number or slot.")
             else: print("Usage: give <unit_number (1 or 2)> <slot_number>")
        elif action == "cancel":
            print("Trade cancelled."); self.is_trading = False; self.trading_unit1 = None; self.trading_unit2 = None; self.display_map()
        else: print("Invalid trade command. Use 'give 1|2 <slot>', or 'cancel'.")

    def handle_take_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.is_capturing: print("Not carrying anyone."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        if len(parts) == 2:
            try: slot_index = int(parts[1]) - 1
            except ValueError: print("Invalid slot number."); return
            # Unit method handles logic and messages
            if self.selected_unit.take_captive_item(slot_index):
                self.selected_unit.set_acted() # Cost action AFTER success
                self.display_map()
        else: print("Usage: take <captive_slot_number> (use 'item' to see slots)")

    def handle_release_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.is_capturing: print("Not carrying anyone."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        # Find adjacent empty tile
        found_spot = False; release_x, release_y = -1, -1
        for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            cx,cy = self.selected_unit.x+dx, self.selected_unit.y+dy
            if self.is_valid_coordinate(cx,cy) and self.get_unit_at(cx,cy) is None:
                release_x, release_y = cx, cy; found_spot = True; break
        if found_spot:
            # Unit method handles logic and messages
            if self.selected_unit.release_captive(self, release_x, release_y):
                 self.selected_unit.set_acted() # Cost action AFTER success
                 self.display_map()
        else: print("No adjacent empty space to release captive!")

    def handle_drop_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        # Unit method handles logic, messages, and set_acted
        if len(parts) == 2:
            try: index = int(parts[1]) - 1
            except ValueError: print("Invalid slot number."); return
            if self.selected_unit.drop_item(index): self.display_map()
        else: print("Usage: drop <slot_number>")

    def handle_escape_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        if self.get_terrain_at(self.selected_unit.x, self.selected_unit.y) == ESCAPE_SYMBOL:
            # Unit method handles messages
            if self.selected_unit.escape():
                self.selected_unit.set_acted() # Cost action AFTER success
                self.escaped_player_names.add(self.selected_unit.name)
                self.check_game_over() # Check win condition immediately
                # Don't display map here, let main loop handle it or game over message
        else: print("Not on an escape tile ('X').")

    def handle_visit_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        unit_x, unit_y = self.selected_unit.x, self.selected_unit.y
        # Event manager handles checks and rewards
        if self.event_manager.trigger_visit_event(self.selected_unit, unit_x, unit_y):
            self.selected_unit.set_acted() # Cost action AFTER success
            self.display_map()
        else: print("Cannot visit this location (or already visited).")

    # --- Polished Info/Targets Commands ---
    def handle_info_command(self, parts):
        if len(parts) == 3:
             target_unit = None; try: x, y = int(parts[1]), int(parts[2]); target_unit = self.get_unit_at(x, y); except ValueError: print("Invalid coords."); return
             if target_unit:
                 print(f"\n--- Info: {target_unit.name} ({target_unit.symbol}) ---"); print(f"  Team: {target_unit.team}, Status: {'Alive' if target_unit.is_alive else 'Defeated'} {'(Exh)' if target_unit.is_exhausted else ''} {'<Carry>' if target_unit.is_capturing else ''}"); print(f"  HP: {target_unit.hp}/{target_unit.max_hp}, Fatigue: {target_unit.fatigue}"); t_props=self.get_terrain_props(target_unit.x, target_unit.y); ldr_bonus=self.calculate_leadership_bonus(target_unit); ldr_str=f"(Ldr+{ldr_bonus})" if ldr_bonus > 0 else ""; print(f"  Pos: ({target_unit.x},{target_unit.y}) on {t_props['name']} {ldr_str}");
                 stats=["strength","magic","skill","speed","luck","defense","resistance","constitution","move","pcc","leadership_stars"]; print(f"  Stats (Base -> Eff):"); stat_strs=[]
                 for stat in stats: base=target_unit.get_base_stat(stat); eff=getattr(target_unit, stat, base); show_eff=base!=eff and stat not in ['pcc','leadership_stars']; stat_strs.append(f"{stat.capitalize()[:3]} {base}{'->'+str(eff) if show_eff else ''}")
                 for i in range(0, len(stat_strs), 3): print("    "+" | ".join(stat_strs[i:i+3]))
                 print(f"  Skills: {', '.join(sorted(list(target_unit.skills))) if target_unit.skills else 'None'}"); wpn=target_unit.equipped_weapon; print(f"  Weapon: {wpn or 'None'}");
                 if wpn: eff_hit=target_unit.hit_rate+ldr_bonus; eff_avo=target_unit.avoid+t_props['avoid']+ldr_bonus; print(f"  Combat: AS={target_unit.attack_speed} Hit={eff_hit} Avo={eff_avo} Crit={target_unit.crit_rate_base}(+{target_unit.pcc}*ASΔ) C.Avo={target_unit.crit_avoid} Atk={target_unit.attack_power}")
                 else: print("  Combat: N/A"); self.display_inventory(target_unit)
             else: print(f"No active unit at ({x},{y}).")
        else: print("Usage: i <x> <y>")

    def handle_moves_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act() or self.selected_unit.has_moved: print("Cannot move."); return
        moves=self.get_valid_moves(self.selected_unit);
        if moves: print(f"Moves (Max Cost: {self.selected_unit.move}):"); coords=sorted(moves.items(), key=lambda i:(i[1],i[0][1],i[0][0])); print(" "+", ".join([f"({x},{y} C:{c})" for (x,y),c in coords]))
        else: print("Cannot move anywhere.")

    def handle_targets_command(self, parts):
        if not self.selected_unit: print("No unit selected."); return
        if not self.selected_unit.can_act(): print("Already acted."); return
        attacker = self.selected_unit; atk_wpn = attacker.equipped_weapon
        if not atk_wpn: print("No weapon equipped."); return
        targets = self.get_attack_targets(attacker)
        if targets:
            print(f"\n--- Targets for {attacker.name} ({atk_wpn.name}) ---")
            ldr_bonus_atk = self.calculate_leadership_bonus(attacker); atk_trn = self.get_terrain_props(attacker.x, attacker.y)
            for defender in targets:
                print(f" -> {defender.name} at ({defender.x},{defender.y}) [{defender.hp}/{defender.max_hp} HP]")
                def_wpn = defender.equipped_weapon; ldr_bonus_def = self.calculate_leadership_bonus(defender); def_trn = self.get_terrain_props(defender.x, defender.y)
                # Attacker -> Defender Forecast
                atk_hit_base=attacker.hit_rate; atk_mt_base=attacker.attack_power; atk_crit_base=attacker.crit_rate_base; atk_as=attacker.attack_speed; atk_pcc=attacker.pcc
                wt_h_a, wt_m_a = self.calculate_weapon_triangle(atk_wpn, def_wpn)
                atk_hit = atk_hit_base+wt_h_a+ldr_bonus_atk; atk_mt = atk_mt_base+wt_m_a; pcc_bonus_atk=max(0,atk_as-defender.attack_speed)*atk_pcc; atk_crit_eff=atk_crit_base+pcc_bonus_atk
                def_avo=defender.avoid+def_trn['avoid']+ldr_bonus_def; is_phys_atk=atk_wpn.is_physical(); b_def=defender.defense if is_phys_atk else defender.resistance; t_def=def_trn['defense'] if is_phys_atk else 0; eff_mit=b_def+t_def; def_crit_avo=defender.crit_avoid
                disp_hit=max(0,min(100,atk_hit-def_avo)); disp_dmg=max(0,atk_mt-eff_mit); disp_crit=max(0,min(100,atk_crit_eff-def_crit_avo)); doubles="x2" if atk_as-defender.attack_speed>=FOLLOW_UP_THRESHOLD else ""
                print(f"    Attack: {disp_dmg} Dmg ({disp_hit}% Hit, {disp_crit}% Crit) AS:{atk_as} {doubles}")
                # Defender -> Attacker Forecast
                dist=self.distance(attacker.x,attacker.y,defender.x,defender.y)
                if defender.is_alive and def_wpn and dist in def_wpn.range:
                    def_hit_base=defender.hit_rate; def_mt_base=defender.attack_power; def_crit_base=defender.crit_rate_base; def_as=defender.attack_speed; def_pcc=defender.pcc
                    wt_h_d, wt_m_d = self.calculate_weapon_triangle(def_wpn, atk_wpn) # Reverse WT
                    def_hit=def_hit_base+wt_h_d+ldr_bonus_def; def_mt=def_mt_base+wt_m_d; pcc_bonus_def=max(0,def_as-atk_as)*def_pcc; def_crit_eff=def_crit_base+pcc_bonus_def
                    atk_avo=attacker.avoid+atk_trn['avoid']+ldr_bonus_atk; is_phys_def=def_wpn.is_physical(); a_def=attacker.defense if is_phys_def else attacker.resistance; a_trn_def=atk_trn['defense'] if is_phys_def else 0; atk_mit=a_def+a_trn_def; atk_crit_avo=attacker.crit_avoid
                    disp_ctr_hit=max(0,min(100,def_hit-atk_avo)); disp_ctr_dmg=max(0,def_mt-atk_mit); disp_ctr_crit=max(0,min(100,def_crit_eff-atk_crit_avo)); ctr_doubles="x2" if def_as-atk_as>=FOLLOW_UP_THRESHOLD else ""
                    print(f"    Counter: {disp_ctr_dmg} Dmg ({disp_ctr_hit}% Hit, {disp_ctr_crit}% Crit) AS:{def_as} {ctr_doubles}")
                else: print("    Counter: ---")
        else: print("No targets in range.")

    # --- AI Turn Handling ---
    def handle_enemy_turn(self):
        """Orchestrates the Enemy Phase, having each enemy unit act."""
        print("\n--- Enemy Turn ---")
        # Get list of active enemy units
        enemy_units_to_act = [u for u in self.units if u.team == 'Enemy' and u.can_act()]
        # Get list of valid player targets
        player_units = [u for u in self.units if u.team == 'Player' and u.is_alive and not u.is_captured and not u.has_escaped]

        if not player_units: # No targets left
            print("No player units remaining.")
            self.next_turn()
            return

        # Process each enemy unit
        for unit in enemy_units_to_act:
            # Double-check if unit can still act (might have been defeated by Vantage/Wrath from previous enemy action)
            if not unit.can_act(): continue
            print(f"\nEnemy {unit.name}'s action...")

            # --- AI DECISION MAKING ---
            chosen_action = self.decide_enemy_action(unit, player_units)

            # --- EXECUTE ACTION ---
            if chosen_action:
                action_type = chosen_action['type']
                move_target = chosen_action.get('move_target') # Might be None if attacking from current pos
                attack_target = chosen_action.get('attack_target') # Might be None if just moving

                # 1. Move (if specified)
                if move_target and (move_target[0] != unit.x or move_target[1] != unit.y):
                    print(f"Moving to {move_target}...")
                    # move_unit handles checking validity and printing messages
                    move_success = self.move_unit(unit, move_target[0], move_target[1])
                    # If move failed (e.g., path blocked unexpectedly), AI might need to reconsider or wait.
                    if not move_success:
                         print(f"{unit.name} failed to move, waiting instead."); unit.wait(); continue
                    if self.game_over: return # Check if game ended somehow (unlikely from move)

                # 2. Attack (if specified)
                if action_type == 'attack' and attack_target:
                    # Verify target is still valid and in range *after* moving
                    current_player_units = [u for u in self.units if u.team == 'Player' and u.is_alive and not u.is_captured and not u.has_escaped]
                    valid_target_obj = next((p for p in current_player_units if p == attack_target), None)

                    if valid_target_obj and self.distance(unit.x, unit.y, valid_target_obj.x, valid_target_obj.y) in unit.attack_range:
                         print(f"Attacks {valid_target_obj.name}!")
                         self.perform_combat(unit, valid_target_obj) # Handles action cost
                    else:
                         print(f"Target {attack_target.name} is invalid or out of range after moving.")
                         # If only moved but attack failed, ensure action is consumed
                         if not unit.has_acted: unit.set_acted()

                # 3. Move Only (If action was 'move' type)
                elif action_type == 'move':
                     if not unit.has_acted: # Ensure action cost if *only* moving
                          unit.set_acted()
                     print(f"{unit.name} finishes moving.")

                # 4. Wait (If no action decided or only action was invalid move)
                else: # Should only happen if action type wasn't move/attack, or if attack target became invalid before moving
                     print(f"{unit.name} waits.")
                     unit.wait()

            else: # No valid action found by AI
                print(f"{unit.name} waits.")
                unit.wait()

            if self.game_over: return # Check if game ended mid-enemy phase

        print("\n--- End Enemy Turn ---")
        self.next_turn()

    def decide_enemy_action(self, unit, potential_targets):
        """Determines best AI action: attack > move > wait. Returns action dict or None."""
        # 1. Check if can attack without moving
        best_attack_now = None
        if unit.equipped_weapon:
            current_targets = self.get_attack_targets(unit)
            possible_attacks_now = []
            for target in current_targets:
                 if target in potential_targets: # Make sure it's a valid player target
                     dmg_d, dmg_t, lethal, survives = self.predict_combat(unit, target, unit.x, unit.y) # Predict from current spot
                     score = self._score_combat_outcome(unit, target, dmg_d, dmg_t, lethal, survives, unit.x, unit.y, target.x, target.y)
                     if survives and score > -10: # Basic thresholding
                          possible_attacks_now.append({'type':'attack','score':score,'move_target':None,'attack_target':target})
            if possible_attacks_now:
                 possible_attacks_now.sort(key=lambda x:x['score'], reverse=True)
                 best_attack_now = possible_attacks_now[0]
                 print(f" AI Eval: Can attack {best_attack_now['attack_target'].name} from current spot (Score: {best_attack_now['score']:.1f}).")
                 # If a good immediate attack exists, maybe prioritize it over moving for a slightly better one?
                 # For now, we'll still evaluate moves.

        # 2. Evaluate moving THEN attacking
        reachable_squares = self.get_valid_moves(unit); reachable_squares[(unit.x, unit.y)] = 0; # Include current spot
        possible_move_attacks = []
        for move_x, move_y in reachable_squares:
            # Temporarily assume unit is at move_x, move_y to find targets
            potential_targets_after_move = []
            if unit.equipped_weapon:
                 for r in unit.attack_range:
                     for dx in range(-r,r+1): dy_abs=r-abs(dx);
                     for dy_sign in ([1,-1] if dy_abs!=0 else [1]): dy=dy_abs*dy_sign; cx,cy=move_x+dx,move_y+dy;
                     target_at_pos = self.get_unit_at(cx,cy) # Check who is there
                     if target_at_pos and target_at_pos in potential_targets and target_at_pos not in potential_targets_after_move:
                         # Check if defender is within range *of the moved position*
                         if self.distance(move_x, move_y, cx, cy) in unit.attack_range:
                             potential_targets_after_move.append(target_at_pos)

            # Evaluate combat for each target reachable after moving to (move_x, move_y)
            for target in potential_targets_after_move:
                dmg_d, dmg_t, lethal, survives = self.predict_combat(unit, target, move_x, move_y)
                score = self._score_combat_outcome(unit, target, dmg_d, dmg_t, lethal, survives, move_x, move_y, target.x, target.y)
                if survives and score > -10:
                     possible_move_attacks.append({'type':'attack','score':score,'move_target':(move_x,move_y),'attack_target':target})

        # 3. Compare best immediate attack vs best move-attack
        best_action = None
        if possible_move_attacks:
            possible_move_attacks.sort(key=lambda x:x['score'], reverse=True)
            best_move_attack = possible_move_attacks[0]
            print(f" AI Eval: Best move-attack option scores {best_move_attack['score']:.1f} vs {best_move_attack['attack_target'].name} from {best_move_attack['move_target']}.")
            if best_attack_now and best_attack_now['score'] >= best_move_attack['score'] - 5: # Prioritize attacking now unless moving is significantly better
                 best_action = best_attack_now
            else:
                 best_action = best_move_attack
        elif best_attack_now: # Only attack-now option was available
             best_action = best_attack_now

        # Return best attack action if found
        if best_action:
             # Prevent moving if already at the best spot
             if best_action['move_target'] == (unit.x, unit.y): best_action['move_target'] = None
             return best_action

        # 4. No suitable attack found - Move towards priority target
        print(" AI Eval: No suitable attack found. Determining best move...")
        move = self.find_best_move_towards_target(unit, potential_targets)
        return {'type': 'move', 'move_target': move} if move else None # Return move action or None (wait)

    def _score_combat_outcome(self, attacker, defender, dmg_dealt, dmg_taken, is_lethal, attacker_survives, atk_x, atk_y, def_x, def_y):
        """Calculates a score based on predicted combat outcome."""
        if not attacker_survives: return -float('inf') # Never choose actions that kill self
        score = 0
        if is_lethal: score += 100
        score += dmg_dealt * 1.5 # Damage dealt is good
        score -= dmg_taken * 1.2 # Damage taken is bad
        # Terrain Penalty (Target)
        target_terrain = self.get_terrain_props(def_x, def_y)
        score -= (target_terrain['defense'] * 5 + target_terrain['avoid'] * 0.5) # More refined penalty based on bonus
        # Terrain Bonus (Attacker - where they end turn)
        attacker_terrain = self.get_terrain_props(atk_x, atk_y)
        score += (attacker_terrain['defense'] * 3 + attacker_terrain['avoid'] * 0.3) # Bonus for ending safely
        # Skill Awareness Penalty
        if SKILL_WRATH in defender.skills and defender.hp - dmg_dealt <= defender.max_hp / 2 and dmg_dealt < defender.hp: score -= 50 # Avoid activating enemy Wrath if possible
        if SKILL_VANTAGE in defender.skills and defender.hp - dmg_dealt <= defender.max_hp / 2 and dmg_dealt < defender.hp: score -= 30 # Avoid activating enemy Vantage
        # Add bonus for defeating high-priority targets? (e.g., Leif)
        if is_lethal and defender.name == "Leif": score += 200
        return score

    # --- Combat Prediction (Updated for Ldr/PCC) ---
    def predict_combat(self, attacker, defender, ax, ay):
        """Predicts combat outcome: (dmg_dealt, dmg_taken, is_lethal, attacker_survives)."""
        dmg_d,dmg_t,lethal,survives = 0,0,False,True; wpn=attacker.equipped_weapon; if not wpn: return 0,0,False,True
        # Attacker Stats + Ldr
        astr=attacker.strength;amag=attacker.magic;askl=attacker.skill;aspd=attacker.speed;alck=attacker.luck;acon=attacker.constitution; wt=wpn.weight if wpn else 0; p=max(0,wt-acon); eff_as=max(0,aspd-p); b_crit=attacker.crit_rate_base; b_hit=attacker.hit_rate; ldr_a=self.calculate_leadership_bonus(attacker); atk_pcc=attacker.pcc
        # Defender Stats + Terrain + Ldr
        d_trn=self.get_terrain_props(defender.x,defender.y); d_base_avo=defender.avoid; ldr_d=self.calculate_leadership_bonus(defender); eff_avo=d_base_avo+d_trn['avoid']+ldr_d; is_phys_atk=wpn.is_physical(); b_def=defender.defense if is_phys_atk else defender.resistance; t_def=d_trn['defense'] if is_phys_atk else 0; eff_mit=b_def+t_def; d_crit_avo=defender.crit_avoid; def_wpn=defender.equipped_weapon; def_pcc=defender.pcc
        # WT
        wt_h_a, wt_m_a = self.calculate_weapon_triangle(wpn, def_wpn)
        eff_hit=b_hit+wt_h_a+ldr_a
        # Attacker 1st strike prediction
        acc=max(0,min(100,eff_hit-eff_avo)); pcc_b=max(0,eff_as-defender.attack_speed)*atk_pcc; eff_crit=b_crit+pcc_b; crit_c=max(0,min(100,eff_crit-d_crit_avo))
        if acc > 30: # Assume hit if chance > 30%
            a_pwr_s=astr if is_phys_atk else amag; eff_a_pwr=a_pwr_s+wpn.might+wt_m_a; p_dmg=max(0,eff_a_pwr-eff_mit)
            # Simplified crit prediction: add expected crit damage? (p_dmg * crit_c/100 * 2)
            expected_crit_dmg = p_dmg * (crit_c / 100.0) * 2
            dmg_d += p_dmg + expected_crit_dmg # Add expected crit damage

        # Defender counter prediction
        dist=self.distance(ax,ay,defender.x,defender.y)
        if defender.is_alive and def_wpn and dist in def_wpn.range:
            a_trn=self.get_terrain_props(ax,ay); d_hit_base=defender.hit_rate; d_mt_base=defender.attack_power; d_crit_base=defender.crit_rate_base; def_as=defender.attack_speed;
            wt_h_d, wt_m_d = self.calculate_weapon_triangle(def_wpn, wpn)
            d_hit=d_hit_base+wt_h_d+ldr_d; d_mt=d_mt_base+wt_m_d; d_pcc_b=max(0,def_as-eff_as)*def_pcc; d_eff_crit=d_crit_base+d_pcc_b
            a_base_avo=attacker.avoid; a_avo=a_base_avo+a_trn['avoid']+ldr_a; is_phys_def=def_wpn.is_physical(); a_mit_s=attacker.defense if is_phys_def else attacker.resistance; a_trn_def=a_trn['defense'] if is_phys_def else 0; a_eff_mit=a_mit_s+a_trn_def; a_crit_avo=attacker.crit_avoid
            d_acc=max(0,min(100,d_hit-a_avo)); d_crit_c=max(0,min(100,d_eff_crit-a_crit_avo))
            if d_acc > 30: # Assume hit
                 p_ctr_dmg=max(0,d_mt-a_eff_mit);
                 exp_ctr_crit_dmg = p_ctr_dmg * (d_crit_c / 100.0) * 2
                 dmg_t += p_ctr_dmg + exp_ctr_crit_dmg # Add expected crit damage

        # Follow-ups (Simplified prediction using expected damage)
        if eff_as-defender.attack_speed>=FOLLOW_UP_THRESHOLD and acc > 30: dmg_d += p_dmg + expected_crit_dmg
        if defender.is_alive and def_wpn and dist in def_wpn.range and defender.attack_speed-eff_as>=FOLLOW_UP_THRESHOLD and d_acc > 30: dmg_t += p_ctr_dmg + exp_ctr_crit_dmg

        # Round damage for prediction outcome
        dmg_d, dmg_t = math.floor(dmg_d), math.floor(dmg_t)
        if dmg_d>=defender.hp: lethal=True
        if dmg_t>=attacker.hp: survives=False
        return dmg_d,dmg_t,lethal,survives

    # --- Find Best Move (Simplified Manhattan Heuristic) ---
    def find_best_move_towards_target(self, unit, potential_targets):
        """Finds reachable square closest (Manhattan dist) to priority target."""
        if not potential_targets: return None
        priority_target = None # Find Leif or closest target (same logic as before)
        leif=next((t for t in potential_targets if t.name=="Leif"),None);
        if leif: priority_target=leif
        else: min_d=float('inf'); [min_d:=d, priority_target:=t for t in potential_targets if (d:=self.distance(unit.x,unit.y,t.x,t.y))<min_d]
        if not priority_target: return None

        reachable = self.get_valid_moves(unit)
        if not reachable: print(f" AI Move: Cannot move."); return None # Cannot move at all

        best_move = None
        # Initialize with current distance, favoring staying put if no closer move found
        min_dist_to_target = self.distance(unit.x, unit.y, priority_target.x, priority_target.y)

        # Check reachable squares for closer distance
        for move_coord in reachable:
            dist = self.distance(move_coord[0], move_coord[1], priority_target.x, priority_target.y)
            # Use <= to allow moving to an equally close square if current isn't ideal
            # or just < to only move if strictly closer? Let's use <
            if dist < min_dist_to_target:
                 min_dist_to_target = dist
                 best_move = move_coord
            # Optional tie-breaker: if dist == min_dist_to_target, prefer lower move cost?
            # elif dist == min_dist_to_target and best_move and reachable[move_coord] < reachable[best_move]:
            #      best_move = move_coord

        if best_move: print(f" AI Move: Best towards {priority_target.name} is {best_move} (dist {min_dist_to_target}).")
        else: print(f" AI Move: No move gets closer to {priority_target.name}.")

        return best_move

    # Run Game (Unchanged)
    def run_game(self):
        print("Starting Thracia 776 Simulation (Chapter 1)...")
        while not self.game_over:
            self.display_map() # Display map at start of each phase
            if self.current_turn == 'Player':
                self.handle_player_turn()
            else: # Enemy Turn
                self.handle_enemy_turn()
        # Game Over
        print("\n" + "="*30); print(" " * 10 + "GAME OVER"); print("="*30)
        self.display_map() # Show final map state
        print(f"Result: {self.winner} Wins!")
        print("="*30)


# --- Setup and Run ---
if __name__ == "__main__":
    # Define constants for house rewards and reinforcements if not already done
    # (Assuming they are defined above EventManager/Game class)

    # Create Game Instance
    game = Game(DEFAULT_MAP_LAYOUT)

    # Add Units (with PCC and Leadership Stars)
    leif_inv=[copy.deepcopy(IRON_SWORD),copy.deepcopy(VULNERARY)]; game.add_unit(Unit(name="Leif",symbol='L',team='Player',max_hp=22,strength=5,magic=0,skill=6,speed=7,luck=5,defense=4,resistance=1,constitution=6,move=6, pcc=1, leadership_stars=1, x=11,y=13, initial_inventory=leif_inv, required_to_escape=True))
    eyvel_inv=[copy.deepcopy(STEEL_SWORD),copy.deepcopy(VULNERARY)]; game.add_unit(Unit(name="Eyvel",symbol='E',team='Player',max_hp=28,strength=9,magic=5,skill=12,speed=13,luck=8,defense=8,resistance=6,constitution=7,move=7, pcc=3, leadership_stars=2, x=13,y=11, initial_inventory=eyvel_inv, initial_skills=[SKILL_ADEPT]))
    halvan_inv=[copy.deepcopy(IRON_AXE),copy.deepcopy(VULNERARY)]; game.add_unit(Unit(name="Halvan",symbol='H',team='Player',max_hp=32,strength=10,magic=0,skill=7,speed=8,luck=5,defense=7,resistance=1,constitution=12,move=5, pcc=2, leadership_stars=0, x=10,y=14, initial_inventory=halvan_inv, initial_skills=[SKILL_VANTAGE]))
    osian_inv=[copy.deepcopy(PUGI)]; game.add_unit(Unit(name="Osian",symbol='O',team='Player',max_hp=30,strength=9,magic=0,skill=5,speed=6,luck=4,defense=6,resistance=0,constitution=11,move=5, pcc=4, leadership_stars=0, x=12,y=12, initial_inventory=osian_inv, initial_skills=[SKILL_WRATH]))
    dagdar_inv=[copy.deepcopy(STEEL_AXE),copy.deepcopy(VULNERARY)]; game.add_unit(Unit(name="Dagdar",symbol='D',team='Player',max_hp=35,strength=11,magic=0,skill=8,speed=9,luck=6,defense=9,resistance=2,constitution=14,move=6, pcc=1, leadership_stars=3, x=3, y=1, initial_inventory=dagdar_inv))
    tanya_inv=[copy.deepcopy(IRON_BOW)]; game.add_unit(Unit(name="Tanya",symbol='T',team='Player',max_hp=18,strength=4,magic=0,skill=6,speed=10,luck=7,defense=3,resistance=0,constitution=5,move=6, pcc=3, leadership_stars=0, x=5, y=1, initial_inventory=tanya_inv))
    # Enemies (Add PCC/Ldr stars - assume 0 for bandits, 1 PCC for boss?)
    bandit1_inv=[copy.deepcopy(IRON_AXE)]; game.add_unit(Unit(name="Bandit",symbol='b',team='Enemy',max_hp=20,strength=6,magic=0,skill=3,speed=5,luck=2,defense=3,resistance=0,constitution=9,move=5, pcc=0, leadership_stars=0, x=12,y=7, initial_inventory=bandit1_inv))
    bandit2_inv=[copy.deepcopy(IRON_AXE)]; game.add_unit(Unit(name="Bandit",symbol='b',team='Enemy',max_hp=21,strength=7,magic=0,skill=2,speed=6,luck=1,defense=4,resistance=0,constitution=10,move=5, pcc=0, leadership_stars=0, x=12,y=8, initial_inventory=bandit2_inv))
    bandit3_inv=[copy.deepcopy(IRON_LANCE)]; game.add_unit(Unit(name="Bandit",symbol='b',team='Enemy',max_hp=19,strength=5,magic=0,skill=4,speed=5,luck=3,defense=3,resistance=1,constitution=8,move=5, pcc=0, leadership_stars=0, x=8, y=10, initial_inventory=bandit3_inv))
    weissman_inv=[copy.deepcopy(STEEL_AXE),copy.deepcopy(VULNERARY)]; game.add_unit(Unit(name="Weissman",symbol='W',team='Enemy',max_hp=38,strength=12,magic=0,skill=6,speed=7,luck=3,defense=10,resistance=2,constitution=13,move=5, pcc=1, leadership_stars=0, x=6, y=12, initial_inventory=weissman_inv))

    # Auto-equip first weapon
    for unit in game.units:
        if unit.inventory and isinstance(unit.inventory[0], Weapon):
            unit.equip_item(0) # Doesn't cost action/fatigue

    # Start the game loop
    game.run_game()