"""
Inventory System Module

This module manages all aspects of items held by units, including adding, removing, equipping,
using, and trading items. It also handles item durability and special item interactions like
repair and the unique "Broken" state in Thracia 776.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union

# Import necessary modules/classes
from src.core_engine.game_state import GameStateManager, ItemInstance, StatusEffectEnum, ObjectStateEnum
from src.core_engine.data_provider import DataProvider, ItemTypeEnum, RankEnum, WeaponTypeEnum, TerrainTypeEnum

# Constants
WEAPON = ItemTypeEnum.WEAPON
STAFF = ItemTypeEnum.STAFF
CONSUMABLE = ItemTypeEnum.CONSUMABLE
KEY = ItemTypeEnum.KEY
SCROLL = ItemTypeEnum.SCROLL

# Maximum inventory size
MAX_INVENTORY_SIZE = 7  # Thracia 776 typically limits unit inventory size to 7 items

class InventorySystem:
    """
    Manages all aspects of items held by units, including adding, removing, equipping,
    using, and trading items.
    """
    
    def __init__(self):
        """Initialize the InventorySystem."""
        self.gameStateManager = None
        self.dataProvider = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, dataProvider_instance: DataProvider) -> None:
        """
        Initialize the InventorySystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        logging.info("InventorySystem initialized.")
    
    # --- Item Management ---
    
    def add_item_to_inventory(self, unit_id: str, item_id: str, durability: Optional[int] = None) -> bool:
        """
        Add an item to a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_id: ID of the item to add
            durability: Current durability of the item (uses max durability if None)
            
        Returns:
            True if the item was added successfully, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            logging.warning(f"Cannot add item: Unit {unit_id} not found")
            return False
        
        # Check inventory limit
        if len(unit.inventory) >= MAX_INVENTORY_SIZE:
            logging.info(f"Inventory full for unit {unit_id}")
            return False
        
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            logging.warning(f"Invalid item_id {item_id} for add_item")
            return False
        
        # Create item instance
        instance = ItemInstance(
            item_id=item_id,
            current_durability=durability if durability is not None else item_data.max_durability
        )
        
        # Add to inventory
        unit.inventory.append(instance)
        logging.info(f"Added item {item_data.name} to unit {unit_id}")
        return True
    
    def remove_item_from_inventory(self, unit_id: str, item_index: int) -> Optional[ItemInstance]:
        """
        Remove an item from a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_index: Index of the item in the inventory
            
        Returns:
            The removed ItemInstance or None if the operation failed
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            logging.warning(f"Cannot remove item: Invalid unit or item index")
            return None
        
        # Remove the item
        removed_instance = unit.inventory.pop(item_index)
        
        # Update equipped weapon index if needed
        if unit.equipped_weapon_index == item_index:
            self.unequip_item(unit_id)
        elif unit.equipped_weapon_index > item_index:
            # Adjust equipped index if item removed was before it
            unit.equipped_weapon_index -= 1
        
        logging.info(f"Removed item at index {item_index} from unit {unit_id}")
        return removed_instance
    
    def equip_item(self, unit_id: str, item_index: int) -> bool:
        """
        Equip an item from a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_index: Index of the item in the inventory
            
        Returns:
            True if the item was equipped successfully, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            logging.warning(f"Cannot equip item: Invalid unit or item index")
            return False
        
        item_instance = unit.inventory[item_index]
        item_data = self.dataProvider.get_item_data(item_instance.item_id)
        
        # Check if item is a weapon or staff
        if item_data.type not in [WEAPON, STAFF]:
            logging.info(f"Cannot equip item type {item_data.type}")
            return False
        
        # Check weapon rank requirement
        if hasattr(item_data, 'weapon_type') and hasattr(item_data, 'required_rank'):
            required_rank = item_data.required_rank
            unit_rank = unit.weapon_ranks.get(item_data.weapon_type, RankEnum.E)  # Default to E if no rank
            
            # Compare ranks
            if self._is_rank_higher(required_rank, unit_rank):
                logging.info(f"Unit {unit_id} rank {unit_rank} too low for {item_data.name} (requires {required_rank})")
                return False
        
        # Equip the item
        unit.equipped_weapon_index = item_index
        logging.info(f"Unit {unit_id} equipped {item_data.name}")
        return True
    
    def unequip_item(self, unit_id: str) -> bool:
        """
        Unequip the currently equipped item.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            True if the item was unequipped successfully, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            logging.warning(f"Cannot unequip item: Unit {unit_id} not found")
            return False
        
        unit.equipped_weapon_index = -1
        logging.info(f"Unit {unit_id} unequipped item")
        return True
    
    # --- Durability ---
    
    def decrement_item_durability(self, unit_id: str, item_index: int, amount: int = 1) -> bool:
        """
        Decrement the durability of an item in a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_index: Index of the item in the inventory
            amount: Amount to decrement durability by
            
        Returns:
            True if the item still has uses, False if it broke or was removed
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            logging.warning(f"Cannot decrement durability: Invalid unit or item index")
            return False
        
        item_instance = unit.inventory[item_index]
        item_data = self.dataProvider.get_item_data(item_instance.item_id)
        
        # Check if item is indestructible
        if item_data.max_durability <= 0:
            return True
        
        # Decrement durability
        item_instance.current_durability -= amount
        logging.info(f"Item {item_data.name} durability reduced to {item_instance.current_durability}/{item_data.max_durability} for unit {unit_id}")
        
        # Check if item broke
        if item_instance.current_durability <= 0:
            logging.info(f"Item {item_data.name} broke for unit {unit_id}")
            
            # Check if item is repairable
            broken_item_id = self._get_broken_item_id(item_instance.item_id)
            
            if broken_item_id:
                # Replace with broken version
                item_instance.item_id = broken_item_id
                item_instance.current_durability = 0
                logging.info(f"Item replaced with {broken_item_id}")
                return False  # Item broke
            else:
                # Remove non-repairable item
                self.remove_item_from_inventory(unit_id, item_index)
                return False  # Item was removed
        
        return True  # Item still has uses
    
    # --- Repair ---
    
    def repair_item(self, unit_id: str, item_index: int) -> bool:
        """
        Repair a broken item in a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_index: Index of the item in the inventory
            
        Returns:
            True if the item was repaired successfully, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            logging.warning(f"Cannot repair item: Invalid unit or item index")
            return False
        
        item_instance = unit.inventory[item_index]
        
        # Get original item ID from broken item
        original_item_id = self._get_original_item_id_from_broken(item_instance.item_id)
        
        if not original_item_id:
            logging.info(f"Item {item_instance.item_id} is not a known broken item")
            return False
        
        # Get original item data
        original_item_data = self.dataProvider.get_item_data(original_item_id)
        if not original_item_data:
            logging.warning(f"Cannot find original item data for {original_item_id}")
            return False
        
        # Repair the item
        item_instance.item_id = original_item_id
        item_instance.current_durability = original_item_data.max_durability
        logging.info(f"Repaired item for unit {unit_id} to {original_item_data.name} ({item_instance.current_durability}/{original_item_data.max_durability})")
        return True
    
    # --- Trading ---
    
    def initiate_trade(self, unit1_id: str, unit2_id: str) -> Optional[Dict[str, List[ItemInstance]]]:
        """
        Initiate a trade between two units.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            
        Returns:
            Dictionary containing the inventories of both units (and captive if applicable) or None if trade cannot be initiated
        """
        unit1 = self.gameStateManager.get_unit(unit1_id)
        unit2 = self.gameStateManager.get_unit(unit2_id)
        if not unit1 or not unit2:
            logging.warning(f"Cannot initiate trade: One or both units not found")
            return None
        
        # Check adjacency
        if not self._are_units_adjacent(unit1_id, unit2_id):
            logging.info("Units not adjacent for trade")
            return None
        
        # Check if target is ally or captive
        is_target_captive = (unit1.carrying_unit_id == unit2_id and unit2.is_captured)
        is_target_ally = (unit2.faction == unit1.faction)
        
        if not is_target_ally and not is_target_captive:
            logging.info("Cannot trade with target unit (not ally or captive)")
            return None
        
        # Prepare trade data
        trade_data = {
            'unit1_inventory': unit1.inventory,
            'unit2_inventory': unit2.inventory,
            'captive_inventory': None
        }
        
        if is_target_captive:
            # In Thracia, you access the captive's inventory directly
            trade_data['captive_inventory'] = unit2.inventory
            trade_data['unit2_inventory'] = []  # Show unit2 slot as empty, use captive slot
        
        logging.info(f"Initiating trade between {unit1_id} and {unit2_id}" + (" (accessing captive)" if is_target_captive else ""))
        return trade_data
    
    def execute_trade(self, unit1_id: str, unit2_id: str, item_transfers: List[Tuple[str, int, str, int]]) -> bool:
        """
        Execute a trade between two units.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            item_transfers: List of tuples (source_unit_id, source_index, dest_unit_id, dest_index)
            
        Returns:
            True if the trade was executed successfully, False otherwise
        """
        unit1 = self.gameStateManager.get_unit(unit1_id)
        unit2 = self.gameStateManager.get_unit(unit2_id)
        if not unit1 or not unit2:
            logging.warning(f"Cannot execute trade: One or both units not found")
            return False
        
        # Check if unit2 is a captive
        captive_unit = None
        if unit1.carrying_unit_id == unit2_id and unit2.is_captured:
            captive_unit = unit2
        
        # Create copies of inventories to simulate transfers
        unit1_inventory_copy = unit1.inventory.copy()
        unit2_inventory_copy = unit2.inventory.copy() if not captive_unit else []
        captive_inventory_copy = captive_unit.inventory.copy() if captive_unit else []
        
        # Track which slots will be filled
        unit1_filled_slots = set(range(len(unit1_inventory_copy)))
        unit2_filled_slots = set(range(len(unit2_inventory_copy)))
        captive_filled_slots = set(range(len(captive_inventory_copy)))
        
        # Track items to move and their destinations
        items_to_move = []
        
        # First pass: validate all transfers
        for source_unit_id, source_index, dest_unit_id, dest_index in item_transfers:
            # Get source inventory
            source_inventory = None
            source_filled_slots = None
            if source_unit_id == unit1_id:
                source_inventory = unit1_inventory_copy
                source_filled_slots = unit1_filled_slots
            elif source_unit_id == unit2_id:
                source_inventory = unit2_inventory_copy
                source_filled_slots = unit2_filled_slots
            elif source_unit_id == "CAPTIVE" and captive_unit:
                source_inventory = captive_inventory_copy
                source_filled_slots = captive_filled_slots
            else:
                logging.warning(f"Invalid source unit ID: {source_unit_id}")
                return False
            
            # Get destination inventory
            dest_inventory = None
            dest_filled_slots = None
            if dest_unit_id == unit1_id:
                dest_inventory = unit1_inventory_copy
                dest_filled_slots = unit1_filled_slots
            elif dest_unit_id == unit2_id:
                dest_inventory = unit2_inventory_copy
                dest_filled_slots = unit2_filled_slots
            elif dest_unit_id == "CAPTIVE" and captive_unit:
                dest_inventory = captive_inventory_copy
                dest_filled_slots = captive_filled_slots
            else:
                logging.warning(f"Invalid destination unit ID: {dest_unit_id}")
                return False
            
            # Validate source index
            if source_index < 0 or source_index >= len(source_inventory):
                logging.warning(f"Invalid source index: {source_index}")
                return False
            
            # Validate destination index
            if dest_index < 0 or dest_index >= MAX_INVENTORY_SIZE:
                logging.warning(f"Invalid destination index: {dest_index}")
                return False
            
            # Check if destination slot is available or within inventory bounds
            if dest_index >= len(dest_inventory) and dest_index > len(dest_filled_slots):
                logging.warning(f"Invalid destination index: {dest_index}")
                return False
            
            # Mark source slot as empty (unless it's involved in a swap)
            if source_index in source_filled_slots:
                source_filled_slots.remove(source_index)
            
            # Mark destination slot as filled
            dest_filled_slots.add(dest_index)
            
            # Check inventory size limits
            if len(dest_filled_slots) > MAX_INVENTORY_SIZE:
                logging.warning(f"Destination inventory would exceed maximum size")
                return False
            
            # Add to items to move
            items_to_move.append((source_unit_id, source_index, dest_unit_id, dest_index))
        
        # Second pass: create a temporary storage for all items being moved
        temp_storage = {}  # (unit_id, index) -> item
        
        # Store all source items in temporary storage
        for source_unit_id, source_index, dest_unit_id, dest_index in items_to_move:
            # Get source unit
            source_unit = None
            if source_unit_id == unit1_id:
                source_unit = unit1
            elif source_unit_id == unit2_id:
                source_unit = unit2
            elif source_unit_id == "CAPTIVE":
                source_unit = captive_unit
            
            # Store the item
            temp_storage[(source_unit_id, source_index)] = source_unit.inventory[source_index]
            
            # Mark the source slot as empty
            source_unit.inventory[source_index] = None
        
        # Third pass: move items from temporary storage to destinations
        for source_unit_id, source_index, dest_unit_id, dest_index in items_to_move:
            # Get destination unit
            dest_unit = None
            if dest_unit_id == unit1_id:
                dest_unit = unit1
            elif dest_unit_id == unit2_id:
                dest_unit = unit2
            elif dest_unit_id == "CAPTIVE":
                dest_unit = captive_unit
            
            # Get the item from temporary storage
            item_to_move = temp_storage[(source_unit_id, source_index)]
            
            # Check if we need to extend the destination inventory
            while len(dest_unit.inventory) <= dest_index:
                dest_unit.inventory.append(None)
            
            # Move the item
            dest_unit.inventory[dest_index] = item_to_move
            
            # Update equipped weapon indices if needed
            if source_unit_id == dest_unit_id and dest_unit.equipped_weapon_index == source_index:
                # If we're moving an equipped weapon within the same unit, update the equipped index
                dest_unit.equipped_weapon_index = dest_index
            # Special case for swapping items between units where both have equipped weapons
            # In this case, we want to preserve the equipped status for both units
            elif source_unit_id != dest_unit_id:
                # Check if this is part of a swap operation (both units exchanging items)
                is_swap = False
                for s_unit_id, s_idx, d_unit_id, d_idx in items_to_move:
                    if s_unit_id == dest_unit_id and d_unit_id == source_unit_id:
                        is_swap = True
                        break
                
                # If this is a swap and the destination index is the equipped weapon, don't unequip
                if not is_swap and dest_unit.equipped_weapon_index == dest_index:
                    dest_unit.equipped_weapon_index = -1
        
        # Final pass: clean up inventories by removing None entries
        unit1.inventory = [item for item in unit1.inventory if item is not None]
        if not captive_unit:
            unit2.inventory = [item for item in unit2.inventory if item is not None]
        if captive_unit:
            captive_unit.inventory = [item for item in captive_unit.inventory if item is not None]
        
        # Adjust equipped weapon indices if they're now invalid
        if unit1.equipped_weapon_index >= len(unit1.inventory):
            unit1.equipped_weapon_index = -1
        if unit2.equipped_weapon_index >= len(unit2.inventory):
            unit2.equipped_weapon_index = -1
        if captive_unit and captive_unit.equipped_weapon_index >= len(captive_unit.inventory):
            captive_unit.equipped_weapon_index = -1
        
        logging.info(f"Executed trade between {unit1_id} and {unit2_id}")
        return True
    
    # --- Item Usage ---
    
    def get_equipped_weapon(self, unit_id: str) -> Optional[str]:
        """
        Get the equipped weapon of a unit.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            Item ID of the equipped weapon or None if no weapon is equipped
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or unit.equipped_weapon_index < 0 or unit.equipped_weapon_index >= len(unit.inventory):
            return None
        
        item_instance = unit.inventory[unit.equipped_weapon_index]
        return item_instance.item_id
    
    def get_usable_items(self, unit_id: str) -> List[str]:
        """
        Get the list of usable items in a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            
        Returns:
            List of item IDs that can be used by the unit
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit:
            return []
        
        usable_items = []
        for item_instance in unit.inventory:
            item_data = self.dataProvider.get_item_data(item_instance.item_id)
            if not item_data:
                continue
            
            # Check if item is usable (consumable, staff, etc.)
            if item_data.type in [CONSUMABLE, STAFF]:
                usable_items.append(item_instance.item_id)
        
        return usable_items
    
    def use_item(self, unit_id: str, item_index: int, target_id: Optional[str] = None, target_tile: Optional[Tuple[int, int]] = None) -> bool:
        """
        Use an item from a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_index: Index of the item in the inventory
            target_id: ID of the target unit (for items that target units)
            target_tile: Coordinates of the target tile (for items that target tiles)
            
        Returns:
            True if the item was used successfully, False otherwise
        """
        unit = self.gameStateManager.get_unit(unit_id)
        if not unit or item_index < 0 or item_index >= len(unit.inventory):
            logging.warning(f"Cannot use item: Invalid unit or item index")
            return False
        
        item_instance = unit.inventory[item_index]
        item_data = self.dataProvider.get_item_data(item_instance.item_id)
        if not item_data:
            logging.warning(f"Invalid item data for {item_instance.item_id}")
            return False
        
        success = False
        
        # Handle different item types
        if item_data.type == CONSUMABLE:
            # Apply consumable effect
            effect_applied = self._apply_item_effect(unit_id, item_data.effects, target_id)
            if effect_applied:
                # decrement_item_durability returns False when item breaks or is removed
                # but that's actually a success for consumable usage
                self.decrement_item_durability(unit_id, item_index)
                success = True
        
        elif item_data.type == KEY:
            # Use key on lock
            if target_tile and self._is_tile_lock(target_tile):
                lock_opened = self._open_lock(target_tile, getattr(item_data, 'key_type', None))
                if lock_opened:
                    # decrement_item_durability returns False when item breaks or is removed
                    # but that's actually a success for key usage
                    self.decrement_item_durability(unit_id, item_index)
                    success = True
        
        elif item_data.type == SCROLL:
            # Scrolls are passive items that don't get "used" actively
            logging.info(f"Scrolls are passive items and cannot be actively used")
            return False
        
        elif item_data.type == STAFF:
            # Staves are handled by the combat system, not directly through use_item
            logging.info(f"Staves are used through the combat system, not directly")
            return False
        
        # Set unit as acted if item was used successfully
        if success:
            self.gameStateManager.set_unit_acted(unit_id)
            logging.info(f"Unit {unit_id} used item {item_data.name}")
        else:
            logging.info(f"Unit {unit_id} failed to use item {item_data.name}")
        
        return success
    
    # --- Helper Methods ---
    
    def _is_rank_higher(self, rank1: RankEnum, rank2: RankEnum) -> bool:
        """
        Check if rank1 is higher than rank2.
        
        Args:
            rank1: First rank
            rank2: Second rank
            
        Returns:
            True if rank1 is higher than rank2, False otherwise
        """
        rank_values = {
            RankEnum.E: 1,
            RankEnum.D: 2,
            RankEnum.C: 3,
            RankEnum.B: 4,
            RankEnum.A: 5,
            RankEnum.S: 6
        }
        
        return rank_values.get(rank1, 0) > rank_values.get(rank2, 0)
    
    def _get_broken_item_id(self, item_id: str) -> Optional[str]:
        """
        Get the broken version of an item ID.
        
        Args:
            item_id: Original item ID
            
        Returns:
            Broken item ID or None if the item is not repairable
        """
        # This would be implemented based on DataProvider's data structure
        # For now, use a simple convention: prefix "BROKEN_" to the item ID
        item_data = self.dataProvider.get_item_data(item_id)
        if not item_data:
            return None
        
        # Check if item is repairable (weapons and staves typically are)
        if item_data.type in [WEAPON, STAFF]:
            return f"BROKEN_{item_id}"
        
        return None
    
    def _get_original_item_id_from_broken(self, broken_item_id: str) -> Optional[str]:
        """
        Get the original item ID from a broken item ID.
        
        Args:
            broken_item_id: Broken item ID
            
        Returns:
            Original item ID or None if the item is not a broken item
        """
        # This would be implemented based on DataProvider's data structure
        # For now, use a simple convention: remove "BROKEN_" prefix from the item ID
        if broken_item_id.startswith("BROKEN_"):
            return broken_item_id[7:]
        
        return None
    
    def _are_units_adjacent(self, unit1_id: str, unit2_id: str) -> bool:
        """
        Check if two units are adjacent.
        
        Args:
            unit1_id: ID of the first unit
            unit2_id: ID of the second unit
            
        Returns:
            True if the units are adjacent, False otherwise
        """
        # This would typically use MapSystem, but for now implement directly
        unit1 = self.gameStateManager.get_unit(unit1_id)
        unit2 = self.gameStateManager.get_unit(unit2_id)
        if not unit1 or not unit2:
            return False
        
        x1, y1 = unit1.position
        x2, y2 = unit2.position
        
        # Check Manhattan distance
        return abs(x1 - x2) + abs(y1 - y2) == 1
    
    def _apply_item_effect(self, unit_id: str, effects: List[Dict[str, Any]], target_id: Optional[str] = None) -> bool:
        """
        Apply the effects of an item.
        
        Args:
            unit_id: ID of the unit using the item
            effects: List of effect dictionaries
            target_id: ID of the target unit (if applicable)
            
        Returns:
            True if the effects were applied successfully, False otherwise
        """
        # Target defaults to user if not specified
        target_id = target_id or unit_id
        target = self.gameStateManager.get_unit(target_id)
        if not target:
            return False
        
        success = False
        
        for effect in effects:
            effect_type = effect.get('type')
            
            if effect_type == 'HEAL':
                # Healing effect
                amount = effect.get('amount', 0)
                if amount > 0:
                    self.gameStateManager.apply_healing(target_id, amount)
                    success = True
            
            elif effect_type == 'STAT_BOOST':
                # Permanent stat boost
                stat = effect.get('stat')
                amount = effect.get('amount', 0)
                if stat and amount > 0:
                    # This would need to be implemented in GameStateManager
                    # For now, assume it's successful
                    success = True
            
            elif effect_type == 'CURE_STATUS':
                # Cure status effect
                status = effect.get('status')
                if status:
                    status_enum = getattr(StatusEffectEnum, status, None)
                    if status_enum and target.has_status(status_enum):
                        self.gameStateManager.remove_status_effect(target_id, status_enum)
                        success = True
        
        return success
    
    def _is_tile_lock(self, position: Tuple[int, int]) -> bool:
        """
        Check if a tile contains a lock (door or chest).
        
        Args:
            position: Position (x, y)
            
        Returns:
            True if the tile contains a lock, False otherwise
        """
        # Check if the tile has a door or chest object
        terrain_type = self.gameStateManager.get_terrain_type(position)
        
        # Check if it's a door or a chest (based on terrain type)
        if terrain_type in [TerrainTypeEnum.DOOR, TerrainTypeEnum.GATE]:
            return True
            
        # Check if there's a chest object at this position
        # This would typically be stored in map_state.object_states
        # For now, we'll check if there's an object state for this position
        if position in self.gameStateManager.current_game_state.map_state.object_states:
            object_state = self.gameStateManager.current_game_state.map_state.object_states[position]
            # If it's not already opened/looted, it's a valid lock
            if object_state not in [ObjectStateEnum.OPENED, ObjectStateEnum.LOOTED]:
                return True
                
        return False
    
    def _open_lock(self, position: Tuple[int, int], key_type: Optional[str] = None) -> bool:
        """
        Open a lock on a tile.
        
        Args:
            position: Position (x, y)
            key_type: Type of key
            
        Returns:
            True if the lock was opened successfully, False otherwise
        """
        # Check if the tile has a lock
        if not self._is_tile_lock(position):
            return False
            
        terrain_type = self.gameStateManager.get_terrain_type(position)
        
        # Handle doors
        if terrain_type in [TerrainTypeEnum.DOOR, TerrainTypeEnum.GATE]:
            # Check if the key type matches (if specified)
            # For simplicity, we'll assume any key can open any door for now
            # In a full implementation, we'd check key_type against door type
            
            # Update the terrain to an open door/floor
            # This would typically be handled by the MapSystem
            # For now, we'll just update the object state
            self.gameStateManager.current_game_state.map_state.object_states[position] = ObjectStateEnum.OPENED
            logging.info(f"Door at {position} opened")
            return True
            
        # Handle chests
        if position in self.gameStateManager.current_game_state.map_state.object_states:
            # Check if the key type matches (if specified)
            # For simplicity, we'll assume any key can open any chest for now
            
            # Update the chest state to looted
            self.gameStateManager.current_game_state.map_state.object_states[position] = ObjectStateEnum.LOOTED
            
            # In a full implementation, we'd also give the player the chest's contents
            # This would involve adding an item to the unit's inventory
            logging.info(f"Chest at {position} opened")
            return True
            
        return False
    
    def can_unit_carry_item(self, unit) -> bool:
        """
        Check if a unit can carry an additional item.
        
        Args:
            unit: Unit object
            
        Returns:
            True if the unit can carry an additional item, False otherwise
        """
        if not unit:
            return False
            
        return len(unit.inventory) < MAX_INVENTORY_SIZE
    
    def add_gold_to_party(self, amount: int) -> None:
        """
        Add gold to the party's treasury.
        
        Args:
            amount: Amount of gold to add
        """
        # Update the party's gold in the game state
        current_gold = self.gameStateManager.current_game_state.party_gold
        self.gameStateManager.current_game_state.party_gold = current_gold + amount
        logging.info(f"Added {amount} gold to party treasury. New total: {current_gold + amount}")
        
    def add_item_to_unit(self, unit_id: str, item_id: str, quantity: int = 1) -> bool:
        """
        Add an item to a unit's inventory.
        
        Args:
            unit_id: ID of the unit
            item_id: ID of the item to add
            quantity: Quantity of the item to add (default: 1)
            
        Returns:
            True if the item was added successfully, False otherwise
        """
        # For simplicity, we'll just call add_item_to_inventory for each quantity
        success = True
        for _ in range(quantity):
            if not self.add_item_to_inventory(unit_id, item_id):
                success = False
                break
        
        return success