from typing import TYPE_CHECKING
from .item_data import ItemType

if TYPE_CHECKING:
    from src.character_system.unit_instance import UnitInstance  # Forward reference


class Item:
    """Represents any item in the game."""

    def __init__(self,
                 item_id: str,
                 name: str,
                 item_type: 'ItemType',
                 uses: int,
                 max_uses: int,
                 cost: int,
                 icon_id: str, # Placeholder for IconID type
                 description: str):
        # TEST: ItemID must be unique. (Handled by data loading/validation)
        # TEST: Name must not be empty.
        if not name:
            raise ValueError("Item name cannot be empty.")
        # TEST: Uses must be non-negative (or special value for infinite).
        if uses < -1: # -1 for infinite uses
            raise ValueError("Item uses must be >= -1.")

        self.item_id: str = item_id
        self.name: str = name
        self.item_type: ItemType = item_type
        self.uses: int = uses
        self.max_uses: int = max_uses
        self.cost: int = cost
        self.icon_id: str = icon_id
        self.description: str = description

    def can_be_used_by(self, unit: 'UnitInstance') -> bool:
        """
        Checks if the unit can use/equip this item
        (e.g., weapon rank, class restrictions).
        TEST: Correctly determines usability based on unit.
        """
        # Base implementation, to be overridden by subclasses
        # For now, assume any unit can use any non-specific item
        # Specific checks (like weapon rank for Weapons) will be in subclasses.
        return True

    def __str__(self) -> str:
        return f"{self.name} ({self.uses}/{self.max_uses} uses)"

    def __repr__(self) -> str:
        return f"<Item {self.item_id}: {self.name}>"