from typing import Dict, List, Optional, Any
from .models import Item, ItemType, WeaponType, WeaponRank
from .static_data_loader import StaticDataLoader
import uuid

class ItemManager:
    """
    Manages Item instances in the game, including creation, tracking, and updates.
    """
    def __init__(self, static_loader: StaticDataLoader):
        """
        Initializes the ItemManager.
        Args:
            static_loader: An instance of StaticDataLoader to fetch item definitions.
        """
        self.static_loader = static_loader
        self._items: Dict[str, Item] = {}  # Maps instance_id to Item objects
        self._convoy_items: List[str] = []  # List of item instance_ids in convoy

    def create_item(self, item_id: str, instance_id: Optional[str] = None) -> Optional[Item]:
        """
        Creates a new Item instance based on static data.
        Args:
            item_id: The ID of the item type to create (e.g., "iron_sword").
            instance_id: Optional unique ID for this specific instance. If None, a UUID will be generated.
        Returns:
            The created Item instance, or None if the item definition was not found.
        """
        # Get item definition from static data
        item_def = self.static_loader.get_item_definition(item_id)
        if not item_def:
            print(f"Error: Item definition for '{item_id}' not found.")
            return None

        # Generate instance ID if not provided
        if instance_id is None:
            instance_id = str(uuid.uuid4())

        # Create Item instance from definition
        try:
            # Extract basic properties
            name = item_def.get("name", item_id)
            item_type_str = item_def.get("type", "OTHER")
            
            # Convert string to enum
            try:
                item_type = ItemType[item_type_str.upper()]
            except KeyError:
                print(f"Warning: Unknown item type '{item_type_str}'. Using OTHER.")
                item_type = ItemType.OTHER

            # Handle weapon-specific properties
            weapon_type = None
            if item_type in [ItemType.WEAPON, ItemType.STAFF]:
                weapon_type_str = item_def.get("weapon_type", None)
                if weapon_type_str:
                    try:
                        weapon_type = WeaponType[weapon_type_str.upper()]
                    except KeyError:
                        print(f"Warning: Unknown weapon type '{weapon_type_str}'.")

            # Handle rank requirement
            rank_req_str = item_def.get("rank_req", "NONE")
            try:
                rank_req = WeaponRank[rank_req_str.upper()]
            except KeyError:
                print(f"Warning: Unknown weapon rank '{rank_req_str}'. Using NONE.")
                rank_req = WeaponRank.NONE

            # Create the item
            item = Item(
                id=item_id,
                name=name,
                type=item_type,
                instance_id=instance_id,
                weapon_type=weapon_type,
                might=item_def.get("might", 0),
                hit=item_def.get("hit", 0),
                crit=item_def.get("crit", 0),
                weight=item_def.get("weight", 0),
                range_min=item_def.get("range_min", 1),
                range_max=item_def.get("range_max", 1),
                uses=item_def.get("uses", None),
                max_uses=item_def.get("max_uses", None),
                rank_req=rank_req,
                effects=item_def.get("effects", []),
                value=item_def.get("value", 0)
            )

            # Store the item
            self._items[instance_id] = item
            return item

        except Exception as e:
            print(f"Error creating item '{item_id}': {e}")
            return None

    def get_item(self, instance_id: str) -> Optional[Item]:
        """
        Retrieves an Item instance by its instance ID.
        Args:
            instance_id: The unique ID of the item instance.
        Returns:
            The Item instance, or None if not found.
        """
        return self._items.get(instance_id)

    def update_item_durability(self, instance_id: str, uses_change: int = -1) -> bool:
        """
        Updates the durability (uses) of an item.
        Args:
            instance_id: The unique ID of the item instance.
            uses_change: The change in uses (negative for consumption, positive for repair).
        Returns:
            True if the update was successful, False otherwise.
        """
        item = self.get_item(instance_id)
        if not item:
            print(f"Error: Item with instance ID '{instance_id}' not found.")
            return False

        # If item doesn't use durability, do nothing
        if item.uses is None or item.max_uses is None:
            return True

        # Update uses
        item.uses += uses_change
        
        # Ensure uses doesn't exceed max_uses
        if item.uses > item.max_uses:
            item.uses = item.max_uses
            
        # Check if item is broken
        if item.uses <= 0:
            print(f"Item '{item.name}' has broken!")
            # In some implementations, you might want to remove the item here
            # self.remove_item(instance_id)
            item.uses = 0
            
        return True

    def add_to_convoy(self, instance_id: str) -> bool:
        """
        Adds an item to the convoy.
        Args:
            instance_id: The unique ID of the item instance.
        Returns:
            True if the item was added successfully, False otherwise.
        """
        if instance_id not in self._items:
            print(f"Error: Item with instance ID '{instance_id}' not found.")
            return False
            
        if instance_id in self._convoy_items:
            print(f"Warning: Item already in convoy.")
            return True
            
        self._convoy_items.append(instance_id)
        return True

    def remove_from_convoy(self, instance_id: str) -> bool:
        """
        Removes an item from the convoy.
        Args:
            instance_id: The unique ID of the item instance.
        Returns:
            True if the item was removed successfully, False otherwise.
        """
        if instance_id not in self._convoy_items:
            print(f"Error: Item with instance ID '{instance_id}' not found in convoy.")
            return False
            
        self._convoy_items.remove(instance_id)
        return True

    def get_convoy_items(self) -> List[Item]:
        """
        Gets all items in the convoy.
        Returns:
            A list of Item instances in the convoy.
        """
        return [self._items[instance_id] for instance_id in self._convoy_items if instance_id in self._items]

    def remove_item(self, instance_id: str) -> bool:
        """
        Removes an item from the system entirely.
        Args:
            instance_id: The unique ID of the item instance.
        Returns:
            True if the item was removed successfully, False otherwise.
        """
        if instance_id not in self._items:
            print(f"Error: Item with instance ID '{instance_id}' not found.")
            return False
            
        # Remove from convoy if present
        if instance_id in self._convoy_items:
            self._convoy_items.remove(instance_id)
            
        # Remove from items dictionary
        del self._items[instance_id]
        return True