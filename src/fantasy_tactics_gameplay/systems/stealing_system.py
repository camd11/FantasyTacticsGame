"""
Stealing System Module

This module implements the Thracia 776-style stealing mechanic, allowing thieves to take items
directly from adjacent enemies under certain conditions. The system handles checking steal
conditions, identifying stealable items, and executing the item transfer.
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union, Set

from src.core_engine.game_state import GameStateManager, FactionEnum, StatusEffectEnum
from src.core_engine.data_provider import DataProvider

# Constants
FATIGUE_STEAL = 1  # Fatigue cost for stealing

class StealingSystem:
    """
    Manages the stealing mechanic, allowing thieves to take items from adjacent enemies.
    """
    
    def __init__(self):
        """Initialize the StealingSystem."""
        self.gameStateManager = None
        self.dataProvider = None
        self.mapSystem = None
        self.inventorySystem = None
    
    def initialize(self, gameStateManager_instance: GameStateManager, 
                  dataProvider_instance: DataProvider, 
                  mapSystem_instance, 
                  inventorySystem_instance) -> None:
        """
        Initialize the StealingSystem with the necessary dependencies.
        
        Args:
            gameStateManager_instance: Instance of the GameStateManager
            dataProvider_instance: Instance of the DataProvider
            mapSystem_instance: Instance of the MapSystem
            inventorySystem_instance: Instance of the InventorySystem
        """
        self.gameStateManager = gameStateManager_instance
        self.dataProvider = dataProvider_instance
        self.mapSystem = mapSystem_instance
        self.inventorySystem = inventorySystem_instance
        logging.info("StealingSystem initialized.")
    
    def can_initiate_steal(self, attacker, defender) -> bool:
        """
        Determine if the 'Steal' command should be available for the attacker against the defender.
        
        Args:
            attacker: The unit attempting to steal
            defender: The target unit
            
        Returns:
            True if stealing can be initiated, False otherwise
        """
        # Must have the Steal skill (typically granted by Thief class)
        if not self._has_steal_skill(attacker):
            return False
        
        # Must be adjacent
        if not self.mapSystem.is_adjacent(attacker.position, defender.position):
            return False
        
        # Must have inventory space AND defender must have at least one item potentially stealable
        if len(attacker.inventory) >= 7:  # Max inventory size is 7
            return False
            
        if not self.defender_has_any_stealable_item(attacker, defender):
            return False
        
        return True
    
    def defender_has_any_stealable_item(self, attacker, defender) -> bool:
        """
        Check if the defender has any items that can be stolen by the attacker.
        
        Args:
            attacker: The unit attempting to steal
            defender: The target unit
            
        Returns:
            True if the defender has at least one stealable item, False otherwise
        """
        # If defender inventory is empty, return False
        if not defender.inventory:
            return False
        
        # Check if at least one item meets the core steal conditions (AS and Con/Weight)
        for item in defender.inventory:
            # Check AS condition (Attacker AS > Defender AS)
            is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
            
            # Check Weight condition (Item Weight <= Attacker Con)
            can_carry = item.weight <= attacker.stats["con"]
            
            if is_faster and can_carry and not item.is_equipped:
                return True  # Found at least one potentially stealable item
        
        return False  # No items meet the core conditions
    
    def present_steal_item_selection(self, attacker, defender):
        """
        Present the list of stealable items to the player for selection.
        
        Args:
            attacker: The unit attempting to steal
            defender: The target unit
            
        Returns:
            The selected item or None if no items are eligible or selection is cancelled
        """
        eligible_items = []
        is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
        has_space = len(attacker.inventory) < 7  # Max inventory size is 7
        
        # Pre-calculate conditions that apply to all items for efficiency
        if not is_faster or not has_space:
            # If basic conditions fail, no items are eligible
            logging.info("Cannot steal: Attacker not fast enough or inventory full.")
            return None
        
        for item in defender.inventory:
            # Check specific item weight condition
            can_carry = item.weight <= attacker.stats["con"]
            
            # Only non-equipped items can be stolen
            if can_carry and not item.is_equipped:
                eligible_items.append(item)
        
        if not eligible_items:
            # This might happen if all items are too heavy or equipped
            logging.info("No items light enough to steal.")
            return None
        
        # In a real implementation, this would show a UI for item selection
        # For testing purposes, we'll just return the first eligible item
        if eligible_items:
            return eligible_items[0]
        
        return None
    
    def execute_steal(self, attacker, defender, item_to_steal) -> bool:
        """
        Perform the item transfer and apply side effects.
        
        Args:
            attacker: The unit stealing the item
            defender: The target unit
            item_to_steal: The item being stolen
            
        Returns:
            True if the steal was successful, False otherwise
        """
        # Double-check all conditions before modifying state
        is_faster = attacker.calculated_stats["attack_speed"] > defender.calculated_stats["attack_speed"]
        can_carry = item_to_steal.weight <= attacker.stats["con"]
        has_space = len(attacker.inventory) < 7  # Max inventory size is 7
        
        if not (is_faster and can_carry and has_space):
            # Should not happen if UI filtered correctly, but safety check
            logging.error("Execute steal called with invalid conditions.")
            logging.info("Cannot steal this item.")  # Generic failure message
            return False
        
        # 1. Remove item from defender's inventory
        try:
            defender.inventory.remove(item_to_steal)
        except ValueError:
            logging.error("Failed to remove item from defender inventory during steal.")
            return False
        
        # 2. If item was equipped, defender might need to auto-equip next best weapon
        if item_to_steal.is_equipped:
            self._try_auto_equip_weapon(defender)
        
        # 3. Add item to attacker's inventory
        item_to_steal.is_equipped = False  # Stolen items are never equipped immediately
        attacker.inventory.append(item_to_steal)
        
        # 4. Apply fatigue cost to attacker
        attacker.fatigue += FATIGUE_STEAL
        
        # 5. Mark action as consumed for the turn
        attacker.has_acted = True
        
        logging.info(f"{attacker.name} stole {item_to_steal.name} from {defender.name}!")
        return True
    
    # --- Helper Methods ---
    
    def _has_steal_skill(self, unit) -> bool:
        """
        Check if a unit has the Steal skill.
        
        Args:
            unit: The unit to check
            
        Returns:
            True if the unit has the Steal skill, False otherwise
        """
        return "Steal" in unit.skills
    
    def _try_auto_equip_weapon(self, unit) -> None:
        """
        Try to auto-equip the best available weapon for a unit.
        
        Args:
            unit: The unit to equip a weapon for
        """
        # Find the first equippable weapon in the inventory
        for i, item in enumerate(unit.inventory):
            item_data = self.dataProvider.get_item_data(item.item_id)
            if item_data and item_data.type == "WEAPON":
                unit.equipped_weapon_index = i
                return
        
        # If no weapon found, set equipped_weapon_index to -1
        unit.equipped_weapon_index = -1