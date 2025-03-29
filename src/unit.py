class Unit:
    """
    Represents a character unit on the map.
    """
    def __init__(self, unit_id, name, affiliation, stats, position, inventory=None, status=None):
        self.unit_id = unit_id # Unique identifier
        self.name = name
        self.affiliation = affiliation # 'player', 'enemy', 'npc'
        
        # Base Stats (example structure, adjust as needed)
        self.max_hp = stats.get('hp', 1)
        self.strength = stats.get('str', 0)
        self.magic = stats.get('mag', 0)
        self.skill = stats.get('skl', 0)
        self.speed = stats.get('spd', 0)
        self.luck = stats.get('lck', 0)
        self.defense = stats.get('def', 0)
        self.build = stats.get('bld', 0) # For capturing
        self.move = stats.get('mov', 0)
        self.constitution = stats.get('con', 0) # For rescue/weight

        # Current State
        self.current_hp = self.max_hp
        self.x, self.y = position # Position on the map

        # Inventory and Status
        self.inventory = inventory if inventory is not None else [] # List of Item objects
        self.status = status if status is not None else {} # Dict for statuses like 'poisoned', 'is_captured', 'carrying_unit_id'
        self.equipped_weapon = None # Will hold an Item object

        # Turn-based state
        self.has_moved = False
        self.has_acted = False

    def __repr__(self):
        return f"{self.name}({self.affiliation}@{self.x},{self.y} HP:{self.current_hp}/{self.max_hp})"

    def reset_turn(self):
        """Resets movement and action flags for the start of a new turn."""
        self.has_moved = False
        self.has_acted = False

    # Placeholder methods for actions - to be implemented later
    # def move(self, new_x, new_y): pass
    # def attack(self, target_unit): pass
    # def capture(self, target_unit): pass
    # def drop(self): pass
    # def trade(self, other_unit, item_give, item_receive): pass
    # def use_item(self, item_index, target=None): pass
    # def equip_item(self, item_index): pass