from typing import TYPE_CHECKING, Optional

from .item import Item
from .item_data import ItemType, WeaponRankID, RangeData, StaffEffectType

if TYPE_CHECKING:
    from src.character_system.unit_instance import UnitInstance # Forward reference
    # from src.character_system.character_stats import CharacterStats # If UserStats is a specific class


class Staff(Item):
    """Represents a staff."""

    def __init__(self,
                 item_id: str,
                 name: str,
                 uses: int,
                 max_uses: int,
                 cost: int,
                 icon_id: str,
                 description: str,
                 effect: 'StaffEffectType',
                 effect_potency: int,
                 range_data: 'RangeData',
                 required_rank: 'WeaponRankID',
                 experience_gain: int):
        super().__init__(item_id, name, ItemType.STAFF, uses, max_uses, cost, icon_id, description)

        # TEST: Effect must be a valid StaffEffectType. (Python Enum handles this)
        # TEST: RequiredRank must be a valid WeaponRankID. (Python Enum handles this)

        self.effect: StaffEffectType = effect
        self.effect_potency: int = effect_potency
        self.range_data: RangeData = range_data # This might be a base range, actual range can be dynamic
        self.required_rank: WeaponRankID = required_rank
        self.experience_gain: int = experience_gain

    def calculate_range(self, user_stats: Optional[object] = None) -> RangeData: # Replace 'object' with actual UserStats type
        """
        Calculates the staff's effective range.
        Some staves have range based on Mag/2 etc.
        TEST: Range calculation must be correct.
        """
        # Placeholder: For now, returns the base range.
        # Actual implementation would use user_stats.
        # Example:
        # if self.effect == StaffEffectType.SOME_MAG_BASED_STAFF and user_stats:
        #     mag = getattr(user_stats, 'magic', 0) # Assuming a 'magic' attribute
        #     dynamic_max_range = mag // 2
        #     return RangeData(self.range_data.min_range, dynamic_max_range)
        return self.range_data

    def can_be_used_by(self, unit: 'UnitInstance') -> bool:
        """
        Checks if the unit can use/equip this staff based on staff rank.
        """
        # TODO: Implement actual staff rank check, similar to Weapon.
        # unit_rank = unit.get_weapon_rank(ItemType.STAFF) # or a specific staff rank type
        # return super().can_be_used_by(unit) and unit_rank >= self.required_rank
        return super().can_be_used_by(unit)

    def __str__(self) -> str:
        return f"{self.name} (Effect: {self.effect.name}, Range: {self.range_data}, Uses: {self.uses}/{self.max_uses})"

    def __repr__(self) -> str:
        return f"<Staff {self.item_id}: {self.name}>"