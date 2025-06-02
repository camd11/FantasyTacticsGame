from typing import List, TYPE_CHECKING, Optional, Dict
from .item import Item
from .item_data import (
    ItemType, WeaponRankID, WeaponTypeID, TargetAttribute,
    WeaponSpecialProperty, RangeData, ItemStatBonuses, SkillID
)

if TYPE_CHECKING:
    from src.character_system.unit_instance import UnitInstance # Forward reference


class Weapon(Item):
    """Represents a weapon."""

    _weapon_type_to_item_type_map: Dict[WeaponTypeID, ItemType] = {
        WeaponTypeID.SWORD: ItemType.SWORD,
        WeaponTypeID.LANCE: ItemType.LANCE,
        WeaponTypeID.AXE: ItemType.AXE,
        WeaponTypeID.BOW: ItemType.BOW,
        WeaponTypeID.DAGGER: ItemType.DAGGER, # Or map to SWORD if preferred
        WeaponTypeID.FIRE_TOME: ItemType.FIRE_TOME,
        WeaponTypeID.THUNDER_TOME: ItemType.THUNDER_TOME,
        WeaponTypeID.WIND_TOME: ItemType.WIND_TOME,
        WeaponTypeID.LIGHT_TOME: ItemType.LIGHT_TOME,
        WeaponTypeID.DARK_TOME: ItemType.DARK_TOME,
        WeaponTypeID.BALLISTA: ItemType.BOW, # Ballistae are a type of Bow
    }

    def __init__(self,
                 item_id: str,
                 name: str,
                 uses: int,
                 max_uses: int,
                 cost: int,
                 icon_id: str,
                 description: str,
                 weapon_type: WeaponTypeID,
                 might: int,
                 hit_rate: int,
                 critical_rate: int,
                 weight: int,
                 range_data: RangeData,
                 required_rank: WeaponRankID,
                 effectiveness: Optional[List[TargetAttribute]] = None,
                 granted_skills: Optional[List[SkillID]] = None,
                 stat_bonuses: Optional[ItemStatBonuses] = None,
                 is_magic_damage: bool = False,
                 transforms_to_id: Optional[str] = None,
                 special_properties: Optional[List[WeaponSpecialProperty]] = None,
                 # item_type is now determined internally
                 ):

        derived_item_type = self._weapon_type_to_item_type_map.get(weapon_type)
        if derived_item_type is None:
            # This case should ideally not be reached if WeaponTypeID is comprehensive
            # and the map is complete.
            raise ValueError(f"Cannot map WeaponTypeID {weapon_type} to a base ItemType.")

        super().__init__(item_id, name, derived_item_type, uses, max_uses, cost, icon_id, description)

        # TEST: Weapon properties (Mt, Hit, Wt, Range) must be within reasonable game balance. (Data validation)
        # TEST: RequiredRank must be a valid WeaponRankID. (Python Enum handles this)
        # TEST: Uses should be -1 for unbreakable weapons, or a positive integer. (Handled in base Item)

        self.weapon_type: WeaponTypeID = weapon_type
        self.might: int = might
        self.hit_rate: int = hit_rate
        self.critical_rate: int = critical_rate
        self.weight: int = weight
        self.range_data: RangeData = range_data
        self.required_rank: WeaponRankID = required_rank
        self.effectiveness: List[TargetAttribute] = effectiveness if effectiveness else []
        self.granted_skills: List[SkillID] = granted_skills if granted_skills else []
        self.stat_bonuses: ItemStatBonuses = stat_bonuses if stat_bonuses else ItemStatBonuses()
        self.is_magic_damage: bool = is_magic_damage
        self.transforms_to_id: Optional[str] = transforms_to_id
        self.special_properties: List[WeaponSpecialProperty] = special_properties if special_properties else []

    def can_be_used_by(self, unit: 'UnitInstance') -> bool:
        """
        Checks if the unit can use/equip this weapon based on weapon rank.
        Further checks like class restrictions might be handled at a higher level or in UnitInstance.
        """
        # This is a simplified check. A full check would involve:
        # 1. Getting the unit's weapon rank for this self.weapon_type.
        # 2. Comparing it with self.required_rank.
        # For now, assume it's usable if the base item check passes.
        # TODO: Implement actual weapon rank check.
        # from src.character_system.weapon_rank import WeaponRank # Example
        # unit_rank = unit.get_weapon_rank(self.weapon_type)
        # return super().can_be_used_by(unit) and unit_rank >= self.required_rank
        return super().can_be_used_by(unit)

    def __str__(self) -> str:
        return f"{self.name} (Mt:{self.might} Hit:{self.hit_rate} Crit:{self.critical_rate} Wt:{self.weight} Rng:{self.range_data} Uses:{self.uses}/{self.max_uses})"

    def __repr__(self) -> str:
        return f"<Weapon {self.item_id}: {self.name}>"