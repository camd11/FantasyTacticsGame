from typing import List, TYPE_CHECKING, Optional

from .item import Item
from .item_data import ItemType, UsableEffectType, ClassID

if TYPE_CHECKING:
    from src.character_system.unit_instance import UnitInstance # Forward reference


class UsableItem(Item):
    """Represents a consumable item."""

    def __init__(self,
                 item_id: str,
                 name: str,
                 uses: int,
                 max_uses: int,
                 cost: int,
                 icon_id: str,
                 description: str,
                 effect: 'UsableEffectType',
                 effect_potency: int,
                 promotion_target_classes: Optional[List[ClassID]] = None,
                 duration_turns: int = 0): # 0 or -1 if permanent or instant
        super().__init__(item_id, name, ItemType.CONSUMABLE, uses, max_uses, cost, icon_id, description)

        # TEST: Effect must be a valid UsableEffectType. (Python Enum handles this)
        # TEST: If Effect is PromotionItem, PromotionTargetClasses must not be empty and contain valid ClassIDs.
        if effect == UsableEffectType.PROMOTION_ITEM and not promotion_target_classes:
            raise ValueError("PromotionItem must have PromotionTargetClasses.")
        # TEST: If DurationTurns > 0, effect should be temporary. (Logic check during application)

        self.effect: UsableEffectType = effect
        self.effect_potency: int = effect_potency
        self.promotion_target_classes: List['ClassID'] = promotion_target_classes if promotion_target_classes else []
        self.duration_turns: int = duration_turns

    def apply_effect(self, target_unit: 'UnitInstance') -> bool:
        """
        Consumes the item and applies its effect.
        Returns True if effect applied successfully, False otherwise.
        TEST: Effect applies correctly and item is consumed.
        TEST: Temporary effects apply for correct duration.
        TEST: Promotion items correctly check class eligibility.
        """
        # Placeholder for actual effect logic.
        # This method would typically:
        # 1. Check if the target_unit can benefit from the item.
        # 2. Apply the stat changes, healing, status, or promotion.
        # 3. Decrement item uses or remove it if uses reach 0.

        # For now, just simulate consumption if uses > 0
        if self.uses > 0:
            self.uses -= 1
            return True
        elif self.uses == -1: # Infinite uses
            return True
        return False # No uses left

    def can_be_used_by(self, unit: 'UnitInstance') -> bool:
        """
        Checks if the unit can use this consumable item.
        Most consumables can be used by anyone, but some (like promotion items)
        have specific class restrictions.
        """
        if self.effect == UsableEffectType.PROMOTION_ITEM:
            # TODO: Implement check against unit.current_class and self.promotion_target_classes
            # For now, assume it's usable if base check passes and it's a promotion item.
            # This check should ideally be more robust in the ApplyEffect or a pre-check.
            pass # Placeholder for promotion eligibility check
        return super().can_be_used_by(unit)

    def __str__(self) -> str:
        return f"{self.name} (Effect: {self.effect.name}, Potency: {self.effect_potency}, Uses: {self.uses}/{self.max_uses})"

    def __repr__(self) -> str:
        return f"<UsableItem {self.item_id}: {self.name}>"