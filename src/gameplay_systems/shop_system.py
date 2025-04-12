"""
Shop & Armory System

Handles player interaction with shops and armories on the map.
Allows buying and selling items based on map tile properties and shop inventories.
"""

import logging

# Assuming necessary imports from other modules will be added as needed
# from src.core_engine.game_state import GameState, UnitState
# from src.core_engine.data_provider import DataProvider
# from src.gameplay_systems.map_system import MapSystem
# from src.gameplay_systems.inventory_system import InventorySystem
# from src.gameplay_systems.action_system import ActionSystem
# from src.core_engine.event_system import EventSystem # Or a specific event system interface

logger = logging.getLogger(__name__)

class ShopSystem:
    """Manages shop and armory interactions."""

    def __init__(self, game_state_manager, data_provider, unit_system, map_system, inventory_system, action_system, event_system):
        self.game_state_manager = game_state_manager
        self.data_provider = data_provider
        self.unit_system = unit_system
        self.map_system = map_system
        self.inventory_system = inventory_system
        self.action_system = action_system
        self.event_system = event_system
        logger.info("ShopSystem initialized.")

    def can_unit_use_shop_on_tile(self, unit, tile):
        """
        Checks if a unit can interact with a shop/armory on a given tile.

        Args:
            unit (UnitState): The unit attempting interaction.
            tile (TerrainType): The terrain properties of the tile the unit is on.

        Returns:
            bool: True if the unit can use the shop/armory, False otherwise.
        """
        if unit.has_acted:
            logger.debug(f"Unit {unit.id} cannot use shop: already acted.")
            return False

        if not tile or (not tile.is_shop_tile and not tile.is_armory_tile):
            logger.debug(f"Unit {unit.id} cannot use shop: not on a shop/armory tile.")
            return False

        if not tile.associated_shop_id:
            logger.warning(f"Tile at {unit.position} is shop/armory but has no associated_shop_id.")
            return False

        shop_data = self.data_provider.load_shop_inventory(tile.associated_shop_id)
        if not shop_data:
            logger.error(f"Could not load shop inventory for ID: {tile.associated_shop_id}")
            return False

        if shop_data.type == "SecretShop" and shop_data.requires_member_card:
            # Check if unit has "Member Card" item in inventory
            # Assuming InventorySystem has a method like has_item(unit_id, item_id)
            has_member_card = self.inventory_system.has_item(unit.id, "MEMBER_CARD")
            if not has_member_card:
                logger.debug(f"Unit {unit.id} cannot use secret shop {tile.associated_shop_id}: missing Member Card.")
                return False
            logger.debug(f"Unit {unit.id} can use secret shop {tile.associated_shop_id}: has Member Card.")
            return True
        else:
            # Regular shop/armory
            logger.debug(f"Unit {unit.id} can use {shop_data.type} {tile.associated_shop_id}.")
            return True

    def initiate_shop_interaction(self, unit, tile):
        """
        Initiates the shop/armory interaction process.

        Args:
            unit (UnitState): The unit initiating interaction.
            tile (TerrainType): The terrain properties of the tile.

        Returns:
            bool: True if interaction was successfully initiated, False otherwise.
        """
        if self.can_unit_use_shop_on_tile(unit, tile):
            shop_data = self.data_provider.load_shop_inventory(tile.associated_shop_id)
            game_state = self.game_state_manager.current_game_state
            player_gold = game_state.player_gold

            # Mark unit as acted (using ActionSystem)
            self.action_system.mark_unit_acted(unit)
            logger.info(f"Unit {unit.id} initiated interaction with {shop_data.type} {shop_data.shop_id}. Action consumed.")

            # Trigger UI event (using EventSystem)
            ui_event_type = ""
            if tile.is_armory_tile:
                ui_event_type = "OPEN_ARMORY_UI"
            elif tile.is_shop_tile:
                ui_event_type = "OPEN_SHOP_UI"

            if ui_event_type:
                self.event_system.publish(ui_event_type, {
                    "unit_id": unit.id,
                    "shop_data": shop_data,
                    "player_gold": player_gold
                })
                logger.debug(f"Published {ui_event_type} event for unit {unit.id}.")
                return True
            else:
                logger.error(f"Tile at {unit.position} is shop/armory but type couldn't be determined for UI.")
                return False
        else:
            logger.warning(f"Unit {unit.id} failed to initiate shop interaction at {unit.position}.")
            # Optionally publish a failure event or play an error sound via event system
            self.event_system.publish("SHOP_INTERACTION_FAILED", {"unit_id": unit.id, "reason": "Cannot use shop here"})
            return False

    # --- Purchasing Methods ---
    def can_purchase_item(self, unit, item_id, shop_data, player_gold):
        """
        Checks if a unit can purchase a specific item from the shop.

        Args:
            unit (UnitState): The unit attempting the purchase.
            item_id (str): The ID of the item to purchase.
            shop_data (MockShopInventory): The inventory data of the current shop.
            player_gold (int): The current amount of player gold.

        Returns:
            bool: True if the purchase is possible, False otherwise.
        """
        item_entry = next((item for item in shop_data.available_items if item.item_id == item_id), None)
        if item_entry is None:
            logger.debug(f"Purchase check failed: Item {item_id} not found in shop {shop_data.shop_id}.")
            return False # Item not sold here

        if item_entry.stock == 0:
            logger.debug(f"Purchase check failed: Item {item_id} is out of stock.")
            return False # Out of stock

        item_data = self.data_provider.get_item_data(item_id)
        if not item_data:
             logger.error(f"Purchase check failed: Could not load item data for {item_id}.")
             return False
        if item_data.buy_price < 0:
            logger.debug(f"Purchase check failed: Item {item_id} is not buyable (price < 0).")
            return False # Item not buyable

        if player_gold < item_data.buy_price:
            logger.debug(f"Purchase check failed: Not enough gold ({player_gold}) for {item_id} (cost {item_data.buy_price}).")
            return False # Not enough gold

        # Check inventory space (using InventorySystem mock)
        # Assuming InventorySystem has is_inventory_full(unit_id)
        # And GameState has convoy_is_available flag
        if self.inventory_system.is_inventory_full(unit.id):
            game_state = self.game_state_manager.current_game_state
            # Convoy check based on Thracia spec (assume no convoy unless explicitly available)
            convoy_available = getattr(game_state, 'convoy_is_available', False)
            if convoy_available:
                logger.debug(f"Purchase check: Inventory full for {unit.id}, but convoy is available for {item_id}.")
                return True # Can send to convoy
            else:
                logger.debug(f"Purchase check failed: Inventory full for {unit.id}, no convoy available for {item_id}.")
                return False # Inventory full, no convoy
        else:
            logger.debug(f"Purchase check passed for {unit.id} buying {item_id}.")
            return True # Has space in inventory
        return False # Placeholder

    def execute_purchase(self, unit, item_id, shop_data):
        """
        Executes the purchase of an item for a unit.

        Args:
            unit (UnitState): The unit making the purchase.
            item_id (str): The ID of the item being purchased.
            shop_data (MockShopInventory): The inventory data of the current shop.

        Returns:
            bool: True if the purchase was successful, False otherwise.
        """
        game_state = self.game_state_manager.current_game_state
        player_gold = game_state.player_gold

        if not self.can_purchase_item(unit, item_id, shop_data, player_gold):
            logger.warning(f"Purchase execution failed for {unit.id} buying {item_id}: Pre-check failed (can_purchase_item returned False).")
            self.event_system.publish("PURCHASE_FAILED", {"unit_id": unit.id, "item_id": item_id, "reason": "Pre-check failed"})
            return False

        item_data = self.data_provider.get_item_data(item_id)
        item_entry = next((item for item in shop_data.available_items if item.item_id == item_id), None)

        # --- Execute Purchase ---
        # 1. Deduct gold
        game_state.player_gold -= item_data.buy_price
        logger.info(f"Deducted {item_data.buy_price} gold for purchase. New total: {game_state.player_gold}")

        # 2. Add item
        # Assuming InventorySystem has add_item_to_inventory(unit_id, item_id)
        # Convoy logic deferred based on spec
        convoy_available = getattr(game_state, 'convoy_is_available', False)
        item_added = False
        if self.inventory_system.is_inventory_full(unit.id) and convoy_available:
             # Add to convoy (assuming a method exists, e.g., on game_state_manager or a convoy system)
             # success = self.game_state_manager.add_item_to_convoy(item_id) # Example
             logger.warning(f"Item {item_id} sent to convoy (convoy logic not fully implemented).")
             # For now, assume success if convoy is available
             item_added = True
             self.event_system.publish("ITEM_SENT_TO_CONVOY", {"item_id": item_id})
        else:
            # Add to unit inventory
            item_added = self.inventory_system.add_item_to_inventory(unit.id, item_id)
            if item_added:
                 logger.info(f"Added item {item_id} to unit {unit.id}'s inventory.")
                 self.event_system.publish("ITEM_ADDED_TO_INVENTORY", {"unit_id": unit.id, "item_id": item_id})
            else:
                 # This case should ideally be caught by can_purchase_item, but handle defensively
                 logger.error(f"Failed to add item {item_id} to unit {unit.id}'s inventory despite passing checks.")
                 # Rollback gold deduction? Or handle error state appropriately.
                 # For now, log error and return False.
                 game_state.player_gold += item_data.buy_price # Rollback gold
                 self.event_system.publish("PURCHASE_FAILED", {"unit_id": unit.id, "item_id": item_id, "reason": "Failed to add item to inventory"})
                 return False

        # 3. Decrement stock if limited
        if item_entry and item_entry.stock > 0:
            item_entry.stock -= 1
            logger.info(f"Decremented stock for {item_id} in shop {shop_data.shop_id}. New stock: {item_entry.stock}")
            # Persist stock change if needed (e.g., call data_provider.update_shop_inventory)
            # self.data_provider.update_shop_inventory(shop_data) # Assuming this method exists

        logger.info(f"Purchase successful: Unit {unit.id} bought {item_id}.")
        self.event_system.publish("PURCHASE_SUCCESSFUL", {"unit_id": unit.id, "item_id": item_id, "cost": item_data.buy_price})
        return True

    # --- Selling Methods ---
    def can_sell_item(self, unit, item_instance_id):
        """
        Checks if a unit can sell a specific item instance from their inventory.

        Args:
            unit (UnitState): The unit attempting to sell.
            item_instance_id (str): The unique instance ID of the item in the unit's inventory.

        Returns:
            bool: True if the item can be sold, False otherwise.
        """
        # Assuming InventorySystem has get_item_instance(unit_id, instance_id)
        item_instance = self.inventory_system.get_item_instance(unit.id, item_instance_id)
        if not item_instance:
            logger.warning(f"Sell check failed: Item instance {item_instance_id} not found in unit {unit.id}'s inventory.")
            return False

        item_data = self.data_provider.get_item_data(item_instance.item_id)
        if not item_data:
            logger.error(f"Sell check failed: Could not load item data for {item_instance.item_id}.")
            return False

        if not item_data.is_sellable:
            logger.debug(f"Sell check failed: Item {item_instance.item_id} is flagged as unsellable.")
            return False

        if item_data.sell_price <= 0:
            logger.debug(f"Sell check failed: Item {item_instance.item_id} has a sell price <= 0.")
            return False # Cannot sell if value is 0 or less

        # Optional: Prevent selling equipped item
        # equipped_weapon_id = self.unit_system.get_equipped_weapon_instance_id(unit.id)
        # if equipped_weapon_id == item_instance_id:
        #     logger.debug(f"Sell check failed: Item {item_instance_id} is equipped by unit {unit.id}.")
        #     return False

        logger.debug(f"Sell check passed for unit {unit.id} selling item instance {item_instance_id} ({item_instance.item_id}).")
        return True

    def execute_sell(self, unit, item_instance_id):
        """
        Executes the sale of an item instance from a unit's inventory.

        Args:
            unit (UnitState): The unit selling the item.
            item_instance_id (str): The unique instance ID of the item to sell.

        Returns:
            bool: True if the sale was successful, False otherwise.
        """
        if not self.can_sell_item(unit, item_instance_id):
            logger.warning(f"Sell execution failed for unit {unit.id} selling instance {item_instance_id}: Pre-check failed.")
            self.event_system.publish("SELL_FAILED", {"unit_id": unit.id, "item_instance_id": item_instance_id, "reason": "Pre-check failed"})
            return False

        item_instance = self.inventory_system.get_item_instance(unit.id, item_instance_id)
        # Double check instance exists (should be caught by can_sell_item, but defensive)
        if not item_instance:
             logger.error(f"Sell execution failed: Item instance {item_instance_id} not found in unit {unit.id}'s inventory during execution.")
             self.event_system.publish("SELL_FAILED", {"unit_id": unit.id, "item_instance_id": item_instance_id, "reason": "Item not found during execution"})
             return False

        item_data = self.data_provider.get_item_data(item_instance.item_id)
        # Double check item data exists
        if not item_data:
             logger.error(f"Sell execution failed: Could not load item data for {item_instance.item_id} during execution.")
             self.event_system.publish("SELL_FAILED", {"unit_id": unit.id, "item_instance_id": item_instance_id, "reason": "Item data not found during execution"})
             return False

        game_state = self.game_state_manager.current_game_state

        # --- Execute Sell ---
        # 1. Add gold
        sell_price = item_data.sell_price
        game_state.player_gold += sell_price
        logger.info(f"Added {sell_price} gold for selling {item_instance.item_id}. New total: {game_state.player_gold}")

        # 2. Remove item
        # Assuming InventorySystem has remove_item_from_inventory(unit_id, instance_id)
        item_removed = self.inventory_system.remove_item_from_inventory(unit.id, item_instance_id)

        if item_removed:
            logger.info(f"Removed item instance {item_instance_id} ({item_instance.item_id}) from unit {unit.id}'s inventory.")
            self.event_system.publish("SELL_SUCCESSFUL", {"unit_id": unit.id, "item_id": item_instance.item_id, "instance_id": item_instance_id, "gold_gained": sell_price})
            return True
        else:
            # This indicates an issue with inventory removal after checks passed
            logger.error(f"Failed to remove item instance {item_instance_id} from unit {unit.id}'s inventory after successful sell check.")
            # Rollback gold addition
            game_state.player_gold -= sell_price
            self.event_system.publish("SELL_FAILED", {"unit_id": unit.id, "item_instance_id": item_instance_id, "reason": "Failed to remove item from inventory"})
            return False