from .item import Item
from .item_data import ItemType

class Scroll(Item):
    """Represents a scroll that modifies growth rates."""

    def __init__(self,
                 item_id: str,
                 name: str,
                 cost: int,
                 icon_id: str,
                 description: str,
                 growth_hp_modifier: int = 0,
                 growth_strength_modifier: int = 0,
                 growth_magic_modifier: int = 0,
                 growth_skill_modifier: int = 0,
                 growth_speed_modifier: int = 0,
                 growth_defense_modifier: int = 0,
                 growth_constitution_modifier: int = 0,
                 growth_luck_modifier: int = 0,
                 growth_movement_modifier: int = 0):
        # Scrolls typically have infinite uses or are not "used" in the traditional sense.
        # Their effect is passive while held. Setting uses to -1 (infinite).
        super().__init__(item_id, name, ItemType.SCROLL, uses=-1, max_uses=-1, cost=cost, icon_id=icon_id, description=description)

        # TEST: All growth modifiers must be integers (can be 0, positive, or negative).
        # (Python typing helps, actual validation might occur at data loading)
        self.growth_hp_modifier: int = growth_hp_modifier
        self.growth_strength_modifier: int = growth_strength_modifier
        self.growth_magic_modifier: int = growth_magic_modifier
        self.growth_skill_modifier: int = growth_skill_modifier
        self.growth_speed_modifier: int = growth_speed_modifier
        self.growth_defense_modifier: int = growth_defense_modifier
        self.growth_constitution_modifier: int = growth_constitution_modifier
        self.growth_luck_modifier: int = growth_luck_modifier
        self.growth_movement_modifier: int = growth_movement_modifier

    # Scrolls are typically always "equipped" if in inventory (their effect is passive).
    # The "Hold" mechanic in Thracia 776 means they simply need to be in the unit's personal inventory.
    # Their effect is applied during level-up calculations.
    # No specific 'apply_effect' method here; logic resides in level-up process.
    # TEST: Scroll in inventory correctly modifies growth rates on level up. (Tested in Character/Level-up system)

    def __str__(self) -> str:
        modifiers = []
        if self.growth_hp_modifier: modifiers.append(f"HP:{self.growth_hp_modifier:+}%")
        if self.growth_strength_modifier: modifiers.append(f"Str:{self.growth_strength_modifier:+}%")
        if self.growth_magic_modifier: modifiers.append(f"Mag:{self.growth_magic_modifier:+}%")
        if self.growth_skill_modifier: modifiers.append(f"Skl:{self.growth_skill_modifier:+}%")
        if self.growth_speed_modifier: modifiers.append(f"Spd:{self.growth_speed_modifier:+}%")
        if self.growth_defense_modifier: modifiers.append(f"Def:{self.growth_defense_modifier:+}%")
        if self.growth_constitution_modifier: modifiers.append(f"Con:{self.growth_constitution_modifier:+}%")
        if self.growth_luck_modifier: modifiers.append(f"Luk:{self.growth_luck_modifier:+}%")
        if self.growth_movement_modifier: modifiers.append(f"Mov:{self.growth_movement_modifier:+}%")
        return f"{self.name} (Scroll: {', '.join(modifiers)})"

    def __repr__(self) -> str:
        return f"<Scroll {self.item_id}: {self.name}>"